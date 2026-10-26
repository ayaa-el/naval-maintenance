"""
Script d'entraînement du modèle prédictif.
À lancer manuellement quand on veut (ré)entraîner le modèle :
    python ia/entrainement.py

Pour l'instant, utilise des données d'exemple générées aléatoirement.
À remplacer par un vrai historique d'escales dès qu'il sera disponible.
"""
import os
import random
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor

TYPES_NAVIRE = ["Cargo", "Porte-conteneurs", "Chalutier", "Remorqueur"]
TYPES_AVARIE = ["Soudure", "Peinture", "Moteur", "Electricite"]


def generer_donnees_exemple(n=200):
    """Génère un jeu de données synthétique plausible pour l'entraînement."""
    X, y = [], []
    for _ in range(n):
        type_navire_idx = random.randint(0, len(TYPES_NAVIRE) - 1)
        type_avarie_idx = random.randint(0, len(TYPES_AVARIE) - 1)
        tonnage = random.uniform(200, 5000)

        base = 2 + (tonnage / 1000) + type_avarie_idx * 1.5
        bruit = random.uniform(-1, 1)
        duree_jours = max(1, round(base + bruit))

        X.append([type_navire_idx, type_avarie_idx, tonnage])
        y.append(duree_jours)
    return np.array(X), np.array(y)


def entrainer_et_sauvegarder():
    X, y = generer_donnees_exemple()

    modele = RandomForestRegressor(n_estimators=100, random_state=42)
    modele.fit(X, y)

    chemin = os.path.join(os.path.dirname(__file__), "modele_predictif.joblib")
    joblib.dump(modele, chemin)
    print(f"Modèle entraîné et sauvegardé dans : {chemin}")


if __name__ == "__main__":
    entrainer_et_sauvegarder()
    