from django.contrib import admin
from .models import Ouvrage, Navire, Reservation, Escale, ServiceConsomme


@admin.register(Ouvrage)
class OuvrageAdmin(admin.ModelAdmin):
    list_display = ("id_ouvrage", "nom_ouvrage", "prix_fixe_journalier")


@admin.register(Navire)
class NavireAdmin(admin.ModelAdmin):
    list_display = ("matricule", "nom_navire", "tonnage", "taille")
    search_fields = ("matricule", "nom_navire")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("navire", "ouvrage", "date_entree_souhaitee", "statut")
    list_filter = ("statut", "ouvrage")


class ServiceConsommeInline(admin.TabularInline):
    model = ServiceConsomme
    extra = 1


@admin.register(Escale)
class EscaleAdmin(admin.ModelAdmin):
    list_display = ("navire", "ouvrage", "date_entree", "date_sortie", "statut_facture", "montant_total_facture")
    list_filter = ("statut_facture", "ouvrage")
    inlines = [ServiceConsommeInline]