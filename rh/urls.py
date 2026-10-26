from django.urls import path
from . import views

app_name = "rh"

urlpatterns = [
    # Employés
    path("", views.liste_employes, name="liste_employes"),
    path("ajouter/", views.ajouter_employe, name="ajouter_employe"),
    path("<int:employe_id>/modifier/", views.modifier_employe, name="modifier_employe"),
    path("<int:employe_id>/supprimer/", views.supprimer_employe, name="supprimer_employe"),
    # Pointage / Tâches de réparation
    path("taches/", views.liste_taches, name="liste_taches"),
    path("taches/ajouter/", views.ajouter_tache, name="ajouter_tache"),
    path("taches/<int:tache_id>/modifier/", views.modifier_tache, name="modifier_tache"),
    path("taches/<int:tache_id>/supprimer/", views.supprimer_tache, name="supprimer_tache"),
    # Suivi d'avancement
    path("suivis/", views.liste_suivis, name="liste_suivis"),
    path("suivis/ajouter/", views.ajouter_suivi, name="ajouter_suivi"),
]