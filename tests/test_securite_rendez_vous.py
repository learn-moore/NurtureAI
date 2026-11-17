import json
from uuid import uuid4

import pytest

from fiches_rendez_vous import PreparationRendezVousUrgente
from intentions import MESSAGE_URGENCE
from modeles import Appointment
from securite_rendez_vous import (
    CONSIGNES_CONTROLE_PREPARATION,
    DecisionPreparation,
    lire_decision_preparation,
    preparer_controle_rendez_vous,
)


@pytest.mark.parametrize(
    "sortie, attendu",
    [
        ("PREPARATION_AUTORISEE", DecisionPreparation.AUTORISEE),
        ("POTENTIAL_EMERGENCY", DecisionPreparation.URGENCE),
        ("PREPARATION_NON_AUTORISEE", DecisionPreparation.NON_AUTORISEE),
        ("INDETERMINE", None),
    ],
)
def test_lecture_decision_exacte(sortie, attendu):
    assert lire_decision_preparation(sortie) is attendu


@pytest.mark.parametrize(
    "sortie",
    [
        None,
        42,
        "",
        "   ",
        "PREPARATION_AUTORISEE ",
        "preparation_autorisee",
        "GENERAL_INFORMATION",
        '{"decision": "PREPARATION_AUTORISEE"}',
        ["PREPARATION_AUTORISEE"],
    ],
)
def test_decision_invalide_ne_devient_pas_autorisation(sortie):
    with pytest.raises(ValueError, match="Décision"):
        lire_decision_preparation(sortie)


@pytest.mark.parametrize(
    "notes, questions, attendu",
    [
        (True, False, {"notes": "Notes fictives."}),
        (False, True, {"questions": ["Question fictive ?"]}),
        (
            True,
            True,
            {
                "notes": "Notes fictives.",
                "questions": ["Question fictive ?"],
            },
        ),
    ],
)
def test_controle_transmet_uniquement_selection(
    notes,
    questions,
    attendu,
):
    fiche = Appointment(
        journey_id=str(uuid4()),
        notes="Notes fictives.",
        questions=("Question fictive ?",),
    )

    messages = preparer_controle_rendez_vous(
        fiche,
        inclure_notes=notes,
        inclure_questions=questions,
    )

    assert len(messages) == 2
    assert messages[0] == {
        "role": "system",
        "content": CONSIGNES_CONTROLE_PREPARATION,
    }
    assert messages[1]["role"] == "user"
    assert json.loads(messages[1]["content"]) == {
        "contenu_selectionne": attendu,
    }


def test_urgence_locale_empeche_messages_de_controle():
    fiche = Appointment(
        journey_id=str(uuid4()),
        notes="C’est une urgence médicale pour moi.",
    )

    with pytest.raises(PreparationRendezVousUrgente) as erreur:
        preparer_controle_rendez_vous(
            fiche,
            inclure_notes=True,
        )

    assert str(erreur.value) == MESSAGE_URGENCE