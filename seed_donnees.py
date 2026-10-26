import os
import django
from datetime import date

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from equipements.models import Equipement
from navires.models import Navire, Ouvrage, Escale

User = get_user_model()

def seed():
    print("=== Chargement et Mise à Jour des Utilisateurs & Données ===")

    # 1. Comptes de test par Rôle
    comptes_demo = [
        {"username": "directeur_anp", "role": User.Role.DIRECTEUR, "password": "password123"},
        {"username": "superviseur_anp", "role": User.Role.SUPERVISEUR_ANP, "password": "password123"},
        {"username": "superviseur_haddoun", "role": User.Role.CHEF_EQUIPE, "password": "password123"},
        {"username": "technicien_anp", "role": User.Role.TECHNICIEN_ANP, "password": "password123"},
        {"username": "technicien_haddoun", "role": User.Role.TECHNICIEN_HADDOUN, "password": "password123"},
    ]

    for c_data in comptes_demo:
        u, created = User.objects.get_or_create(username=c_data["username"])
        u.role = c_data["role"]
        u.set_password(c_data["password"])
        u.save()
        status_label = "créé" if created else "mis à jour"
        print(f"[+] Utilisateur {u.username} ({u.get_role_display()}) {status_label}")

    # 2. Équipements ANP
    equipements_demo = [
        {
            "reference": "EQ-BP01",
            "nom": "Bateau-porte n°1",
            "type_equipement": Equipement.Type.BATEAU_PORTE,
            "localisation": "Bassin de Radoub - Forme 1",
            "statut": Equipement.Statut.EN_SERVICE,
        },
        {
            "reference": "EQ-BP02",
            "nom": "Bateau-porte n°2",
            "type_equipement": Equipement.Type.BATEAU_PORTE,
            "localisation": "Bassin de Radoub - Forme 2",
            "statut": Equipement.Statut.EN_REPARATION,
        },
        {
            "reference": "EQ-EL200",
            "nom": "Élévateur à bateaux 200T",
            "type_equipement": Equipement.Type.ELEVATEUR,
            "localisation": "Zone de Carénage ANP",
            "statut": Equipement.Statut.EN_SERVICE,
        },
        {
            "reference": "EQ-GR01",
            "nom": "Grue portuaire mobile",
            "type_equipement": Equipement.Type.GRUE,
            "localisation": "Quai Principal ANP",
            "statut": Equipement.Statut.EN_SERVICE,
        },
        {
            "reference": "EQ-CC01",
            "nom": "Chariot cavalier",
            "type_equipement": Equipement.Type.AUTRE,
            "localisation": "Terre-plein Technique ANP",
            "statut": Equipement.Statut.HORS_SERVICE,
        },
        {
            "reference": "EQ-LEV01",
            "nom": "Équipement de levage",
            "type_equipement": Equipement.Type.AUTRE,
            "localisation": "Atelier Équipements ANP",
            "statut": Equipement.Statut.EN_SERVICE,
        },
    ]

    for eq_data in equipements_demo:
        eq, created = Equipement.objects.get_or_create(
            reference=eq_data["reference"],
            defaults=eq_data,
        )
        if created:
            print(f"[+] Équipement ANP créé : {eq.nom}")

    # 3. Navires et Escales (Haddoun)
    ouvrage, _ = Ouvrage.objects.get_or_create(
        id_ouvrage=1,
        defaults={
            "nom_ouvrage": "Forme de Radoub n°1",
            "prix_fixe_journalier": 5000.00,
        },
    )

    navires_demo = [
        {"matricule": "NAV-01", "nom_navire": "Cargo Atlas", "type_navire": "Cargo", "tonnage": 4500, "taille": "Grande"},
        {"matricule": "NAV-02", "nom_navire": "Pêchmar 3", "type_navire": "Chalutier", "tonnage": 350, "taille": "Petite"},
    ]

    for n_data in navires_demo:
        navire, created = Navire.objects.get_or_create(
            matricule=n_data["matricule"],
            defaults=n_data,
        )
        if created:
            print(f"[+] Navire Haddoun créé : {navire.nom_navire}")
            Escale.objects.get_or_create(
                navire=navire,
                ouvrage=ouvrage,
                date_entree=date.today(),
            )

    print("=== Configuration terminée avec succès ===")

if __name__ == "__main__":
    seed()
