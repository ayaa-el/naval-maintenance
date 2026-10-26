from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from .models import FicheIntervention, OrdreTravail, BonLivraison, Facture, LigneOrdreTravail
from .forms import (
    FicheInterventionEquipementForm,
    FicheInterventionNavireForm,
    FicheInterventionEditForm,
    DiagnosticForm,
    OrdreTravailValidationForm,
    BonLivraisonForm,
    FactureForm,
    OrdreTravailUnlockForm,
    OrdreTravailEditForm,
    BonLivraisonValidationForm,
    LigneOrdreTravailFormSet,
    LigneBonLivraisonFormSet,
)

ALL_ROLES = {"SUPERVISEUR_ANP", "TECHNICIEN_ANP", "CHEF_EQUIPE", "TECHNICIEN_HADDOUN"}
ANP_ROLES = {"TECHNICIEN_ANP", "SUPERVISEUR_ANP"}
HADDOUN_ROLES = {"CHEF_EQUIPE", "TECHNICIEN_HADDOUN"}


# ─── Fiches d'Intervention ───────────────────────────────────────────────────

@login_required
def liste_fiches(request):
    """Vue d'ensemble de toutes les fiches d'intervention."""
    fiches = FicheIntervention.objects.all().order_by("-date_creation")
    return render(request, "conventionnement/liste_fiches.html", {"fiches": fiches})


@login_required
def creer_fiche_equipement(request):
    if request.user.role not in ["SUPERVISEUR_ANP", "TECHNICIEN_ANP"]:
        raise PermissionDenied("Seul le personnel ANP peut créer une fiche équipement.")

    if request.method == "POST":
        form = FicheInterventionEquipementForm(request.POST)
        if form.is_valid():
            fiche = form.save(commit=False)
            fiche.cree_par = request.user
            fiche.save()
            messages.success(request, f"Fiche {fiche.numero_fiche} créée avec succès.")
            return redirect("conventionnement:detail_fiche", fiche_id=fiche.id)
    else:
        form = FicheInterventionEquipementForm()

    return render(request, "conventionnement/creer_fiche_equipement.html", {"form": form})


@login_required
def creer_fiche_navire(request, escale_id):
    """Technicien ANP crée une fiche pour un navire (Escale)."""
    if request.user.role != "TECHNICIEN_ANP":
        raise PermissionDenied("Seul le Technicien ANP peut créer une fiche navire.")

    from navires.models import Escale
    escale = get_object_or_404(Escale, pk=escale_id)

    if request.method == "POST":
        form = FicheInterventionNavireForm(request.POST)
        if form.is_valid():
            fiche = form.save(commit=False)
            fiche.cree_par = request.user
            fiche.escale = escale
            fiche.save()
            messages.success(request, f"Fiche {fiche.numero_fiche} créée avec succès.")
            return redirect("conventionnement:detail_fiche", fiche_id=fiche.id)
    else:
        form = FicheInterventionNavireForm(initial={'escale': escale})

    return render(request, "conventionnement/creer_fiche_navire.html", {"form": form, "escale": escale})


@login_required
def modifier_fiche(request, fiche_id):
    """Modifier la fiche d'intervention avant qu'un OT existe (Superviseur ANP)."""
    fiche = get_object_or_404(FicheIntervention, pk=fiche_id)
    if request.user.role != "SUPERVISEUR_ANP":
        raise PermissionDenied("Seul le Superviseur ANP peut modifier une fiche d'intervention.")
    if hasattr(fiche, "ordre_travail"):
        raise PermissionDenied("Impossible de modifier une fiche ayant déjà un Ordre de Travail.")

    if request.method == "POST":
        form = FicheInterventionEditForm(request.POST, instance=fiche)
        if form.is_valid():
            form.save()
            messages.success(request, "Fiche d'intervention modifiée.")
            return redirect("conventionnement:detail_fiche", fiche_id=fiche.id)
    else:
        form = FicheInterventionEditForm(instance=fiche)

    return render(request, "conventionnement/modifier_fiche.html", {"form": form, "fiche": fiche})


