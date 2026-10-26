from django import forms
from .models import Employe, TacheReparation, SuiviAvancement


class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = ["nom", "prenom", "role_metier", "salaire_base_fixe", "actif"]
        widgets = {
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "prenom": forms.TextInput(attrs={"class": "form-control"}),
            "role_metier": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Soudeur, Peintre..."}),
            "salaire_base_fixe": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "actif": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class TacheReparationForm(forms.ModelForm):
    CHOIX_TACHES = [
        ("Soudure coque", "Soudure coque"),
        ("Peinture navire", "Peinture navire"),
        ("Révision moteur", "Révision moteur"),
        ("Travaux électriques", "Travaux électriques"),
        ("Nettoyage cales", "Nettoyage cales"),
        ("Réparation pompe", "Réparation pompe"),
        ("Maintenance grue", "Maintenance grue"),
        ("Autre", "Autre"),
    ]
    description_travail = forms.ChoiceField(choices=CHOIX_TACHES, widget=forms.Select(attrs={"class": "form-select"}))

    class Meta:
        model = TacheReparation
        fields = ["escale", "equipement", "employe", "description_travail", "date_tache", "heure_debut", "heure_fin", "tarif_horaire_application"]
        widgets = {
            "escale": forms.Select(attrs={"class": "form-select"}),
            "equipement": forms.Select(attrs={"class": "form-select"}),
            "employe": forms.Select(attrs={"class": "form-select"}),
            "date_tache": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "heure_debut": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "heure_fin": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "tarif_horaire_application": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "MAD/heure"}),
        }
        labels = {
            "escale": "Escale (Navire concerné - Optionnel)",
            "equipement": "Équipement concerné (Optionnel)",
            "employe": "Employé Haddoun",
            "description_travail": "Description du travail",
            "date_tache": "Date",
            "heure_debut": "Heure début",
            "heure_fin": "Heure fin",
            "tarif_horaire_application": "Tarif horaire (MAD)",
        }

    def clean(self):
        cleaned_data = super().clean()
        escale = cleaned_data.get("escale")
        equipement = cleaned_data.get("equipement")
        if not escale and not equipement:
            raise forms.ValidationError("Veuillez sélectionner soit une escale, soit un équipement.")
        if escale and equipement:
            raise forms.ValidationError("Une tâche ne peut pas concerner à la fois une escale et un équipement.")
        return cleaned_data


class SuiviAvancementForm(forms.ModelForm):
    class Meta:
        model = SuiviAvancement
        fields = ["escale", "pourcentage_avancement", "commentaire"]
        widgets = {
            "escale": forms.Select(attrs={"class": "form-select"}),
            "pourcentage_avancement": forms.NumberInput(attrs={
                "class": "form-control", "min": 0, "max": 100, "type": "range",
                "oninput": "this.nextElementSibling.value = this.value + '%'"
            }),
            "commentaire": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Observations sur l'avancement..."}),
        }
        labels = {
            "escale": "Escale (Navire concerné)",
            "pourcentage_avancement": "Avancement (%)",
            "commentaire": "Commentaire",
        }



