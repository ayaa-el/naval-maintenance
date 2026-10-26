# 🚢 Plateforme de Gestion de la Maintenance Navale (GMAO)

[![Django](https://img.shields.io/badge/Django-5.0+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

> Application web full-stack dédiée à la gestion, la traçabilité et l'automatisation des opérations de maintenance navale portuaire entre l'**Agence Nationale des Ports (ANP)** et son prestataire de maintenance technique (**Société Haddoun**).

---

## 📌 Présentation du Projet

Dans le cadre des opérations portuaires, la maintenance préventive et corrective des navires et équipements exige un contrôle rigoureux, une traçabilité sans faille et une gestion financière transparente.

Cette plateforme centralise l'ensemble du cycle de vie des interventions :
1. **Fiches d'Intervention** : Déclaration des avaries et pannes techniques par les techniciens de l'ANP.
2. **Diagnostic Technique** : Analyse et précision du problème par l'équipe technique du prestataire (Haddoun).
3. **Ordres de Travail (OT)** : Chiffrage et planification des travaux avec workflow de validation hiérarchique.
4. **Bons de Livraison (BL) & Facturation** : Clôture des travaux, émission des BL et factures avec génération de documents officiels imprimables aux normes de l'ANP.
5. **Gestion Maritime & RH** : Suivi des escales des navires et pointage horaire des équipes.

---

## ⚙️ Fonctionnalités Clés

### 🔒 Gestion des Rôles & Sécurité (RBAC)
Le système applique un contrôle d'accès granulaire selon 5 profils utilisateurs :
* **Directeur ANP** : Tableau de bord stratégique, supervision globale, déverrouillage exceptionnel des ordres de travail.
* **Superviseur ANP** : Validation des Ordres de Travail (OT), validation des Bons de Livraison (BL) et approbation des factures.
* **Technicien ANP** : Déclaration des fiches d'intervention sur navires/équipements et suivi des escales.
* **Superviseur Haddoun (Chef d'équipe)** : Création des OT, fixation des prix, émission des BL et des factures.
* **Technicien Haddoun** : Diagnostic technique terrain et réalisation des travaux sur site.

### 📄 Système Documentaire & Impression Officielle
* Génération de documents individuels optimisés pour l'impression officielle (Logo ANP, horodatage, numérotation unique et signatures) :
  * Fiche d'intervention
  * Ordre de travail (OT)
  * Bon de livraison (BL)
  * Facture certifiée

### 📊 Tableaux de Bord Adaptatifs
* Dashboards personnalisés avec indicateurs de performance clés (KPIs), alertes d'actions urgentes et statistiques d'interventions.

---

## 🛠️ Stack Technique

* **Backend :** Python 3, Django (MVT architecture, Django ORM, Formsets, Authentication & Permissions)
* **Frontend :** HTML5, CSS3, JavaScript, Bootstrap 5, FontAwesome, Chart.js
* **Base de données :** SQLite (Développement) / Compatible PostgreSQL & MySQL
* **Génération de documents :** Templates HTML/CSS print-ready, ReportLab

---

## 🚀 Installation et Lancement

### 1. Cloner le dépôt
```bash
git clone https://github.com/votre-utilisateur/naval-maintenance.git
cd naval-maintenance
```

### 2. Créer et activer l'environnement virtuel
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Appliquer les migrations
```bash
python manage.py migrate
```

### 5. Charger les données de test (optionnel)
```bash
python seed_donnees.py
```

### 6. Lancer le serveur de développement
```bash
python manage.py runserver
```
Accédez à l'application sur : [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📂 Structure du Projet

```text
naval_maintenance/
├── comptes/             # Authentification, profils et gestion des rôles
├── conventionnement/    # Cœur métier : Fiches, OT, BL, Factures et Impressions
├── navires/             # Gestion de la flotte et suivi des escales maritimes
├── equipements/         # Inventaire des équipements portuaires
├── rh/                  # Gestion des employés et pointage horaire
├── static/              # Fichiers CSS, JS, images (dont logo officiel ANP)
├── templates/           # Templates globaux et layout de base
├── manage.py
└── requirements.txt
```

---

## 👩‍💻 Auteur
Développé par **Aya** — Élève-ingénieure en Informatique & Systèmes d'Information.