@login_required
def supprimer_fiche(request, fiche_id):
    """Supprimer la fiche avant qu'un OT existe (Superviseur ANP)."""
    fiche = get_object_or_404(FicheIntervention, pk=fiche_id)
    if request.user.role != "SUPERVISEUR_ANP":
        raise PermissionDenied("Seul le Superviseur ANP peut supprimer une fiche.")
    if hasattr(fiche, "ordre_travail"):
        raise PermissionDenied("Impossible de supprimer une fiche ayant déjà un Ordre de Travail.")

    if request.method == "POST":
        numero = fiche.numero_fiche
        fiche.delete()
        messages.success(request, f"Fiche {numero} supprimée.")
        return redirect("conventionnement:liste_fiches")

    return render(request, "conventionnement/supprimer_fiche.html", {"fiche": fiche})


@login_required
def detail_fiche(request, fiche_id):
    fiche = get_object_or_404(FicheIntervention, pk=fiche_id)
    if request.user.role not in ALL_ROLES:
        raise PermissionDenied
    return render(request, "conventionnement/detail_fiche.html", {"fiche": fiche})


@login_required
def ajouter_diagnostic(request, fiche_id):
    """Haddoun (Technicien ou Superviseur) renseigne le diagnostic technique."""
    fiche = get_object_or_404(FicheIntervention, pk=fiche_id)
    if request.user.role not in ["TECHNICIEN_HADDOUN", "CHEF_EQUIPE"]:
        raise PermissionDenied("Seul Haddoun (Technicien ou Superviseur) peut renseigner le diagnostic technique.")
    if hasattr(fiche, "ordre_travail"):
        fiche.ordre_travail.assert_can_be_modified_by(request.user)

    if request.method == "POST":
        form = DiagnosticForm(request.POST, instance=fiche)
        if form.is_valid():
            # Si un diagnostic prédéfini a été choisi et que le champ libre est vide, on l'utilise
            predefined = request.POST.get("diagnostic_predefined", "")
            fiche = form.save(commit=False)
            if predefined and not fiche.precision_probleme:
                fiche.precision_probleme = predefined
            fiche.traite_par = request.user
            fiche.save()
            messages.success(request, "Diagnostic technique enregistré.")
            return redirect("conventionnement:detail_fiche", fiche_id=fiche.id)
    else:
        form = DiagnosticForm(instance=fiche)

    return render(request, "conventionnement/ajouter_diagnostic.html", {"form": form, "fiche": fiche})


# ─── Ordre de Travail ─────────────────────────────────────────────────────────

@login_required
def creer_ordre_travail(request, fiche_id):
    """Superviseur Haddoun (CHEF_EQUIPE) crée l'OT avec ses lignes de service après diagnostic."""
    fiche = get_object_or_404(FicheIntervention, pk=fiche_id)
    if request.user.role != "CHEF_EQUIPE":
        raise PermissionDenied("Seul le Superviseur Haddoun peut créer un ordre de travail.")
    if hasattr(fiche, "ordre_travail"):
        messages.info(request, "Un OT existe déjà pour cette fiche.")
        return redirect("conventionnement:detail_ordre", ordre_id=fiche.ordre_travail.id)
    if not fiche.precision_probleme:
        raise PermissionDenied("Le diagnostic technique doit être renseigné par Haddoun avant de créer l'OT.")

    if request.method == "POST":
        # Crée l'OT d'abord pour le formset
        ordre = OrdreTravail(fiche_intervention=fiche, cree_par=request.user)
        ordre.save()
        formset = LigneOrdreTravailFormSet(request.POST, instance=ordre)
        if formset.is_valid():
            lignes = formset.save(commit=False)
            for ligne in lignes:
                ligne.ordre_travail = ordre
                ligne.save()
            for obj in formset.deleted_objects:
                obj.delete()
            ordre.calculer_montant_total()
            messages.success(request, f"Ordre de travail {ordre.numero_ordre} créé.")
            return redirect("conventionnement:detail_ordre", ordre_id=ordre.id)
        else:
            # Annuler la création si le formset est invalide
            ordre.delete()
    else:
        formset = LigneOrdreTravailFormSet()

    return render(request, "conventionnement/creer_ordre_travail.html", {
        "formset": formset,
        "fiche": fiche,
    })


