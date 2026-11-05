import pytest

from datetime import date, timedelta, datetime, timezone
from streamlit.testing.v1 import AppTest

from modeles import UserProfile, PregnancyJourney, Appointment, ConceptionJourney
from persistance import exporter_profil, importer_profil

@pytest.fixture(autouse=True)
def simuler_stockage_navigateur(monkeypatch):
    import stockage_navigateur

    reponse = {
        "lecture": "ok",
        "texte": "",
        "erreur_operation": None,
    }

    def faux_stockage(json_propose, *, cle_stockage, key, on_effacement, sauvegarde_auto=False,):
        return reponse.copy()

    monkeypatch.setattr(
        stockage_navigateur,
        "afficher_stockage_navigateur",
        faux_stockage,
    )

    monkeypatch.setattr(
        stockage_navigateur,
        "lire_sauvegarde_initiale",
        lambda: {"lecture": "ok", "texte": ""},
    )

    return reponse

def test_reperes_grossesse_conserves_apres_changement_parcours():
    app = AppTest.from_file("../app.py").run()
    assert not app.exception

    # Ouvrir le parcours grossesse.
    app.radio[0].set_value("Grossesse en cours").run()

    # Saisir une date située 65 jours avant aujourd'hui.
    dernieres_regles = date.today() - timedelta(days=65)
    app.date_input(key="date_regles_grossesse").set_value(
        dernieres_regles
    )

    # Valider le formulaire.
    app.button[0].click().run()

    assert not app.exception
    assert len(app.metric) == 2
    assert app.metric[0].value == "9 SA + 2 jours"
    assert app.metric[1].value == "7 SG + 2 jours"

    # Aller au parcours conception, puis revenir.
    app.radio[0].set_value("Projet de conception").run()
    app.radio[0].set_value("Grossesse en cours").run()

    assert not app.exception
    assert len(app.metric) == 2
    assert app.metric[0].value == "9 SA + 2 jours"
    assert (
        app.date_input(key="date_regles_grossesse").value == dernieres_regles
    )

def test_dpa_conservee_apres_changement_parcours():
    app = AppTest.from_file("../app.py").run()

    app.radio[0].set_value("Grossesse en cours").run()

    app.radio(key="methode_datation_grossesse").set_value("dpa").run()

    dpa = date.today() + timedelta(days=100)
    app.date_input(key="date_accouchement_grossesse").set_value(dpa)
    app.button[0].click().run()

    assert not app.exception
    assert len(app.metric) == 0

    app.radio[0].set_value("Projet de conception").run()
    app.radio[0].set_value("Grossesse en cours").run()

    assert not app.exception
    assert app.radio(key="methode_datation_grossesse").value == "dpa"
    assert app.date_input(key="date_accouchement_grossesse").value == dpa
    assert len(app.metric) == 0

def test_date_vide_ne_remplace_pas_les_reperes_valides():
    app = AppTest.from_file("../app.py").run()
    app.radio[0].set_value("Grossesse en cours").run()

    # Enregistrer une première saisie valide.
    dernieres_regles = date.today() - timedelta(days=65)
    app.date_input(key="date_regles_grossesse").set_value(
        dernieres_regles
    )
    app.button[0].click().run()

    assert not app.exception
    assert app.metric[0].value == "9 SA + 2 jours"

    # Vider le champ et soumettre à nouveau.
    app.date_input(key="date_regles_grossesse").set_value(None)
    app.button[0].click().run()

    assert not app.exception
    assert len(app.error) == 1
    assert app.error[0].value == "Renseignez une date pour continuer."

    # Les derniers repères valides doivent rester présents.
    assert (
        app.session_state["suivi_grossesse"]["date_reference"]
        == dernieres_regles
    )
    assert app.metric[0].value == "9 SA + 2 jours"

def test_changement_methode_sans_validation_conserve_les_reperes():
    app = AppTest.from_file("../app.py").run()
    app.radio[0].set_value("Grossesse en cours").run()

    # Valider des repères fondés sur les dernières règles.
    dernieres_regles = date.today() - timedelta(days=65)
    app.date_input(key="date_regles_grossesse").set_value(
        dernieres_regles
    )
    app.button[0].click().run()

    assert not app.exception
    assert app.metric[0].value == "9 SA + 2 jours"

    # Choisir la méthode DPA sans soumettre le formulaire.
    app.radio(key="methode_datation_grossesse").set_value("dpa").run()

    assert not app.exception
    assert app.radio(key="methode_datation_grossesse").value == "dpa"

    # Les résultats doivent toujours utiliser la saisie validée.
    suivi = app.session_state["suivi_grossesse"]

    assert suivi["methode_datation"] == "dernieres_regles"
    assert suivi["date_reference"] == dernieres_regles
    assert app.metric[0].value == "9 SA + 2 jours"

@pytest.mark.parametrize(
    "methode, cle_date, decalage",
    [
        ("dernieres_regles", "date_regles_grossesse", -65),
        ("dpa", "date_accouchement_grossesse", 100),
    ],
)
def test_effacement_reperes_grossesse(methode, cle_date, decalage):
    app = AppTest.from_file("../app.py").run()
    app.radio[0].set_value("Grossesse en cours").run()

    app.radio(key="methode_datation_grossesse").set_value(methode).run()

    date_saisie = date.today() + timedelta(days=decalage)
    app.date_input(key=cle_date).set_value(date_saisie)
    app.button[0].click().run()

    assert not app.exception
    assert app.session_state["suivi_grossesse"] is not None

    # L'effacement nécessite une confirmation.
    assert app.button(key="effacer_reperes_grossesse").disabled

    app.checkbox(key="confirmer_effacement_grossesse").check().run()

    assert not app.button(key="effacer_reperes_grossesse").disabled

    # Effacer les données validées et remettre le formulaire à zéro.
    app.button(key="effacer_reperes_grossesse").click().run()

    assert not app.exception
    assert app.session_state["suivi_grossesse"] is None
    assert app.radio(key="methode_datation_grossesse").value == "dernieres_regles"
    assert app.date_input(key="date_regles_grossesse").value is None
    assert len(app.metric) == 0

    # Vérifier qu'un changement de parcours ne restaure rien.
    app.radio[0].set_value("Projet de conception").run()
    app.radio[0].set_value("Grossesse en cours").run()

    assert not app.exception
    assert app.session_state["suivi_grossesse"] is None
    assert app.date_input(key="date_regles_grossesse").value is None

def test_effacement_conception_preserve_grossesse():
    app = AppTest.from_file("../app.py").run()

    # Enregistrer des repères grossesse.
    app.radio[0].set_value("Grossesse en cours").run()

    date_grossesse = date.today() - timedelta(days=65)
    app.date_input(key="date_regles_grossesse").set_value(date_grossesse)
    app.button[0].click().run()

    assert not app.exception
    assert app.metric[0].value == "9 SA + 2 jours"

    # Enregistrer des repères conception.
    app.radio[0].set_value("Projet de conception").run()

    app.date_input(key="conception_dernieres_regles").set_value(
        date.today() - timedelta(days=10)
    )
    app.number_input(key="conception_duree_cycle").set_value(30)
    app.number_input(key="conception_duree_regles").set_value(6)
    app.radio(key="conception_regularite").set_value("Irrégulier")
    app.button[0].click().run()

    assert not app.exception
    assert app.session_state["suivi_conception"] is not None

    # Confirmer puis effacer uniquement le suivi conception.
    assert app.button(key="effacer_reperes_conception").disabled

    app.checkbox(key="confirmer_effacement_conception").check().run()

    assert not app.button(key="effacer_reperes_conception").disabled

    app.button(key="effacer_reperes_conception").click().run()

    assert not app.exception
    assert app.session_state["suivi_conception"] is None
    assert app.date_input(key="conception_dernieres_regles").value is None
    assert app.number_input(key="conception_duree_cycle").value == 28
    assert app.number_input(key="conception_duree_regles").value == 5
    assert app.radio(key="conception_regularite").value == "Je ne sais pas"
    assert len(app.metric) == 0

    # Le suivi grossesse doit rester disponible.
    app.radio[0].set_value("Grossesse en cours").run()

    assert not app.exception
    assert app.session_state["suivi_grossesse"]["date_reference"] == date_grossesse
    assert app.metric[0].value == "9 SA + 2 jours"

    # Le suivi conception effacé ne doit pas réapparaître.
    app.radio[0].set_value("Projet de conception").run()

    assert not app.exception
    assert app.session_state["suivi_conception"] is None
    assert app.date_input(key="conception_dernieres_regles").value is None
    assert len(app.metric) == 0

def test_consulter_autre_ecran_ne_change_pas_parcours_actif():
    app = AppTest.from_file("../app.py").run()

    assert not app.exception
    assert app.session_state["profil"].active_journey_id is None

    # Démarrer un parcours conception.
    app.button(key="demarrer_parcours").click().run()

    assert not app.exception

    profil = app.session_state["profil"]
    identifiant_actif = profil.active_journey_id

    assert len(profil.journeys) == 1
    assert profil.journeys[0].type == "conception"
    assert identifiant_actif == profil.journeys[0].id

    # Consulter l'écran grossesse.
    app.radio[0].set_value("Grossesse en cours").run()

    assert not app.exception

    profil = app.session_state["profil"]

    assert profil.active_journey_id == identifiant_actif
    assert len(profil.journeys) == 1
    assert profil.journeys[0].type == "conception"

    # Aucun bouton ne doit proposer un deuxième démarrage.
    assert all(
        bouton.key != "demarrer_parcours"
        for bouton in app.button
    )

def test_terminer_parcours_conserve_historique():
    app = AppTest.from_file("../app.py").run()

    app.button(key="demarrer_parcours").click().run()

    identifiant = app.session_state["profil"].active_journey_id

    assert app.button(key="terminer_parcours_actif").disabled

    app.checkbox(key="confirmer_fin_parcours").check().run()
    app.button(key="terminer_parcours_actif").click().run()

    assert not app.exception

    profil = app.session_state["profil"]

    assert profil.active_journey_id is None
    assert len(profil.journeys) == 1
    assert profil.journeys[0].id == identifiant
    assert profil.journeys[0].status == "completed"
    assert profil.journeys[0].end_date == date.today()
    assert app.button(key="demarrer_parcours") is not None

