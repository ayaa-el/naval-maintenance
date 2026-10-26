from django import forms
from django.forms import inlineformset_factory

from .models import FicheIntervention, BonLivraison, Facture, OrdreTravail, LigneOrdreTravail


# ─── Fiche d'Intervention ─────────────────────────────────────────────────────

TYPE_AVARIE_CHOICES = [
    ("", "-- Choisir le type d'avarie --"),
    ("Soudure", "🔧 Soudure"),
    ("Peinture", "🖌️ Peinture"),
    ("Moteur", "⚙️ Moteur / Mécanique"),
    ("Electricite", "⚡ Électricité"),
    ("Hydraulique", "💧 Hydraulique"),
    ("Structure", "🏗️ Structure / Coque"),
    ("Autre", "📋 Autre"),
]

class FicheInterventionEquipementForm(forms.ModelForm):
    PROBLEMES_EQUIPEMENT = [
        ("", "-- Choisissez un problème fréquent --"),
        ("Dysfonctionnement du vérin d'ouverture du bateau-porte", "Dysfonctionnement du vérin d'ouverture"),
        ("Fissure détectée sur le vantail du bateau-porte", "Fissure détectée sur le vantail"),
        ("Problème d'étanchéité des joints du bateau-porte", "Problème d'étanchéité des joints"),
        ("Panne du treuil de manœuvre", "Panne du treuil de manœuvre"),
        ("Corrosion importante sur la structure du bateau-porte", "Corrosion importante"),
    ]
    predefined_probleme = forms.ChoiceField(
        choices=PROBLEMES_EQUIPEMENT,
        required=False,
        label="Problème fréquent (optionnel)",
        widget=forms.Select(attrs={"class": "form-select", "onchange": "document.getElementById('id_description_probleme').value = this.value;"})
    )

    class Meta:
        model = FicheIntervention
        fields = ["equipement", "type_avarie", "predefined_probleme", "description_probleme"]
        widgets = {
            "equipement": forms.Select(attrs={"class": "form-select"}),
            "type_avarie": forms.Select(
                choices=TYPE_AVARIE_CHOICES,
                attrs={"class": "form-select"}
            ),
            "description_probleme": forms.Textarea(attrs={
                "rows": 4, "class": "form-control", "id": "id_description_probleme",
                "placeholder": "Décrivez le problème constaté..."
            }),
        }
        labels = {
            "equipement": "Équipement concerné",
            "type_avarie": "Type d'avarie",
            "description_probleme": "Description du problème initial",
        }


class FicheInterventionNavireForm(forms.ModelForm):
    PROBLEMES_NAVIRE = [
        ("", "-- Choisissez un problème fréquent --"),
        ("Fissure suspectée sur la coque sous la ligne de flottaison", "Fissure suspectée sur la coque"),
        ("Avarie de l'hélice principale", "Avarie de l'hélice principale"),
        ("Surchauffe anormale du moteur principal", "Surchauffe anormale du moteur"),
        ("Problème d'étanchéité des cales à cargaison", "Problème d'étanchéité des cales"),
        ("Corrosion sur le safran de gouvernail", "Corrosion sur le safran"),
    ]
    predefined_probleme = forms.ChoiceField(
        choices=PROBLEMES_NAVIRE,
        required=False,
        label="Problème fréquent (optionnel)",
        widget=forms.Select(attrs={"class": "form-select", "onchange": "document.getElementById('id_description_probleme').value = this.value;"})
    )

    class Meta:
        model = FicheIntervention
        fields = ["escale", "type_avarie", "predefined_probleme", "description_probleme"]
        widgets = {
            "escale": forms.Select(attrs={"class": "form-select"}),
            "type_avarie": forms.Select(
                choices=TYPE_AVARIE_CHOICES,
                attrs={"class": "form-select"}
            ),
            "description_probleme": forms.Textarea(attrs={
                "rows": 4, "class": "form-control", "id": "id_description_probleme",
                "placeholder": "Décrivez le problème constaté..."
            }),
        }
        labels = {
            "escale": "Escale du navire concerné",
            "type_avarie": "Type d'avarie",
            "description_probleme": "Description du problème constaté",
        }


