import json

from citations_documentaires import retrouver_sources_citees
from generation_simulee import generer_reponse_simulee
from messages_assistant import preparer_messages


def preparer_reponse_simulee(
    question: str,
    resultats: tuple[dict, ...],
    max_caracteres: int = 6000,
) -> dict:
    """Relie préparation, simulation et contrôle des références."""
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

    reponse = generer_reponse_simulee(messages)

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