@pytest.mark.parametrize(
    "ecran_depart, ecran_consulte, ancien_type, nouveau_type",
    [
        (
            "Projet de conception",
            "Grossesse en cours",
            "conception",
            "pregnancy",
        ),
        (
            "Grossesse en cours",
            "Projet de conception",
            "pregnancy",
            "conception",
        ),
    ],
)
def test_transition_depuis_parcours_actif(ecran_depart, ecran_consulte, ancien_type, nouveau_type,):
    app = AppTest.from_file("../app.py").run()

    # Démarrer le parcours choisi.
    app.radio[0].set_value(ecran_depart).run()
    app.button(key="demarrer_parcours").click().run()

    assert not app.exception

    ancien_identifiant = app.session_state["profil"].active_journey_id

    # Consulter l'autre écran ne doit pas déterminer la transition.
    app.radio[0].set_value(ecran_consulte).run()

    assert app.button(key="changer_parcours_actif").disabled

    app.checkbox(key="confirmer_changement_parcours").check().run()

    assert not app.button(key="changer_parcours_actif").disabled

    app.button(key="changer_parcours_actif").click().run()

    assert not app.exception

    profil = app.session_state["profil"]
    assert len(profil.journeys) == 2

    ancien, nouveau = profil.journeys

    assert ancien.id == ancien_identifiant
    assert ancien.type == ancien_type
    assert ancien.status == "completed"
    assert ancien.end_date == date.today()

    assert nouveau.type == nouveau_type
    assert nouveau.status == "active"
    assert nouveau.start_date == date.today()
    assert nouveau.id != ancien.id
    assert profil.active_journey_id == nouveau.id

    # La confirmation doit être renouvelée pour une autre transition.
    assert not app.checkbox(key="confirmer_changement_parcours").value
    assert app.button(key="changer_parcours_actif").disabled

def test_transition_ouvre_ecran_du_nouveau_parcours():
    app = AppTest.from_file("../app.py").run()

    # Démarrer en conception et rester sur cet écran.
    app.button(key="demarrer_parcours").click().run()

    assert app.radio(key="ecran_consulte").value == "Projet de conception"

    # Passer à la grossesse.
    app.checkbox(key="confirmer_changement_parcours").check().run()
    app.button(key="changer_parcours_actif").click().run()

    assert not app.exception
    assert app.radio(key="ecran_consulte").value == "Grossesse en cours"

    # Revenir à un nouveau parcours conception.
    app.checkbox(key="confirmer_changement_parcours").check().run()
    app.button(key="changer_parcours_actif").click().run()

    assert not app.exception
    assert app.radio(key="ecran_consulte").value == "Projet de conception"

def test_reperes_conception_conserves_apres_transition():
    app = AppTest.from_file("../app.py").run()

    # Démarrer le parcours conception.
    app.button(key="demarrer_parcours").click().run()

    # Valider les repères du formulaire.
    dernieres_regles = date.today() - timedelta(days=12)

    app.date_input(key="conception_dernieres_regles").set_value(
        dernieres_regles
    )
    app.number_input(key="conception_duree_cycle").set_value(30)
    app.number_input(key="conception_duree_regles").set_value(6)
    app.radio(key="conception_regularite").set_value("Irrégulier")
    app.button[0].click().run()

    # Rattacher les repères au parcours actif.
    app.button(key="enregistrer_reperes_conception").click().run()

    assert not app.exception

    profil = app.session_state["profil"]
    ancien_identifiant = profil.active_journey_id
    reperes = profil.journeys[0].details

    assert reperes is not None
    assert reperes.last_period_date == dernieres_regles
    assert reperes.average_cycle_length == 30
    assert reperes.period_length == 6
    assert reperes.cycle_regularity == "irregular"

    # Passer au parcours grossesse.
    app.checkbox(key="confirmer_changement_parcours").check().run()
    app.button(key="changer_parcours_actif").click().run()

    assert not app.exception

    profil = app.session_state["profil"]
    ancien, nouveau = profil.journeys

    assert ancien.id == ancien_identifiant
    assert ancien.status == "completed"
    assert ancien.details == reperes

    assert nouveau.type == "pregnancy"
    assert nouveau.status == "active"
    assert nouveau.details is None
    assert profil.active_journey_id == nouveau.id

@pytest.mark.parametrize(
    "methode_formulaire, cle_date, decalage, methode_modele",
    [
        (
            "dernieres_regles",
            "date_regles_grossesse",
            -65,
            "last_period",
        ),
        (
            "dpa",
            "date_accouchement_grossesse",
            100,
            "due_date",
        ),
    ],
)
def test_enregistrer_reperes_grossesse(
    methode_formulaire,
    cle_date,
    decalage,
    methode_modele,
):
    app = AppTest.from_file("../app.py").run()

    # Démarrer un parcours grossesse.
    app.radio(key="ecran_consulte").set_value("Grossesse en cours").run()
    app.button(key="demarrer_parcours").click().run()

    # Saisir et valider les repères.
    app.radio(key="methode_datation_grossesse").set_value(
        methode_formulaire
    ).run()

    date_saisie = date.today() + timedelta(days=decalage)
    app.date_input(key=cle_date).set_value(date_saisie)
    app.button[0].click().run()

    # Enregistrer dans le parcours actif.
    app.button(key="enregistrer_reperes_grossesse").click().run()

    assert not app.exception
    assert not app.error

    profil = app.session_state["profil"]
    reperes = profil.journeys[0].details

    assert reperes is not None
    assert reperes.dating_method == methode_modele

    if methode_modele == "last_period":
        assert reperes.last_period_date == date_saisie
        assert reperes.estimated_due_date is None
    else:
        assert reperes.estimated_due_date == date_saisie
        assert reperes.last_period_date is None

    # Terminer le parcours sans perdre les repères.
    app.checkbox(key="confirmer_fin_parcours").check().run()
    app.button(key="terminer_parcours_actif").click().run()

    assert not app.exception

    profil = app.session_state["profil"]

    assert profil.active_journey_id is None
    assert profil.journeys[0].status == "completed"
    assert profil.journeys[0].details == reperes

@pytest.mark.parametrize(
    "methode, cle_date, decalage",
    [
        ("dernieres_regles", "date_regles_grossesse", -65),
        ("dpa", "date_accouchement_grossesse", 100),
    ],
)
def test_reprendre_reperes_grossesse(methode, cle_date, decalage):
    app = AppTest.from_file("../app.py").run()

    # Créer le parcours et enregistrer ses repères.
    app.radio(key="ecran_consulte").set_value("Grossesse en cours").run()
    app.button(key="demarrer_parcours").click().run()

    app.radio(key="methode_datation_grossesse").set_value(methode).run()

    date_saisie = date.today() + timedelta(days=decalage)
    app.date_input(key=cle_date).set_value(date_saisie)
    app.button[0].click().run()

    app.button(key="enregistrer_reperes_grossesse").click().run()

    assert not app.exception
    assert not app.error

    profil_enregistre = app.session_state["profil"]

    # Réinitialiser uniquement la saisie temporaire.
    app.checkbox(key="confirmer_effacement_grossesse").check().run()
    app.button(key="effacer_reperes_grossesse").click().run()

    assert app.session_state["suivi_grossesse"] is None
    assert app.date_input(key="date_regles_grossesse").value is None

    # Reprendre les repères du parcours actif.
    app.button(key="reprendre_reperes_grossesse").click().run()

    assert not app.exception
    assert app.radio(key="methode_datation_grossesse").value == methode
    assert app.date_input(key=cle_date).value == date_saisie

    # La reprise ne valide pas automatiquement le formulaire.
    assert app.session_state["suivi_grossesse"] is None
    assert len(app.metric) == 0

    # Le profil enregistré reste inchangé.
    assert app.session_state["profil"] == profil_enregistre

    # La personne peut ensuite valider les champs restaurés.
    app.button[0].click().run()

    assert not app.exception
    assert not app.error
    assert (
        app.session_state["suivi_grossesse"]["date_reference"]
        == date_saisie
    )

def test_import_remplace_profil_apres_confirmation():
    app = AppTest.from_file("../app.py").run()

    # Créer un profil et une saisie temporaire dans l'application.
    app.button(key="demarrer_parcours").click().run()
    app.date_input(key="conception_dernieres_regles").set_value(
        date.today() - timedelta(days=10)
    )
    app.button[0].click().run()

    assert not app.exception
    assert app.session_state["suivi_conception"] is not None

    profil_initial = app.session_state["profil"]

    # Préparer un autre profil à importer.
    profil_attendu = UserProfile().demarrer_parcours(
        "pregnancy",
        date.today(),
    )
    profil_attendu = profil_attendu.renseigner_reperes_actifs(
        PregnancyJourney(
            dating_method="due_date",
            estimated_due_date=date.today() + timedelta(days=100),
        )
    )

    contenu = exporter_profil(profil_attendu).encode("utf-8")

    # Sélectionner le fichier ne doit rien remplacer.
    app.file_uploader(key="fichier_import").upload(
        "profil-test.json",
        contenu,
        "application/json",
    ).run()

    assert not app.exception
    assert not app.error
    assert app.session_state["profil"] == profil_initial
    assert app.button(key="appliquer_import").disabled

    # Cocher la confirmation ne suffit pas non plus.
    app.checkbox(key="confirmer_import").check().run()

    assert app.session_state["profil"] == profil_initial
    assert not app.button(key="appliquer_import").disabled

    # Seul le clic applique le remplacement.
    app.button(key="appliquer_import").click().run()

    assert not app.exception
    assert not app.error
    assert app.session_state["profil"] == profil_attendu

    assert app.session_state["suivi_conception"] is None
    assert app.session_state["suivi_grossesse"] is None
    assert app.radio(key="ecran_consulte").value == "Grossesse en cours"
    assert app.date_input(key="date_regles_grossesse").value is None

    assert not app.checkbox(key="confirmer_import").value
    assert app.button(key="appliquer_import").disabled

def test_changer_fichier_annule_confirmation_import():
    app = AppTest.from_file("../app.py").run()
    app.button(key="demarrer_parcours").click().run()

    profil_initial = app.session_state["profil"]

    premier_profil = UserProfile().demarrer_parcours(
        "conception",
        date.today(),
    )
    second_profil = UserProfile().demarrer_parcours(
        "pregnancy",
        date.today(),
    )

    # Sélectionner un premier fichier et confirmer.
    app.file_uploader(key="fichier_import").set_value(
        (
            "premier.json",
            exporter_profil(premier_profil).encode("utf-8"),
            "application/json",
        )
    ).run()

    assert not app.exception
    assert not app.error

    app.checkbox(key="confirmer_import").check().run()

    assert not app.button(key="appliquer_import").disabled

    # Remplacer le fichier sélectionné par un autre.
    app.file_uploader(key="fichier_import").set_value(
        (
            "second.json",
            exporter_profil(second_profil).encode("utf-8"),
            "application/json",
        )
    ).run()

    assert not app.exception
    assert not app.error
    assert not app.checkbox(key="confirmer_import").value
    assert app.button(key="appliquer_import").disabled
    assert app.session_state["profil"] == profil_initial

    # Confirmer à nouveau, puis importer le second fichier.
    app.checkbox(key="confirmer_import").check().run()
    app.button(key="appliquer_import").click().run()

    assert not app.exception
    assert app.session_state["profil"] == second_profil

