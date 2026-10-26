import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)

BLEU_ANP = colors.HexColor("#1F3864")


def generer_facture_pdf(escale):
    """Crée le fichier PDF de la facture pour une escale donnée, avec une mise en page soignée."""

    dossier = os.path.join(os.getcwd(), "factures")
    os.makedirs(dossier, exist_ok=True)

    nom_fichier = f"{escale.numero_facture or 'facture_temp'}.pdf"
    chemin_complet = os.path.join(dossier, nom_fichier)

    doc = SimpleDocTemplate(
        chemin_complet,
        pagesize=A4,
        topMargin=1.2 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    titre_style = ParagraphStyle(
        "TitreANP", parent=styles["Heading1"], textColor=colors.white,
        fontSize=18, alignment=1, spaceAfter=4,
    )
    numero_facture_style = ParagraphStyle(
        "NumeroFacture", parent=styles["Heading2"], textColor=BLEU_ANP,
        fontSize=15, alignment=0, spaceAfter=0,
    )

    elements = []

    # --- Ligne du haut : logo aligné à droite, hors de la bannière bleue ---
    logo_path = os.path.join(os.getcwd(), "static", "logo_anp.png")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2.5 * cm, height=2.5 * cm)
        ligne_logo = Table([["", logo]], colWidths=[13.5 * cm, 3 * cm])
        ligne_logo.setStyle(TableStyle([
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(ligne_logo)

    # --- Bannière bleue : titre uniquement (plus de logo ici) ---
    entete_table = Table(
        [[Paragraph("Agence Nationale des Ports (ANP)<br/>Facture de Séjour Portuaire",
                     titre_style)]],
        colWidths=[16.5 * cm],
    )
    entete_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLEU_ANP),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    elements.append(entete_table)
    elements.append(Spacer(1, 0.8 * cm))

    # --- Numéro de facture, affiché en évidence tout en haut ---
    elements.append(Paragraph(
        f"N° Facture : {escale.numero_facture or 'Non généré'}",
        numero_facture_style,
    ))
    elements.append(Spacer(1, 0.6 * cm))

    # --- Tableau des informations générales (nom, matricule, ouvrage, dates, statut) ---
    infos = [
        ["Nom du navire", escale.navire.nom_navire],
        ["Matricule", escale.navire.matricule],
        ["Ouvrage", escale.ouvrage.nom_ouvrage],
        ["Date d'entrée", str(escale.date_entree)],
        ["Date de sortie", str(escale.date_sortie) if escale.date_sortie else "En cours"],
        ["Statut", escale.get_statut_facture_display()],
    ]
    table_infos = Table(infos, colWidths=[5 * cm, 11.5 * cm])
    table_infos.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF1FB")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.75, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(table_infos)
    elements.append(Spacer(1, 0.8 * cm))

    # --- Tableau des services consommés (uniquement s'il y en a) ---
    services = escale.services.all()
    if services.exists():
        elements.append(Paragraph("<b>Services consommés</b>", styles["Heading3"]))
        elements.append(Spacer(1, 0.3 * cm))
        lignes_services = [["Service", "Quantité", "Prix unitaire", "Montant"]]
        for s in services:
            montant = float(s.quantite) * float(s.prix_unitaire)
            lignes_services.append([
                s.nom_service,
                str(s.quantite),
                f"{s.prix_unitaire} MAD",
                f"{montant:.2f} MAD",
            ])
        table_services = Table(lignes_services, colWidths=[6 * cm, 3 * cm, 3.5 * cm, 3.5 * cm])
        table_services.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLEU_ANP),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.75, colors.grey),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(table_services)
        elements.append(Spacer(1, 0.8 * cm))

    # --- Montant total, mis en valeur ---
    table_total = Table(
        [["MONTANT TOTAL", f"{escale.montant_total_facture} MAD"]],
        colWidths=[11 * cm, 5 * cm],
    )
    table_total.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLEU_ANP),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 13),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (1, 0), (1, 0), 12),
    ]))
    elements.append(table_total)

    doc.build(elements)

    escale.chemin_facture_pdf = chemin_complet
    escale.save()
    return chemin_complet