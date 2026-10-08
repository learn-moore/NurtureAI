from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


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