@pytest.mark.parametrize(
    "contenu",
    [
        b"ceci n'est pas du JSON",
        b'{"schema_version": 2, "profil": {}}',
        b'{"schema_version": 1, "profil": {}}',
        b"\xff\xfe",
    ],
)
def test_import_invalide_preserve_profil(contenu):
    app = AppTest.from_file("../app.py").run()
    app.button(key="demarrer_parcours").click().run()

    profil_initial = app.session_state["profil"]

    app.file_uploader(key="fichier_import").set_value(
        (
            "export-invalide.json",
            contenu,
            "application/json",
        )
    ).run()

    assert not app.exception
    assert len(app.error) == 1
    assert app.session_state["profil"] == profil_initial

    assert all(
        bouton.key != "appliquer_import"
        for bouton in app.button
    )

def test_effacement_complet_apres_import():
    app = AppTest.from_file("../app.py").run()

    profil_importe = UserProfile().demarrer_parcours(
        "pregnancy",
        date.today(),
    )

    # Importer un profil.
    app.file_uploader(key="fichier_import").upload(
        "profil-test.json",
        exporter_profil(profil_importe).encode("utf-8"),
        "application/json",
    ).run()

    app.checkbox(key="confirmer_import").check().run()
    app.button(key="appliquer_import").click().run()

    assert not app.exception
    assert app.session_state["profil"] == profil_importe

    # L'effacement nécessite sa propre confirmation.
    assert app.button(key="effacer_profil_complet").disabled

    app.checkbox(key="confirmer_effacement_total").check().run()
    app.button(key="effacer_profil_complet").click().run()

    assert not app.exception

    profil_vide = app.session_state["profil"]

    assert profil_vide.id != profil_importe.id
    assert profil_vide.journeys == ()
    assert profil_vide.active_journey_id is None

    assert app.session_state["suivi_conception"] is None
    assert app.session_state["suivi_grossesse"] is None
    assert app.file_uploader(key="fichier_import").value is None

    assert not app.checkbox(key="confirmer_effacement_total").value
    assert app.button(key="effacer_profil_complet").disabled

    # Une nouvelle exécution ne doit rien restaurer.
    app.run()

    assert not app.exception
    assert app.session_state["profil"] == profil_vide
    assert app.file_uploader(key="fichier_import").value is None

def test_nouveau_parcours_conception_demarre_sans_anciens_reperes():
    app = AppTest.from_file("../app.py").run()

    # Créer un premier parcours conception et enregistrer ses repères.
    app.button(key="demarrer_parcours").click().run()

    ancienne_date = date.today() - timedelta(days=12)

    app.date_input(key="conception_dernieres_regles").set_value(
        ancienne_date
    )
    app.number_input(key="conception_duree_cycle").set_value(30)
    app.number_input(key="conception_duree_regles").set_value(6)
    app.radio(key="conception_regularite").set_value("Irrégulier")
    app.button[0].click().run()

    app.button(key="enregistrer_reperes_conception").click().run()

    assert not app.exception
    assert not app.error

    anciens_reperes = app.session_state["profil"].journeys[0].details

    # Passer en grossesse, puis démarrer un nouveau parcours conception.
    for _ in range(2):
        app.checkbox(key="confirmer_changement_parcours").check().run()
        app.button(key="changer_parcours_actif").click().run()

        assert not app.exception

    profil = app.session_state["profil"]

    assert len(profil.journeys) == 3

    ancien = profil.journeys[0]
    nouveau = profil.journeys[2]

    # L'ancien parcours conserve ses repères.
    assert ancien.status == "completed"
    assert ancien.details == anciens_reperes
    assert ancien.details.last_period_date == ancienne_date

    # Le nouveau parcours est actif, sans repères hérités.
    assert nouveau.type == "conception"
    assert nouveau.status == "active"
    assert nouveau.details is None
    assert profil.active_journey_id == nouveau.id

    # Le formulaire est lui aussi réinitialisé.
    assert app.session_state["suivi_conception"] is None
    assert app.date_input(key="conception_dernieres_regles").value is None
    assert app.number_input(key="conception_duree_cycle").value == 28
    assert app.number_input(key="conception_duree_regles").value == 5
    assert app.radio(key="conception_regularite").value == "Je ne sais pas"

def test_restauration_locale_remplace_profil_apres_confirmation(simuler_stockage_navigateur,):
    app = AppTest.from_file("../app.py").run()

    # Préparer un profil actuel avec une saisie temporaire.
    app.button(key="demarrer_parcours").click().run()
    app.date_input(key="conception_dernieres_regles").set_value(
        date.today() - timedelta(days=10)
    )
    app.button[0].click().run()

    assert not app.exception
    assert app.session_state["suivi_conception"] is not None

    profil_initial = app.session_state["profil"]

    # Préparer une sauvegarde différente du profil actuel.
    profil_attendu = UserProfile().demarrer_parcours(
        "pregnancy",
        date.today(),
    )
    profil_attendu = profil_attendu.renseigner_reperes_actifs(
        PregnancyJourney(
            dating_method="due_date",
            estimated_due_date=date.today() + timedelta(days=100),
        )
    )

    simuler_stockage_navigateur["texte"] = exporter_profil(
        profil_attendu
    )
    app.run()

    # La présence d'une sauvegarde ne remplace rien.
    assert not app.exception
    assert not app.error
    assert app.session_state["profil"] == profil_initial
    assert app.button(key="restaurer_profil_local").disabled

    # La confirmation seule ne remplace rien non plus.
    app.checkbox(key="confirmer_restauration_locale").check().run()

    assert app.session_state["profil"] == profil_initial
    assert not app.button(key="restaurer_profil_local").disabled

    # Le clic déclenche la restauration.
    app.button(key="restaurer_profil_local").click().run()

    assert not app.exception
    assert not app.error
    assert app.session_state["profil"] == profil_attendu

    assert app.session_state["suivi_conception"] is None
    assert app.session_state["suivi_grossesse"] is None
    assert app.radio(key="ecran_consulte").value == "Grossesse en cours"
    assert app.date_input(key="date_regles_grossesse").value is None

    assert not app.checkbox(key="confirmer_restauration_locale").value
    assert app.button(key="restaurer_profil_local").disabled

def test_changer_sauvegarde_annule_confirmation_locale(simuler_stockage_navigateur,):
    premier_profil = UserProfile().demarrer_parcours(
        "conception",
        date.today(),
    )
    second_profil = UserProfile().demarrer_parcours(
        "pregnancy",
        date.today(),
    )

    # Présenter une première sauvegarde.
    simuler_stockage_navigateur["texte"] = exporter_profil(
        premier_profil
    )
    app = AppTest.from_file("../app.py").run()

    assert not app.exception
    profil_initial = app.session_state["profil"]

    # Confirmer sa restauration, sans encore cliquer.
    app.checkbox(key="confirmer_restauration_locale").check().run()

    assert not app.exception
    assert not app.button(key="restaurer_profil_local").disabled

    # Le composant transmet maintenant une autre sauvegarde.
    simuler_stockage_navigateur["texte"] = exporter_profil(
        second_profil
    )
    app.run()

    assert not app.exception
    assert not app.error
    assert app.session_state["profil"] == profil_initial
    assert not app.checkbox(key="confirmer_restauration_locale").value
    assert app.button(key="restaurer_profil_local").disabled

    # Une nouvelle confirmation permet de restaurer le second profil.
    app.checkbox(key="confirmer_restauration_locale").check().run()
    app.button(key="restaurer_profil_local").click().run()

    assert not app.exception
    assert not app.error
    assert app.session_state["profil"] == second_profil

@pytest.mark.parametrize(
    "lecture, texte, erreur_attendue",
    [
        ("ok", "", False),
        ("ok", "ceci n'est pas du JSON", True),
        ("ok", '{"schema_version": 99, "profil": {}}', True),
        ("erreur", None, True),
    ],
    ids=[
        "absente",
        "json_invalide",
        "version_inconnue",
        "lecture_refusee",
    ],
)
def test_sauvegarde_inutilisable_preserve_profil(
    simuler_stockage_navigateur,
    lecture,
    texte,
    erreur_attendue,
):
    app = AppTest.from_file("../app.py").run()

    # Préparer un profil et une saisie temporaire.
    app.button(key="demarrer_parcours").click().run()
    app.date_input(key="conception_dernieres_regles").set_value(
        date.today() - timedelta(days=10)
    )
    app.button[0].click().run()

    assert not app.exception

    profil_initial = app.session_state["profil"]
    saisie_initiale = app.session_state["suivi_conception"].copy()

    # Simuler la réponse du navigateur.
    simuler_stockage_navigateur.update(
        lecture=lecture,
        texte=texte,
    )
    app.run()

    # Aucun remplacement ni effacement des données actuelles.
    assert not app.exception
    assert app.session_state["profil"] == profil_initial
    assert app.session_state["suivi_conception"] == saisie_initiale

    assert bool(app.error) == erreur_attendue
    assert all(
        bouton.key != "restaurer_profil_local"
        for bouton in app.button
    )

def test_demarrage_attend_puis_restaure_sans_ecraser_la_session(
    monkeypatch,
):
    import stockage_navigateur

    # Le navigateur n'a pas encore répondu.
    reponse_initiale = {"resultat": None}

    monkeypatch.setattr(
        stockage_navigateur,
        "lire_sauvegarde_initiale",
        lambda: reponse_initiale["resultat"],
    )

    app = AppTest.from_file("../app.py").run()

    assert not app.exception
    assert "profil" not in app.session_state
    assert not app.radio

    # Le navigateur transmet une sauvegarde valide.
    profil_attendu = UserProfile().demarrer_parcours(
        "pregnancy",
        date.today(),
    )
    profil_attendu = profil_attendu.renseigner_reperes_actifs(
        PregnancyJourney(
            dating_method="due_date",
            estimated_due_date=date.today() + timedelta(days=100),
        )
    )

    reponse_initiale["resultat"] = { # type: ignore
        "lecture": "ok",
        "texte": exporter_profil(profil_attendu),
    }
    app.run()

    assert not app.exception
    assert not app.error
    assert app.session_state["profil"] == profil_attendu
    assert app.radio(key="ecran_consulte").value == "Grossesse en cours"

    # Modifier le profil restauré en terminant son parcours.
    app.checkbox(key="confirmer_fin_parcours").check().run()
    app.button(key="terminer_parcours_actif").click().run()

    assert not app.exception

    profil_modifie = app.session_state["profil"]

    assert profil_modifie.active_journey_id is None
    assert profil_modifie.journeys[0].status == "completed"

    # Une réexécution ne doit pas réappliquer l'ancienne sauvegarde.
    app.run()

    assert not app.exception
    assert app.session_state["profil"] == profil_modifie

