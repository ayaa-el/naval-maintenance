from django.contrib.auth import views as auth_views, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages

from .forms import ProfilForm

from equipements.models import Equipement
from navires.models import Navire, Escale, Ouvrage
from conventionnement.models import FicheIntervention, OrdreTravail, BonLivraison, Facture

ROLES_ANP = ["SUPERVISEUR_ANP", "TECHNICIEN_ANP"]
ROLES_HADDOUN = ["TECHNICIEN_HADDOUN", "CHEF_EQUIPE"]


def choix_organisation(request):
    """Première page vue : choisir Haddoun ou ANP avant de se connecter."""
    return render(request, "comptes/choix_organisation.html")


class ConnexionView(auth_views.LoginView):
    """Écran de connexion, propre à l'organisation choisie juste avant."""
    template_name = "comptes/connexion.html"

    def dispatch(self, request, *args, **kwargs):
        self.organisation = kwargs.get("organisation")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organisation"] = self.organisation
        context["organisation_label"] = "Haddoun" if self.organisation == "haddoun" else "ANP"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.get_user()
        roles_attendus = ROLES_ANP if self.organisation == "anp" else ROLES_HADDOUN

        if user.role not in roles_attendus:
            logout(self.request)
            label = "ANP" if self.organisation == "anp" else "Haddoun"
            messages.error(self.request, f"Ce compte n'appartient pas à l'espace {label}.")
            return redirect("comptes:connexion", organisation=self.organisation)

        return response

    def get_success_url(self):
        return reverse_lazy("comptes:accueil")


def deconnexion(request):
    logout(request)
    return redirect("comptes:choix_organisation")


@login_required
def mon_profil(request):
    if request.method == 'POST':
        form = ProfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect('comptes:mon_profil')
    else:
        form = ProfilForm(instance=request.user)
    
    return render(request, "comptes/profil.html", {'form': form})


@login_required
def accueil(request):
    """Point d'entrée unique après connexion : tableau de bord dédié selon le rôle exact."""
    user = request.user
    role = user.role

    # ─── SUPERVISEUR ANP ─────────────────────────────────────────────────────
    if role == "SUPERVISEUR_ANP":
        from rh.models import TacheReparation, Employe
        context = {
            "total_equipements": Equipement.objects.count(),
            "equipements_en_service": Equipement.objects.filter(statut=Equipement.Statut.EN_SERVICE).count(),
            "equipements_en_reparation": Equipement.objects.filter(statut=Equipement.Statut.EN_REPARATION).count(),
            "equipements_hors_service": Equipement.objects.filter(statut=Equipement.Statut.HORS_SERVICE).count(),
            "fiches_ouvertes": FicheIntervention.objects.filter(equipement__isnull=False).count(),
            "ot_attente_validation": OrdreTravail.objects.filter(
                fiche_intervention__equipement__isnull=False,
                status=OrdreTravail.Statut.ATTENTE_VALIDATION_ANP
            ).count(),
            "bl_attente_validation": BonLivraison.objects.filter(
                ordre_travail__fiche_intervention__equipement__isnull=False,
                statut=BonLivraison.Statut.EN_ATTENTE
            ).count(),
            "factures_a_valider": Facture.objects.filter(statut=Facture.Statut.NON_PAYEE).count(),
            "total_employes": Employe.objects.filter(actif=True).count(),
            "taches_recentes": TacheReparation.objects.all().order_by("-date_tache")[:8],
            "equipements_list": Equipement.objects.all().order_by("nom"),
        }
        return render(request, "comptes/dashboard_superviseur_anp.html", context)

    # ─── TECHNICIEN ANP ──────────────────────────────────────────────────────
    elif role == "TECHNICIEN_ANP":
        from rh.models import TacheReparation
        # CORRECTIF: precision_probleme est un TextField (jamais NULL). Utiliser exact=""
        fiches_a_diagnostiquer = FicheIntervention.objects.filter(
            equipement__isnull=False,
            precision_probleme__exact=""
        )
        context = {
            "fiches_a_diagnostiquer": fiches_a_diagnostiquer,
            "fiches_a_diagnostiquer_count": fiches_a_diagnostiquer.count(),
            "navires_en_escale": Escale.objects.filter(date_sortie__isnull=True).count(),
            "taches_recentes": TacheReparation.objects.filter(saisi_par=user).order_by("-date_tache")[:5],
        }
        return render(request, "comptes/dashboard_technicien_anp.html", context)

    # ─── SUPERVISEUR HADDOUN (CHEF_EQUIPE) ───────────────────────────────────
    elif role == "CHEF_EQUIPE":
        from rh.models import TacheReparation
        ouvrages = Ouvrage.objects.all().order_by("id_ouvrage")
        occupation_ouvrages = []
        for ouvrage in ouvrages:
            escales = Escale.objects.filter(ouvrage=ouvrage, date_sortie__isnull=True)
            occupation_ouvrages.append({"ouvrage": ouvrage, "escales": escales})

        context = {
            "occupation_ouvrages": occupation_ouvrages,
            "taches_recentes": TacheReparation.objects.all().order_by("-date_tache")[:5],
            # CORRECTIF: TextField - utiliser exclude au lieu de isnull
            "fiches_avec_diagnostic": FicheIntervention.objects.filter(
                equipement__isnull=False,
                ordre_travail__isnull=True
            ).exclude(precision_probleme__exact="").count(),
            "ot_termines_sans_bl": OrdreTravail.objects.filter(
                status=OrdreTravail.Statut.TERMINE,
                bon_livraison__isnull=True
            ).count(),
            "bl_valides_sans_facture": BonLivraison.objects.filter(
                statut=BonLivraison.Statut.VALIDE,
                facture__isnull=True
            ).count(),
            "factures_en_attente_anp": Facture.objects.filter(statut=Facture.Statut.NON_PAYEE).count(),
            "recent_fiches": FicheIntervention.objects.filter(
                equipement__isnull=False
            ).exclude(precision_probleme__exact="").order_by("-date_creation")[:5],
        }
        return render(request, "comptes/dashboard_superviseur_haddoun.html", context)

    # ─── TECHNICIEN HADDOUN ──────────────────────────────────────────────────
    else:  # TECHNICIEN_HADDOUN
        ot_valides = OrdreTravail.objects.filter(
            status=OrdreTravail.Statut.VALIDE
        ).order_by("-id")
        context = {
            "ot_valides": ot_valides,
            "ot_valides_count": ot_valides.count(),
            "ot_termines": OrdreTravail.objects.filter(status=OrdreTravail.Statut.TERMINE).count(),
        }
        return render(request, "comptes/dashboard_technicien_haddoun.html", context)