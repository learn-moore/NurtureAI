from datetime import date
from uuid import uuid4

import pytest

from modeles import Appointment
from fiches_rendez_vous import exporter_fiche_texte


@pytest.mark.parametrize(
    "date_rdv, libelle",
    [
        (None, "Date à définir"),
        (date(2026, 10, 15), "15/10/2026"),
    ],
)
def test_export_fiche_complete(date_rdv, libelle):
    fiche = Appointment(
        journey_id=str(uuid4()),
        appointment_type="follow_up",
        date=date_rdv,
        topics=("travel", "nutrition"),
        notes="Première ligne\n**Texte personnel**",
        questions=("Première question ?", "Deuxième question ?"),
    )

    texte = exporter_fiche_texte(fiche)

    assert texte == (
        "NurtureAI : préparation de rendez-vous\n"
        "Type : Consultation de suivi\n"
        f"Date : {libelle}\n"
        "Thèmes : Voyage, Alimentation\n"
        "\n"
        "Notes\n"
        "Première ligne\n**Texte personnel**\n"
        "\n"
        "Questions\n"
        "1. Première question ?\n"
        "2. Deuxième question ?\n"
        "\n"
        "Fiche personnelle de préparation, ne remplaçant pas un avis médical.\n"
    )


def test_export_fiche_sans_contenu_facultatif():
    fiche = Appointment(journey_id=str(uuid4()))

    texte = exporter_fiche_texte(fiche)

    assert "Type : Autre\n" in texte
    assert "Date : Date à définir\n" in texte
    assert "Aucun thème sélectionné." in texte
    assert "Aucune note renseignée." in texte
    assert "Aucune question renseignée." in texte