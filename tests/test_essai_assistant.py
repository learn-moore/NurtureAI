import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


CHEMIN_APP = (
    Path(__file__).resolve().parents[1]
    / "essai_assistant.py"
)


@pytest.mark.parametrize(
    "scenario, statut, appels",
    [
        (
            "Réponse avec référence",
            "references_controlees",
            ["classification", "generation"],
        ),
        (
            "Aucun passage trouvé",
            "sans_contexte",
            ["classification"],
        ),
        (
            "Urgence repérée localement",
            "urgence_potentielle",
            [],
        ),
        (
            "Situation médicale personnelle",
            "generation_non_autorisee",
            ["classification"],
        ),
        (
            "Demande hors périmètre",
            "generation_non_autorisee",
            ["classification"],
        ),
        (
            "Demande indéterminée",
            "generation_non_autorisee",
            ["classification"],
        ),
        (
            "Générateur indisponible",
            "generation_indisponible",
            ["classification", "generation"],
        ),
        (
            "Référence inventée",
            "reponse_rejetee",
            ["classification", "generation"],
        ),
        (
            "Réponse sans citation",
            "sans_citation",
            ["classification", "generation"],
        ),
        (
            "Classification indisponible",
            "classification_indisponible",
            ["classification"],
        ),
        (
            "Classification invalide",
            "classification_invalide",
            ["classification"],
        ),
        (
            "Urgence personnelle, classifieur indisponible",
            "urgence_potentielle",
            [],
        ),
        (
            "Urgence d’un proche, classifieur indisponible",
            "urgence_potentielle",
            [],
        ),
    ],
)
def test_scenario_assistant(scenario, statut, appels):
    app = AppTest.from_file(str(CHEMIN_APP)).run()

    app.selectbox(
        key="scenario_assistant"
    ).set_value(scenario).run()

    assert not app.exception
    assert not app.json
    assert not any(
        element.value.startswith("Statut :")
        for element in app.caption
    )

    app.button(key="executer_scenario").click().run()

    assert not app.exception
    assert f"Statut : {statut}" in [
        element.value for element in app.caption
    ]
    assert json.loads(app.json[0].value) == appels

    textes = [element.value for element in app.text]
    assert not any(
        "Détail technique fictif" in texte
        for texte in textes
    )
    liens = [
        texte for texte in textes
        if texte.startswith("https://")
    ]

    if statut == "references_controlees":
        assert liens == ["https://example.org/calendrier"]
        assert any("[calendrier]" in texte for texte in textes)
    else:
        assert liens == []

    assert not any(
        "source_inventee" in texte or "Panne simulée" in texte
        for texte in textes
    )

    if statut == "sans_citation":
        assert "Le calendrier présente les rendez-vous." not in textes

    # Une nouvelle exécution sans clic ne relance pas le scénario.
    app.run()

    assert not app.exception
    assert not app.json
    assert not any(
        element.value.startswith("Statut :")
        for element in app.caption
    )