@login_required
def modifier_ordre_travail(request, ordre_id):
    """Superviseur Haddoun modifie les lignes de l'OT AVANT validation ANP."""
    ordre = get_object_or_404(OrdreTravail, pk=ordre_id)
    if request.user.role != "CHEF_EQUIPE":
        raise PermissionDenied("Seul le Superviseur Haddoun peut modifier l'OT.")
    if ordre.status not in [OrdreTravail.Statut.ATTENTE_VALIDATION_ANP, OrdreTravail.Statut.REFUSE]:
        raise PermissionDenied("L'OT ne peut être modifié qu'avant validation ou après refus.")

    if request.method == "POST":
        formset = LigneOrdreTravailFormSet(request.POST, instance=ordre)
        if formset.is_valid():
            lignes = formset.save(commit=False)
            for ligne in lignes:
                ligne.ordre_travail = ordre
                ligne.save()
            for obj in formset.deleted_objects:
                obj.delete()
            ordre.calculer_montant_total()
            messages.success(request, "Ordre de travail mis à jour.")
            return redirect("conventionnement:detail_ordre", ordre_id=ordre.id)
    else:
        formset = LigneOrdreTravailFormSet(instance=ordre)

    return render(request, "conventionnement/modifier_ot.html", {"formset": formset, "ordre": ordre})


@login_required
def supprimer_ordre_travail(request, ordre_id):
    """Superviseur Haddoun supprime l'OT AVANT validation ANP."""
    ordre = get_object_or_404(OrdreTravail, pk=ordre_id)
    if request.user.role != "CHEF_EQUIPE":
        raise PermissionDenied("Seul le Superviseur Haddoun peut supprimer l'OT.")
    if ordre.status not in [OrdreTravail.Statut.ATTENTE_VALIDATION_ANP, OrdreTravail.Statut.REFUSE]:
        raise PermissionDenied("L'OT ne peut être supprimé qu'avant validation ou après refus.")

    if request.method == "POST":
        fiche_id = ordre.fiche_intervention.id
        numero = ordre.numero_ordre
        ordre.delete()
        messages.success(request, f"Ordre de travail {numero} supprimé.")
        return redirect("conventionnement:detail_fiche", fiche_id=fiche_id)

    return render(request, "conventionnement/supprimer_ot.html", {"ordre": ordre})


@login_required
def generer_ordre_travail(request, fiche_id):
    fiche = get_object_or_404(FicheIntervention, pk=fiche_id, escale__isnull=False)
    if request.user.role != "SUPERVISEUR_ANP":
        raise PermissionDenied("Seul le Superviseur ANP peut générer un ordre de travail pour un navire.")
    if hasattr(fiche, "ordre_travail"):
        messages.info(request, "Un ordre de travail existe déjà pour cette fiche.")
        return redirect("conventionnement:detail_fiche", fiche_id=fiche.id)

    ordre = OrdreTravail.objects.create(fiche_intervention=fiche, cree_par=request.user)
    ordre.generer_depuis_taches()
    messages.success(request, f"Ordre de travail {ordre.numero_ordre} créé pour la fiche navire.")
    return redirect("conventionnement:detail_ordre", ordre_id=ordre.id)


@login_required
def detail_ordre(request, ordre_id):
    ordre = get_object_or_404(OrdreTravail, pk=ordre_id)
    if request.user.role not in ALL_ROLES:
        raise PermissionDenied
    return render(request, "conventionnement/detail_ordre.html", {"ordre": ordre})


