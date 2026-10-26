from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import Employe, TacheReparation, SuiviAvancement
from .forms import EmployeForm, TacheReparationForm, SuiviAvancementForm


def check_superviseur_anp(user):
    if user.role not in ["SUPERVISEUR_ANP"]:
        raise PermissionDenied("Vous n'avez pas l'autorisation de gérer les employés.")


def check_technicien_anp(user):
    if user.role not in ["TECHNICIEN_ANP", "SUPERVISEUR_ANP"]:
        raise PermissionDenied("Accès réservé au Technicien ANP.")


# ─── EMPLOYÉS ─────────────────────────────────────────────────────────────────

@login_required
def liste_employes(request):
    if request.user.role not in ["TECHNICIEN_ANP", "SUPERVISEUR_ANP"]:
        raise PermissionDenied("Accès réservé au personnel ANP.")
    employes = Employe.objects.all().order_by("-actif", "nom")
    return render(request, "rh/liste_employes.html", {"employes": employes})


@login_required
def ajouter_employe(request):
    check_superviseur_anp(request.user)
    if request.method == "POST":
        form = EmployeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Employé ajouté avec succès.")
            return redirect("rh:liste_employes")
    else:
        form = EmployeForm(initial={"actif": True})
    return render(request, "rh/form_employe.html", {"form": form, "action": "Ajouter"})


@login_required
def modifier_employe(request, employe_id):
    check_superviseur_anp(request.user)
    employe = get_object_or_404(Employe, pk=employe_id)
    if request.method == "POST":
        form = EmployeForm(request.POST, instance=employe)
        if form.is_valid():
            form.save()
            messages.success(request, "Employé modifié avec succès.")
            return redirect("rh:liste_employes")
    else:
        form = EmployeForm(instance=employe)
    return render(request, "rh/form_employe.html", {"form": form, "action": "Modifier", "employe": employe})


@login_required
def supprimer_employe(request, employe_id):
    check_superviseur_anp(request.user)
    employe = get_object_or_404(Employe, pk=employe_id)
    employe.actif = False
    employe.save()
    messages.success(request, f"L'employé {employe.prenom} {employe.nom} a été désactivé.")
    return redirect("rh:liste_employes")


# ─── POINTAGE / TÂCHES DE RÉPARATION ──────────────────────────────────────────

@login_required
def liste_taches(request):
    check_technicien_anp(request.user)
    taches = TacheReparation.objects.all().order_by("-date_tache")
    return render(request, "rh/liste_taches.html", {"taches": taches})


@login_required
def ajouter_tache(request):
    check_technicien_anp(request.user)
    if request.method == "POST":
        form = TacheReparationForm(request.POST)
        if form.is_valid():
            tache = form.save(commit=False)
            tache.saisi_par = request.user
            tache.save()
            messages.success(request, "Pointage enregistré avec succès.")
            return redirect("rh:liste_taches")
    else:
        form = TacheReparationForm()
    return render(request, "rh/form_tache.html", {"form": form, "action": "Ajouter"})


@login_required
def modifier_tache(request, tache_id):
    check_technicien_anp(request.user)
    tache = get_object_or_404(TacheReparation, pk=tache_id)
    if request.method == "POST":
        form = TacheReparationForm(request.POST, instance=tache)
        if form.is_valid():
            form.save()
            messages.success(request, "Pointage modifié avec succès.")
            return redirect("rh:liste_taches")
    else:
        form = TacheReparationForm(instance=tache)
    return render(request, "rh/form_tache.html", {"form": form, "action": "Modifier", "tache": tache})


@login_required
def supprimer_tache(request, tache_id):
    check_technicien_anp(request.user)
    tache = get_object_or_404(TacheReparation, pk=tache_id)
    if request.method == "POST":
        tache.delete()
        messages.success(request, "Pointage supprimé.")
        return redirect("rh:liste_taches")
    return render(request, "rh/supprimer_tache.html", {"tache": tache})


# ─── SUIVI D'AVANCEMENT ───────────────────────────────────────────────────────

@login_required
def liste_suivis(request):
    check_technicien_anp(request.user)
    suivis = SuiviAvancement.objects.all().order_by("-date_suivi")
    return render(request, "rh/liste_suivis.html", {"suivis": suivis})


@login_required
def ajouter_suivi(request):
    check_technicien_anp(request.user)
    if request.method == "POST":
        form = SuiviAvancementForm(request.POST)
        if form.is_valid():
            suivi = form.save(commit=False)
            suivi.technicien_anp = request.user
            suivi.save()
            messages.success(request, "Suivi d'avancement enregistré.")
            return redirect("rh:liste_suivis")
    else:
        form = SuiviAvancementForm()
    return render(request, "rh/form_suivi.html", {"form": form})