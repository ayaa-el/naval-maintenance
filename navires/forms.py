from django import forms
from .models import Navire, Escale, Ouvrage

class NavireForm(forms.ModelForm):
    ouvrage = forms.ModelChoiceField(
        queryset=Ouvrage.objects.all(),
        required=False,
        label="Ouvrage d'escale initial (optionnel)",
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Aucun (Pas d'escale en cours) --"
    )

    class Meta:
        model = Navire
        fields = ['matricule', 'nom_navire', 'type_navire', 'tonnage', 'taille', 'ouvrage']
        widgets = {
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_navire': forms.TextInput(attrs={'class': 'form-control'}),
            'type_navire': forms.Select(attrs={'class': 'form-select'}),
            'tonnage': forms.NumberInput(attrs={'class': 'form-control'}),
            'taille': forms.Select(attrs={'class': 'form-select'}),
        }

class EscaleForm(forms.ModelForm):
    class Meta:
        model = Escale
        fields = ['ouvrage', 'date_entree']
        widgets = {
            'ouvrage': forms.Select(attrs={'class': 'form-select'}),
            'date_entree': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
