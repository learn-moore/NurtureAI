import json
import re


class CitationInconnue(ValueError):
    """Signale une référence absente du contexte transmis."""

def extraire_citations(reponse: str) -> tuple[str, ...]:
    """Extrait les références entre crochets, sans doublons."""
    if not isinstance(reponse, str):
        raise ValueError("La réponse doit être un texte.")

    identifiants = re.findall(r"\[([^\[\]\r\n]+)\]", reponse)

    return tuple(dict.fromkeys(identifiants))


def trouver_citations_inconnues(
    reponse: str,
    contexte: str,
) -> tuple[str, ...]:
    """Repère les références absentes d'un contexte construit par l'application."""
    citations = extraire_citations(reponse)
    documents = json.loads(contexte)

    identifiants_autorises = {
        document["id"]
        for document in documents
    }

    return tuple(
        citation
        for citation in citations
        if citation not in identifiants_autorises
    )

def retrouver_sources_citees(
    reponse: str,
    contexte: str,
) -> tuple[dict[str, str], ...]:
    """Retrouve les métadonnées des sources citées dans le contexte."""
    inconnues = trouver_citations_inconnues(reponse, contexte)

    if inconnues:
        raise CitationInconnue(
            "Références absentes du contexte : "
            + ", ".join(inconnues)
        )

    documents = json.loads(contexte)
    documents_par_id = {
        document["id"]: document
        for document in documents
    }

    sources = []

    for identifiant in extraire_citations(reponse):
        document = documents_par_id[identifiant]

        source = {
            "id": document["id"],
            "title": document["title"],
            "source": document["source"],
            "url": document["url"],
        }

        for champ in ("source_version", "reuse_notice"):
            if champ in document:
                source[champ] = document[champ]

        sources.append(source)

    return tuple(sources)

