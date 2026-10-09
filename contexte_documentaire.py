import json


def construire_contexte(
    resultats: tuple[dict, ...],
    max_caracteres: int = 6000,
) -> str:
    """Prépare un contexte JSON à partir de résultats déjà contrôlés."""
    if type(max_caracteres) is not int or max_caracteres < 2:
        raise ValueError("La taille maximale doit être un entier supérieur ou égal à 2.")

    documents = []
    contexte = "[]"

    for resultat in resultats:
        passage = resultat["passage"]

        document = {
            "id": passage["id"],
            "title": passage["title"],
            "content": passage["content"],
            "source": passage["source"],
            "url": passage["url"],
        }

        candidat = json.dumps(
            [*documents, document],
            ensure_ascii=False,
        )

        if len(candidat) > max_caracteres:
            break

        documents.append(document)
        contexte = candidat

    return contexte