def test_sauvegarde_auto_attend_confirmation_et_sarrete_sur_erreur(
    monkeypatch,
    simuler_stockage_navigateur,
):
    import stockage_navigateur

    demandes = []
    reponse = simuler_stockage_navigateur

    def observer_stockage(
        json_propose,
        *,
        cle_stockage,
        key,
        on_effacement,
        sauvegarde_auto=False,
    ):
        demandes.append(sauvegarde_auto)
        return reponse.copy()

    monkeypatch.setattr(
        stockage_navigateur,
        "afficher_stockage_navigateur",
        observer_stockage,
    )

    # Un profil initial vide ne déclenche pas de sauvegarde.
    app = AppTest.from_file("../app.py").run()

    assert not app.exception
    assert demandes[-1] is False

    # La création d'un parcours demande une sauvegarde.
    app.button(key="demarrer_parcours").click().run()

    assert not app.exception
    assert demandes[-1] is True

    profil_cree = app.session_state["profil"]

    # Simuler la confirmation du navigateur.
    reponse["texte"] = exporter_profil(profil_cree)
    app.session_state["stockage_profil"] = reponse.copy()
    app.run()

    assert not app.exception
    assert demandes[-1] is False

    # Une nouvelle modification demande un nouvel enregistrement.
    app.checkbox(key="confirmer_fin_parcours").check().run()
    app.button(key="terminer_parcours_actif").click().run()

    assert not app.exception
    assert demandes[-1] is True

    profil_modifie = app.session_state["profil"]
    assert profil_modifie.active_journey_id is None

    # Simuler un échec, sans actualiser la copie sauvegardée.
    reponse["erreur_operation"] = "Conflit de sauvegarde simulé."
    app.session_state["stockage_profil"] = reponse.copy()
    app.run()

    assert not app.exception
    assert app.error
    assert demandes[-1] is False
    assert app.session_state["profil"] == profil_modifie

    # L'erreur persistante empêche une nouvelle tentative automatique.
    app.run()

    assert not app.exception
    assert demandes[-1] is False

@pytest.mark.parametrize(
    "duree, attendu, attendu_sg",
    [
        (280, "25 SA + 5 jours", "23 SG + 5 jours"),
        (287, "26 SA + 5 jours", "24 SG + 5 jours"),
    ],
)
def test_convention_dpa_conservee_apres_reinitialisation(
    duree,
    attendu,
    attendu_sg,
):
    app = AppTest.from_file("../app.py").run()

    app.radio(key="ecran_consulte").set_value(
        "Grossesse en cours"
    ).run()
    app.button(key="demarrer_parcours").click().run()
    app.radio(key="methode_datation_grossesse").set_value("dpa").run()

    # Valider une DPA et sa convention.
    dpa = date.today() + timedelta(days=100)

    app.date_input(key="date_accouchement_grossesse").set_value(dpa)
    app.selectbox(key="terme_reference_grossesse").set_value(duree)
    app.button[0].click().run()

    assert not app.exception
    assert app.metric[0].value == attendu
    assert app.metric[1].value == attendu_sg

    # Enregistrer les repères dans le parcours.
    app.button(key="enregistrer_reperes_grossesse").click().run()

    assert not app.exception

    profil_enregistre = app.session_state["profil"]
    reperes = profil_enregistre.journeys[0].details

    assert reperes.estimated_due_date == dpa
    assert reperes.term_reference_days == duree
    assert reperes.dating_rule_version == "sa-reference-v1"

    # Vider le formulaire sans modifier le parcours.
    app.checkbox(key="confirmer_effacement_grossesse").check().run()
    app.button(key="effacer_reperes_grossesse").click().run()

    assert not app.exception
    assert app.session_state["suivi_grossesse"] is None
    assert app.session_state["terme_reference_grossesse"] is None
    assert app.session_state["profil"] == profil_enregistre

    # Reprendre les repères enregistrés.
    app.button(key="reprendre_reperes_grossesse").click().run()

    assert not app.exception
    assert app.radio(key="methode_datation_grossesse").value == "dpa"
    assert app.date_input(key="date_accouchement_grossesse").value == dpa
    assert app.selectbox(key="terme_reference_grossesse").value == duree

    app.button[0].click().run()

    assert not app.exception
    assert app.metric[0].value == attendu
    assert app.metric[1].value == attendu_sg

@pytest.mark.parametrize("methode, duree, attendu", [
    ("dernieres_regles", None, "Trimestre estimé : 2"),
    ("dpa", 280, "Trimestre estimé : 2"),
    ("dpa", None, None),
])
def test_affichage_trimestre_selon_reperes(methode, duree, attendu):
    app = AppTest.from_file("../app.py").run()

    app.session_state["suivi_grossesse"] = {
        "methode_datation": methode,
        "date_reference": (
            date.today() - timedelta(days=98)
            if methode == "dernieres_regles"
            else date.today() + timedelta(days=182)
        ),
        "term_reference_days": duree,
    }

    app.radio[0].set_value("Grossesse en cours").run()

    assert not app.exception

    trimestres = [
        element.value for element in app.markdown
        if element.value.startswith("Trimestre estimé :")
    ]

    assert trimestres == ([] if attendu is None else [attendu])

@pytest.mark.parametrize(
    "methode, terme, decalage, attendu",
    [
        ("dpa", 280, 140, 50),
        ("dpa", 287, 147, 48),
        ("dpa", 280, -10, 100),
        ("dpa", None, 140, None),
        ("dpa", 280, 300, None),
        ("dernieres_regles", None, -140, None),
    ],
)
def test_barre_progression_grossesse(methode, terme, decalage, attendu):
    app = AppTest.from_file("../app.py").run()
    profil_avant = app.session_state["profil"]

    app.session_state["suivi_grossesse"] = {
        "methode_datation": methode,
        "date_reference": date.today() + timedelta(days=decalage),
        "term_reference_days": terme,
    }

    app.radio[0].set_value("Grossesse en cours").run()

    assert not app.exception

    barres = app.get("progress")

    if attendu is None:
        assert len(barres) == 0
    else:
        assert len(barres) == 1
        assert barres[0].proto.value == attendu

    assert app.session_state["profil"] == profil_avant

@pytest.mark.parametrize(
    "terme, attendu",
    [(None, None), (280, 50), (287, 48)],
)
def test_progression_ddr_et_convention_enregistree(terme, attendu):
    app = AppTest.from_file("../app.py").run()
    app.radio[0].set_value("Grossesse en cours").run()
    app.button(key="demarrer_parcours").click().run()

    app.date_input(key="date_regles_grossesse").set_value(
        date.today() - timedelta(days=140)
    )
    app.selectbox(key="terme_reference_grossesse").set_value(terme)
    app.button[0].click().run()

    assert not app.exception

    barres = app.get("progress")
    assert len(barres) == (0 if attendu is None else 1)

    if attendu is not None:
        assert barres[0].proto.value == attendu

    app.button(key="enregistrer_reperes_grossesse").click().run()

    assert not app.exception

    profil = app.session_state["profil"]
    reperes = next(
        journey.details
        for journey in profil.journeys
        if journey.id == profil.active_journey_id
    )

    assert reperes.term_reference_days == terme
    assert reperes.dating_rule_version == (
        None if terme is None else "sa-reference-v1"
    )

    app.checkbox(key="confirmer_effacement_grossesse").check().run()
    app.button(key="effacer_reperes_grossesse").click().run()
    app.button(key="reprendre_reperes_grossesse").click().run()

    assert not app.exception
    assert app.selectbox(key="terme_reference_grossesse").value == terme

@pytest.mark.parametrize(
    "methode, terme",
    [
        ("dernieres_regles", 280),
        ("dernieres_regles", 287),
        ("dernieres_regles", None),
        ("dpa", 280),
        ("dpa", None),
    ],
)
def test_affichage_dpa_estimee_sans_modifier_reperes(methode, terme):
    app = AppTest.from_file("../app.py").run()

    reference = (
        date.today() - timedelta(days=140)
        if methode == "dernieres_regles"
        else date.today() + timedelta(days=140)
    )

    suivi = {
        "methode_datation": methode,
        "date_reference": reference,
        "term_reference_days": terme,
    }

    app.session_state["suivi_grossesse"] = suivi.copy()
    profil_avant = app.session_state["profil"]

    app.radio[0].set_value("Grossesse en cours").run()

    assert not app.exception

    estimations = [
        element.value for element in app.markdown
        if element.value.startswith("DPA estimée :")
    ]

    if methode == "dernieres_regles" and terme is not None:
        attendu = reference + timedelta(days=terme)
        assert estimations == [
            f"DPA estimée : {attendu:%d/%m/%Y}"
        ]
    else:
        assert estimations == []

    assert app.session_state["suivi_grossesse"] == suivi
    assert app.session_state["profil"] == profil_avant

@pytest.mark.parametrize(
    "methode, terme, decalage, message_attendu",
    [
        ("dpa", None, -1, True),
        ("dpa", 280, -1, True),
        ("dpa", 280, 0, False),
        ("dpa", 280, 1, False),
        ("dernieres_regles", 280, -281, True),
        ("dernieres_regles", 287, -287, False),
        ("dernieres_regles", None, -300, False),
    ],
)
def test_dpa_depassee_sans_cloture(
    methode, terme, decalage, message_attendu
):
    app = AppTest.from_file("../app.py").run()

    profil = UserProfile().demarrer_parcours(
        "pregnancy",
        date.today(),
    )
    app.session_state["profil"] = profil
    app.session_state["suivi_grossesse"] = {
        "methode_datation": methode,
        "date_reference": date.today() + timedelta(days=decalage),
        "term_reference_days": terme,
    }

    app.radio[0].set_value("Grossesse en cours").run()

    assert not app.exception

    messages = [
        element.value for element in app.info
        if element.value.startswith("La DPA affichée est passée.")
    ]

    assert len(messages) == int(message_attendu)
    assert app.session_state["profil"] == profil
    assert app.session_state["profil"].active_journey_id is not None

@pytest.mark.parametrize(
    "date_rdv",
    [None, date(2026, 10, 15)],
)
def test_creer_et_afficher_fiche_rendez_vous(date_rdv):
    app = AppTest.from_file("../app.py").run()
    app.button(key="demarrer_parcours").click().run()

    identifiant = app.session_state["profil"].active_journey_id

    app.selectbox(
        key=f"type_rdv_{identifiant}"
    ).set_value("follow_up")
    app.date_input(
        key=f"date_rdv_{identifiant}"
    ).set_value(date_rdv)
    app.button(key="creer_rendez_vous").click().run()

    assert not app.exception

    profil = app.session_state["profil"]
    assert len(profil.appointments) == 1

    fiche = profil.appointments[0]
    assert fiche.journey_id == identifiant
    assert fiche.appointment_type == "follow_up"
    assert fiche.date == date_rdv

    attendu = (
        date_rdv.strftime("%d/%m/%Y")
        if date_rdv else "Date à définir"
    )
    titres = [
        element.label for element in app.expander
        if element.label.startswith("Fiche ")
    ]
    assert titres == [
        f"Fiche 1 : Consultation de suivi ({attendu})"
    ]
    assert importer_profil(exporter_profil(profil)) == profil

    app.run()

    assert not app.exception
    assert app.session_state["profil"].appointments == (fiche,)


