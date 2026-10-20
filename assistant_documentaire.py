import json
from collections.abc import Callable

from citations_documentaires import retrouver_sources_citees
from generation_simulee import generer_reponse_simulee
from messages_assistant import preparer_messages
from intentions import Intention, autoriser_generation_documentaire, ClassificationIndisponible, reperer_declaration_urgence
from intentions import MESSAGE_URGENCE, VERSION_MESSAGE_URGENCE, MESSAGE_SITUATION_PERSONNELLE, MESSAGE_HORS_PERIMETRE, MESSAGE_DEMANDE_INDETERMINEE
from recherche_documentaire import rechercher_corpus


def preparer_reponse(
    question: str,
    resultats: tuple[dict, ...],
    max_caracteres: int = 6000,
    *,
    generer: Callable[[tuple[dict[str, str], ...]], str],
) -> dict:
    """Relie préparation, génération et contrôle des références."""
    messages = preparer_messages(
        question,
        resultats,
        max_caracteres=max_caracteres,
    )

    if not messages:
        return {
            "statut": "sans_contexte",
            "reponse": (
                "Aucun passage disponible dans le contexte "
                "pour préparer une réponse."
            ),
            "sources": (),
        }

    reponse = generer(messages)

    if not isinstance(reponse, str) or not reponse.strip():
        raise ValueError("La génération doit produire un texte non vide.")

    donnees = json.loads(messages[1]["content"])
    contexte_transmis = json.dumps(
        donnees["documents"],
        ensure_ascii=False,
    )

    sources = retrouver_sources_citees(
        reponse,
        contexte_transmis,
    )

    if not sources:
        return {
            "statut": "sans_citation",
            "reponse": reponse,
            "sources": (),
        }

    return {
        "statut": "references_controlees",
        "reponse": reponse,
        "sources": sources,
    }


def preparer_reponse_simulee(
    question: str,
    resultats: tuple[dict, ...],
    max_caracteres: int = 6000,
) -> dict:
    """Exécute la chaîne documentaire avec le générateur simulé."""
    return preparer_reponse(
        question,
        resultats,
        max_caracteres=max_caracteres,
        generer=generer_reponse_simulee,
    )

class GenerationIndisponible(RuntimeError):
    """Signale une indisponibilité attendue du service de génération."""

def preparer_reponse_selon_intention(
    question: str,
    resultats: tuple[dict, ...],
    max_caracteres: int = 6000,
    *,
    intention: Intention | None,
    generer: Callable[[tuple[dict[str, str], ...]], str],
) -> dict:
    """Contrôle l’intention avant d’accéder à la génération documentaire."""

    if intention is Intention.POTENTIAL_EMERGENCY:
        return {
            "statut": "urgence_potentielle",
            "reponse": MESSAGE_URGENCE,
            "sources": (),
            "version_message": VERSION_MESSAGE_URGENCE,
        }

    if not autoriser_generation_documentaire(intention):
        if intention is Intention.PERSONAL_MEDICAL_SITUATION:
            message = MESSAGE_SITUATION_PERSONNELLE
        elif intention is Intention.OUT_OF_SCOPE:
            message = MESSAGE_HORS_PERIMETRE
        else:
            message = MESSAGE_DEMANDE_INDETERMINEE

        return {
            "statut": "generation_non_autorisee",
            "reponse": message,
            "sources": (),
        }

    return preparer_reponse(
        question,
        resultats,
        max_caracteres=max_caracteres,
        generer=generer,
    )

def traiter_demande(
    question: str,
    corpus: tuple[dict, ...],
    *,
    classer: Callable[[str], Intention | None],
    generer: Callable[[tuple[dict[str, str], ...]], str],
    max_caracteres: int = 6000,
    urgence_signalee: bool = False,
) -> dict:
    """Traite le signalement d’urgence avant toute classification."""
    if type(urgence_signalee) is not bool:
        raise ValueError("Le signalement d’urgence doit être un booléen.")

    if urgence_signalee:
        return {
            "statut": "urgence_signalee",
            "reponse": MESSAGE_URGENCE,
            "sources": (),
            "version_message": VERSION_MESSAGE_URGENCE,
        }

    if not isinstance(question, str) or not question.strip():
        raise ValueError("La question doit être un texte non vide.")

    question = question.strip()

    if reperer_declaration_urgence(question):
        return preparer_reponse_selon_intention(
            question,
            (),
            intention=Intention.POTENTIAL_EMERGENCY,
            generer=generer,
        )

    try:
        intention = classer(question)
    except ClassificationIndisponible:
        return {
            "statut": "classification_indisponible",
            "reponse": (
                "La demande ne peut pas être orientée pour le moment. Aucune réponse automatique n’a été générée."
            ),
            "sources": (),
        }

    resultats = ()

    if autoriser_generation_documentaire(intention):
        resultats = rechercher_corpus(question, corpus)

    return preparer_reponse_selon_intention(
        question,
        resultats,
        max_caracteres=max_caracteres,
        intention=intention,
        generer=generer,
    )
