import pytest

from evaluation_intentions import evaluer_classifieur
from intentions import Intention, ClassificationIndisponible


def test_evaluation_distingue_reussite_erreur_et_indetermination():
    cas = [
        {
            "id": "TEST-01",
            "question": "Question générale fictive",
            "intention_attendue": "GENERAL_INFORMATION",
        },
        {
            "id": "TEST-02",
            "question": "Situation personnelle fictive",
            "intention_attendue": "PERSONAL_MEDICAL_SITUATION",
        },
        {
            "id": "TEST-03",
            "question": "Question ambiguë fictive",
            "intention_attendue": None,
        },
    ]
    questions_recues = []

    def faux_classifieur(question):
        questions_recues.append(question)

        if question == "Question ambiguë fictive":
            return None

        return Intention.GENERAL_INFORMATION

    evaluations = evaluer_classifieur(cas, classer=faux_classifieur)

    assert questions_recues == [
        exemple["question"] for exemple in cas
    ]
    assert [evaluation["conforme"] for evaluation in evaluations] == [
        True,
        False,
        True,
    ]
    assert evaluations[1] == {
        "id": "TEST-02",
        "attendu": "PERSONAL_MEDICAL_SITUATION",
        "obtenu": "GENERAL_INFORMATION",
        "conforme": False,
        "generation_indument_autorisee": True,
        "erreur": None,
    }

@pytest.mark.parametrize(
    "attendu, obtenu, ouverture_indue",
    [
        ("GENERAL_INFORMATION", Intention.GENERAL_INFORMATION, False),
        ("GENERAL_INFORMATION", None, False),
        ("PERSONAL_MEDICAL_SITUATION", Intention.GENERAL_INFORMATION, True),
        ("POTENTIAL_EMERGENCY", Intention.GENERAL_INFORMATION, True),
        ("OUT_OF_SCOPE", Intention.GENERAL_INFORMATION, True),
        (None, Intention.GENERAL_INFORMATION, True),
        ("POTENTIAL_EMERGENCY", Intention.PERSONAL_MEDICAL_SITUATION, False),
    ],
)
def test_evaluation_repere_generation_indument_autorisee(
    attendu,
    obtenu,
    ouverture_indue,
):
    cas = [
        {
            "id": "TEST-AUTORISATION",
            "question": "Demande fictive",
            "intention_attendue": attendu,
        },
    ]

    evaluations = evaluer_classifieur(
        cas,
        classer=lambda question: obtenu,
    )

    assert evaluations[0]["generation_indument_autorisee"] is ouverture_indue
    assert evaluations[0]["conforme"] is (
        attendu == (obtenu.value if obtenu is not None else None)
    )

def test_evaluation_distingue_panne_et_indetermination():
    cas = [
        {
            "id": "PANNE",
            "question": "Question pendant une panne",
            "intention_attendue": None,
        },
        {
            "id": "SUIVANT",
            "question": "Question ambiguë",
            "intention_attendue": None,
        },
    ]
    appels = []

    def classifieur(question):
        appels.append(question)

        if question == "Question pendant une panne":
            raise ClassificationIndisponible("Erreur fictive")

        return None

    evaluations = evaluer_classifieur(cas, classer=classifieur)

    assert appels == [
        "Question pendant une panne",
        "Question ambiguë",
    ]
    assert evaluations[0]["erreur"] == "classification_indisponible"
    assert evaluations[0]["conforme"] is False
    assert evaluations[0]["generation_indument_autorisee"] is False

    assert evaluations[1]["erreur"] is None
    assert evaluations[1]["conforme"] is True