def test_creation_rendez_vous_absente_sans_parcours():
    app = AppTest.from_file("../app.py").run()

    assert not app.exception
    assert all(
        bouton.key != "creer_rendez_vous"
        for bouton in app.button
    )


def test_liste_rendez_vous_filtre_et_trie():
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 1),
    )
    ancienne = Appointment(
        journey_id=profil.active_journey_id, # type: ignore
        appointment_type="preconception",
    )
    profil = profil.ajouter_rendez_vous(ancienne)
    profil = profil.changer_parcours(
        "pregnancy",
        date(2026, 9, 28),
    )

    sans_date = Appointment(journey_id=profil.active_journey_id) # type: ignore
    datee = Appointment(
        journey_id=profil.active_journey_id, # type: ignore
        appointment_type="follow_up",
        date=date(2026, 10, 15),
    )
    profil = profil.ajouter_rendez_vous(sans_date)
    profil = profil.ajouter_rendez_vous(datee)

    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil
    app.run()

    assert not app.exception

    titres = [
        element.label for element in app.expander
        if element.label.startswith("Fiche ")
    ]
    assert titres == [
        "Fiche 1 : Consultation de suivi (15/10/2026)",
        "Fiche 2 : Autre (Date à définir)",
    ]
    assert app.session_state["profil"] == profil

@pytest.mark.parametrize(
    "notes",
    [
        "",
        "Première ligne\n**À conserver tel quel**",
        "n" * 5000,
    ],
)
def test_notes_rendez_vous_saisies_et_affichees(notes):
    app = AppTest.from_file("../app.py").run()
    app.button(key="demarrer_parcours").click().run()

    identifiant = app.session_state["profil"].active_journey_id
    champ = app.text_area(key=f"notes_rdv_{identifiant}")

    assert champ.proto.max_chars == 5000

    champ.set_value(notes)
    app.button(key="creer_rendez_vous").click().run()

    assert not app.exception

    profil = app.session_state["profil"]
    assert profil.appointments[0].notes == notes
    assert importer_profil(exporter_profil(profil)) == profil

    fiche_affichee = next(
        element for element in app.expander
        if element.label.startswith("Fiche 1 :")
    )

    if notes:
        assert notes in [
            element.value for element in fiche_affichee.text
        ]
    else:
        assert "Aucune note renseignée." in [
            element.value for element in fiche_affichee.caption
        ]

@pytest.mark.parametrize(
    "themes, libelle",
    [
        ([], None),
        (["travel", "nutrition"], "Thèmes : Voyage, Alimentation"),
    ],
)
def test_themes_rendez_vous_saisis_et_affiches(themes, libelle):
    app = AppTest.from_file("../app.py").run()
    app.button(key="demarrer_parcours").click().run()

    identifiant = app.session_state["profil"].active_journey_id
    champ = app.multiselect(key=f"themes_rdv_{identifiant}")

    assert champ.options == [
        "Alimentation",
        "Activité physique",
        "Symptômes",
        "Médicaments",
        "Examens",
        "Travail",
        "Voyage",
        "Accouchement",
        "Autre",
    ]

    champ.set_value(themes)
    app.button(key="creer_rendez_vous").click().run()

    assert not app.exception

    profil = app.session_state["profil"]
    assert profil.appointments[0].topics == tuple(themes)
    assert importer_profil(exporter_profil(profil)) == profil

    fiche = next(
        element for element in app.expander
        if element.label.startswith("Fiche 1 :")
    )

    if libelle is None:
        assert "Aucun thème sélectionné." in [
            element.value for element in fiche.caption
        ]
    else:
        assert libelle in [
            element.value for element in fiche.markdown
        ]

@pytest.mark.parametrize(
    "texte, attendu",
    [
        ("", ()),
        (
            "  Première question ?  \n\nDeuxième question ?",
            ("  Première question ?  ", "Deuxième question ?"),
        ),
    ],
)
def test_questions_rendez_vous_et_reinitialisation(texte, attendu):
    app = AppTest.from_file("../app.py").run()
    app.button(key="demarrer_parcours").click().run()
    identifiant = app.session_state["profil"].active_journey_id

    app.text_area(
        key=f"questions_rdv_{identifiant}"
    ).set_value(texte)
    app.button(key="creer_rendez_vous").click().run()

    assert not app.exception

    profil = app.session_state["profil"]
    assert len(profil.appointments) == 1
    assert profil.appointments[0].questions == attendu
    assert importer_profil(exporter_profil(profil)) == profil
    assert app.text_area(
        key=f"questions_rdv_{identifiant}"
    ).value == ""

    fiche = next(
        element for element in app.expander
        if element.label.startswith("Fiche 1 :")
    )

    if attendu:
        assert [element.value for element in fiche.text] == [
            f"{numero}. {question}".rstrip()
            for numero, question in enumerate(attendu, start=1)
        ]
    else:
        assert "Aucune question renseignée." in [
            element.value for element in fiche.caption
        ]


@pytest.mark.parametrize(
    "texte",
    ["q" * 501, "\n".join(["Question ?"] * 31)],
)
def test_questions_invalides_conservent_saisie(texte):
    app = AppTest.from_file("../app.py").run()
    app.button(key="demarrer_parcours").click().run()
    identifiant = app.session_state["profil"].active_journey_id

    app.text_area(
        key=f"questions_rdv_{identifiant}"
    ).set_value(texte)
    app.text_area(
        key=f"notes_rdv_{identifiant}"
    ).set_value("Notes à garder")
    app.button(key="creer_rendez_vous").click().run()

    assert not app.exception
    assert len(app.error) == 1
    assert app.session_state["profil"].appointments == ()
    assert app.text_area(
        key=f"questions_rdv_{identifiant}"
    ).value == texte
    assert app.text_area(
        key=f"notes_rdv_{identifiant}"
    ).value == "Notes à garder"

    app.text_area(
        key=f"questions_rdv_{identifiant}"
    ).set_value("Question corrigée ?")
    app.button(key="creer_rendez_vous").click().run()

    assert not app.exception
    assert len(app.error) == 0
    assert len(app.session_state["profil"].appointments) == 1

def test_telechargements_correspondent_aux_fiches(monkeypatch):
    import streamlit as st
    from fiches_rendez_vous import exporter_fiche_texte

    appels = []
    bouton_original = st.download_button

    def observer_telechargement(*args, **kwargs):
        if kwargs.get("label") == "Télécharger la fiche (.txt)":
            appels.append(kwargs.copy())
        return bouton_original(*args, **kwargs)

    monkeypatch.setattr(
        st,
        "download_button",
        observer_telechargement,
    )

    profil = UserProfile().demarrer_parcours(
        "pregnancy",
        date(2026, 9, 28),
    )
    premiere = Appointment(
        journey_id=profil.active_journey_id, # type: ignore
        notes="Première fiche",
    )
    seconde = Appointment(
        journey_id=profil.active_journey_id, # type: ignore
        notes="Deuxième fiche",
    )
    profil = profil.ajouter_rendez_vous(premiere)
    profil = profil.ajouter_rendez_vous(seconde)

    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil
    app.run()

    assert not app.exception
    assert len(appels) == 2

    for appel, fiche in zip(appels, (premiere, seconde)):
        assert appel["data"] == exporter_fiche_texte(fiche).encode("utf-8")
        assert appel["file_name"] == (
            f"nurtureai-rendez-vous-{fiche.id}.txt"
        )
        assert appel["mime"] == "text/plain; charset=utf-8"
        assert appel["key"] == f"telecharger_rdv_{fiche.id}"
        assert appel["on_click"] == "ignore"

    assert app.session_state["profil"] == profil

@pytest.mark.parametrize("nombre_fiches", [1, 2])
def test_suppression_fiche_confirmee(nombre_fiches):
    profil = UserProfile().demarrer_parcours(
        "pregnancy",
        date(2026, 9, 28),
    )
    fiches = tuple(
        Appointment(journey_id=profil.active_journey_id) # type: ignore
        for _ in range(nombre_fiches)
    )

    for fiche in fiches:
        profil = profil.ajouter_rendez_vous(fiche)

    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil
    app.run()

    cible = fiches[0]
    cle_confirmation = f"confirmer_suppression_rdv_{cible.id}"
    cle_bouton = f"supprimer_rdv_{cible.id}"

    assert app.button(key=cle_bouton).disabled

    app.checkbox(key=cle_confirmation).check().run()

    assert not app.button(key=cle_bouton).disabled
    assert app.session_state["profil"] == profil

    app.checkbox(key=cle_confirmation).uncheck().run()

    assert app.button(key=cle_bouton).disabled
    assert app.session_state["profil"] == profil

    app.checkbox(key=cle_confirmation).check().run()
    app.button(key=cle_bouton).click().run()

    assert not app.exception

    resultat = app.session_state["profil"]
    assert resultat.appointments == fiches[1:]
    assert resultat.journeys == profil.journeys
    assert resultat.active_journey_id == profil.active_journey_id
    assert importer_profil(exporter_profil(resultat)) == resultat

    assert all(
        bouton.key != cle_bouton
        for bouton in app.button
    )
    assert "Fiche supprimée du profil." in [
        element.value for element in app.success
    ]

    if nombre_fiches == 2:
        assert app.button(
            key=f"supprimer_rdv_{fiches[1].id}"
        ).disabled
    else:
        assert "Aucune fiche de rendez-vous pour ce parcours." in [
            element.value for element in app.info
        ]

@pytest.fixture
def fiche_pour_edition():
    profil = UserProfile().demarrer_parcours(
        "pregnancy",
        date(2026, 9, 28),
    )
    fiche = Appointment(
        journey_id=profil.active_journey_id, # type: ignore
        appointment_type="follow_up",
        notes="Notes initiales",
        questions=("Question initiale ?",),
        topics=("nutrition",),
        created_at=datetime(2026, 9, 28, tzinfo=timezone.utc),
    )

    return profil.ajouter_rendez_vous(fiche), fiche


def test_modifier_fiche_depuis_interface(fiche_pour_edition):
    profil, fiche = fiche_pour_edition
    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil
    app.run()

    cle = f"edition_rdv_{fiche.id}_{fiche.updated_at.isoformat()}"
    app.checkbox(key=cle).check().run()

    assert app.text_area(key=f"notes_{cle}").value == fiche.notes
    assert app.text_area(
        key=f"questions_{cle}"
    ).value == "Question initiale ?"

    app.selectbox(key=f"type_{cle}").set_value("other")
    app.date_input(key=f"date_{cle}").set_value(date(2026, 10, 20))
    app.multiselect(key=f"themes_{cle}").set_value(["travel"])
    app.text_area(key=f"notes_{cle}").set_value("Notes corrigées")
    app.text_area(
        key=f"questions_{cle}"
    ).set_value("Nouvelle question ?")
    app.button(key=f"enregistrer_{cle}").click().run()

    assert not app.exception

    resultat = app.session_state["profil"]
    assert len(resultat.appointments) == 1

    modifiee = resultat.appointments[0]
    assert modifiee.id == fiche.id
    assert modifiee.journey_id == fiche.journey_id
    assert modifiee.created_at == fiche.created_at
    assert modifiee.updated_at > fiche.updated_at
    assert modifiee.appointment_type == "other"
    assert modifiee.date == date(2026, 10, 20)
    assert modifiee.topics == ("travel",)
    assert modifiee.notes == "Notes corrigées"
    assert modifiee.questions == ("Nouvelle question ?",)
    assert importer_profil(exporter_profil(resultat)) == resultat

    assert "Fiche modifiée dans le profil." in [
        element.value for element in app.success
    ]


