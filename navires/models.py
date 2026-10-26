from django.db import models
from datetime import date


class Ouvrage(models.Model):
    """Les 3 ouvrages : Cale Sèche, Bassin d'Armement, Cale de Halage."""
    id_ouvrage = models.PositiveSmallIntegerField(primary_key=True)
    nom_ouvrage = models.CharField(max_length=50)
    prix_fixe_journalier = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nom_ouvrage


class Navire(models.Model):
    matricule = models.CharField(max_length=50, primary_key=True)
    nom_navire = models.CharField(max_length=100)
    tonnage = models.FloatField()
    type_navire = models.CharField(
        max_length=30,
        choices=[
            ("Cargo", "Cargo"),
            ("Porte-conteneurs", "Porte-conteneurs"),
            ("Chalutier", "Chalutier"),
            ("Remorqueur", "Remorqueur"),
        ],
        default="Cargo",
    )
    taille = models.CharField(
        max_length=10,
        choices=[("Grande", "Grande"), ("Petite", "Petite")],
    )

    def __str__(self):
        return f"{self.nom_navire} ({self.matricule})"


class Reservation(models.Model):
    """Réservations pour les Ouvrages 1 (Cale Sèche) et 3 (Cale de Halage) uniquement."""

    class Statut(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        VALIDEE = "VALIDEE", "Validée"
        REFUSEE = "REFUSEE", "Refusée"

    navire = models.ForeignKey(Navire, on_delete=models.CASCADE)
    ouvrage = models.ForeignKey(Ouvrage, on_delete=models.CASCADE)
    date_demande = models.DateField(auto_now_add=True)
    date_entree_souhaitee = models.DateField()
    date_entree_validee = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)

    def __str__(self):
        return f"Réservation {self.navire} - {self.ouvrage} ({self.statut})"


class Escale(models.Model):
    """Le séjour d'un navire dans le port, de son arrivée à sa sortie."""

    class StatutFacture(models.TextChoices):
        NON_PAYE = "NON_PAYE", "Non Payé"
        PAYE = "PAYE", "Payé"

    numero_facture = models.CharField(max_length=30, unique=True, null=True, blank=True)
    navire = models.ForeignKey(Navire, on_delete=models.CASCADE)
    ouvrage = models.ForeignKey(Ouvrage, on_delete=models.CASCADE)
    reservation = models.OneToOneField(Reservation, on_delete=models.SET_NULL, null=True, blank=True)
    date_entree = models.DateField()
    date_sortie = models.DateField(null=True, blank=True)
    statut_facture = models.CharField(max_length=20, choices=StatutFacture.choices, default=StatutFacture.NON_PAYE)
    montant_total_facture = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duree_predite_ia = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Escale {self.navire} du {self.date_entree}"

    def calculer_montant_total(self):
        """Montant = Prix Fixe Journalier x Nombre de Jours + Services consommés + Interventions."""
        fin = self.date_sortie or date.today()
        nb_jours = max((fin - self.date_entree).days, 1)
        montant_ouvrage = nb_jours * float(self.ouvrage.prix_fixe_journalier)
        montant_services = sum(
            s.quantite * float(s.prix_unitaire) for s in self.services.all()
        )
        
        # Ajouter le montant des interventions (Ordres de Travail)
        montant_interventions = 0
        for fiche in self.fiches_intervention.all():
            if hasattr(fiche, 'ordre_travail') and fiche.ordre_travail.status != 'REFUSE':
                montant_interventions += float(fiche.ordre_travail.montant_total)
                
        self.montant_total_facture = montant_ouvrage + montant_services + montant_interventions
        self.save()
        return self.montant_total_facture

    def generer_numero_facture(self):
        """Génère un numéro unique du type FAC-2026-000001."""
        annee = date.today().year
        compteur = Escale.objects.filter(
            numero_facture__startswith=f"FAC-{annee}"
        ).count() + 1
        self.numero_facture = f"FAC-{annee}-{compteur:06d}"
        self.save()
        return self.numero_facture


class ServiceConsomme(models.Model):
    """Eau, électricité... consommés pendant une escale."""
    escale = models.ForeignKey(Escale, on_delete=models.CASCADE, related_name="services")
    nom_service = models.CharField(max_length=100)
    quantite = models.FloatField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nom_service} - {self.escale}"