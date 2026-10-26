"""
Charge le modèle entraîné et permet de prédire la durée d'immobilisation d'un navire.
"""
import os
import joblib

from .entrainement import TYPES_NAVIRE, TYPES_AVARIE

_modele = None  # mis en cache après le premier chargement, pour ne pas recharger à chaque appel


def _charger_modele():
    global _modele
    if _modele is None:
        chemin = os.path.join(os.path.dirname(__file__), "modele_predictif.joblib")
        if os.path.exists(chemin):
            _modele = joblib.load(chemin)
    return _modele


def predire_duree(type_navire: str, type_avarie: str, tonnage: float):
    """
    Retourne la durée prédite (en jours), ou None si le modèle n'est pas encore entraîné
    ou si le type fourni n'est pas reconnu.
    """
    modele = _charger_modele()
    if modele is None:
        return None

    if type_navire not in TYPES_NAVIRE or type_avarie not in TYPES_AVARIE:
        return None

    type_navire_idx = TYPES_NAVIRE.index(type_navire)
    type_avarie_idx = TYPES_AVARIE.index(type_avarie)

    prediction = modele.predict([[type_navire_idx, type_avarie_idx, tonnage]])
    return round(float(prediction[0]), 1)