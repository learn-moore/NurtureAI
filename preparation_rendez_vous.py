from collections.abc import Callable
from datetime import datetime

from assistant_documentaire import GenerationIndisponible
from fiches_rendez_vous import (
    PreparationRendezVousUrgente,
    lire_proposition_questions,
    fusionner_questions_rendez_vous,
)
from intentions import MESSAGE_URGENCE
from messages_assistant import preparer_messages_rendez_vous
from modeles import Appointment, UserProfile


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