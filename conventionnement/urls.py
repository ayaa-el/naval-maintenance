from django.urls import path
from . import views

app_name = "conventionnement"

urlpatterns = [
    # Fiches d'intervention
    path("", views.liste_fiches, name="liste_fiches"),
    path("fiche/creer/equipement/", views.creer_fiche_equipement, name="creer_fiche_equipement"),
    path("fiche/creer/navire/<int:escale_id>/", views.creer_fiche_navire, name="creer_fiche_navire"),
    path("fiche/<int:fiche_id>/", views.detail_fiche, name="detail_fiche"),
    path("fiche/<int:fiche_id>/modifier/", views.modifier_fiche, name="modifier_fiche"),
    path("fiche/<int:fiche_id>/supprimer/", views.supprimer_fiche, name="supprimer_fiche"),
    path("fiche/<int:fiche_id>/diagnostic/", views.ajouter_diagnostic, name="ajouter_diagnostic"),

    # Ordres de Travail
    path("fiche/<int:fiche_id>/ordre/creer/", views.creer_ordre_travail, name="creer_ordre_travail"),
    path("ordre/<int:ordre_id>/", views.detail_ordre, name="detail_ordre"),
    path("ordre/<int:ordre_id>/modifier/lignes/", views.modifier_ordre_travail, name="modifier_ordre_travail"),
    path("ordre/<int:ordre_id>/supprimer/", views.supprimer_ordre_travail, name="supprimer_ordre_travail"),
    path("ordre/<int:ordre_id>/valider/", views.valider_refuser_ordre, name="valider_refuser_ordre"),
    path("ordre/<int:ordre_id>/realiser/", views.realiser_intervention, name="realiser_intervention"),
    path("ordre/generer/<int:fiche_id>/", views.generer_ordre_travail, name="generer_ordre_travail"),
    path("ordre/<int:ordre_id>/deverrouiller/", views.deverrouiller_ordre, name="deverrouiller_ordre"),
    path("ordre/<int:ordre_id>/modifier/", views.modifier_ordre, name="modifier_ordre"),

    # Bons de Livraison
    path("ordre/<int:ordre_id>/bon/creer/", views.creer_bon_livraison, name="creer_bon_livraison"),
    path("bon/<int:bon_id>/modifier/", views.modifier_bon_livraison, name="modifier_bon_livraison"),
    path("bon/<int:bon_id>/supprimer/", views.supprimer_bon_livraison, name="supprimer_bon_livraison"),
    path("bon/<int:bon_id>/valider/", views.valider_bon_livraison, name="valider_bon_livraison"),

    # Factures
    path("bon/<int:bon_id>/facture/creer/", views.creer_facture, name="creer_facture"),
    path("facture/<int:facture_id>/modifier/", views.modifier_facture, name="modifier_facture"),
    path("facture/<int:facture_id>/supprimer/", views.supprimer_facture, name="supprimer_facture"),
    path("facture/<int:facture_id>/valider/", views.valider_facture, name="valider_facture"),

    # Impressions individuelles avec Logo ANP & Date
    path("fiche/<int:fiche_id>/imprimer/", views.imprimer_fiche, name="imprimer_fiche"),
    path("ordre/<int:ordre_id>/imprimer/", views.imprimer_ot, name="imprimer_ot"),
    path("bon/<int:bon_id>/imprimer/", views.imprimer_bl, name="imprimer_bl"),
    path("facture/<int:facture_id>/imprimer/", views.imprimer_facture, name="imprimer_facture"),
]
