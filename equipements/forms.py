from django import forms
from .models import Equipement


class EquipementForm(forms.ModelForm):
    class Meta:
        model = Equipement
        fields = ["reference", "nom", "type_equipement", "localisation", "statut"]
        widgets = {
            "reference": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: EQ-001"}),
            "nom": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom de l'équipement"}),
            "type_equipement": forms.Select(attrs={"class": "form-select"}),
            "localisation": forms.TextInput(attrs={"class": "form-control", "placeholder": "Zone / Quai"}),
            "statut": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "reference": "Référence",
            "nom": "Nom de l'équipement",
            "type_equipement": "Type",
            "localisation": "Localisation",
            "statut": "Statut",
        }
