from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Equipement
from .forms import EquipementForm


def check_peut_gerer(user):
    if user.role not in ["SUPERVISEUR_ANP"]:
        raise PermissionDenied("Seuls le Superviseur ANP peut gérer les équipements.")


@login_required
def liste_equipements(request):
    equipements = Equipement.objects.all().order_by("type_equipement", "nom")
    return render(request, "equipements/liste_equipements.html", {"equipements": equipements})


@login_required
def ajouter_equipement(request):
    check_peut_gerer(request.user)
    if request.method == "POST":
        form = EquipementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Équipement ajouté avec succès.")
            return redirect("equipements:liste_equipements")
    else:
        form = EquipementForm()
    return render(request, "equipements/form_equipement.html", {"form": form, "action": "Ajouter"})


@login_required
def modifier_equipement(request, pk):
    check_peut_gerer(request.user)
    equipement = get_object_or_404(Equipement, pk=pk)
    if request.method == "POST":
        form = EquipementForm(request.POST, instance=equipement)
        if form.is_valid():
            form.save()
            messages.success(request, f"Équipement « {equipement.nom} » modifié avec succès.")
            return redirect("equipements:liste_equipements")
    else:
        form = EquipementForm(instance=equipement)
    return render(request, "equipements/form_equipement.html", {
        "form": form, "action": "Modifier", "equipement": equipement
    })


@login_required
def supprimer_equipement(request, pk):
    check_peut_gerer(request.user)
    equipement = get_object_or_404(Equipement, pk=pk)
    if request.method == "POST":
        nom = equipement.nom
        equipement.delete()
        messages.success(request, f"Équipement « {nom} » supprimé.")
        return redirect("equipements:liste_equipements")
    return render(request, "equipements/supprimer_equipement.html", {"equipement": equipement})
