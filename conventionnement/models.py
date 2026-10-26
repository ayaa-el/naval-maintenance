from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import date
from navires.models import Escale
from rh.models import TacheReparation
from equipements.models import Equipement


def generer_numero(prefixe, model_class, champ):
    """Fonction commune : génère un numéro du type PREFIXE-2026-000001."""
    annee = date.today().year
    compteur = model_class.objects.filter(
        **{f"{champ}__startswith": f"{prefixe}-{annee}"}
    ).count() + 1
    return f"{prefixe}-{annee}-{compteur:06d}"


class FicheIntervention(models.Model):
    """
    Fiche d'intervention commune pour un navire ou un équipement.
    """
    escale = models.ForeignKey(Escale, null=True, blank=True, on_delete=models.CASCADE, related_name="fiches_intervention")
    equipement = models.ForeignKey("equipements.Equipement", null=True, blank=True, on_delete=models.CASCADE, related_name="fiches_intervention")
    numero_fiche = models.CharField(max_length=30, unique=True, blank=True, editable=False)
    description_probleme = models.TextField(help_text="Problème initial déclaré par l'ANP ou par l'utilisateur")
    type_avarie = models.CharField(
        max_length=30,
        choices=[
            ("Soudure", "Soudure"),
            ("Peinture", "Peinture"),
            ("Moteur", "Moteur"),
            ("Electricite", "Électricité"),
        ],
        default="Soudure",
    )
    date_creation = models.DateField(auto_now_add=True)
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="fiches_creees", help_text="Utilisateur ayant créé la fiche",
    )

    precision_probleme = models.TextField(
        blank=True, help_text="Problème exact précisé par Haddoun après traitement",
    )
    traite_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="fiches_traitees", help_text="Personne Haddoun ayant précisé le problème",
    )

    def save(self, *args, **kwargs):
        if not self.numero_fiche:
            self.numero_fiche = generer_numero("FI", FicheIntervention, "numero_fiche")
        super().save(*args, **kwargs)

    def clean(self):
        from django.core.exceptions import ValidationError

        if bool(self.escale) == bool(self.equipement):
            raise ValidationError(
                "Une fiche d'intervention doit concerner soit une escale, soit un équipement, mais pas les deux."
            )

    def __str__(self):
        cible = self.escale if self.escale else self.equipement
        return f"Fiche {self.numero_fiche} - {cible}"

    @property
    def has_ordre_travail(self):
        return hasattr(self, "ordre_travail")

    @property
    def is_equipement(self):
        return self.equipement is not None

    @property
    def is_navire(self):
        return self.escale is not None

    @property
    def cible_label(self):
        if self.is_navire:
            return self.escale.navire.nom_navire
        return self.equipement.nom if self.equipement else "-"