@login_required
def valider_refuser_ordre(request, ordre_id):
    """Superviseur ANP valide ou refuse l'OT."""
    ordre = get_object_or_404(OrdreTravail, pk=ordre_id)
    if request.user.role != "SUPERVISEUR_ANP":
        raise PermissionDenied("Seul le Superviseur ANP peut valider un ordre de travail.")
    if not ordre.can_be_validated():
        raise PermissionDenied("Cet ordre ne peut pas être validé ou refusé.")

    if request.method == "POST":
        form = OrdreTravailValidationForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data["status"]
            ordre.valide_par = request.user
            ordre.date_validation = timezone.now().date()
            ordre.refuse_commentaire = form.cleaned_data["refuse_commentaire"]
            ordre.status = status
            ordre.save()
            messages.success(request, "Statut de l'ordre de travail mis à jour.")
            return redirect("conventionnement:detail_ordre", ordre_id=ordre.id)
    else:
        form = OrdreTravailValidationForm()

    return render(request, "conventionnement/valider_refuser_ordre.html", {"form": form, "ordre": ordre})


@login_required
def realiser_intervention(request, ordre_id):
    """Technicien Haddoun marque l'intervention comme réalisée."""
    ordre = get_object_or_404(OrdreTravail, pk=ordre_id)
    if request.user.role not in ["TECHNICIEN_HADDOUN", "CHEF_EQUIPE"]:
        raise PermissionDenied("Seul le Technicien/Superviseur Haddoun peut réaliser l'intervention.")
    if not ordre.can_be_realized():
        raise PermissionDenied("L'ordre doit être validé par l'ANP avant d'être réalisé.")

    if request.method == "POST":
        ordre.realise_par = request.user
        ordre.date_realisation = timezone.now().date()
        ordre.status = OrdreTravail.Statut.TERMINE
        ordre.save()
        messages.success(request, "Intervention marquée comme réalisée.")
        return redirect("conventionnement:detail_ordre", ordre_id=ordre.id)

    return render(request, "conventionnement/realiser_intervention.html", {"ordre": ordre})


# ─── Bon de Livraison ─────────────────────────────────────────────────────────

@login_required
def creer_bon_livraison(request, ordre_id):
    """Superviseur Haddoun crée le BL avec les prix après réalisation."""
    ordre = get_object_or_404(OrdreTravail, pk=ordre_id)
    if request.user.role != "CHEF_EQUIPE":
        raise PermissionDenied("Seul le Superviseur Haddoun peut créer un bon de livraison.")
    if not ordre.can_create_bonlivraison():
        raise PermissionDenied("Le bon de livraison ne peut pas être créé pour cet ordre.")

    if request.method == "POST":
        form = BonLivraisonForm(request.POST)
        formset = LigneBonLivraisonFormSet(request.POST, instance=ordre)
        if form.is_valid() and formset.is_valid():
            bon = form.save(commit=False)
            bon.ordre_travail = ordre
            bon.save()
            formset.save()
            ordre.calculer_montant_total()  # Recalculer le montant total avec les prix saisis
            messages.success(request, f"Bon de livraison {bon.numero_bon} créé.")
            return redirect("conventionnement:detail_ordre", ordre_id=ordre.id)
    else:
        form = BonLivraisonForm()
        formset = LigneBonLivraisonFormSet(instance=ordre)

    return render(request, "conventionnement/creer_bon_livraison.html", {
        "form": form,
        "formset": formset,
        "ordre": ordre,
    })


