from django.contrib import admin
from .models import FicheIntervention, OrdreTravail, LigneOrdreTravail, BonLivraison, Facture


@admin.register(FicheIntervention)
class FicheInterventionAdmin(admin.ModelAdmin):
    list_display = ("numero_fiche", "escale", "date_creation", "cree_par")


class LigneOrdreTravailInline(admin.TabularInline):
    model = LigneOrdreTravail
    extra = 1


@admin.register(OrdreTravail)
class OrdreTravailAdmin(admin.ModelAdmin):
    list_display = ("numero_ordre", "fiche_intervention", "montant_total", "date_creation")
    inlines = [LigneOrdreTravailInline]


@admin.register(BonLivraison)
class BonLivraisonAdmin(admin.ModelAdmin):
    list_display = ("numero_bon", "ordre_travail", "statut", "valide_par", "date_validation")
    list_filter = ("statut",)


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ("numero_facture", "bon_livraison", "montant_total", "statut")
    list_filter = ("statut",)