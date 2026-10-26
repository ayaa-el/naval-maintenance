import json
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from equipements.models import Equipement
from navires.models import Navire, Ouvrage, Escale
from conventionnement.models import FicheIntervention, OrdreTravail, BonLivraison, Facture
from conventionnement import views

class ConventionnementViewsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.factory = RequestFactory()
        
        self.haddoun = User.objects.create_user(username="haddoun", password="testpass", role="CHEF_EQUIPE")
        self.anp = User.objects.create_user(username="anp", password="testpass", role="SUPERVISEUR_ANP")
        self.directeur = User.objects.create_user(username="directeur", password="testpass", role="DIRECTEUR")

        self.add_fiche_perm = Permission.objects.get(codename="add_ficheintervention")
        self.change_fiche_perm = Permission.objects.get(codename="change_ficheintervention")
        self.create_ot_perm = Permission.objects.get(codename="can_create_ordretravail")
        self.validate_ot_perm = Permission.objects.get(codename="can_validate_ordretravail")
        self.realize_perm = Permission.objects.get(codename="can_realize_intervention")
        self.create_bl_perm = Permission.objects.get(codename="can_create_bonlivraison")
        self.create_facture_perm = Permission.objects.get(codename="can_create_facture")
        self.unlock_perm = Permission.objects.get(codename="can_unlock_ordretravail")
        
        self.haddoun.user_permissions.set([
            self.change_fiche_perm, self.create_ot_perm, self.realize_perm,
            self.create_bl_perm, self.create_facture_perm
        ])
        self.anp.user_permissions.set([self.add_fiche_perm, self.change_fiche_perm, self.validate_ot_perm])
        self.directeur.user_permissions.set([self.change_fiche_perm, self.unlock_perm, Permission.objects.get(codename="change_ordretravail")])
        
        self.haddoun = User.objects.get(pk=self.haddoun.pk)
        self.anp = User.objects.get(pk=self.anp.pk)
        self.directeur = User.objects.get(pk=self.directeur.pk)

        self.equipement = Equipement.objects.create(reference="EQ-01", nom="Pompe", type_equipement=Equipement.Type.BATEAU_PORTE)
        self.navire = Navire.objects.create(matricule="NAV-1", nom_navire="Bateau", tonnage=1000, type_navire="Cargo", taille="Petite")
        self.ouvrage = Ouvrage.objects.create(id_ouvrage=1, nom_ouvrage="Cale", prix_fixe_journalier=1000)
        self.escale = Escale.objects.create(navire=self.navire, ouvrage=self.ouvrage, date_entree="2026-06-01", date_sortie="2026-06-05")

    def setup_request(self, request, user):
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.contrib.messages.middleware import MessageMiddleware
        
        request.user = user
        middleware = SessionMiddleware(lambda r: None)
        middleware.process_request(request)
        request.session.save()
        
        middleware2 = MessageMiddleware(lambda r: None)
        middleware2.process_request(request)
        return request

    def test_workflow_equipement(self):
        # A. TECHNICIEN_ANP crée une fiche
        request = self.setup_request(self.factory.post(reverse("conventionnement:creer_fiche_equipement"), {"equipement": self.equipement.id, "type_avarie": "Soudure", "description_probleme": "Panne"}), self.anp)
        response = views.creer_fiche_equipement(request)
        self.assertEqual(response.status_code, 302)
        fiche = FicheIntervention.objects.get(description_probleme="Panne")
        
        # B. TECHNICIEN_HADDOUN ajoute diagnostic
        request = self.setup_request(self.factory.post(reverse("conventionnement:ajouter_diagnostic", args=[fiche.id]), {"precision_probleme": "Moteur HS"}), self.haddoun)
        response = views.ajouter_diagnostic(request, fiche.id)
        fiche.refresh_from_db()
        self.assertEqual(fiche.precision_probleme, "Moteur HS")
        
        # C. SUPERVISEUR_ANP crée OT
        post_data = {
            "lignes-TOTAL_FORMS": "1",
            "lignes-INITIAL_FORMS": "0",
            "lignes-MIN_NUM_FORMS": "1",
            "lignes-MAX_NUM_FORMS": "1000",
            "lignes-0-description": "Test",
            "lignes-0-quantite": "1",
            "lignes-0-prix_unitaire": "100",
        }
        request = self.setup_request(self.factory.post(reverse("conventionnement:creer_ordre_travail", args=[fiche.id]), post_data), self.anp)
        response = views.creer_ordre_travail(request, fiche.id)
        ordre = OrdreTravail.objects.get(fiche_intervention=fiche)
        self.assertEqual(ordre.status, OrdreTravail.Statut.ATTENTE_VALIDATION_ANP)
        
        # A. TECHNICIEN_ANP valide OT
        request = self.setup_request(self.factory.post(reverse("conventionnement:valider_refuser_ordre", args=[ordre.id]), {"status": OrdreTravail.Statut.VALIDE}), self.anp)
        views.valider_refuser_ordre(request, ordre.id)
        ordre.refresh_from_db()
        self.assertEqual(ordre.status, OrdreTravail.Statut.VALIDE)
        
        # B. TECHNICIEN_HADDOUN réalise
        request = self.setup_request(self.factory.post(reverse("conventionnement:realiser_intervention", args=[ordre.id])), self.haddoun)
        views.realiser_intervention(request, ordre.id)
        ordre.refresh_from_db()
        self.assertEqual(ordre.status, OrdreTravail.Statut.TERMINE)
        
        # B. TECHNICIEN_HADDOUN crée BL
        post_data_bl = {
            "commentaire": "Fait",
            "lignes-TOTAL_FORMS": "1",
            "lignes-INITIAL_FORMS": "1",
            "lignes-MIN_NUM_FORMS": "0",
            "lignes-MAX_NUM_FORMS": "1000",
            "lignes-0-id": str(ordre.lignes.first().id),
            "lignes-0-description": "Test",
            "lignes-0-quantite": "1",
            "lignes-0-prix_unitaire": "120.00",
        }
        request = self.setup_request(self.factory.post(reverse("conventionnement:creer_bon_livraison", args=[ordre.id]), post_data_bl), self.haddoun)
        views.creer_bon_livraison(request, ordre.id)
        bon = BonLivraison.objects.get(ordre_travail=ordre)
        
        # A. TECHNICIEN_ANP valide BL
        request = self.setup_request(self.factory.post(reverse("conventionnement:valider_bon_livraison", args=[bon.id]), {"status": BonLivraison.Statut.VALIDE}), self.anp)
        views.valider_bon_livraison(request, bon.id)
        bon.refresh_from_db()
        self.assertEqual(bon.statut, BonLivraison.Statut.VALIDE)
        
        # B. TECHNICIEN_HADDOUN crée Facture
        request = self.setup_request(self.factory.post(reverse("conventionnement:creer_facture", args=[bon.id]), {"montant_total": "100.00", "condition_paiement": "Virement bancaire"}), self.haddoun)
        views.creer_facture(request, bon.id)
        ordre.refresh_from_db()
        self.assertTrue(ordre.bloque_apres_facture)
        facture = Facture.objects.get(bon_livraison=bon)

        # C. SUPERVISEUR_HADDOUN valide la Facture (Paiement)
        request = self.setup_request(self.factory.post(reverse("conventionnement:valider_facture", args=[facture.id])), self.haddoun)
        views.valider_facture(request, facture.id)
        facture.refresh_from_db()
        self.assertEqual(facture.statut, Facture.Statut.PAYEE)
        
        # D. Sécurité : HADDOUN ne peut plus modifier l'OT ou le diagnostic
        request = self.setup_request(self.factory.post(reverse("conventionnement:ajouter_diagnostic", args=[fiche.id]), {"precision_probleme": "Nouveau"}), self.haddoun)
        with self.assertRaises(PermissionDenied):
            views.ajouter_diagnostic(request, fiche.id)
            
        # C. DIRECTEUR déverrouille
        request = self.setup_request(self.factory.post(reverse("conventionnement:deverrouiller_ordre", args=[ordre.id]), {"deverrouillage_commentaire": "ok"}), self.directeur)
        views.deverrouiller_ordre(request, ordre.id)
        ordre.refresh_from_db()
        self.assertEqual(ordre.deverrouille_par, self.directeur)
        self.assertFalse(ordre.is_locked)
        self.assertTrue(ordre.bloque_apres_facture) # Traçabilité conservée
        
        # C. DIRECTEUR modifie après déverrouillage
        request = self.setup_request(self.factory.post(reverse("conventionnement:modifier_ordre", args=[ordre.id]), {"montant_total": "200.00"}), self.directeur)
        views.modifier_ordre(request, ordre.id)
        ordre.refresh_from_db()
        self.assertEqual(ordre.montant_total, 200)

    def test_navire_workflow_preserved(self):
        fiche_navire = FicheIntervention.objects.create(escale=self.escale, description_probleme="Navire", cree_par=self.haddoun)
        request = self.setup_request(self.factory.post(reverse("conventionnement:generer_ordre_travail", args=[fiche_navire.id])), self.anp)
        views.generer_ordre_travail(request, fiche_navire.id)
        self.assertTrue(OrdreTravail.objects.filter(fiche_intervention=fiche_navire).exists())
