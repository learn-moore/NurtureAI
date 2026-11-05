import pytest
import json
from uuid import uuid4
from dataclasses import replace
from datetime import date, timedelta

from assistant_documentaire import GenerationIndisponible
from fiches_rendez_vous import exporter_fiche_texte
from intentions import MESSAGE_URGENCE
from modeles import Appointment, UserProfile
from preparation_rendez_vous import proposer_questions_rendez_vous, enregistrer_questions_relues


@pytest.fixture
def fiche():
    return Appointment(
        journey_id=str(uuid4()),
        appointment_type="follow_up",
        notes="Je souhaite discuter de mon alimentation.",
        questions=("Question non sélectionnée ?",),
    )


@pytest.mark.parametrize(
    "sortie, statut, questions",
    [
        (
            '{"questions": ["Quels sujets alimentaires aborder ?"]}',
            "proposition_disponible",
            ("Quels sujets alimentaires aborder ?",),
        ),
        (
            '{"questions": []}',
            "aucune_proposition",
            (),
        ),
        (
            "SORTIE_INVALIDE_NON_PUBLIQUE",
            "proposition_rejetee",
            (),
        ),
    ],
)
def test_proposition_separee_de_la_fiche(
    fiche,
    sortie,
    statut,
    questions,
):
    appels = []
    export_original = exporter_fiche_texte(fiche)

    def faux_generateur(messages):
        appels.append(messages)
        assert json.loads(messages[1]["content"]) == {
            "contenu_selectionne": {"notes": fiche.notes},
        }
        return sortie

    resultat = proposer_questions_rendez_vous(
        fiche,
        generer=faux_generateur,
        inclure_notes=True,
    )

    assert len(appels) == 1
    assert resultat["statut"] == statut
    assert resultat["questions"] == questions
    assert exporter_fiche_texte(fiche) == export_original
    assert "SORTIE_INVALIDE_NON_PUBLIQUE" not in json.dumps(resultat)


def test_panne_preserve_fiche_sans_relance(fiche):
    appels = []
    export_original = exporter_fiche_texte(fiche)

    def generateur_indisponible(messages):
        appels.append(messages)
        raise GenerationIndisponible("DETAIL_TECHNIQUE_NON_PUBLIC")

    resultat = proposer_questions_rendez_vous(
        fiche,
        generer=generateur_indisponible,
        inclure_notes=True,
    )

    assert len(appels) == 1
    assert resultat["statut"] == "generation_indisponible"
    assert resultat["questions"] == ()
    assert "DETAIL_TECHNIQUE_NON_PUBLIC" not in json.dumps(resultat)
    assert exporter_fiche_texte(fiche) == export_original


def test_urgence_locale_bloque_generateur():
    fiche = Appointment(
        journey_id=str(uuid4()),
        appointment_type="other",
        notes="C’est une urgence médicale pour moi.",
    )
    export_original = exporter_fiche_texte(fiche)

    def generateur_interdit(messages):
        pytest.fail("Une urgence reconnue doit bloquer le générateur.")

    resultat = proposer_questions_rendez_vous(
        fiche,
        generer=generateur_interdit,
        inclure_notes=True,
    )

    assert resultat == {
        "statut": "urgence_locale",
        "questions": (),
        "message": MESSAGE_URGENCE,
    }
    assert exporter_fiche_texte(fiche) == export_original

@pytest.fixture
def profil_avec_fiche():
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 11, 1),
    )
    fiche = Appointment(
        journey_id=profil.active_journey_id, # type: ignore
        appointment_type="follow_up",
        notes="Notes originales à conserver.",
        questions=("Question initiale ?",),
    )

    return profil.ajouter_rendez_vous(fiche), fiche


@pytest.mark.parametrize("confirmer", [False, True])
def test_enregistrement_exige_confirmation(
    profil_avec_fiche,
    confirmer,
):
    profil, fiche = profil_avec_fiche
    export_original = exporter_fiche_texte(fiche)
    instant = fiche.created_at + timedelta(seconds=1)

    resultat = enregistrer_questions_relues(
        profil,
        fiche,
        ("Question ajoutée après relecture ?",),
        modifie_le=instant,
        confirmer=confirmer,
    )

    if confirmer:
        nouvelle_fiche = resultat.appointments[0]
        assert nouvelle_fiche.questions == (
            "Question initiale ?",
            "Question ajoutée après relecture ?",
        )
        assert nouvelle_fiche.notes == fiche.notes
        assert nouvelle_fiche.id == fiche.id
        assert nouvelle_fiche.updated_at == instant
    else:
        assert resultat is profil

    assert profil.appointments[0] == fiche
    assert exporter_fiche_texte(fiche) == export_original


@pytest.mark.parametrize("supprimer", [False, True])
def test_fiche_obsolete_refuse_enregistrement(
    profil_avec_fiche,
    supprimer,
):
    profil, fiche = profil_avec_fiche

    if supprimer:
        profil_courant = profil.supprimer_rendez_vous(fiche.id)
        message_attendu = "n’existe plus"
    else:
        fiche_modifiee = replace(
            fiche,
            notes="Notes modifiées depuis l’aperçu.",
        )
        profil_courant = replace(
            profil,
            appointments=(fiche_modifiee,),
        )
        message_attendu = "a changé"

    fiches_avant = profil_courant.appointments

    with pytest.raises(ValueError, match=message_attendu):
        enregistrer_questions_relues(
            profil_courant,
            fiche,
            ("Question issue de l’ancienne version ?",),
            modifie_le=fiche.created_at + timedelta(seconds=2),
            confirmer=True,
        )

    assert profil_courant.appointments == fiches_avant