def test_edition_invalide_et_abandon(fiche_pour_edition):
    profil, fiche = fiche_pour_edition
    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil
    app.run()

    cle = f"edition_rdv_{fiche.id}_{fiche.updated_at.isoformat()}"
    app.checkbox(key=cle).check().run()
    app.text_area(key=f"notes_{cle}").set_value("Brouillon")
    app.text_area(key=f"questions_{cle}").set_value("q" * 501)
    app.button(key=f"enregistrer_{cle}").click().run()

    assert not app.exception
    assert len(app.error) == 1
    assert app.session_state["profil"] == profil
    assert app.text_area(key=f"notes_{cle}").value == "Brouillon"
    assert app.text_area(key=f"questions_{cle}").value == "q" * 501

    app.checkbox(key=cle).uncheck().run()
    app.checkbox(key=cle).check().run()

    assert not app.exception
    assert app.session_state["profil"] == profil
    assert app.text_area(key=f"notes_{cle}").value == fiche.notes
    assert app.text_area(
        key=f"questions_{cle}"
    ).value == "Question initiale ?"

@pytest.mark.parametrize("nouveau_parcours", [False, True])
def test_fiche_archivee_consultable_sans_modification(nouveau_parcours):
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 1),
    )
    fiche = Appointment(
        journey_id=profil.active_journey_id, # type: ignore
        notes="Notes du parcours terminé",
        date=date(2026, 12, 1),
    )
    profil = profil.ajouter_rendez_vous(fiche)
    profil = profil.terminer_parcours_actif(date(2026, 9, 28))

    if nouveau_parcours:
        profil = profil.demarrer_parcours(
            "pregnancy",
            date(2026, 9, 28),
        )
        profil = profil.ajouter_rendez_vous(
            Appointment(
                journey_id=profil.active_journey_id, # type: ignore
                notes="Notes du nouveau parcours",
            )
        )

    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil
    app.run()

    assert not app.exception

    archive = next(
        element for element in app.expander
        if element.label.startswith("Parcours 1 :")
    )
    textes = "\n".join(element.value for element in archive.text)

    assert "Notes du parcours terminé" in textes
    assert "01/12/2026" in textes
    assert "Notes du nouveau parcours" not in textes
    assert len(archive.get("download_button")) == 1
    assert len(archive.button) == 0
    assert len(archive.checkbox) == 0
    assert app.session_state["profil"] == profil


def test_archive_sans_fiche():
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 1),
    )
    profil = profil.terminer_parcours_actif(date(2026, 9, 28))

    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil
    app.run()

    assert not app.exception

    archive = next(
        element for element in app.expander
        if element.label.startswith("Parcours 1 :")
    )

    assert "Aucune fiche de rendez-vous pour ce parcours." in [
        element.value for element in archive.caption
    ]
    assert len(archive.get("download_button")) == 0

@pytest.mark.parametrize("origine", ["fichier", "navigateur"])
@pytest.mark.parametrize("nombre_fiches", [0, 2])
def test_apercu_compte_rendez_vous_avant_confirmation(
    origine, nombre_fiches, simuler_stockage_navigateur
):
    sauvegarde = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 1),
    )

    if nombre_fiches:
        sauvegarde = sauvegarde.ajouter_rendez_vous(
            Appointment(journey_id=sauvegarde.active_journey_id) # type: ignore
        )
        sauvegarde = sauvegarde.changer_parcours(
            "pregnancy",
            date(2026, 9, 28),
        )
        sauvegarde = sauvegarde.ajouter_rendez_vous(
            Appointment(journey_id=sauvegarde.active_journey_id) # type: ignore
        )

    app = AppTest.from_file("../app.py").run()
    profil_initial = app.session_state["profil"]

    if origine == "fichier":
        app.file_uploader(key="fichier_import").upload(
            "profil.json",
            exporter_profil(sauvegarde).encode("utf-8"),
            "application/json",
        ).run()

        libelle = f"Nombre de rendez-vous : {nombre_fiches}"
        confirmation = "confirmer_import"
        bouton = "appliquer_import"
    else:
        simuler_stockage_navigateur.update(
            lecture="ok",
            texte=exporter_profil(sauvegarde),
        )
        app.run()

        libelle = (
            f"Nombre de rendez-vous sauvegardés : {nombre_fiches}"
        )
        confirmation = "confirmer_restauration_locale"
        bouton = "restaurer_profil_local"

    assert not app.exception
    assert libelle in [
        element.value for element in app.markdown
    ]
    assert app.session_state["profil"] == profil_initial
    assert app.button(key=bouton).disabled

    app.checkbox(key=confirmation).check().run()
    app.button(key=bouton).click().run()

    assert not app.exception
    assert app.session_state["profil"] == sauvegarde

@pytest.mark.parametrize("origine", ["fichier", "navigateur"])
def test_restauration_meme_profil_efface_brouillons_rdv(
    fiche_pour_edition, origine, simuler_stockage_navigateur
):
    profil, fiche = fiche_pour_edition
    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil
    app.run()

    cle_creation = f"notes_rdv_{profil.active_journey_id}"
    cle_edition = f"edition_rdv_{fiche.id}_{fiche.updated_at.isoformat()}"
    cle_suppression = f"confirmer_suppression_rdv_{fiche.id}"

    app.text_area(
        key=cle_creation
    ).set_value("Brouillon de création")
    app.checkbox(key=cle_edition).check().run()
    app.text_area(
        key=f"notes_{cle_edition}"
    ).set_value("Brouillon de modification")
    app.checkbox(key=cle_suppression).check().run()

    if origine == "fichier":
        app.file_uploader(key="fichier_import").upload(
            "profil.json",
            exporter_profil(profil).encode("utf-8"),
            "application/json",
        ).run()

        confirmation = "confirmer_import"
        bouton = "appliquer_import"
    else:
        simuler_stockage_navigateur.update(
            lecture="ok",
            texte=exporter_profil(profil),
        )
        app.run()

        confirmation = "confirmer_restauration_locale"
        bouton = "restaurer_profil_local"

    assert app.text_area(
        key=cle_creation
    ).value == "Brouillon de création"
    assert app.text_area(
        key=f"notes_{cle_edition}"
    ).value == "Brouillon de modification"
    assert app.checkbox(key=cle_suppression).value

    app.checkbox(key=confirmation).check().run()
    app.button(key=bouton).click().run()

    assert not app.exception
    assert app.session_state["profil"] == profil
    assert app.text_area(key=cle_creation).value == ""
    assert not app.checkbox(key=cle_edition).value
    assert not app.checkbox(key=cle_suppression).value
    assert app.button(
        key=f"supprimer_rdv_{fiche.id}"
    ).disabled

    app.checkbox(key=cle_edition).check().run()

    assert app.text_area(
        key=f"notes_{cle_edition}"
    ).value == fiche.notes

def test_calendrier_sans_parcours():
    app = AppTest.from_file("../app.py").run()

    assert not app.exception
    assert "Aucun parcours disponible pour le calendrier." in [
        element.value for element in app.info
    ]
    assert all(
        element.key != "calendrier_parcours"
        for element in app.selectbox
    )


def test_calendrier_consulte_archive_sans_changer_actif():
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 1),
    )
    ancien_id = profil.active_journey_id
    profil = profil.ajouter_rendez_vous(
        Appointment(
            journey_id=ancien_id, # type: ignore
            date=date(2026, 10, 12),
            appointment_type="follow_up",
        )
    )
    profil = profil.changer_parcours(
        "pregnancy",
        date(2026, 9, 28),
    )
    profil = profil.ajouter_rendez_vous(
        Appointment(
            journey_id=profil.active_journey_id, # type: ignore
            date=date(2026, 10, 16),
            appointment_type="ultrasound",
        )
    )

    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil
    app.run()

    assert app.selectbox(
        key="calendrier_parcours"
    ).value == profil.active_journey_id

    app.selectbox(
        key="calendrier_parcours"
    ).set_value(ancien_id)
    app.date_input(
        key="calendrier_mois"
    ).set_value(date(2026, 10, 1)).run()

    assert not app.exception

    textes = [element.value for element in app.markdown]
    assert "12/10/2026 : Consultation de suivi" in textes
    assert "16/10/2026 : Échographie" not in textes
    assert app.session_state["profil"] == profil


@pytest.mark.parametrize("mois", [None, date(2027, 1, 1)])
def test_calendrier_date_absente_ou_mois_vide(mois):
    app = AppTest.from_file("../app.py").run()
    app.button(key="demarrer_parcours").click().run()
    app.date_input(key="calendrier_mois").set_value(mois).run()

    assert not app.exception

    attendu = (
        "Choisissez une date pour consulter son mois."
        if mois is None
        else "Aucun rendez-vous daté pour ce mois et ce parcours."
    )
    assert attendu in [element.value for element in app.info]

@pytest.mark.parametrize(
    "depart, bouton, attendu",
    [
        (date(2026, 12, 31), "calendrier_suivant", date(2027, 1, 1)),
        (date(2027, 1, 31), "calendrier_precedent", date(2026, 12, 1)),
    ],
)
def test_navigation_mois_change_annee(depart, bouton, attendu):
    app = AppTest.from_file("../app.py").run()
    app.button(key="demarrer_parcours").click().run()

    profil = app.session_state["profil"]
    fiche = Appointment(
        journey_id=profil.active_journey_id,
        date=attendu,
        appointment_type="follow_up",
    )
    profil = profil.ajouter_rendez_vous(fiche)
    app.session_state["profil"] = profil

    app.date_input(key="calendrier_mois").set_value(depart).run()
    app.button(key=bouton).click().run()

    assert not app.exception
    assert app.date_input(key="calendrier_mois").value == attendu
    assert f"{attendu:%d/%m/%Y} : Consultation de suivi" in [
        element.value for element in app.markdown
    ]
    assert app.session_state["profil"] == profil

@pytest.mark.parametrize(
    "limite, bouton",
    [
        (date.min, "calendrier_precedent"),
        (date.max, "calendrier_suivant"),
    ],
)
def test_navigation_mois_limites(limite, bouton):
    app = AppTest.from_file("../app.py").run()
    app.button(key="demarrer_parcours").click().run()
    app.date_input(key="calendrier_mois").set_value(limite).run()

    assert not app.exception
    assert app.button(key=bouton).disabled


