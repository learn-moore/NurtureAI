import json
import pytest
from pathlib import Path

import streamlit as st
from streamlit.testing.v1 import AppTest

import generation_groq
from classification_intentions import (
    CONSIGNES_CLASSIFICATION,
    VERSION_CLASSIFICATION,
)
from assistant_documentaire import GenerationIndisponible


CHEMIN_APP = (
    Path(__file__).resolve().parents[1]
    / "essai_classification.py"
)


def test_historique_et_export_classification(monkeypatch):
    appels = []
    exports = []

    def faux_generateur(messages, *, cle_api, modele):
        appels.append(messages)
        return "GENERAL_INFORMATION"

    def faux_telechargement(label, *, data, **options):
        exports.append({
            "contenu": json.loads(data),
            "options": options,
        })
        return False

    monkeypatch.setattr(
        generation_groq,
        "generer_reponse_groq",
        faux_generateur,
    )
    monkeypatch.setattr(
        st,
        "download_button",
        faux_telechargement,
    )

    app = AppTest.from_file(str(CHEMIN_APP))
    app.secrets["GROQ_API_KEY"] = "cle-fictive"
    app.run()

    assert not app.exception
    assert app.button[0].disabled
    assert appels == []
    assert exports == []

    app.checkbox(
        key="autorisation_classification"
    ).check().run()

    assert not app.exception
    assert appels == []

    app.button[0].click().run()

    assert not app.exception
    assert len(appels) == 1

    historique = app.session_state["historique_classification"]
    assert len(historique) == 1

    premier = historique[0]
    premier_id = premier["id_essai"]

    assert premier["cas"]["id"] == "INT-01"
    assert premier["resultat"]["conforme"] is True
    assert premier["version_classification"] == VERSION_CLASSIFICATION
    assert premier["consignes"] == CONSIGNES_CLASSIFICATION

    # Une nouvelle exécution de la page ne crée pas d'essai.
    app.run()

    assert not app.exception
    assert len(appels) == 1
    assert len(
        app.session_state["historique_classification"]
    ) == 1

    # Refaire le même cas conserve également le premier résultat.
    app.button[0].click().run()

    assert not app.exception
    assert len(appels) == 2

    historique = app.session_state["historique_classification"]
    assert len(historique) == 2
    assert historique[0]["id_essai"] == premier_id
    assert historique[1]["id_essai"] != premier_id

    # Changer de cas conserve l'historique et retire l'autorisation.
    app.selectbox(
        key="cas_classification"
    ).set_value("INT-02").run()

    assert not app.exception
    assert not app.checkbox(
        key="autorisation_classification"
    ).value
    assert app.button[0].disabled
    assert len(appels) == 2

    historique = app.session_state["historique_classification"]
    assert len(historique) == 2

    dernier_export = exports[-1]
    assert dernier_export["contenu"] == {
        "schema_version": 1,
        "essais": historique,
    }
    assert dernier_export["options"]["mime"] == "application/json"
    assert dernier_export["options"]["on_click"] == "ignore"
    assert "cle-fictive" not in json.dumps(
        dernier_export["contenu"]
    )

@pytest.mark.parametrize(
    "scenario, erreur_attendue",
    [
        ("indisponible", "classification_indisponible"),
        ("format_invalide", "classification_invalide"),
        ("requete_refusee", "requete_refusee"),
        ("generation_interrompue", "generation_interrompue"),
        ("reponse_vide", "reponse_vide"),
    ],
)
def test_echec_conserve_dans_historique(
    monkeypatch,
    scenario,
    erreur_attendue,
):
    appels = []
    exports = []

    def faux_generateur(messages, *, cle_api, modele):
        appels.append(messages)

        if scenario == "indisponible":
            raise GenerationIndisponible(
                "Détail technique fictif"
            )

        erreurs_fournisseur = {
            "requete_refusee": generation_groq.RequeteGroqRefusee,
            "generation_interrompue": (
                generation_groq.GenerationGroqInterrompue
            ),
            "reponse_vide": generation_groq.ReponseGroqVide,
        }

        if scenario in erreurs_fournisseur:
            raise erreurs_fournisseur[scenario](
                "Détail technique fictif"
            )

        return "Une catégorie qui n'existe pas"

    def faux_telechargement(label, *, data, **options):
        exports.append(json.loads(data))
        return False

    monkeypatch.setattr(
        generation_groq,
        "generer_reponse_groq",
        faux_generateur,
    )
    monkeypatch.setattr(
        st,
        "download_button",
        faux_telechargement,
    )

    app = AppTest.from_file(str(CHEMIN_APP))
    app.secrets["GROQ_API_KEY"] = "cle-fictive"
    app.run()

    app.checkbox(
        key="autorisation_classification"
    ).check().run()
    app.button[0].click().run()

    assert not app.exception
    assert len(appels) == 1
    assert len(app.error) == 1

    historique = app.session_state["historique_classification"]
    assert len(historique) == 1

    resultat = historique[0]["resultat"]
    assert resultat["erreur"] == erreur_attendue
    assert resultat["obtenu"] is None
    assert resultat["conforme"] is False
    assert resultat["generation_indument_autorisee"] is False

    assert exports[-1]["essais"] == historique
    assert "Détail technique fictif" not in json.dumps(
        exports[-1]
    )
    assert "Détail technique fictif" not in app.error[0].value

    # Réafficher la page ne relance pas l'essai échoué.
    app.run()

    assert not app.exception
    assert len(appels) == 1
    assert len(
        app.session_state["historique_classification"]
    ) == 1

