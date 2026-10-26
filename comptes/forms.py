from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'telephone', 'date_naissance', 'cin', 'photo_profil']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de famille'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email professionnel'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'N° de téléphone'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'N° de Carte Nationale'}),
            'photo_profil': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
        labels = {
            'username': 'Nom d\'utilisateur',
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Adresse électronique',
            'telephone': 'N° de Téléphone',
            'date_naissance': 'Date de Naissance',
            'cin': 'CIN (Carte Nationale)',
            'photo_profil': 'Photo de profil'
        }
