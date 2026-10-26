from django.db import models
from django.conf import settings
from datetime import datetime


class Employe(models.Model):
    """Employé de Haddoun qui répare physiquement les navires (pas d'accès au système)."""
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    role_metier = models.CharField(max_length=50, blank=True)
    salaire_base_fixe = models.DecimalField(max_digits=10, decimal_places=2)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def calculer_salaire(self, date_debut, date_fin):
        taches = self.tachereparation_set.filter(date_tache__range=(date_debut, date_fin))
        total_prime = sum(t.duree_heures * float(t.tarif_horaire_application) for t in taches)
        return float(self.salaire_base_fixe) + total_prime


class TacheReparation(models.Model):
    """
    Une tâche de réparation : réalisée physiquement par un Employé Haddoun,
    mais pointée (saisie dans le système) par un Technicien ANP qui surveille le travail.
    """
    escale = models.ForeignKey("navires.Escale", on_delete=models.CASCADE, null=True, blank=True, related_name="taches")
    equipement = models.ForeignKey("equipements.Equipement", on_delete=models.CASCADE, null=True, blank=True, related_name="taches", help_text="Équipement concerné par la réparation")
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, help_text="Employé Haddoun ayant réalisé la réparation")
    saisi_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="taches_pointees", help_text="Technicien ANP ayant saisi le pointage",
    )
    description_travail = models.TextField()
    date_tache = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    duree_heures = models.FloatField(editable=False, null=True, blank=True)
    tarif_horaire_application = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        from django.core.exceptions import ValidationError
        if bool(self.escale) == bool(self.equipement):
            raise ValidationError("Une tâche doit concerner soit une escale, soit un équipement, mais pas les deux.")

    def save(self, *args, **kwargs):
        debut = datetime.combine(self.date_tache, self.heure_debut)
        fin = datetime.combine(self.date_tache, self.heure_fin)
        self.duree_heures = round((fin - debut).total_seconds() / 3600, 2)
        super().save(*args, **kwargs)

    @property
    def montant(self):
        if self.duree_heures and self.tarif_horaire_application:
            return round(self.duree_heures * float(self.tarif_horaire_application), 2)
        return 0.0

    def __str__(self):
        cible = self.escale if self.escale else self.equipement
        return f"{self.employe} - {self.description_travail} sur {cible} ({self.date_tache})"


class SuiviAvancement(models.Model):
    """Saisie quotidienne de l'avancement d'une réparation, par le Technicien ANP (surveillance)."""
    escale = models.ForeignKey("navires.Escale", on_delete=models.CASCADE, related_name="suivis")
    technicien_anp = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="suivis_avancement", help_text="Technicien ANP ayant constaté l'avancement",
    )
    date_suivi = models.DateField(auto_now_add=True)
    pourcentage_avancement = models.PositiveSmallIntegerField()
    commentaire = models.TextField(blank=True)

    class Meta:
        unique_together = ("escale", "date_suivi")

    def __str__(self):
        return f"{self.escale} - {self.pourcentage_avancement}% ({self.date_suivi})"