class FicheInterventionEditForm(forms.ModelForm):
    """Modification de la fiche avant validation (Superviseur ANP)."""
    class Meta:
        model = FicheIntervention
        fields = ["equipement", "type_avarie", "description_probleme"]
        widgets = {
            "equipement": forms.Select(attrs={"class": "form-select"}),
            "type_avarie": forms.Select(
                choices=TYPE_AVARIE_CHOICES,
                attrs={"class": "form-select"}
            ),
            "description_probleme": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        }
        labels = {
            "equipement": "Équipement concerné",
            "type_avarie": "Type d'avarie",
            "description_probleme": "Description du problème",
        }


class DiagnosticForm(forms.ModelForm):
    """Technicien ANP renseigne le diagnostic précis."""

    DIAGNOSTIC_CHOICES = [
        ("", "-- Ou choisissez un diagnostic prédéfini --"),
        ("Usure normale des pièces mécaniques", "Usure normale des pièces mécaniques"),
        ("Corrosion avancée de la structure", "Corrosion avancée de la structure"),
        ("Fuite hydraulique sur circuit principal", "Fuite hydraulique sur circuit principal"),
        ("Court-circuit dans le câblage électrique", "Court-circuit dans le câblage électrique"),
        ("Rupture de soudure sur le châssis", "Rupture de soudure sur le châssis"),
        ("Défaillance du système de freinage", "Défaillance du système de freinage"),
        ("Détérioration du revêtement de peinture", "Détérioration du revêtement de peinture"),
        ("Anomalie moteur — surchauffe détectée", "Anomalie moteur — surchauffe détectée"),
    ]

    diagnostic_predefined = forms.ChoiceField(
        choices=DIAGNOSTIC_CHOICES,
        required=False,
        label="Diagnostic prédéfini (optionnel)",
        widget=forms.Select(attrs={"class": "form-select", "id": "id_diagnostic_predefined"}),
    )

    class Meta:
        model = FicheIntervention
        fields = ["precision_probleme"]
        widgets = {
            "precision_probleme": forms.Textarea(attrs={
                "rows": 5, "class": "form-control",
                "id": "id_precision_probleme",
                "placeholder": "Détaillez précisément le problème technique constaté..."
            }),
        }
        labels = {
            "precision_probleme": "Diagnostic technique détaillé",
        }


# ─── Ordre de Travail ─────────────────────────────────────────────────────────

class LigneOrdreTravailForm(forms.ModelForm):
    SERVICES_CHOICES = [
        ("", "-- Ou choisissez un service --"),
        ("Main-d'œuvre soudure", "Main-d'œuvre soudure"),
        ("Main-d'œuvre peinture", "Main-d'œuvre peinture"),
        ("Main-d'œuvre mécanique", "Main-d'œuvre mécanique"),
        ("Main-d'œuvre électricité", "Main-d'œuvre électricité"),
        ("Fourniture — Pièces de rechange", "Fourniture — Pièces de rechange"),
        ("Location matériel lourd", "Location matériel lourd"),
        ("Transport et logistique", "Transport et logistique"),
        ("Nettoyage industriel", "Nettoyage industriel"),
        ("Contrôle qualité", "Contrôle qualité"),
    ]

    description_predefined = forms.ChoiceField(
        choices=SERVICES_CHOICES,
        required=False,
        label="Service prédéfini",
        widget=forms.Select(attrs={"class": "form-select ligne-predefined"}),
    )

    class Meta:
        model = LigneOrdreTravail
        fields = ["description", "quantite"]
        widgets = {
            "description": forms.TextInput(attrs={
                "class": "form-control ligne-description",
                "placeholder": "Ou saisissez une description libre..."
            }),
            "quantite": forms.NumberInput(attrs={
                "class": "form-control ligne-quantite",
                "min": "0.5", "step": "0.5", "value": "1"
            }),
        }
        labels = {
            "description": "Description libre",
            "quantite": "Quantité / Heures",
        }