class OrdreTravail(models.Model):
    """Ordre de Travail créé par un Technicien Haddoun après diagnostic ANP/Équipement."""

    class Statut(models.TextChoices):
        BROUILLON = "BROUILLON", "Brouillon"
        ATTENTE_VALIDATION_ANP = "ATTENTE_VALIDATION_ANP", "En attente de validation ANP"
        VALIDE = "VALIDE", "Validé"
        EN_COURS = "EN_COURS", "En cours"
        TERMINE = "TERMINE", "Terminé"
        REFUSE = "REFUSE", "Refusé"

    fiche_intervention = models.OneToOneField(FicheIntervention, on_delete=models.CASCADE, related_name="ordre_travail")
    numero_ordre = models.CharField(max_length=30, unique=True, blank=True, editable=False)
    date_creation = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=30,
        choices=Statut.choices,
        default=Statut.ATTENTE_VALIDATION_ANP,
        help_text="Statut du workflow d'Ordre de Travail.",
    )
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="ordres_crees", help_text="Technicien Haddoun ayant créé l'ordre de travail",
    )
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="ordres_valides", help_text="Technicien ANP ayant validé l'ordre de travail",
    )
    date_validation = models.DateField(null=True, blank=True)
    refuse_commentaire = models.TextField(blank=True)
    realise_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="ordres_realises", help_text="Technicien Haddoun ayant réalisé l'intervention",
    )
    date_realisation = models.DateField(null=True, blank=True)
    bloque_apres_facture = models.BooleanField(
        default=False,
        help_text="Verrouille l'ordre de travail après émission d'une facture.",
    )
    deverrouille_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ordres_deverrouilles",
        help_text="Directeur ayant déverrouillé l'ordre après facturation.",
    )
    date_deverrouillage = models.DateField(null=True, blank=True)
    deverrouillage_commentaire = models.TextField(blank=True)

    class Meta:
        permissions = [
            ("can_validate_ordretravail", "Peut valider ou refuser un ordre de travail"),
            ("can_realize_intervention", "Peut réaliser une intervention"),
            ("can_create_ordretravail", "Peut créer un ordre de travail"),
            ("can_create_bonlivraison", "Peut créer un bon de livraison"),
            ("can_create_facture", "Peut créer une facture"),
            ("can_unlock_ordretravail", "Peut déverrouiller un ordre de travail"),
        ]

    def save(self, *args, **kwargs):
        if not self.numero_ordre:
            self.numero_ordre = generer_numero("OT", OrdreTravail, "numero_ordre")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"OT {self.numero_ordre}"

    @property
    def has_bon_livraison(self):
        return hasattr(self, "bon_livraison")

    @property
    def has_facture(self):
        return self.has_bon_livraison and hasattr(self.bon_livraison, "facture")

    @property
    def is_locked(self):
        return self.bloque_apres_facture and self.deverrouille_par is None

    def can_be_modified_by(self, user):
        if self.bloque_apres_facture:
            return getattr(user, "role", None) == "DIRECTEUR"
        return True

    def assert_can_be_modified_by(self, user):
        if not self.can_be_modified_by(user):
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied("Cet ordre de travail est verrouillé après facturation.")

    def can_be_validated(self):
        return self.status == self.Statut.ATTENTE_VALIDATION_ANP and not self.is_locked

    def can_be_realized(self):
        return self.status == self.Statut.VALIDE and not self.is_locked

    def can_create_bonlivraison(self):
        return self.status == self.Statut.TERMINE and not self.is_locked and not self.has_bon_livraison

    def can_create_facture(self):
        return self.has_bon_livraison and not self.has_facture and not self.is_locked

    def calculer_montant_total(self):
        """Additionne les lignes de l'ordre de travail (tâches/services + quantité)."""
        total = sum(l.montant for l in self.lignes.all())
        self.montant_total = total
        self.save()
        return total

    def generer_depuis_taches(self):
        """Récupère automatiquement les tâches de réparation déjà saisies par le Technicien ANP."""
        escale = self.fiche_intervention.escale
        for tache in TacheReparation.objects.filter(escale=escale):
            LigneOrdreTravail.objects.get_or_create(
                ordre_travail=self,
                description=tache.description_travail,
                defaults={
                    "quantite": tache.duree_heures or 1,
                    "prix_unitaire": tache.tarif_horaire_application,
                },
            )
        self.calculer_montant_total()


class LigneOrdreTravail(models.Model):
    """Une ligne de service/tâche dans l'ordre de travail : description + quantité + prix."""
    ordre_travail = models.ForeignKey(OrdreTravail, on_delete=models.CASCADE, related_name="lignes")
    description = models.CharField(max_length=255)
    quantite = models.FloatField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def montant(self):
        return self.quantite * float(self.prix_unitaire)

    def __str__(self):
        return f"{self.description} ({self.ordre_travail.numero_ordre})"


class BonLivraison(models.Model):
    """Créé par Haddoun, doit correspondre à l'Ordre de Travail.

    Le statut peut rester en attente dans le workflow équipement si aucune validation
    explicite par l'ANP n'est prévue.
    """

    class Statut(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente de validation"
        VALIDE = "VALIDE", "Validé par l'ANP"
        REFUSE = "REFUSE", "Refusé (non conforme)"

    ordre_travail = models.OneToOneField(OrdreTravail, on_delete=models.CASCADE, related_name="bon_livraison")
    numero_bon = models.CharField(max_length=30, unique=True, blank=True, editable=False)
    date_creation = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="bons_valides", help_text="Technicien ANP ayant validé le bon",
    )
    date_validation = models.DateField(null=True, blank=True)
    commentaire = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.numero_bon:
            self.numero_bon = generer_numero("BL", BonLivraison, "numero_bon")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"BL {self.numero_bon} ({self.statut})"


class Facture(models.Model):
    """Facture finale envoyée par Haddoun à l'ANP, uniquement possible si le Bon de Livraison est validé."""

    class Statut(models.TextChoices):
        NON_PAYEE = "NON_PAYEE", "Non payée"
        PAYEE = "PAYEE", "Payée"

    bon_livraison = models.OneToOneField(BonLivraison, on_delete=models.CASCADE, related_name="facture")
    numero_facture = models.CharField(max_length=30, unique=True, blank=True, editable=False)
    date_creation = models.DateField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.NON_PAYEE)

    def save(self, *args, **kwargs):
        if not self.numero_facture:
            self.numero_facture = generer_numero("FC", Facture, "numero_facture")
        super().save(*args, **kwargs)

        ordre = self.bon_livraison.ordre_travail
        if not ordre.bloque_apres_facture:
            ordre.bloque_apres_facture = True
            ordre.save(update_fields=["bloque_apres_facture"])

    def __str__(self):
        return f"Facture {self.numero_facture} ({self.statut})"