@login_required
def modifier_bon_livraison(request, bon_id):
    """Superviseur Haddoun modifie le BL AVANT validation ANP."""
    bon = get_object_or_404(BonLivraison, pk=bon_id)
    ordre = bon.ordre_travail
    if request.user.role != "CHEF_EQUIPE":
        raise PermissionDenied("Seul le Superviseur Haddoun peut modifier le bon de livraison.")
    if bon.statut != BonLivraison.Statut.EN_ATTENTE:
        raise PermissionDenied("Le BL ne peut être modifié qu'avant validation ANP.")

    if request.method == "POST":
        form = BonLivraisonForm(request.POST, instance=bon)
        formset = LigneBonLivraisonFormSet(request.POST, instance=ordre)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            ordre.calculer_montant_total()  # Recalculer le total
            messages.success(request, "Bon de livraison mis à jour.")
            return redirect("conventionnement:detail_ordre", ordre_id=ordre.id)
    else:
        form = BonLivraisonForm(instance=bon)
        formset = LigneBonLivraisonFormSet(instance=ordre)

    return render(request, "conventionnement/modifier_bl.html", {
        "form": form,
        "formset": formset,
        "bon": bon,
        "ordre": ordre,
    })


@login_required
def supprimer_bon_livraison(request, bon_id):
    """Superviseur Haddoun supprime le BL AVANT validation ANP."""
    bon = get_object_or_404(BonLivraison, pk=bon_id)
    ordre = bon.ordre_travail
    if request.user.role != "CHEF_EQUIPE":
        raise PermissionDenied("Seul le Superviseur Haddoun peut supprimer le bon de livraison.")
    if bon.statut != BonLivraison.Statut.EN_ATTENTE:
        raise PermissionDenied("Le BL ne peut être supprimé qu'avant validation ANP.")

    if request.method == "POST":
        numero = bon.numero_bon
        bon.delete()
        messages.success(request, f"Bon de livraison {numero} supprimé.")
        return redirect("conventionnement:detail_ordre", ordre_id=ordre.id)

    return render(request, "conventionnement/supprimer_bl.html", {"bon": bon, "ordre": ordre})


@login_required
def valider_bon_livraison(request, bon_id):
    """Superviseur ANP valide ou refuse le BL."""
    bon = get_object_or_404(BonLivraison, pk=bon_id)
    ordre = bon.ordre_travail
    if request.user.role != "SUPERVISEUR_ANP":
        raise PermissionDenied("Seul le Superviseur ANP peut valider un bon de livraison.")
    if ordre.bloque_apres_facture:
        raise PermissionDenied("Impossible de modifier le statut d'un BL lié à un OT facturé.")

    if request.method == "POST":
        form = BonLivraisonValidationForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data["status"]
            bon.valide_par = request.user
            bon.date_validation = timezone.now().date()
            if form.cleaned_data["commentaire"]:
                bon.commentaire = form.cleaned_data["commentaire"]
            bon.statut = status
            bon.save()
            messages.success(request, "Statut du bon de livraison mis à jour.")
            return redirect("conventionnement:detail_ordre", ordre_id=ordre.id)
    else:
        form = BonLivraisonValidationForm(initial={"status": bon.statut})

    return render(request, "conventionnement/valider_bl.html", {"form": form, "bon": bon, "ordre": ordre})


# ─── Facture ──────────────────────────────────────────────────────────────────

@login_required
def creer_facture(request, bon_id):
    """Superviseur Haddoun crée la facture après validation du BL."""
    bon = get_object_or_404(BonLivraison, pk=bon_id)
    ordre = bon.ordre_travail
    if request.user.role != "CHEF_EQUIPE":
        raise PermissionDenied("Seul le Superviseur Haddoun peut créer une facture.")
    if ordre.fiche_intervention.escale is not None:
        raise PermissionDenied("Cette vue est réservée au workflow équipement.")
    if bon.statut != BonLivraison.Statut.VALIDE:
        raise PermissionDenied("La facture ne peut être créée qu'après validation du BL.")
    if not ordre.can_create_facture():
        raise PermissionDenied("La facture ne peut pas être créée pour cet ordre.")

    if request.method == "POST":
        form = FactureForm(request.POST)
        if form.is_valid():
            facture = form.save(commit=False)
            facture.bon_livraison = bon
            facture.save()
            messages.success(request, f"Facture {facture.numero_facture} créée.")
            return redirect("conventionnement:detail_ordre", ordre_id=ordre.id)
    else:
        form = FactureForm(initial={"montant_total": ordre.montant_total})

    return render(request, "conventionnement/creer_facture.html", {
        "form": form,
        "bon": bon,
        "ordre": ordre,
    })


