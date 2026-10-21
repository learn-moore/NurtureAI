import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import assistant_groq
from intentions import MESSAGE_URGENCE


CHEMIN_APP = (
    Path(__file__).resolve().parents[1]
    / "essai_assistant_groq.py"
)


def test_autorisation_avant_les_deux_appels(monkeypatch):
    appels = []

    def faux_appel(messages, *, cle_api, modele):
        assert cle_api == "cle-fictive"
        appels.append(messages)

        if len(appels) == 1:
            return "GENERAL_INFORMATION"

        assert len(appels) == 2
        return "Le calendrier présente les rendez-vous [calendrier]."

    monkeypatch.setattr(
        assistant_groq,
        "generer_reponse_groq",
        faux_appel,
    )

    app = AppTest.from_file(str(CHEMIN_APP))
    app.secrets["GROQ_API_KEY"] = "cle-fictive"
    app.run()

    assert not app.exception
    assert app.button(key="executer_assistant_groq").disabled
    assert appels == []

    # Les aperçus sont comparés ensuite aux messages réellement envoyés.
    apercus = [
        json.loads(element.value)
        for element in app.json
    ]
    assert len(apercus) == 2

    app.checkbox(
        key="autorisation_assistant_groq"
    ).check().run()

    assert not app.exception
    assert appels == []
    assert not app.button(key="executer_assistant_groq").disabled

    app.button(key="executer_assistant_groq").click().run()

    assert not app.exception
    assert len(appels) == 2
    assert [list(messages) for messages in appels] == apercus
    assert "Statut : references_controlees" in [
        element.value for element in app.caption
    ]
    assert "https://example.org/calendrier" in [
        element.value for element in app.text
    ]

    app.run()

    assert not app.exception
    assert len(appels) == 2

    app.selectbox(key="question_assistant_groq").set_value(
        "Et pour moi ?"
    ).run()

    assert not app.exception
    assert not app.checkbox(
        key="autorisation_assistant_groq"
    ).value
    assert app.button(key="executer_assistant_groq").disabled
    assert len(appels) == 2


def test_urgence_locale_sans_envoi(monkeypatch):
    def appel_interdit(*args, **kwargs):
        pytest.fail("Aucun appel distant ne doit être effectué.")

    monkeypatch.setattr(
        assistant_groq,
        "generer_reponse_groq",
        appel_interdit,
    )

    app = AppTest.from_file(str(CHEMIN_APP))
    app.secrets["GROQ_API_KEY"] = ""
    app.run()

    app.selectbox(key="question_assistant_groq").set_value(
        "C’est une urgence médicale pour moi."
    ).run()

    assert not app.exception
    assert MESSAGE_URGENCE in [
        element.value for element in app.warning
    ]
    assert not app.button
    assert not app.checkbox
    assert not app.error

@pytest.mark.parametrize(
    "categorie, statut",
    [
        ("PERSONAL_MEDICAL_SITUATION", "generation_non_autorisee"),
        ("OUT_OF_SCOPE", "generation_non_autorisee"),
        ("INDETERMINE", "generation_non_autorisee"),
        ("POTENTIAL_EMERGENCY", "urgence_potentielle"),
        ("CATEGORIE_INVENTEE", "classification_invalide"),
    ],
)
def test_classification_bloque_second_appel(
    monkeypatch,
    categorie,
    statut,
):
    appels = []

    def faux_appel(messages, *, cle_api, modele):
        appels.append(messages)

        if len(appels) > 1:
            pytest.fail(
                "La classification devait empêcher le second appel."
            )

        return categorie

    monkeypatch.setattr(
        assistant_groq,
        "generer_reponse_groq",
        faux_appel,
    )

    app = AppTest.from_file(str(CHEMIN_APP))
    app.secrets["GROQ_API_KEY"] = "cle-fictive"
    app.run()

    # La question initiale dispose d’un contexte documentaire.
    assert not app.exception
    assert len(app.json) == 2

    app.checkbox(
        key="autorisation_assistant_groq"
    ).check().run()

    assert appels == []

    app.button(key="executer_assistant_groq").click().run()

    assert not app.exception
    assert len(appels) == 1
    assert f"Statut : {statut}" in [
        element.value for element in app.caption
    ]

    assert not any(
        element.value.startswith("https://")
        for element in app.text
    )

    app.run()

    assert not app.exception
    assert len(appels) == 1