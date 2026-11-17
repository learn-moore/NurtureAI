from collections.abc import Callable
from datetime import datetime

from assistant_documentaire import GenerationIndisponible
from fiches_rendez_vous import (
    PreparationRendezVousUrgente,
    lire_proposition_questions,
    fusionner_questions_rendez_vous,
    preparer_contenu_ia,
)
from intentions import MESSAGE_URGENCE
from messages_assistant import preparer_messages_rendez_vous
from modeles import Appointment, UserProfile
from securite_rendez_vous import (
    DecisionPreparation,
    lire_decision_preparation,
    preparer_controle_rendez_vous,
)
from fidelite_rendez_vous import (
    VerdictFidelite,
    lire_verdict_fidelite,
    preparer_messages_fidelite,
)


def proposer_questions_rendez_vous(
    fiche,
    *,
    generer: Callable,
    inclure_notes: bool = False,
    inclure_questions: bool = False,
) -> dict:
    """Produit une proposition séparée, sans modifier la fiche."""
    try:
        messages = preparer_messages_rendez_vous(
            fiche,
            inclure_notes=inclure_notes,
            inclure_questions=inclure_questions,
        )
    except PreparationRendezVousUrgente:
        return {
            "statut": "urgence_locale",
            "questions": (),
            "message": MESSAGE_URGENCE,
        }

    try:
        sortie = generer(messages)
    except GenerationIndisponible:
        return {
            "statut": "generation_indisponible",
            "questions": (),
            "message": (
                "La préparation est temporairement indisponible. Votre fiche reste inchangée."
            ),
        }

    try:
        questions = lire_proposition_questions(sortie)
    except ValueError:
        return {
            "statut": "proposition_rejetee",
            "questions": (),
            "message": (
                "La proposition ne respecte pas le format attendu. Elle n’est pas affichée. Votre fiche reste inchangée."
            ),
        }

    if not questions:
        return {
            "statut": "aucune_proposition",
            "questions": (),
            "message": (
                "Aucune question n’a été proposée à partir du contenu sélectionné."
            ),
        }

    return {
        "statut": "proposition_disponible",
        "questions": questions,
        "message": (
            "Proposition à relire et à modifier avant tout enregistrement dans la fiche."
        ),
    }

def enregistrer_questions_relues(
    profil: UserProfile,
    fiche_reference: Appointment,
    questions_relues: tuple[str, ...],
    *,
    modifie_le: datetime,
    confirmer: bool = False,
) -> UserProfile:
    """Retourne un profil modifié uniquement après confirmation."""
    if type(confirmer) is not bool:
        raise ValueError("La confirmation doit être booléenne.")

    if not confirmer:
        return profil

    fiche_actuelle = next(
        (
            fiche
            for fiche in profil.appointments
            if fiche.id == fiche_reference.id
        ),
        None,
    )

    if fiche_actuelle is None:
        raise ValueError("La fiche de rendez-vous n’existe plus.")

    if fiche_actuelle != fiche_reference:
        raise ValueError(
            "La fiche a changé depuis la préparation. Préparez une nouvelle proposition."
        )

    questions = fusionner_questions_rendez_vous(
        fiche_actuelle,
        questions_relues,
    )

    if questions == fiche_actuelle.questions:
        return profil

    return profil.modifier_rendez_vous(
        fiche_actuelle.id,
        appointment_type=fiche_actuelle.appointment_type,
        date=fiche_actuelle.date,
        notes=fiche_actuelle.notes,
        questions=questions,
        topics=fiche_actuelle.topics,
        modifie_le=modifie_le,
    )

def controler_et_proposer_questions(
    fiche,
    *,
    controler: Callable,
    generer: Callable,
    inclure_notes: bool = False,
    inclure_questions: bool = False,
) -> dict:
    """Autorise la reformulation uniquement après un contrôle favorable."""
    try:
        messages_controle = preparer_controle_rendez_vous(
            fiche,
            inclure_notes=inclure_notes,
            inclure_questions=inclure_questions,
        )
    except PreparationRendezVousUrgente:
        return {
            "statut": "urgence_locale",
            "questions": (),
            "message": MESSAGE_URGENCE,
        }

    try:
        decision = lire_decision_preparation(
            controler(messages_controle)
        )
    except GenerationIndisponible:
        return {
            "statut": "controle_indisponible",
            "questions": (),
            "message": (
                "Le contrôle préalable est indisponible. Aucune reformulation n’a été effectuée."
            ),
        }
    except ValueError:
        return {
            "statut": "controle_invalide",
            "questions": (),
            "message": (
                "Le contrôle préalable n’a pas fourni de décision valide. Aucune reformulation n’a été effectuée."
            ),
        }

    if decision is DecisionPreparation.URGENCE:
        return {
            "statut": "urgence_detectee",
            "questions": (),
            "message": MESSAGE_URGENCE,
        }

    if decision is not DecisionPreparation.AUTORISEE:
        return {
            "statut": "preparation_non_autorisee",
            "questions": (),
            "message": (
                "Le contrôle préalable ne permet pas d’autoriser la préparation automatique. Votre fiche reste disponible pour une préparation manuelle."
            ),
        }

    return proposer_questions_rendez_vous(
        fiche,
        generer=generer,
        inclure_notes=inclure_notes,
        inclure_questions=inclure_questions,
    )

def controler_proposer_et_verifier_questions(
    fiche: Appointment,
    *,
    controler: Callable,
    generer: Callable,
    verifier_fidelite: Callable,
    inclure_notes: bool = False,
    inclure_questions: bool = False,
) -> dict:
    """Ne retourne une proposition que si le contrôle la juge fidèle."""
    choix = {
        "inclure_notes": inclure_notes,
        "inclure_questions": inclure_questions,
    }
    resultat = controler_et_proposer_questions(
        fiche,
        controler=controler,
        generer=generer,
        **choix,
    )

    if resultat["statut"] != "proposition_disponible":
        return resultat

    messages = preparer_messages_fidelite(
        preparer_contenu_ia(fiche, **choix),
        resultat["questions"],
    )

    try:
        verdict = lire_verdict_fidelite(verifier_fidelite(messages))
    except GenerationIndisponible:
        statut = "fidelite_indisponible"
    except ValueError:
        statut = "fidelite_invalide"
    else:
        if verdict is VerdictFidelite.FIDELE:
            return resultat
        statut = (
            "fidelite_indeterminee"
            if verdict is VerdictFidelite.INDETERMINE
            else "proposition_non_fidele"
        )

    return {
        "statut": statut,
        "questions": (),
        "message": (
            "La fidélité de la proposition n’a pas été confirmée. Votre fiche reste inchangée et vous pouvez la préparer manuellement."
        ),
    }