@login_required
def modifier_facture(request, facture_id):
    """Superviseur Haddoun modifie la facture AVANT validation ANP."""
    from .models import Facture as FactureModel
    facture = get_object_or_404(FactureModel, pk=facture_id)
    ordre = facture.bon_livraison.ordre_travail
    if request.user.role != "CHEF_EQUIPE":
        raise PermissionDenied("Seul le Superviseur Haddoun peut modifier la facture.")
    if facture.statut == FactureModel.Statut.PAYEE:
        raise PermissionDenied("La facture est déjà validée par l'ANP.")

    if request.method == "POST":
        form = FactureForm(request.POST, instance=facture)
        if form.is_valid():
            form.save()
            messages.success(request, "Facture mise à jour.")
            return redirect("conventionnement:detail_ordre", ordre_id=ordre.id)
    else:
        form = FactureForm(instance=facture)

    return render(request, "conventionnement/modifier_facture.html", {
        "form": form,
        "facture": facture,
        "ordre": ordre,
    })


@login_required
def supprimer_facture(request, facture_id):
    """Superviseur Haddoun supprime la facture AVANT validation ANP."""
    from .models import Facture as FactureModel
    facture = get_object_or_404(FactureModel, pk=facture_id)
    ordre = facture.bon_livraison.ordre_travail
    if request.user.role != "CHEF_EQUIPE":
        raise PermissionDenied("Seul le Superviseur Haddoun peut supprimer la facture.")
    if facture.statut == FactureModel.Statut.PAYEE:
        raise PermissionDenied("La facture est déjà validée et ne peut pas être supprimée.")

    if request.method == "POST":
        numero = facture.numero_facture
        # Déverrouiller l'OT
        ordre.bloque_apres_facture = False
        ordre.deverrouille_par = None
        ordre.date_deverrouillage = None
        ordre.deverrouillage_commentaire = ''
        ordre.save(update_fields=['bloque_apres_facture', 'deverrouille_par', 'date_deverrouillage', 'deverrouillage_commentaire'])
        facture.delete()
        messages.success(request, f"Facture {numero} supprimée.")
        return redirect("conventionnement:detail_ordre", ordre_id=ordre.id)

    return render(request, "conventionnement/supprimer_facture.html", {
        "facture": facture,
        "ordre": ordre,
    })


@login_required
def valider_facture(request, facture_id):
    """Superviseur ANP valide le paiement de la facture Haddoun."""
    from .models import Facture as FactureModel
    facture = get_object_or_404(FactureModel, pk=facture_id)
    ordre = facture.bon_livraison.ordre_travail
    if request.user.role != "SUPERVISEUR_ANP":
        raise PermissionDenied("Seul le Superviseur ANP peut valider (payer) une facture.")
    if facture.statut == FactureModel.Statut.PAYEE:
        messages.info(request, "Cette facture est déjà payée.")
        return redirect("conventionnement:detail_ordre", ordre_id=ordre.id)

    if request.method == "POST":
        facture.statut = FactureModel.Statut.PAYEE
        facture.save()
        messages.success(request, f"Facture {facture.numero_facture} marquée comme PAYÉE par l'ANP.")
        return redirect("conventionnement:detail_ordre", ordre_id=ordre.id)

    return render(request, "conventionnement/valider_facture.html", {"facture": facture, "ordre": ordre})


# ─── Déverrouillage / Modification Directeur ANP ─────────────────────────────

