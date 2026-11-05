from datetime import date
from uuid import uuid4

import pytest
import json

from modeles import Appointment
from fiches_rendez_vous import exporter_fiche_texte, preparer_contenu_ia, lire_proposition_questions, fusionner_questions_rendez_vous


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

@pytest.fixture
def fiche_pour_ia():
    return Appointment(
        journey_id=str(uuid4()),
        appointment_type="follow_up",
        date=date(2026, 11, 20),
        topics=("nutrition",),
        notes="Notes fictives à conserver.",
        questions=("Première question ?", "Deuxième question ?"),
    )


@pytest.mark.parametrize(
    "inclure_notes, inclure_questions, attendu",
    [
        (
            True,
            False,
            {"notes": "Notes fictives à conserver."},
        ),
        (
            False,
            True,
            {
                "questions": [
                    "Première question ?",
                    "Deuxième question ?",
                ],
            },
        ),
        (
            True,
            True,
            {
                "notes": "Notes fictives à conserver.",
                "questions": [
                    "Première question ?",
                    "Deuxième question ?",
                ],
            },
        ),
    ],
)
def test_selection_champs_ia(
    fiche_pour_ia,
    inclure_notes,
    inclure_questions,
    attendu,
):
    contenu = preparer_contenu_ia(
        fiche_pour_ia,
        inclure_notes=inclure_notes,
        inclure_questions=inclure_questions,
    )

    assert contenu == attendu


def test_aucune_transmission_par_defaut(fiche_pour_ia):
    with pytest.raises(ValueError, match="champ non vide"):
        preparer_contenu_ia(fiche_pour_ia)


def test_selection_vide_refusee():
    fiche = Appointment(
        journey_id=str(uuid4()),
        appointment_type="other",
        notes="   ",
    )

    with pytest.raises(ValueError, match="champ non vide"):
        preparer_contenu_ia(
            fiche,
            inclure_notes=True,
            inclure_questions=True,
        )


def test_contenu_prepare_independant_de_la_fiche(fiche_pour_ia):
    export_original = exporter_fiche_texte(fiche_pour_ia)

    contenu = preparer_contenu_ia(
        fiche_pour_ia,
        inclure_notes=True,
        inclure_questions=True,
    )
    contenu["notes"] = "Texte modifié dans la copie."
    contenu["questions"].append("Question ajoutée dans la copie ?")

    assert exporter_fiche_texte(fiche_pour_ia) == export_original

@pytest.mark.parametrize(
    "questions, attendu",
    [
        ([], ()),
        (["  Question fictive ?  "], ("Question fictive ?",)),
        (["x" * 500] * 30, tuple(["x" * 500] * 30)),
    ],
)
def test_lire_proposition_questions_valide(questions, attendu):
    sortie = json.dumps({"questions": questions})

    assert lire_proposition_questions(sortie) == attendu


@pytest.mark.parametrize(
    "sortie",
    [
        None,
        42,
        "",
        "   ",
        "Texte sans JSON",
        '```json\n{"questions": []}\n```',
        "[]",
        "{}",
        '{"questions": "Une question ?"}',
        '{"questions": null}',
        '{"questions": [""]}',
        '{"questions": ["   "]}',
        '{"questions": [42]}',
        '{"questions": [], "notes": "Ajout non autorisé"}',
        '{"questions": [], "questions": ["Remplacement silencieux ?"]}',
        json.dumps({"questions": ["Question ?"] * 31}),
        json.dumps({"questions": ["x" * 501]}),
    ],
)
def test_lire_proposition_questions_refuse_sortie_invalide(sortie):
    with pytest.raises(ValueError):
        lire_proposition_questions(sortie)

@pytest.mark.parametrize(
    "proposition, attendu",
    [
        (
            (),
            ("Première question ?", "Deuxième question ?"),
        ),
        (
            ("Première question ?", "Nouvelle question ?"),
            (
                "Première question ?",
                "Deuxième question ?",
                "Nouvelle question ?",
            ),
        ),
        (
            ("Nouvelle question ?", "Nouvelle question ?"),
            (
                "Première question ?",
                "Deuxième question ?",
                "Nouvelle question ?",
            ),
        ),
    ],
)
def test_fusion_conserve_questions_et_fiche(
    fiche_pour_ia,
    proposition,
    attendu,
):
    export_original = exporter_fiche_texte(fiche_pour_ia)

    resultat = fusionner_questions_rendez_vous(
        fiche_pour_ia,
        proposition,
    )

    assert resultat == attendu
    assert exporter_fiche_texte(fiche_pour_ia) == export_original


def test_fusion_accepte_doublon_quand_fiche_complete(fiche_pour_ia):
    from dataclasses import replace

    questions = tuple(f"Question {numero} ?" for numero in range(30))
    fiche = replace(fiche_pour_ia, questions=questions)

    assert fusionner_questions_rendez_vous(
        fiche,
        (questions[0],),
    ) == questions


def test_fusion_refuse_depassement_sans_modifier_fiche(fiche_pour_ia):
    from dataclasses import replace

    fiche = replace(
        fiche_pour_ia,
        questions=tuple(
            f"Question {numero} ?" for numero in range(30)
        ),
    )
    export_original = exporter_fiche_texte(fiche)

    with pytest.raises(ValueError, match="30"):
        fusionner_questions_rendez_vous(
            fiche,
            ("Question supplémentaire ?",),
        )

    assert exporter_fiche_texte(fiche) == export_original