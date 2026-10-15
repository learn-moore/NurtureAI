import pytest
import json

import assistant_documentaire
from intentions import Intention, autoriser_generation_documentaire, convertir_intention


@pytest.mark.parametrize(
    "intention, attendu",
    [
        (Intention.GENERAL_INFORMATION, True),
        (Intention.PERSONAL_MEDICAL_SITUATION, False),
        (Intention.POTENTIAL_EMERGENCY, False),
        (Intention.OUT_OF_SCOPE, False),
        (None, False),
    ],
)
def test_autorisation_generation_selon_intention(intention, attendu):
    assert autoriser_generation_documentaire(intention) is attendu

@pytest.mark.parametrize(
    "intention",
    [
        Intention.PERSONAL_MEDICAL_SITUATION,
        Intention.POTENTIAL_EMERGENCY,
        Intention.OUT_OF_SCOPE,
        None,
    ],
)
def test_intention_bloquee_n_accede_pas_a_la_generation(
    monkeypatch,
    intention,
):
    def preparation_interdite(*args, **kwargs):
        pytest.fail("La préparation documentaire devait être bloquée.")

    def generation_interdite(messages):
        pytest.fail("Le générateur ne devait pas être appelé.")

    monkeypatch.setattr(
        assistant_documentaire,
        "preparer_reponse",
        preparation_interdite,
    )

    resultat = assistant_documentaire.preparer_reponse_selon_intention(
        "Demande fictive",
        (),
        intention=intention,
        generer=generation_interdite,
    )

    assert resultat["statut"] == "generation_non_autorisee"
    assert resultat["sources"] == ()

@pytest.mark.parametrize(
    "budget, statut_attendu, nombre_appels",
    [
        (6000, "references_controlees", 1),
        (2, "sans_contexte", 0),
    ],
)
def test_intention_generale_respecte_contexte_et_budget(
    budget,
    statut_attendu,
    nombre_appels,
):
    passage = {
        "id": "calendrier",
        "title": "Calendrier fictif",
        "content": "Le calendrier présente les rendez-vous.",
        "source": "Source fictive",
        "url": "https://example.org/calendrier",
    }
    resultats = ({"passage": passage, "score": 1},)
    appels = []

    def generateur_fictif(messages):
        appels.append(messages)
        return "Le calendrier présente les rendez-vous [calendrier]."

    resultat = assistant_documentaire.preparer_reponse_selon_intention(
        "Que présente le calendrier ?",
        resultats,
        max_caracteres=budget,
        intention=Intention.GENERAL_INFORMATION,
        generer=generateur_fictif,
    )

    assert resultat["statut"] == statut_attendu
    assert len(appels) == nombre_appels

    if nombre_appels:
        donnees = json.loads(appels[0][1]["content"])
        assert donnees["question"] == "Que présente le calendrier ?"
        assert donnees["documents"] == [passage]
        assert resultat["reponse"] == (
            "Le calendrier présente les rendez-vous [calendrier]."
        )
        assert [source["id"] for source in resultat["sources"]] == [
            "calendrier",
        ]
    else:
        assert resultat["sources"] == ()

@pytest.mark.parametrize("intention", list(Intention))
def test_conversion_reconnait_categories(intention):
    assert convertir_intention(intention.value) is intention


@pytest.mark.parametrize(
    "valeur",
    [
        None,
        42,
        "",
        "INCONNUE",
        "general_information",
        " GENERAL_INFORMATION ",
        "GENERAL_INFORMATION avec réserve",
        {"intention": "GENERAL_INFORMATION"},
    ],
)
def test_conversion_invalide_n_autorise_pas_generation(valeur):
    intention = convertir_intention(valeur)

    assert intention is None
    assert autoriser_generation_documentaire(intention) is False

