import pytest
import json
from uuid import uuid4
from dataclasses import replace
from datetime import date, timedelta

from assistant_documentaire import GenerationIndisponible
from fiches_rendez_vous import exporter_fiche_texte
from intentions import MESSAGE_URGENCE
from modeles import Appointment, UserProfile
from preparation_rendez_vous import (
    proposer_questions_rendez_vous,
    enregistrer_questions_relues,
    controler_et_proposer_questions,
    controler_proposer_et_verifier_questions,
    )


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

@pytest.mark.parametrize(
    "sortie, statut",
    [
        ("POTENTIAL_EMERGENCY", "urgence_detectee"),
        ("PREPARATION_NON_AUTORISEE", "preparation_non_autorisee"),
        ("INDETERMINE", "preparation_non_autorisee"),
        ("VALEUR_INVALIDE_NON_PUBLIQUE", "controle_invalide"),
        (None, "controle_invalide"),
        (
            GenerationIndisponible("DETAIL_TECHNIQUE_NON_PUBLIC"),
            "controle_indisponible",
        ),
    ],
)
def test_controle_defavorable_bloque_reformulation(
    fiche,
    sortie,
    statut,
):
    appels = []

    def controler(messages):
        appels.append("controle")
        if isinstance(sortie, Exception):
            raise sortie
        return sortie

    def generer(messages):
        pytest.fail("La reformulation devait être bloquée.")

    resultat = controler_et_proposer_questions(
        fiche,
        controler=controler,
        generer=generer,
        inclure_notes=True,
    )

    assert appels == ["controle"]
    assert resultat["statut"] == statut
    assert resultat["questions"] == ()
    assert "NON_PUBLIC" not in json.dumps(resultat)

    if statut == "urgence_detectee":
        assert resultat["message"] == MESSAGE_URGENCE


def test_controle_favorable_precede_reformulation(fiche):
    appels = []

    def controler(messages):
        appels.append(("controle", messages))
        return "PREPARATION_AUTORISEE"

    def generer(messages):
        appels.append(("reformulation", messages))
        return '{"questions": ["Quels sujets alimentaires aborder ?"]}'

    resultat = controler_et_proposer_questions(
        fiche,
        controler=controler,
        generer=generer,
        inclure_notes=True,
    )

    assert [etape for etape, _ in appels] == [
        "controle",
        "reformulation",
    ]
    attendu = {
        "contenu_selectionne": {"notes": fiche.notes},
    }
    assert json.loads(appels[0][1][1]["content"]) == attendu
    assert json.loads(appels[1][1][1]["content"]) == attendu
    assert resultat["statut"] == "proposition_disponible"
    assert resultat["questions"] == (
        "Quels sujets alimentaires aborder ?",
    )


def test_urgence_locale_bloque_controle_et_reformulation(fiche):
    fiche_urgente = replace(
        fiche,
        notes="C’est une urgence médicale pour moi.",
    )

    def appel_interdit(messages):
        pytest.fail("Aucun appel ne devait être effectué.")

    resultat = controler_et_proposer_questions(
        fiche_urgente,
        controler=appel_interdit,
        generer=appel_interdit,
        inclure_notes=True,
    )

    assert resultat == {
        "statut": "urgence_locale",
        "questions": (),
        "message": MESSAGE_URGENCE,
    }

@pytest.mark.parametrize(
    "sortie, statut",
    [
        ("FIDELE", "proposition_disponible"),
        ("NON_FIDELE", "proposition_non_fidele"),
        ("INDETERMINE", "fidelite_indeterminee"),
        ("FIDELE avec explication", "fidelite_invalide"),
        (None, "fidelite_indisponible"),
    ],
)
def test_seule_une_proposition_fidele_est_retournee(fiche, sortie, statut):
    appels = []
    question = "Pourrions-nous parler de mon alimentation ?"
    fiche_avant = exporter_fiche_texte(fiche)

    def controler(messages):
        appels.append("securite")
        return "PREPARATION_AUTORISEE"

    def generer(messages):
        appels.append("reformulation")
        return json.dumps({"questions": [question]})

    def verifier_fidelite(messages):
        appels.append("fidelite")
        assert json.loads(messages[1]["content"]) == {
            "contenu_selectionne": {"notes": fiche.notes},
            "questions_proposees": [question],
        }

        if sortie is None:
            raise GenerationIndisponible("DETAIL_TECHNIQUE_NON_PUBLIC")
        return sortie

    resultat = controler_proposer_et_verifier_questions(
        fiche,
        controler=controler,
        generer=generer,
        verifier_fidelite=verifier_fidelite,
        inclure_notes=True,
    )

    assert appels == ["securite", "reformulation", "fidelite"]
    assert resultat["statut"] == statut
    assert resultat["questions"] == ((question,) if sortie == "FIDELE" else ())
    assert "DETAIL_TECHNIQUE_NON_PUBLIC" not in json.dumps(resultat)

    if sortie != "FIDELE":
        assert question not in json.dumps(resultat)

    assert exporter_fiche_texte(fiche) == fiche_avant


@pytest.mark.parametrize(
    "decision, sortie, statut",
    [
        ("POTENTIAL_EMERGENCY", None, "urgence_detectee"),
        ("PREPARATION_AUTORISEE", '{"questions":[]}', "aucune_proposition"),
        ("PREPARATION_AUTORISEE", "JSON invalide", "proposition_rejetee"),
    ],
)
def test_pas_de_controle_fidelite_sans_proposition(fiche, decision, sortie, statut):
    def generer(messages):
        assert sortie is not None, "La reformulation devait être bloquée."
        return sortie

    def verifier_fidelite(messages):
        pytest.fail("Aucune proposition ne devait être transmise au vérificateur.")

    resultat = controler_proposer_et_verifier_questions(
        fiche,
        controler=lambda messages: decision,
        generer=generer,
        verifier_fidelite=verifier_fidelite,
        inclure_notes=True,
    )

    assert resultat["statut"] == statut
    assert resultat["questions"] == ()