@login_required
def deverrouiller_ordre(request, ordre_id):
    ordre = get_object_or_404(OrdreTravail, pk=ordre_id)
    if request.user.role != "DIRECTEUR":
        raise PermissionDenied("Seul le Directeur ANP peut déverrouiller un ordre de travail.")
    if not ordre.is_locked:
        raise PermissionDenied("Cet ordre n'est pas verrouillé.")

    if request.method == "POST":
        form = OrdreTravailUnlockForm(request.POST)
        if form.is_valid():
            ordre.deverrouille_par = request.user
            ordre.date_deverrouillage = timezone.now().date()
            ordre.deverrouillage_commentaire = form.cleaned_data["deverrouillage_commentaire"]
            ordre.save()
            messages.success(request, "Ordre de travail déverrouillé.")
            return redirect("conventionnement:detail_ordre", ordre_id=ordre.id)
    else:
        form = OrdreTravailUnlockForm()

    return render(request, "conventionnement/deverrouiller_ordre.html", {"form": form, "ordre": ordre})


@login_required
def modifier_ordre(request, ordre_id):
    """Directeur ANP modifie l'OT après déverrouillage."""
    ordre = get_object_or_404(OrdreTravail, pk=ordre_id)
    if request.user.role != "DIRECTEUR":
        raise PermissionDenied("Seul le Directeur ANP peut modifier un ordre de travail déverrouillé.")
    if ordre.is_locked:
        raise PermissionDenied("L'ordre de travail doit être déverrouillé avant modification.")

    if request.method == "POST":
        form = OrdreTravailEditForm(request.POST, instance=ordre)
        if form.is_valid():
            form.save()
            messages.success(request, "Ordre de travail modifié.")
            return redirect("conventionnement:detail_ordre", ordre_id=ordre.id)
    else:
        form = OrdreTravailEditForm(instance=ordre)

    return render(request, "conventionnement/modifier_ordre.html", {"form": form, "ordre": ordre})


# ─── Vues d'Impression Individuelle Professionnelle ───────────────────────────

@login_required
def imprimer_fiche(request, fiche_id):
    """Impression exclusive et autonome de la Fiche d'Intervention avec logo ANP."""
    fiche = get_object_or_404(FicheIntervention, pk=fiche_id)
    if request.user.role not in ALL_ROLES:
        raise PermissionDenied
    return render(request, "conventionnement/print_fiche.html", {
        "fiche": fiche,
        "date_impression": timezone.now(),
    })


@login_required
def imprimer_ot(request, ordre_id):
    """Impression exclusive et autonome de l'Ordre de Travail avec logo ANP."""
    ordre = get_object_or_404(OrdreTravail, pk=ordre_id)
    if request.user.role not in ALL_ROLES:
        raise PermissionDenied
    return render(request, "conventionnement/print_ot.html", {
        "ordre": ordre,
        "fiche": ordre.fiche_intervention,
        "lignes": ordre.lignes.all(),
        "date_impression": timezone.now(),
    })


@login_required
def imprimer_bl(request, bon_id):
    """Impression exclusive et autonome du Bon de Livraison avec logo ANP."""
    bon = get_object_or_404(BonLivraison, pk=bon_id)
    ordre = bon.ordre_travail
    if request.user.role not in ALL_ROLES:
        raise PermissionDenied
    return render(request, "conventionnement/print_bl.html", {
        "bon": bon,
        "ordre": ordre,
        "fiche": ordre.fiche_intervention,
        "lignes": ordre.lignes.all(),
        "date_impression": timezone.now(),
    })


@login_required
def imprimer_facture(request, facture_id):
    """Impression exclusive et autonome de la Facture avec logo ANP."""
    facture = get_object_or_404(Facture, pk=facture_id)
    bon = facture.bon_livraison
    ordre = bon.ordre_travail
    if request.user.role not in ALL_ROLES:
        raise PermissionDenied
    return render(request, "conventionnement/print_facture.html", {
        "facture": facture,
        "bon": bon,
        "ordre": ordre,
        "fiche": ordre.fiche_intervention,
        "lignes": ordre.lignes.all(),
        "date_impression": timezone.now(),
    })
