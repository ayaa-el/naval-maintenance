from django.contrib.auth.models import AbstractUser
from django.db import models


class Utilisateur(AbstractUser):
    """
    Remplace le User Django par défaut pour y ajouter le rôle.
    Django gère automatiquement le hachage sécurisé du mot de passe.
    """

    class Role(models.TextChoices):
        SUPERVISEUR_ANP = "SUPERVISEUR_ANP", "Superviseur ANP"
        TECHNICIEN_ANP = "TECHNICIEN_ANP", "Technicien ANP"
        CHEF_EQUIPE = "CHEF_EQUIPE", "Superviseur Haddoun"
        TECHNICIEN_HADDOUN = "TECHNICIEN_HADDOUN", "Technicien Haddoun"

    role = models.CharField(max_length=30, choices=Role.choices)
    photo_profil = models.ImageField(upload_to="profils/", blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="N° de Téléphone")
    date_naissance = models.DateField(blank=True, null=True, verbose_name="Date de Naissance")
    cin = models.CharField(max_length=20, blank=True, null=True, verbose_name="CIN (Carte Nationale)")

    def is_anp(self):
        return self.role in {
            self.Role.SUPERVISEUR_ANP,
            self.Role.TECHNICIEN_ANP,
        }

    def is_haddoun(self):
        return self.role in {
            self.Role.CHEF_EQUIPE,
            self.Role.TECHNICIEN_HADDOUN,
        }

    def is_technicien_haddoun(self):
        return self.role == self.Role.TECHNICIEN_HADDOUN

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"