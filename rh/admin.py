from django.contrib import admin
from .models import Employe, TacheReparation, SuiviAvancement


@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ("prenom", "nom", "role_metier", "salaire_base_fixe", "actif")
    list_filter = ("actif", "role_metier")
    search_fields = ("nom", "prenom")


@admin.register(TacheReparation)
class TacheReparationAdmin(admin.ModelAdmin):
    list_display = ("employe", "escale", "date_tache", "duree_heures", "tarif_horaire_application")
    list_filter = ("date_tache",)


@admin.register(SuiviAvancement)
class SuiviAvancementAdmin(admin.ModelAdmin):
    list_display = ("escale", "technicien_anp", "date_suivi", "pourcentage_avancement")
    list_filter = ("date_suivi",)