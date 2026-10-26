from django.urls import path
from . import views

app_name = "equipements"

urlpatterns = [
    path("", views.liste_equipements, name="liste_equipements"),
    path("ajouter/", views.ajouter_equipement, name="ajouter_equipement"),
    path("<int:pk>/modifier/", views.modifier_equipement, name="modifier_equipement"),
    path("<int:pk>/supprimer/", views.supprimer_equipement, name="supprimer_equipement"),
]
