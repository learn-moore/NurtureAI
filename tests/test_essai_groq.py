from pathlib import Path

from streamlit.testing.v1 import AppTest

import generation_groq
from assistant_documentaire import GenerationIndisponible


CHEMIN_APP = Path(__file__).resolve().parents[1] / "essai_groq.py"


def test_essai_attend_autorisation_et_clic(monkeypatch):
    appels = []

    def faux_generateur(messages, *, cle_api, modele):
        appels.append(messages)
        return "Réponse fictive [calendrier]."

    monkeypatch.setattr(
        generation_groq,
        "generer_reponse_groq",
        faux_generateur,
    )

    app = AppTest.from_file(str(CHEMIN_APP))
    app.secrets["GROQ_API_KEY"] = "cle-fictive"
    app.run()

    assert not app.exception
    assert not app.checkbox[0].value
    assert app.button[0].disabled
    assert appels == []

    app.checkbox[0].check().run()

    assert not app.exception
    assert not app.button[0].disabled
    assert appels == []

    app.button[0].click().run()

    assert not app.exception
    assert len(appels) == 1
    assert "Réponse fictive [calendrier]." in [
        element.value for element in app.text
    ]
    assert "https://example.org/calendrier" in [
        element.value for element in app.text
    ]

    app.run()

    assert not app.exception
    assert len(appels) == 1

def test_essai_signale_indisponibilite_sans_relance(monkeypatch):
    appels = []

    def generateur_indisponible(messages, *, cle_api, modele):
        appels.append(messages)
        raise GenerationIndisponible(
            "Détail technique fictif à ne pas afficher"
        )

    monkeypatch.setattr(
        generation_groq,
        "generer_reponse_groq",
        generateur_indisponible,
    )

    app = AppTest.from_file(str(CHEMIN_APP))
    app.secrets["GROQ_API_KEY"] = "cle-fictive"
    app.run()

    app.checkbox[0].check().run()
    app.button[0].click().run()

    assert not app.exception
    assert len(appels) == 1
    assert len(app.error) == 1
    assert app.error[0].value == (
        "Groq est indisponible ou le quota est atteint."
    )

    assert not any(
        element.value.startswith("https://example.org/")
        for element in app.text
    )

    app.run()

    assert not app.exception
    assert len(appels) == 1

