import json

from pathlib import Path
from urllib.parse import urlsplit
from datetime import date

CHAMPS_TEXTE_PASSAGE = (
    "id",
    "topic",
    "title",
    "content",
    "source",
    "url",
    "country",
)

THEMES_CORPUS = frozenset({
    "conception",
    "suivi_grossesse",
    "nutrition",
    "habitudes_de_vie",
    "medicaments",
    "signes_alerte",
})


def lire_date_passage(
    valeur: object,
    champ: str,
    *,
    nullable: bool = False,
) -> date | None:
    if valeur is None and nullable:
        return None

    if not isinstance(valeur, str):
        raise ValueError(f"Le champ {champ} doit respecter AAAA-MM-JJ.")

    try:
        resultat = date.fromisoformat(valeur)
    except ValueError as erreur:
        raise ValueError(
            f"Le champ {champ} doit respecter AAAA-MM-JJ."
        ) from erreur

    if resultat.isoformat() != valeur:
        raise ValueError(f"Le champ {champ} doit respecter AAAA-MM-JJ.")

    return resultat

def valider_passage(passage: dict) -> None:
    if not isinstance(passage, dict):
        raise ValueError("Un passage doit être un objet.")

    for champ in CHAMPS_TEXTE_PASSAGE:
        valeur = passage.get(champ)

        if not isinstance(valeur, str) or not valeur.strip():
            raise ValueError(f"Le champ {champ} doit contenir du texte.")

    if passage["id"] != passage["id"].strip():
        raise ValueError("L’identifiant ne doit pas avoir d’espaces aux extrémités.")

    if passage["topic"] not in THEMES_CORPUS:
        raise ValueError("Thème topic non pris en charge.")

    url = passage["url"]

    if any(caractere.isspace() or ord(caractere) < 32 for caractere in url):
        raise ValueError("L’URL de source contient des caractères interdits.")

    try:
        adresse = urlsplit(url)
        port = adresse.port
    except ValueError as erreur:
        raise ValueError("L’URL de source est invalide.") from erreur

    if (
        adresse.scheme != "https"
        or not adresse.hostname
        or adresse.username is not None
        or adresse.password is not None
        or port == 0
    ):
        raise ValueError("La source doit avoir une URL HTTPS valide sans identifiants.")

    for champ in ("publication_date", "retrieved_at", "reviewed_at"):
        if champ not in passage:
            raise ValueError(f"Le champ {champ} est obligatoire.")

    publication = lire_date_passage(
        passage["publication_date"],
        "publication_date",
        nullable=True,
    )
    consultation = lire_date_passage(
        passage["retrieved_at"],
        "retrieved_at",
    )
    revue = lire_date_passage(
        passage["reviewed_at"],
        "reviewed_at",
        nullable=True,
    )

    assert consultation is not None

    if publication is not None and publication > consultation:
        raise ValueError("La publication ne peut pas être postérieure à la consultation.")

    if revue is not None and revue < consultation:
        raise ValueError("La revue ne peut pas être antérieure à la consultation.")

    valeurs_autorisees = {
        "editorial_status": ("draft", "approved", "rejected"),
        "reuse_status": ("to_review", "approved", "rejected"),
        "usage": ("rag", "cross_check"),
    }

    for champ, valeurs in valeurs_autorisees.items():
        valeur = passage.get(champ)

        if not isinstance(valeur, str) or valeur not in valeurs:
            raise ValueError(f"Valeur invalide pour {champ}.")

    if passage["editorial_status"] == "approved" and revue is None:
        raise ValueError(
            "Un passage approuvé nécessite une date reviewed_at."
        )

def valider_corpus(passages: list[dict]) -> tuple[dict, ...]:
    if not isinstance(passages, list):
        raise ValueError("Le corpus doit être une liste de passages.")

    identifiants = set()

    for passage in passages:
        valider_passage(passage)

        identifiant = passage["id"]

        if identifiant in identifiants:
            raise ValueError(f"Identifiant de passage en double : {identifiant}.")

        identifiants.add(identifiant)

    return tuple(passages)

def charger_corpus(chemin: Path) -> tuple[dict, ...]:
    try:
        texte = chemin.read_text(encoding="utf-8")
        donnees = json.loads(texte)
    except (OSError, UnicodeError, json.JSONDecodeError) as erreur:
        raise ValueError(
            "Impossible de lire le corpus documentaire."
        ) from erreur

    champs = {"schema_version", "passages"}

    if not isinstance(donnees, dict) or set(donnees) != champs:
        raise ValueError("Structure du fichier de corpus invalide.")

    version = donnees["schema_version"]

    if type(version) is not int or version != 1:
        raise ValueError("Version du corpus non prise en charge.")

    return valider_corpus(donnees["passages"])

