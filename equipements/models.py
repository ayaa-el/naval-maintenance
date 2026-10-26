from django.db import models


class Equipement(models.Model):
    class Type(models.TextChoices):
        BATEAU_PORTE = "BATEAU_PORTE", "Bateau-porte"
        ELEVATEUR = "ELEVATEUR", "Élévateur"
        GRUE = "GRUE", "Grue"
        AUTRE = "AUTRE", "Autre"

    class Statut(models.TextChoices):
        EN_SERVICE = "EN_SERVICE", "En service"
        EN_REPARATION = "EN_REPARATION", "En réparation"
        HORS_SERVICE = "HORS_SERVICE", "Hors service"

    reference = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=100)
    type_equipement = models.CharField(max_length=20, choices=Type.choices, default=Type.AUTRE)
    localisation = models.CharField(max_length=100, blank=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_SERVICE)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nom} ({self.get_type_equipement_display()})"
