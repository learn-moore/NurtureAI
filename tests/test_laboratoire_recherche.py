from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import assistant_documentaire


CHEMIN_APP = (
    Path(__file__).resolve().parents[1]
    / "laboratoire_recherche.py"
)


@pytest.mark.parametrize(
    "theme, titres_attendus",
    [
        (
            "Tous les thèmes",
            [
                "1. Calendrier de démonstration",
                "2. Sauvegarde de démonstration",
                "3. Export de démonstration",
            ],
        ),
        ("conception", ["1. Export de démonstration"]),
        ("nutrition", []),
    ],
)
def test_laboratoire_recherche_et_filtre(theme, titres_attendus):
    app = AppTest.from_file(str(CHEMIN_APP)).run()

    assert not app.exception

    app.text_input(key="question_recherche").set_value("profil")
    app.selectbox[0].set_value(theme)
    app.button[0].click().run()

    assert not app.exception
    assert [
        element.value for element in app.subheader
    ] == titres_attendus

    if not titres_attendus:
        assert (
            "Aucun passage correspondant dans ce périmètre."
        ) in [
            element.value for element in app.info
        ]

    assert len(app.get("download_button")) == 1


def test_laboratoire_refuse_question_vide():
    app = AppTest.from_file(str(CHEMIN_APP)).run()

    app.text_input(key="question_recherche").set_value("   ")
    app.button[0].click().run()

    assert not app.exception
    assert "Saisissez une question non vide." in [
        element.value for element in app.warning
    ]
    assert len(app.subheader) == 0
    assert len(app.get("download_button")) == 0

@pytest.mark.parametrize(
    "theme, reponse, statut",
    [
        (
            "Tous les thèmes",
            "Les rendez-vous sont affichés [calendrier].",
            "reconnue",
        ),
        (
            "Tous les thèmes",
            "Les rendez-vous [calendrier] et un détail [invente].",
            "inconnue",
        ),
        (
            "conception",
            "Les rendez-vous sont affichés [calendrier].",
            "inconnue",
        ),
        (
            "Tous les thèmes",
            "Les documents sont insuffisants.",
            "sans_citation",
        ),
    ],
)
def test_laboratoire_controle_references(theme, reponse, statut):
    app = AppTest.from_file(str(CHEMIN_APP)).run()

    app.text_input(key="question_recherche").set_value("profil")
    app.selectbox[0].set_value(theme)
    app.text_area(key="reponse_fictive").set_value(reponse)
    app.button[0].click().run()

    assert not app.exception

    controle = next(
        element
        for element in app.expander
        if element.label == "Contrôle des références de la réponse fictive"
    )

    if statut == "reconnue":
        assert len(controle.success) == 1
        assert not controle.error
        assert not controle.warning
        assert "https://example.org/calendrier" in [
            element.value for element in controle.text
        ]

    elif statut == "inconnue":
        assert len(controle.error) == 1
        assert "Références absentes du contexte" in controle.error[0].value
        assert not controle.success
        assert not controle.text

    else:
        assert len(controle.warning) == 1
        assert "Aucune citation détectée" in controle.warning[0].value
        assert not controle.success
        assert not controle.error
        assert not controle.text

@pytest.mark.parametrize(
    "theme, identifiant",
    [
        ("Tous les thèmes", "calendrier"),
        ("conception", "export"),
        ("nutrition", None),
    ],
)
def test_laboratoire_affiche_simulation(theme, identifiant):
    app = AppTest.from_file(str(CHEMIN_APP)).run()

    app.text_input(key="question_recherche").set_value("profil")
    app.selectbox[0].set_value(theme)
    app.button[0].click().run()

    assert not app.exception

    simulation = next(
        element
        for element in app.expander
        if element.label == "Réponse simulée"
    )

    assert not simulation.error

    if identifiant is None:
        assert len(simulation.info) == 1
        assert "Aucun passage disponible" in simulation.info[0].value
        assert not simulation.text
    else:
        assert not simulation.info
        assert f"[{identifiant}]" in simulation.text[0].value
        assert "Démonstration sur un corpus fictif." in (
            simulation.text[0].value
        )
        assert f"https://example.org/{identifiant}" in [
            element.value for element in simulation.text
        ]


def test_laboratoire_masque_simulation_invalide(monkeypatch):
    def generation_invalide(messages):
        return "Une information à ne pas afficher [invente]."

    monkeypatch.setattr(
        assistant_documentaire,
        "generer_reponse_simulee",
        generation_invalide,
    )

    app = AppTest.from_file(str(CHEMIN_APP)).run()
    app.text_input(key="question_recherche").set_value("profil")
    app.button[0].click().run()

    assert not app.exception

    simulation = next(
        element
        for element in app.expander
        if element.label == "Réponse simulée"
    )

    assert len(simulation.error) == 1
    assert "invente" in simulation.error[0].value
    assert not simulation.text

def test_laboratoire_signale_simulation_sans_citation(monkeypatch):
    reponse = "Les documents sont insuffisants pour répondre."

    def generation_sans_citation(messages):
        return reponse

    monkeypatch.setattr(
        assistant_documentaire,
        "generer_reponse_simulee",
        generation_sans_citation,
    )

    app = AppTest.from_file(str(CHEMIN_APP)).run()
    app.text_input(key="question_recherche").set_value("profil")
    app.button[0].click().run()

    assert not app.exception

    simulation = next(
        element
        for element in app.expander
        if element.label == "Réponse simulée"
    )

    assert len(simulation.warning) == 1
    assert "Aucune citation détectée" in simulation.warning[0].value
    assert not simulation.error
    assert not simulation.success

    assert [
        element.value for element in simulation.text
    ] == [reponse]

    assert not any(
        "Les références appartiennent au contexte" in element.value
        for element in simulation.caption
    )

def test_laboratoire_conserve_recherche_si_generation_indisponible(
    monkeypatch,
):
    def generation_indisponible(messages):
        raise assistant_documentaire.GenerationIndisponible(
            "Détail technique fictif à ne pas afficher"
        )

    monkeypatch.setattr(
        assistant_documentaire,
        "generer_reponse_simulee",
        generation_indisponible,
    )

    app = AppTest.from_file(str(CHEMIN_APP)).run()
    app.text_input(key="question_recherche").set_value("profil")
    app.button[0].click().run()

    assert not app.exception

    simulation = next(
        element
        for element in app.expander
        if element.label == "Réponse simulée"
    )

    assert len(simulation.error) == 1
    assert simulation.error[0].value == (
        "La génération est temporairement indisponible. "
        "Les passages documentaires restent consultables."
    )
    assert not simulation.text

    assert [
        element.value for element in app.subheader
    ] == [
        "1. Calendrier de démonstration",
        "2. Sauvegarde de démonstration",
        "3. Export de démonstration",
    ]
    assert "Le calendrier présente les rendez-vous du profil." in [
        element.value for element in app.text
    ]

    boutons = app.get("download_button")
    assert len(boutons) == 1
    assert not boutons[0].disabled # type: ignore