def test_navigation_mois_desactivee_sans_date():
    app = AppTest.from_file("../app.py").run()
    app.button(key="demarrer_parcours").click().run()
    app.date_input(key="calendrier_mois").set_value(None).run()

    assert not app.exception
    assert app.button(key="calendrier_precedent").disabled
    assert app.button(key="calendrier_suivant").disabled

@pytest.mark.parametrize("nombre_fiches", [0, 2])
def test_grille_calendrier_affiche_nombre_rendez_vous(nombre_fiches):
    profil = UserProfile().demarrer_parcours(
        "pregnancy",
        date(2026, 9, 28),
    )

    for _ in range(nombre_fiches):
        profil = profil.ajouter_rendez_vous(
            Appointment(
                journey_id=profil.active_journey_id, # type: ignore
                date=date(2026, 10, 12),
            )
        )

    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil
    app.run()

    app.date_input(
        key="calendrier_mois"
    ).set_value(date(2026, 10, 1)).run()

    assert not app.exception
    assert len(app.table) == 1

    grille = app.table[0].value

    assert list(grille.columns) == [
        "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"
    ]
    assert grille.shape == (5, 7)
    assert grille.iloc[0]["Lun"] == ""
    assert grille.iloc[0]["Jeu"] == "1"
    assert grille.iloc[2]["Lun"] == "12 (2 RDV)" if nombre_fiches else "12"
    assert grille.iloc[4]["Sam"] == "31"
    assert grille.iloc[4]["Dim"] == ""
    assert app.session_state["profil"] == profil

@pytest.mark.parametrize("archive", [False, True])
def test_calendrier_regles_et_rendez_vous_meme_jour(archive):
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 1),
    )
    identifiant = profil.active_journey_id

    profil = profil.renseigner_reperes_actifs(
        ConceptionJourney(
            last_period_date=date(2026, 9, 28),
            period_length=5,
        )
    )
    profil = profil.ajouter_rendez_vous(
        Appointment(
            journey_id=identifiant, # type: ignore
            date=date(2026, 9, 28),
        )
    )

    if archive:
        profil = profil.changer_parcours(
            "pregnancy",
            date(2026, 9, 29),
        )

    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil
    app.run()

    app.selectbox(
        key="calendrier_parcours"
    ).set_value(identifiant)
    app.date_input(
        key="calendrier_mois"
    ).set_value(date(2026, 9, 1)).run()

    assert not app.exception

    grille = app.table[0].value
    assert grille.iloc[4]["Lun"] == (
        "28 (1 RDV) ; Début des règles déclaré"
    )
    assert grille.iloc[4]["Mar"] == "29 ; Jour de règles estimé"

    app.date_input(
        key="calendrier_mois"
    ).set_value(date(2026, 10, 1)).run()

    assert not app.exception

    grille = app.table[0].value
    assert grille.iloc[0]["Jeu"] == "1 ; Jour de règles estimé"
    assert grille.iloc[0]["Ven"] == "2 ; Jour de règles estimé"
    assert grille.iloc[0]["Sam"] == "3"
    assert app.session_state["profil"] == profil


def test_calendrier_conception_sans_date_ne_projette_pas_regles():
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 1),
    )
    profil = profil.renseigner_reperes_actifs(ConceptionJourney())

    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil
    app.run()

    assert not app.exception

    cellules = app.table[0].value.to_numpy().flatten()
    assert all("règles" not in cellule for cellule in cellules)

@pytest.mark.parametrize(
    "methode, terme, jour, libelle",
    [
        ("due_date", None, 20, "DPA renseignée"),
        ("last_period", 280, 8, "DPA estimée"),
        ("last_period", 287, 15, "DPA estimée"),
        ("last_period", None, 20, None),
    ],
)
def test_calendrier_affiche_dpa_sans_modifier_profil(
    methode, terme, jour, libelle
):
    profil = UserProfile().demarrer_parcours(
        "pregnancy",
        date(2026, 1, 1),
    )
    identifiant = profil.active_journey_id
    assert identifiant is not None

    profil = profil.renseigner_reperes_actifs(
        PregnancyJourney(
            dating_method=methode,
            last_period_date=date(2026, 1, 1),
            estimated_due_date=(
                date(2026, 10, 20)
                if methode == "due_date"
                else None
            ),
            term_reference_days=terme,
            dating_rule_version=(
                "sa-reference-v1" if terme is not None else None
            ),
        )
    )
    profil = profil.ajouter_rendez_vous(
        Appointment(
            journey_id=identifiant,
            date=date(2026, 10, jour),
        )
    )

    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil
    app.run()

    app.date_input(
        key="calendrier_mois"
    ).set_value(date(2026, 10, 1)).run()

    assert not app.exception

    cellules = app.table[0].value.to_numpy().flatten()
    attendu = f"{jour} (1 RDV)"

    if libelle is not None:
        attendu += f" ; {libelle}"
    else:
        assert all("DPA" not in cellule for cellule in cellules)

    assert attendu in cellules
    assert app.session_state["profil"] == profil

@pytest.mark.parametrize(
    "mois, mois_vide",
    [(9, True), (10, False)],
)
def test_calendrier_message_mois_vide_tient_compte_dpa(
    mois, mois_vide
):
    profil = UserProfile().demarrer_parcours(
        "pregnancy",
        date(2026, 1, 1),
    )
    profil = profil.renseigner_reperes_actifs(
        PregnancyJourney(
            dating_method="due_date",
            estimated_due_date=date(2026, 10, 20),
        )
    )

    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil
    app.run()

    app.date_input(
        key="calendrier_mois"
    ).set_value(date(2026, mois, 1)).run()

    assert not app.exception

    messages = [element.value for element in app.info]

    assert (
        "Aucun événement pour ce mois et ce parcours." in messages
    ) == mois_vide

    if not mois_vide:
        cellules = app.table[0].value.to_numpy().flatten()
        assert "20 ; DPA renseignée" in cellules

    assert app.session_state["profil"] == profil

@pytest.mark.parametrize("avec_rendez_vous", [False, True])
def test_calendrier_prochaines_regles_et_rendez_vous(
    avec_rendez_vous,
):
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 1),
    )
    identifiant = profil.active_journey_id
    assert identifiant is not None

    profil = profil.renseigner_reperes_actifs(
        ConceptionJourney(
            last_period_date=date(2026, 9, 12),
            average_cycle_length=28,
        )
    )

    if avec_rendez_vous:
        profil = profil.ajouter_rendez_vous(
            Appointment(
                journey_id=identifiant,
                date=date(2026, 10, 10),
            )
        )

    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil
    app.run()

    app.date_input(
        key="calendrier_mois"
    ).set_value(date(2026, 10, 1)).run()

    assert not app.exception

    cellules = app.table[0].value.to_numpy().flatten()
    debut = "10 (1 RDV)" if avec_rendez_vous else "10"

    assert (
        f"{debut} ; Début des prochaines règles estimé"
    ) in cellules

    assert "Aucun événement pour ce mois et ce parcours." not in [
        element.value for element in app.info
    ]

    app.date_input(
        key="calendrier_mois"
    ).set_value(date(2026, 11, 1)).run()

    assert not app.exception

    cellules = app.table[0].value.to_numpy().flatten()
    assert all(
        "prochaines règles" not in cellule
        for cellule in cellules
    )
    assert app.session_state["profil"] == profil

@pytest.mark.parametrize("cas", ["vide", "erreur", "fiche"])
def test_affichage_timeline_grossesse(monkeypatch, cas):
    import timeline

    profil = UserProfile().demarrer_parcours(
        "pregnancy",
        date(2026, 1, 1),
    )
    reperes = PregnancyJourney(
        dating_method="due_date",
        estimated_due_date=date(2026, 10, 22),
    )
    profil = profil.renseigner_reperes_actifs(reperes)
    appels = []

    def fausse_timeline(reperes_recus, date_reference):
        assert type(date_reference) is date
        appels.append(reperes_recus)

        if cas == "erreur":
            raise ValueError("Erreur simulée")

        if cas == "vide":
            return ()

        return (
            {
                "position": "unknown",
                "etape": {
                    "title": "Étape fictive de test",
                    "when": "Période de test.",
                    "why": "Objectif de test.",
                    "how": "Description de test.",
                    "questions": ["Question de test ?"],
                    "source": {
                        "name": "Source fictive",
                        "title": "Document fictif de test",
                        "retrieved_at": "2026-10-02",
                        "url": "https://example.org/",
                    },
                },
            },
        )

    monkeypatch.setattr(
        timeline,
        "construire_timeline",
        fausse_timeline,
    )

    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil

    app.radio(
        key="ecran_consulte"
    ).set_value("Grossesse en cours").run()

    assert not app.exception
    assert appels == [reperes]
    assert app.session_state["profil"] == profil
    assert "Mes données" in [
        element.value for element in app.subheader
    ]

    if cas == "vide":
        assert (
            "Aucune fiche de suivi disponible pour le moment."
        ) in [element.value for element in app.info]

    elif cas == "erreur":
        assert any(
            "Les étapes de suivi sont indisponibles." in element.value
            for element in app.warning
        )

    else:
        fiche = next(
            element for element in app.expander
            if element.label == "Étape fictive de test"
        )

        assert "Position indéterminée" in [
            element.value for element in fiche.caption
        ]
        assert "1. Question de test ?" in [
            element.value for element in fiche.text
        ]

@pytest.mark.parametrize(
    "jours_sa, libelle",
    [
        (77, "Période en cours"),
        (98, "Période passée"),
    ],
)
def test_timeline_reelle_affiche_sources_et_position(
    jours_sa, libelle
):
    from timeline import charger_timeline

    etape = next(
        etape for etape in charger_timeline()["etapes"]
        if etape["id"] == "echographie_premier_trimestre"
    )

    origine = date.today() - timedelta(days=jours_sa)

    profil = UserProfile().demarrer_parcours(
        "pregnancy",
        origine,
    )
    profil = profil.renseigner_reperes_actifs(
        PregnancyJourney(
            dating_method="last_period",
            last_period_date=origine,
        )
    )

    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil

    app.radio(
        key="ecran_consulte"
    ).set_value("Grossesse en cours").run()

    assert not app.exception

    fiche = next(
        element for element in app.expander
        if element.label == etape["title"]
    )

    assert libelle in [
        element.value for element in fiche.caption
    ]

    textes = [element.value for element in fiche.text]
    assert etape["source"]["title"] in textes

    secondaire = etape["secondary_sources"][0]
    assert secondaire["title"] in textes

    liens = {
        element.proto.label: element.proto.url
        for element in fiche.get("link_button")
    }

    assert liens["Consulter la source"] == (
        etape["source"]["url"]
    )
    assert liens["Consulter la référence secondaire"] == (
        secondaire["url"]
    )
    assert liens["Conditions de réutilisation"] == (
        secondaire["terms_url"]
    )

    assert any(
        "Référence de recoupement" in element.value
        for element in fiche.caption
    )

    assert app.session_state["profil"] == profil

