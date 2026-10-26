from django.urls import path
from . import views

app_name = "comptes"

urlpatterns = [
    path("", views.choix_organisation, name="choix_organisation"),
    path("connexion/<str:organisation>/", views.ConnexionView.as_view(), name="connexion"),
    path("deconnexion/", views.deconnexion, name="deconnexion"),
    path("profil/", views.mon_profil, name="mon_profil"),
    path("accueil/", views.accueil, name="accueil"),
]