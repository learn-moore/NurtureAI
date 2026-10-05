import json
from pathlib import Path
from urllib.parse import urlsplit

from timeline import valider_source_etape, valider_statut_editorial, valider_sources_secondaires, lire_date_editoriale

CHEMIN_FICHES = (
    Path(__file__).resolve().parent
    / "donnees"
    / "fiches_hebdomadaires.json"
)

def selectionner_fiche_semaine(
    fiches: tuple[dict, ...],
    jours_sa: int | None,
) -> dict | None:
    """Sélectionne une semaine SA révolue parmi des fiches déjà validées."""
    if jours_sa is None:
        return None

    if type(jours_sa) is not int or jours_sa < 0:
        raise ValueError("L’âge en jours SA doit être un entier positif ou nul.")

    semaine_sa = jours_sa // 7
    correspondances = [
        fiche for fiche in fiches
        if fiche["week_sa"] == semaine_sa
    ]

    if len(correspondances) > 1:
        raise ValueError("Plusieurs fiches correspondent à la même semaine SA.")

    return correspondances[0] if correspondances else None

def valider_attribution_fiche(fiche: dict) -> None:
    if "attribution" not in fiche:
        return

    attribution = fiche["attribution"]
    champs = {"mode", "text", "url"}

    if not isinstance(attribution, dict) or set(attribution) != champs:
        raise ValueError("Structure d’attribution invalide.")

    if attribution["mode"] not in ("licence", "reference"):
        raise ValueError("Mode d’attribution inconnu.")

    texte = attribution["text"]
    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("L’attribution doit contenir du texte.")

    url = attribution["url"]
    if not isinstance(url, str):
        raise ValueError("L’URL d’attribution doit être du texte.")

    adresse = urlsplit(url)

    if (
        adresse.scheme != "https"
        or not adresse.hostname
        or adresse.username is not None
        or adresse.password is not None
        or any(caractere.isspace() for caractere in url)
    ):
        raise ValueError(
            "L’attribution doit avoir une URL HTTPS sans identifiants."
        )

def fiche_hebdomadaire_affichable(fiche: dict) -> bool:
    if not isinstance(fiche, dict):
        raise ValueError("Une fiche doit être un objet.")

    for champ in ("id", "title", "body"):
        valeur = fiche.get(champ)

        if not isinstance(valeur, str) or not valeur.strip():
            raise ValueError(f"Le champ {champ} doit contenir du texte.")

    if fiche["id"] != fiche["id"].strip():
        raise ValueError("L’identifiant ne doit pas avoir d’espaces aux extrémités.")

    semaine = fiche.get("week_sa")

    if type(semaine) is not int or semaine < 0:
        raise ValueError("La semaine SA doit être un entier positif ou nul.")

    valider_statut_editorial(fiche)
    valider_source_etape(fiche)
    valider_sources_secondaires(fiche)
    valider_attribution_fiche(fiche)

    return (
        fiche["editorial_status"] == "approved"
        and fiche["source"]["reuse_status"] == "approved"
        and fiche["reviewed_at"] is not None
    )

def charger_fiches_hebdomadaires(
    chemin: Path = CHEMIN_FICHES,
) -> tuple[dict, ...]:
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as erreur:
        raise ValueError(
            "Impossible de lire les fiches hebdomadaires."
        ) from erreur

    champs = {"schema_version", "content_version", "fiches"}
    if not isinstance(donnees, dict) or set(donnees) != champs:
        raise ValueError("Structure du fichier de fiches invalide.")

    version = donnees["schema_version"]
    if type(version) is not int or version != 1:
        raise ValueError("Version du format de fiches non prise en charge.")

    lire_date_editoriale(
        donnees["content_version"], "content_version"
    )

    if not isinstance(donnees["fiches"], list):
        raise ValueError("Les fiches doivent être une liste.")

    identifiants = set()
    semaines = set()
    affichables = []

    for fiche in donnees["fiches"]:
        afficher = fiche_hebdomadaire_affichable(fiche)
        identifiant = fiche["id"]
        semaine = fiche["week_sa"]

        if identifiant in identifiants or semaine in semaines:
            raise ValueError("Identifiant ou semaine SA en double.")

        identifiants.add(identifiant)
        semaines.add(semaine)

        if afficher:
            affichables.append(fiche)

    return tuple(
        sorted(affichables, key=lambda fiche: fiche["week_sa"])
    )

