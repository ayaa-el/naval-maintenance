from django.urls import path
from . import views

app_name = "navires"

urlpatterns = [
    path("", views.liste_navires, name="liste_navires"),
    path("ouvrages/", views.liste_ouvrages, name="liste_ouvrages"),
    path("ajouter/", views.ajouter_navire, name="ajouter_navire"),
    path("<str:navire_id>/modifier/", views.modifier_navire, name="modifier_navire"),
    path("<str:navire_id>/supprimer/", views.supprimer_navire, name="supprimer_navire"),
    path("<str:navire_id>/escale/ajouter/", views.ajouter_escale, name="ajouter_escale"),
    path("escale/<int:escale_id>/clore/", views.clore_escale, name="clore_escale"),
]