from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import HttpResponse
import openpyxl

from navires.models import Escale, Navire
from navires.pdf_generator import generer_facture_pdf
from rh.models import Employe, TacheReparation
from conventionnement.models import FicheIntervention, BonLivraison, OrdreTravail, Facture
from equipements.models import Equipement


@login_required
def liste_escales(request):
    """Affiche toutes les escales, avec leur statut de paiement."""
    escales = Escale.objects.all().order_by("-date_entree")
    # Recalculer le montant pour les escales non payées pour afficher les montants en temps réel
    for escale in escales:
        if escale.statut_facture != Escale.StatutFacture.PAYE:
            escale.calculer_montant_total()
    return render(request, "facturation/liste_escales.html", {"escales": escales})


@login_required
def valider_paiement(request, escale_id):
    if request.user.role != "SUPERVISEUR_ANP":
        messages.error(request, "Seul le Superviseur ANP peut valider un paiement.")
        return redirect("facturation:liste_escales")

    escale = get_object_or_404(Escale, pk=escale_id)

    escale.calculer_montant_total()
    if not escale.numero_facture:
        escale.generer_numero_facture()
    generer_facture_pdf(escale)

    escale.statut_facture = Escale.StatutFacture.PAYE
    escale.save()

    messages.success(request, f"Paiement validé pour {escale.navire.nom_navire}. Facture {escale.numero_facture} générée.")
    return redirect("facturation:liste_escales")


@login_required
@login_required
def tableau_bord(request):
    """Tableau de bord Directeur ANP : Synthèse Globale ANP & HADDOUN."""
    if request.user.role != "DIRECTEUR":
        messages.error(request, "Accès réservé au Directeur ANP.")
        return redirect("comptes:accueil")

    # Mettre à jour les montants des escales non payées
    for escale in Escale.objects.filter(statut_facture="NON_PAYE"):
        escale.calculer_montant_total()

    ca_total = Escale.objects.filter(statut_facture="PAYE").aggregate(total=Sum("montant_total_facture"))["total"] or 0
    montant_en_attente = Escale.objects.filter(statut_facture="NON_PAYE").aggregate(total=Sum("montant_total_facture"))["total"] or 0
    nombre_escales_total = Escale.objects.count()
    nombre_navires = Navire.objects.count()

    total_equipements = Equipement.objects.count()
    equipements_en_service = Equipement.objects.filter(statut=Equipement.Statut.EN_SERVICE).count()
    equipements_en_reparation = Equipement.objects.filter(statut=Equipement.Statut.EN_REPARATION).count()
    equipements_hors_service = Equipement.objects.filter(statut=Equipement.Statut.HORS_SERVICE).count()

    total_fiches = FicheIntervention.objects.count()
    fiches_avec_ordre = FicheIntervention.objects.filter(ordre_travail__isnull=False).count()
    ot_verrouilles = OrdreTravail.objects.filter(bloque_apres_facture=True).count()
    factures_equipement_total = Facture.objects.aggregate(total=Sum("montant_total"))["total"] or 0

    ca_par_ouvrage = (Escale.objects.filter(statut_facture="PAYE")
                      .values("ouvrage__nom_ouvrage")
                      .annotate(total=Sum("montant_total_facture")).order_by("-total"))

    escales_par_ouvrage = (Escale.objects.values("ouvrage__nom_ouvrage")
                           .annotate(nombre=Count("id")).order_by("-nombre"))

    top_employes = (TacheReparation.objects.values("employe__nom", "employe__prenom")
                    .annotate(total_heures=Sum("duree_heures")).order_by("-total_heures")[:5])

    context = {
        "ca_total": ca_total,
        "montant_en_attente": montant_en_attente,
        "nombre_escales_total": nombre_escales_total,
        "nombre_navires": nombre_navires,
        "total_equipements": total_equipements,
        "equipements_en_service": equipements_en_service,
        "equipements_en_reparation": equipements_en_reparation,
        "equipements_hors_service": equipements_hors_service,
        "ca_par_ouvrage": list(ca_par_ouvrage),
        "escales_par_ouvrage": list(escales_par_ouvrage),
        "top_employes": list(top_employes),
        "total_fiches": total_fiches,
        "fiches_avec_ordre": fiches_avec_ordre,
        "ot_verrouilles": ot_verrouilles,
        "factures_equipement_total": factures_equipement_total,
    }
    return render(request, "facturation/dashboard_directeur_anp.html", context)


@login_required
def tableau_bord_haddoun(request):
    """Tableau de bord Directeur Haddoun : Focus purement Naval et Financier."""
    if request.user.role != "DIRECTEUR_HADDOUN":
        messages.error(request, "Accès réservé au Directeur Haddoun.")
        return redirect("comptes:accueil")

    # Mettre à jour les montants des escales non payées
    for escale in Escale.objects.filter(statut_facture="NON_PAYE"):
        escale.calculer_montant_total()

    ca_total = Escale.objects.filter(statut_facture="PAYE").aggregate(total=Sum("montant_total_facture"))["total"] or 0
    nombre_escales_total = Escale.objects.count()
    nombre_navires = Navire.objects.count()
    
    total_fiches = FicheIntervention.objects.filter(escale__isnull=False).count()
    fiches_avec_ordre = FicheIntervention.objects.filter(escale__isnull=False, ordre_travail__isnull=False).count()
    
    ca_par_ouvrage = (Escale.objects.filter(statut_facture="PAYE")
                      .values("ouvrage__nom_ouvrage")
                      .annotate(total=Sum("montant_total_facture")).order_by("-total"))

    escales_par_ouvrage = (Escale.objects.values("ouvrage__nom_ouvrage")
                           .annotate(nombre=Count("id")).order_by("-nombre"))

    top_employes = (TacheReparation.objects.values("employe__nom", "employe__prenom")
                    .annotate(total_heures=Sum("duree_heures")).order_by("-total_heures")[:5])

    context = {
        "ca_total": ca_total,
        "nombre_escales_total": nombre_escales_total,
        "nombre_navires": nombre_navires,
        "ca_par_ouvrage": list(ca_par_ouvrage),
        "escales_par_ouvrage": list(escales_par_ouvrage),
        "top_employes": list(top_employes),
        "total_fiches": total_fiches,
        "fiches_avec_ordre": fiches_avec_ordre,
    }
    return render(request, "facturation/dashboard_directeur_haddoun.html", context)



@login_required
def exporter_excel(request):
    """Exporte la liste des factures (escales) au format Excel."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Factures"

    ws.append(["Numéro Facture", "Navire", "Ouvrage", "Date Entrée", "Date Sortie", "Montant (MAD)", "Statut"])

    for escale in Escale.objects.all().order_by("-date_entree"):
        ws.append([
            escale.numero_facture or "-",
            escale.navire.nom_navire,
            escale.ouvrage.nom_ouvrage,
            str(escale.date_entree),
            str(escale.date_sortie) if escale.date_sortie else "En cours",
            float(escale.montant_total_facture),
            escale.get_statut_facture_display(),
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=factures_export.xlsx"
    wb.save(response)
    return response