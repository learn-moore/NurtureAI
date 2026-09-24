import pytest

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

