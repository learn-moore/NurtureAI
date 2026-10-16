import json

import pytest

from assistant_documentaire import GenerationIndisponible
from classification_intentions import (
    CONSIGNES_CLASSIFICATION,
    classer_demande_experimentale,
)
from intentions import ClassificationIndisponible, Intention


@pytest.mark.parametrize(
    "sortie, attendu",
    [
        ("GENERAL_INFORMATION", Intention.GENERAL_INFORMATION),
        ("PERSONAL_MEDICAL_SITUATION", Intention.PERSONAL_MEDICAL_SITUATION),
        ("POTENTIAL_EMERGENCY", Intention.POTENTIAL_EMERGENCY),
        ("OUT_OF_SCOPE", Intention.OUT_OF_SCOPE),
        ("INDETERMINE", None),
    ],
)
def test_classification_convertit_sortie(sortie, attendu):
    resultat = classer_demande_experimentale(
        "Question fictive",
        generer=lambda messages: sortie,
    )

    assert resultat is attendu


@pytest.mark.parametrize(
    "sortie",
    [
        None,
        "",
        "general_information",
        " GENERAL_INFORMATION ",
        "GENERAL_INFORMATION avec réserve",
        '{"intention": "GENERAL_INFORMATION"}',
    ],
)
def test_classification_refuse_sortie_invalide(sortie):
    with pytest.raises(ValueError, match="catégorie non conforme"):
        classer_demande_experimentale(
            "Question fictive",
            generer=lambda messages: sortie,
        )


def test_classification_transmet_seulement_question_et_consignes():
    appels = []

    def faux_generateur(messages):
        appels.append(messages)
        return "INDETERMINE"

    classer_demande_experimentale(
        "  Question fictive  ",
        generer=faux_generateur,
    )

    assert len(appels) == 1
    messages = appels[0]

    assert len(messages) == 2
    assert messages[0] == {
        "role": "system",
        "content": CONSIGNES_CLASSIFICATION,
    }
    assert messages[1]["role"] == "user"
    assert json.loads(messages[1]["content"]) == {
        "question": "Question fictive",
    }


def test_classification_traduit_indisponibilite():
    def generateur_indisponible(messages):
        raise GenerationIndisponible("Détail technique fictif")

    with pytest.raises(ClassificationIndisponible) as erreur:
        classer_demande_experimentale(
            "Question fictive",
            generer=generateur_indisponible,
        )

    assert str(erreur.value) == (
        "Le service de classification est indisponible."
    )


@pytest.mark.parametrize("question", ["", "   ", None, 42])
def test_classification_refuse_question_avant_generation(question):
    def generation_interdite(messages):
        pytest.fail("Le générateur ne devait pas être appelé.")

    with pytest.raises(ValueError, match="question"):
        classer_demande_experimentale(
            question,
            generer=generation_interdite,
        )