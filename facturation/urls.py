from django.urls import path
from . import views

app_name = "facturation"

urlpatterns = [
    path("", views.liste_escales, name="liste_escales"),
    path("valider/<int:escale_id>/", views.valider_paiement, name="valider_paiement"),
    path("tableau-bord/", views.tableau_bord, name="tableau_bord"),
    path("export-excel/", views.exporter_excel, name="exporter_excel"),
]
