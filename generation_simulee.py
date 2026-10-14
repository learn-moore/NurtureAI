import json


def generer_reponse_simulee(
    messages: tuple[dict[str, str], ...],
) -> str:
    """Produit une réponse déterministe depuis les messages du laboratoire."""
    if not messages:
        raise ValueError("La génération simulée nécessite des messages.")

    donnees = json.loads(messages[1]["content"])
    documents = donnees["documents"]

    if not documents:
        raise ValueError("La génération simulée nécessite un document.")

    premier_document = documents[0]

    return (
        "Démonstration sur un corpus fictif.\n\n"
        f"{premier_document['content']} "
        f"[{premier_document['id']}]"
    )