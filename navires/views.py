from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from datetime import date
from .models import Navire, Ouvrage, Escale
from .forms import NavireForm, EscaleForm


def est_autorise_navire(user):
    return user.role in ["SUPERVISEUR_ANP", "TECHNICIEN_ANP", "CHEF_EQUIPE", "TECHNICIEN_HADDOUN"]


@login_required
def liste_navires(request):
    navires = Navire.objects.all().order_by("nom_navire")
    donnees = []
    for navire in navires:
        escales_en_cours = Escale.objects.filter(navire=navire, date_sortie__isnull=True)
        donnees.append({"navire": navire, "escales_en_cours": escales_en_cours})
    
    context = {
        "donnees": donnees,
        "peut_modifier": est_autorise_navire(request.user) if request.user.is_authenticated else False
    }
    return render(request, "navires/liste_navires.html", context)


@login_required
def liste_ouvrages(request):
    """Vue d'occupation : montre chaque ouvrage et le(s) navire(s) actuellement présents."""
    ouvrages = Ouvrage.objects.all().order_by("id_ouvrage")
    donnees = []
    for ouvrage in ouvrages:
        escales_en_cours = Escale.objects.filter(ouvrage=ouvrage, date_sortie__isnull=True)
        donnees.append({"ouvrage": ouvrage, "escales": escales_en_cours})
    return render(request, "navires/liste_ouvrages.html", {"donnees": donnees})


@login_required
@user_passes_test(est_autorise_navire)
def ajouter_navire(request):
    if request.method == "POST":
        form = NavireForm(request.POST)
        if form.is_valid():
            navire = form.save()
            ouvrage = form.cleaned_data.get("ouvrage")
            if ouvrage:
                Escale.objects.create(
                    navire=navire,
                    ouvrage=ouvrage,
                    date_entree=date.today()
                )
            messages.success(request, "Navire ajouté avec succès.")
            return redirect("navires:liste_navires")
    else:
        form = NavireForm()
    return render(request, "navires/form_navire.html", {"form": form, "titre": "Ajouter un navire"})


@login_required
@user_passes_test(est_autorise_navire)
def modifier_navire(request, navire_id):
    navire = get_object_or_404(Navire, matricule=navire_id)
    if request.method == "POST":
        form = NavireForm(request.POST, instance=navire)
        if form.is_valid():
            form.save()
            messages.success(request, "Navire modifié avec succès.")
            return redirect("navires:liste_navires")
    else:
        form = NavireForm(instance=navire)
    return render(request, "navires/form_navire.html", {"form": form, "titre": f"Modifier {navire.nom_navire}"})


@login_required
@user_passes_test(est_autorise_navire)
def supprimer_navire(request, navire_id):
    navire = get_object_or_404(Navire, matricule=navire_id)
    if request.method == "POST":
        navire.delete()
        messages.success(request, "Navire supprimé avec succès.")
        return redirect("navires:liste_navires")
    return render(request, "navires/supprimer_navire.html", {"navire": navire})


@login_required
@user_passes_test(est_autorise_navire)
def ajouter_escale(request, navire_id):
    navire = get_object_or_404(Navire, matricule=navire_id)
    if request.method == "POST":
        form = EscaleForm(request.POST)
        if form.is_valid():
            escale = form.save(commit=False)
            escale.navire = navire
            escale.save()
            messages.success(request, "Escale ajoutée avec succès.")
            return redirect("navires:liste_navires")
    else:
        form = EscaleForm(initial={'date_entree': date.today()})
    return render(request, "navires/form_escale.html", {"form": form, "navire": navire})


@login_required
@user_passes_test(est_autorise_navire)
def clore_escale(request, escale_id):
    escale = get_object_or_404(Escale, pk=escale_id)
    if request.method == "POST":
        escale.date_sortie = date.today()
        escale.save()
        messages.success(request, "Escale clôturée avec succès.")
    return redirect("navires:liste_navires")