@pytest.mark.parametrize(
    "jours_sa, type_element, attendu",
    [
        (76, "markdown", "**Prochaine période disponible**"),
        (77, "markdown", "**Repère actuel**"),
        (98, "markdown", "**Prochaine période disponible**"),
        (139, "markdown", "**Prochaine période disponible**"),
        (140, "markdown", "**Repère actuel**"),
        (174, "markdown", "**Repère actuel**"),
        (175, "markdown", "**Prochaine période disponible**"),
        (209, "markdown", "**Prochaine période disponible**"),
        (210, "markdown", "**Repère actuel**"),
        (244, "markdown", "**Repère actuel**"),
        (
            245,
            "info",
            "Aucune prochaine période dans les fiches disponibles. Cela ne signifie pas que le suivi est terminé.",
        ),
        (
            None,
            "info",
            "Complétez les repères de datation enregistrés pour situer les étapes de suivi.",
        ),
    ],
)
def test_timeline_repere_mis_en_avant(
    jours_sa, type_element, attendu
):
    origine = date.today() - timedelta(days=jours_sa or 0)

    profil = UserProfile().demarrer_parcours(
        "pregnancy",
        origine,
    )

    if jours_sa is not None:
        profil = profil.renseigner_reperes_actifs(
            PregnancyJourney(
                dating_method="last_period",
                last_period_date=origine,
            )
        )

    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil

    app.radio(
        key="ecran_consulte"
    ).set_value("Grossesse en cours").run()

    assert not app.exception

    assert attendu in [
        element.value for element in app.get(type_element) # type: ignore
    ]

    if jours_sa is None or jours_sa == 245:
        assert not any(
            element.value in (
                "**Repère actuel**",
                "**Prochaine période disponible**",
            )
            for element in app.markdown
        )

    assert app.session_state["profil"] == profil

@pytest.mark.parametrize(
    "cas",
    ["sans_parcours", "sans_reperes", "vide", "erreur", "fiche", "licence", "reference",],
)
def test_affichage_fiche_hebdomadaire(monkeypatch, cas):
    import fiches_hebdomadaires

    appels = []

    def faux_chargement():
        appels.append(True)

        if cas == "erreur":
            raise ValueError("Erreur simulée")

        if cas == "vide":
            return ()

        fiche = {
            "week_sa": 9,
            "title": "Fiche hebdomadaire fictive",
            "body": "Texte réservé au test.",
            "source": {
                "name": "Source fictive",
                "title": "Document fictif",
                "url": "https://example.org/semaine",
                "retrieved_at": "2026-10-04",
            },
        }

        if cas == "licence":
            fiche["attribution"] = {
                "mode": "licence",
                "text": "Mention de licence fictive.",
                "url": "https://example.org/licence",
            }

        if cas == "reference":
            fiche["attribution"] = {
                "mode": "reference",
                "text": "Reference: example.org",
                "url": "https://example.org/",
            }

        return (fiche,)

    monkeypatch.setattr(
        fiches_hebdomadaires,
        "charger_fiches_hebdomadaires",
        faux_chargement,
    )

    profil = UserProfile()
    origine = date.today() - timedelta(days=65)

    if cas != "sans_parcours":
        profil = profil.demarrer_parcours("pregnancy", origine)

        if cas != "sans_reperes":
            profil = profil.renseigner_reperes_actifs(
                PregnancyJourney(
                    dating_method="last_period",
                    last_period_date=origine,
                )
            )

    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil

    app.radio(
        key="ecran_consulte"
    ).set_value("Grossesse en cours").run()

    assert not app.exception
    assert app.session_state["profil"] == profil
    assert bool(appels) == (
        cas not in ("sans_parcours", "sans_reperes")
    )

    attendus = {
        "sans_parcours": (
            "info",
            "Démarrez un parcours grossesse pour consulter les fiches hebdomadaires.",
        ),
        "sans_reperes": (
            "info",
            "Complétez les repères enregistrés pour déterminer la semaine SA.",
        ),
        "vide": (
            "info",
            "Aucune fiche disponible pour 9 SA révolues.",
        ),
        "erreur": (
            "warning",
            "La fiche hebdomadaire est indisponible : les repères ou le contenu doivent être vérifiés.",
        ),
        "fiche": (
            "text",
            "Texte réservé au test.",
        ),
        "licence": (
            "text",
            "Mention de licence fictive.",
        ),
        "reference": (
            "text",
            "Texte réservé au test.",
        ),
    }

    type_element, texte = attendus[cas]
    assert texte in [
        element.value for element in app.get(type_element) # type: ignore
    ]

    if cas in ("fiche", "reference"):
        liens = {
            element.proto.label: element.proto.url
            for element in app.get("link_button")
        }
        assert liens["Source de la fiche hebdomadaire"] == (
            "https://example.org/semaine"
        )

    if cas == "reference":
        liens = {
            element.proto.label: element.proto.url
            for element in app.get("link_button")
        }

        assert liens["Reference: example.org"] == (
            "https://example.org/"
        )
        assert "Licence de la fiche hebdomadaire" not in liens

        assert "Document fictif" in [
            element.value for element in app.text
        ]
        assert (
            "Source : Source fictive ; consultée le 2026-10-04."
        ) in [
            element.value for element in app.caption
        ]

    if cas == "licence":
        liens = {
            element.proto.label: element.proto.url
            for element in app.get("link_button")
        }

        assert liens["Licence de la fiche hebdomadaire"] == (
            "https://example.org/licence"
        )
        assert "Source de la fiche hebdomadaire" not in liens

        assert "Document fictif" not in [
            element.value for element in app.text
        ]
        assert not any(
            "Source fictive" in element.value
            for element in app.caption
        )

@pytest.mark.parametrize(
    "methode, duree_reference",
    [
        ("last_period", None),
        ("due_date", 280),
        ("due_date", 287),
    ],
)
def test_affichage_fiche_reelle_9_sa(methode, duree_reference):
    aujourd_hui = date.today()
    origine = aujourd_hui - timedelta(days=65)

    profil = UserProfile().demarrer_parcours(
        "pregnancy",
        origine,
    )

    if methode == "last_period":
        reperes = PregnancyJourney(
            dating_method="last_period",
            last_period_date=origine,
        )
    else:
        assert duree_reference is not None

        reperes = PregnancyJourney(
            dating_method="due_date",
            estimated_due_date=(
                aujourd_hui
                + timedelta(days=duree_reference - 65)
            ),
            term_reference_days=duree_reference,
            dating_rule_version="sa-reference-v1",
        )

    profil = profil.renseigner_reperes_actifs(reperes)

    app = AppTest.from_file("../app.py").run()
    app.session_state["profil"] = profil

    app.radio(
        key="ecran_consulte"
    ).set_value("Grossesse en cours").run()

    assert not app.exception

    textes = [element.value for element in app.text]

    assert "Autour de 9 SA : visage et premiers mouvements" in textes
    assert any("Des mouvements précoces" in texte for texte in textes)

    liens = {
        element.proto.label: element.proto.url
        for element in app.get("link_button")
    }

    assert liens["Source de la fiche hebdomadaire"] == (
        "https://www.betterhealth.vic.gov.au/"
        "health/HealthyLiving/pregnancy-week-by-week"
    )
    assert liens["Reference: www.betterhealth.vic.gov.au"] == (
        "https://www.betterhealth.vic.gov.au/"
    )
    assert "Licence de la fiche hebdomadaire" not in liens

    assert "Références complémentaires" in [
        element.label for element in app.expander
    ]

    assert liens["Consulter : Pregnancy at week 9"] == (
        "https://www.pregnancybirthbaby.org.au/"
        "pregnancy/pregnancy-stages/pregnancy-at-week-9"
    )
    assert liens["Consulter : Your baby's movements"] == (
        "https://www.nhs.uk/pregnancy/keeping-well/"
        "your-babys-movements/"
    )

    assert app.session_state["profil"] == profil

def test_aide_urgence_accessible_pendant_lecture_profil(monkeypatch):
    import stockage_navigateur
    from intentions import MESSAGE_URGENCE

    monkeypatch.setattr(
        stockage_navigateur,
        "lire_sauvegarde_initiale",
        lambda: None,
    )

    app = AppTest.from_file("../app.py").run()

    assert not app.exception

    assert "Lecture de votre sauvegarde locale…" in [
        element.value for element in app.info
    ]

    assert "Besoin d’aide en urgence ?" in [
        element.label for element in app.expander
    ]

    assert MESSAGE_URGENCE in [
        element.value for element in app.warning
    ]

    assert len(app.radio) == 0

def test_assistant_integre_conserve_et_efface_reponse(monkeypatch):
    import json
    import assistant_groq
    from intentions import MESSAGE_URGENCE

    appels = []
    reponse = "Réponse fictive [conception_consultation_objectif]."

    def faux_appel(messages, *, cle_api, modele):
        assert cle_api == "cle-fictive"
        appels.append(messages)

        if len(appels) == 1:
            return "GENERAL_INFORMATION"

        assert len(appels) == 2
        return json.dumps({
            "type": "reponse",
            "texte": reponse,
        })

    monkeypatch.setattr(
        assistant_groq,
        "generer_reponse_groq",
        faux_appel,
    )

    app = AppTest.from_file("../app.py")
    app.secrets["GROQ_API_KEY"] = "cle-fictive"
    app.run()
    assert not app.exception
    profil_initial = app.session_state["profil"]

    app.text_area(key="assistant_question").set_value(
        "À quoi sert une consultation avant une grossesse ?"
    )
    app.button(key="assistant_preparer").click().run()
    app.checkbox(key="assistant_autorisation").check().run()
    app.button(key="assistant_envoyer").click().run()

    assert not app.exception
    assert len(appels) == 2
    assert reponse in [element.value for element in app.markdown]

    # Changer d’écran ne doit ni effacer ni régénérer la réponse.
    app.radio(key="ecran_consulte").set_value(
        "Grossesse en cours"
    ).run()

    assert not app.exception
    assert len(appels) == 2
    assert reponse in [element.value for element in app.markdown]

    # Une nouvelle question retire la réponse et l’autorisation.
    app.text_area(key="assistant_question").set_value(
        "Quels sujets préparer avant une grossesse ?"
    ).run()

    assert not app.exception
    assert "assistant_resultat" not in app.session_state
    assert reponse not in [
        element.value for element in app.markdown
    ]

    app.button(key="assistant_preparer").click().run()

    assert not app.exception
    assert not app.checkbox(key="assistant_autorisation").value

    # Le traitement local d’urgence laisse la page accessible.
    app.text_area(key="assistant_question").set_value(
        "C’est une urgence médicale pour moi."
    ).run()
    app.button(key="assistant_preparer").click().run()

    assert not app.exception
    assert len(appels) == 2
    assert MESSAGE_URGENCE in [
        element.value for element in app.warning
    ]
    assert "Mes données" in [
        element.value for element in app.subheader
    ]
    assert app.session_state["profil"] == profil_initial