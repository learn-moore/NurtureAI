from datetime import date, timedelta
from streamlit.testing.v1 import AppTest

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
    assert len(app.metric) == 1
    assert app.metric[0].value == "9 SA + 2 jours"

    # Aller au parcours conception, puis revenir.
    app.radio[0].set_value("Projet de conception").run()
    app.radio[0].set_value("Grossesse en cours").run()

    assert not app.exception
    assert len(app.metric) == 1
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