LigneOrdreTravailFormSet = inlineformset_factory(
    OrdreTravail,
    LigneOrdreTravail,
    form=LigneOrdreTravailForm,
    extra=3,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class LigneBonLivraisonForm(forms.ModelForm):
    class Meta:
        model = LigneOrdreTravail
        fields = ["description", "quantite", "prix_unitaire"]
        widgets = {
            "description": forms.TextInput(attrs={"class": "form-control-plaintext", "readonly": "readonly"}),
            "quantite": forms.NumberInput(attrs={"class": "form-control-plaintext", "readonly": "readonly"}),
            "prix_unitaire": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01", "placeholder": "0.00"}),
        }
        labels = {
            "description": "Service / Tâche",
            "quantite": "Quantité / Heures",
            "prix_unitaire": "Prix unitaire (MAD)",
        }


LigneBonLivraisonFormSet = inlineformset_factory(
    OrdreTravail,
    LigneOrdreTravail,
    form=LigneBonLivraisonForm,
    extra=0,
    can_delete=False,
)


class OrdreTravailValidationForm(forms.Form):
    status = forms.ChoiceField(
        choices=(
            (OrdreTravail.Statut.VALIDE, "✅ Valider cet ordre de travail"),
            (OrdreTravail.Statut.REFUSE, "❌ Refuser cet ordre de travail"),
        ),
        widget=forms.RadioSelect,
        label="Décision",
    )
    refuse_commentaire = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        required=False,
        label="Commentaire (obligatoire en cas de refus)",
    )

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        commentaire = cleaned_data.get("refuse_commentaire")
        if status == OrdreTravail.Statut.REFUSE and not commentaire:
            raise forms.ValidationError("Un commentaire est requis lorsque l'ordre est refusé.")
        return cleaned_data


# ─── Bon de Livraison ─────────────────────────────────────────────────────────


class BonLivraisonForm(forms.ModelForm):
    class Meta:
        model = BonLivraison
        fields = ["commentaire"]
        widgets = {
            "commentaire": forms.Textarea(attrs={
                "rows": 3, "class": "form-control",
                "placeholder": "Remarques ou précisions sur la livraison..."
            }),
        }
        labels = {
            "commentaire": "Commentaire / Remarques",
        }


class BonLivraisonValidationForm(forms.Form):
    status = forms.ChoiceField(
        choices=(
            (BonLivraison.Statut.VALIDE, "✅ Valider ce bon de livraison"),
            (BonLivraison.Statut.REFUSE, "❌ Refuser ce bon de livraison"),
        ),
        widget=forms.RadioSelect,
        label="Décision",
    )
    commentaire = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        required=False,
        label="Commentaire (obligatoire en cas de refus)",
    )

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        commentaire = cleaned_data.get("commentaire")
        if status == BonLivraison.Statut.REFUSE and not commentaire:
            raise forms.ValidationError("Un commentaire est requis lorsque le bon est refusé.")
        return cleaned_data


# ─── Facture ──────────────────────────────────────────────────────────────────

class FactureForm(forms.ModelForm):
    CONDITION_PAIEMENT_CHOICES = [
        ("Virement bancaire", "🏦 Virement bancaire"),
        ("Chèque", "📄 Chèque"),
        ("Espèces", "💵 Espèces"),
        ("Lettre de crédit", "📋 Lettre de crédit"),
    ]

    condition_paiement = forms.ChoiceField(
        choices=CONDITION_PAIEMENT_CHOICES,
        widget=forms.RadioSelect,
        label="Mode de paiement",
        initial="Virement bancaire",
    )

    class Meta:
        model = Facture
        fields = ["montant_total"]
        widgets = {
            "montant_total": forms.NumberInput(attrs={
                "class": "form-control", "step": "0.01",
                "placeholder": "Montant en MAD..."
            }),
        }
        labels = {
            "montant_total": "Montant Total (MAD)",
        }


# ─── Divers ───────────────────────────────────────────────────────────────────

class OrdreTravailUnlockForm(forms.Form):
    deverrouillage_commentaire = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        required=False,
        label="Raison du déverrouillage",
    )


class OrdreTravailEditForm(forms.ModelForm):
    class Meta:
        model = OrdreTravail
        fields = ["montant_total", "refuse_commentaire"]
        widgets = {
            "montant_total": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "refuse_commentaire": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }
        labels = {
            "montant_total": "Montant total (MAD)",
            "refuse_commentaire": "Commentaire",
        }
