import json
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from modeles import PregnancyJourney
from calculs import calculer_age_depuis_dernieres_regles, calculer_age_depuis_dpa

CHEMIN_TIMELINE = (
    Path(__file__).resolve().parent
    / "donnees"
    / "timeline_grossesse.json"
)

def charger_timeline(chemin: Path = CHEMIN_TIMELINE) -> dict:
    try:
        texte = chemin.read_text(encoding="utf-8")
        donnees = json.loads(texte)
    except (OSError, UnicodeError, json.JSONDecodeError) as erreur:
        raise ValueError(
            "Impossible de lire le fichier de timeline."
        ) from erreur

    champs = {"schema_version", "content_version", "etapes"}
    if not isinstance(donnees, dict) or set(donnees) != champs:
        raise ValueError("Structure de timeline invalide.")

    version = donnees["schema_version"]
    if type(version) is not int or version != 1:
        raise ValueError(
            "Version du format de timeline non prise en charge."
        )

    version_contenu = donnees["content_version"]
    if not isinstance(version_contenu, str):
        raise ValueError(
            "La version du contenu doit être une date ISO."
        )

    try:
        date_version = date.fromisoformat(version_contenu)
    except ValueError as erreur:
        raise ValueError(
            "La version du contenu doit être une date ISO."
        ) from erreur

    if date_version.isoformat() != version_contenu:
        raise ValueError(
            "La version du contenu doit respecter AAAA-MM-JJ."
        )

    etapes = donnees["etapes"]
    if not isinstance(etapes, list) or any(
        not isinstance(etape, dict) for etape in etapes
    ):
        raise ValueError(
            "Les étapes doivent être une liste d’objets."
        )

    identifiants = set()

    for etape in etapes:
        valider_statut_editorial(etape)
        valider_texte_etape(etape)
        valider_source_etape(etape)
        valider_fenetre_timeline(etape.get("window"))

        identifiant = etape["id"]

        if identifiant in identifiants:
            raise ValueError(
                f"Identifiant de timeline dupliqué : {identifiant}"
            )

        identifiants.add(identifiant)

    return donnees

def valider_fenetre_timeline(fenetre: object) -> None:
    champs = {"unit", "start", "end", "bounds"}

    if not isinstance(fenetre, dict) or set(fenetre) != champs:
        raise ValueError(
            "Structure de fenêtre de timeline invalide."
        )

    if fenetre["unit"] != "days_sa":
        raise ValueError(
            "La fenêtre doit être exprimée en jours SA."
        )

    if fenetre["bounds"] != "inclusive":
        raise ValueError(
            "Les bornes de la fenêtre doivent être inclusives."
        )

    debut = fenetre["start"]
    fin = fenetre["end"]

    if type(debut) is not int or type(fin) is not int:
        raise ValueError(
            "Les bornes de la fenêtre doivent être des entiers."
        )

    if not 0 <= debut <= fin:
        raise ValueError(
            "La fenêtre doit respecter 0 <= début <= fin."
        )

def valider_texte_etape(etape: dict) -> None:
    for champ in ("id", "title", "when", "why", "how"):
        valeur = etape.get(champ)

        if not isinstance(valeur, str) or not valeur.strip():
            raise ValueError(
                f"Le champ {champ} doit contenir du texte."
            )

    if etape["id"] != etape["id"].strip():
        raise ValueError(
            "L’identifiant ne doit pas commencer ou finir par des espaces."
        )

    questions = etape.get("questions")

    if not isinstance(questions, list) or not questions:
        raise ValueError(
            "La fiche doit contenir une liste non vide de questions."
        )

    if any(
        not isinstance(question, str) or not question.strip()
        for question in questions
    ):
        raise ValueError(
            "Chaque question doit contenir du texte."
        )

def lire_date_editoriale(
    valeur: object,
    champ: str,
    *,
    facultative: bool = False,
) -> date | None:
    if valeur is None and facultative:
        return None

    if not isinstance(valeur, str):
        raise ValueError(
            f"Le champ {champ} doit être une date ISO."
        )

    try:
        resultat = date.fromisoformat(valeur)
    except ValueError as erreur:
        raise ValueError(
            f"Date invalide pour {champ}."
        ) from erreur

    if resultat.isoformat() != valeur:
        raise ValueError(
            f"Le champ {champ} doit respecter AAAA-MM-JJ."
        )

    return resultat


def valider_source_etape(etape: dict) -> None:
    source = etape.get("source")
    champs = {
        "name", "title", "url", "section",
        "publication_date", "displayed_date",
        "retrieved_at", "reuse_status",
    }

    if not isinstance(source, dict) or set(source) != champs:
        raise ValueError("Structure de source invalide.")

    for champ in ("name", "title", "section", "url"):
        valeur = source[champ]

        if not isinstance(valeur, str) or not valeur.strip():
            raise ValueError(
                f"Le champ source.{champ} doit contenir du texte."
            )

    url = source["url"]
    adresse = urlsplit(url)

    if (
        any(caractere.isspace() for caractere in url)
        or adresse.scheme != "https"
        or not adresse.hostname
        or adresse.username is not None
        or adresse.password is not None
    ):
        raise ValueError(
            "La source doit avoir une URL HTTPS sans identifiants."
        )

    if source["reuse_status"] not in (
        "to_review", "approved", "rejected"
    ):
        raise ValueError(
            "Statut de réutilisation de source inconnu."
        )

    consultation = lire_date_editoriale(
        source["retrieved_at"],
        "retrieved_at",
    )
    assert consultation is not None

    for champ in ("publication_date", "displayed_date"):
        valeur = lire_date_editoriale(
            source[champ],
            champ,
            facultative=True,
        )

        if valeur is not None and valeur > consultation:
            raise ValueError(
                f"{champ} ne peut pas suivre la consultation de la source."
            )

    if "reviewed_at" not in etape:
        raise ValueError(
            "Le champ reviewed_at est obligatoire, même s’il vaut null."
        )

    revue = lire_date_editoriale(
        etape["reviewed_at"],
        "reviewed_at",
        facultative=True,
    )

    if revue is not None and revue < consultation:
        raise ValueError(
            "La revue ne peut pas précéder la consultation de la source."
        )

def valider_statut_editorial(etape: dict) -> None:
    if etape.get("editorial_status") not in (
        "draft", "approved", "rejected"
    ):
        raise ValueError(
            "Statut éditorial de timeline inconnu."
        )


def charger_etapes_affichables(
    chemin: Path = CHEMIN_TIMELINE,
) -> tuple[dict, ...]:
    donnees = charger_timeline(chemin)

    return tuple(
        etape
        for etape in donnees["etapes"]
        if etape["editorial_status"] == "approved"
        and etape["source"]["reuse_status"] == "approved"
        and etape["reviewed_at"] is not None
    )

def situer_fenetre_timeline(
    fenetre: dict,
    jours_sa: int | None,
) -> str:
    valider_fenetre_timeline(fenetre)

    if jours_sa is None:
        return "unknown"

    if type(jours_sa) is not int or jours_sa < 0:
        raise ValueError(
            "L’âge en jours SA doit être un entier positif ou nul."
        )

    if jours_sa < fenetre["start"]:
        return "upcoming"

    if jours_sa <= fenetre["end"]:
        return "current"

    return "past"

def calculer_jours_sa_timeline(
    reperes: PregnancyJourney | None,
    date_reference: date,
) -> int | None:
    if type(date_reference) is not date:
        raise ValueError(
            "La date de référence doit être une date."
        )

    if reperes is None:
        return None

    if reperes.dating_method == "last_period":
        origine = reperes.last_period_date

        if type(origine) is not date:
            raise ValueError(
                "La date des dernières règles est invalide."
            )

        semaines, jours = calculer_age_depuis_dernieres_regles(
            origine,
            date_reference,
        )
    else:
        dpa = reperes.estimated_due_date

        if type(dpa) is not date:
            raise ValueError("La DPA est invalide.")

        if reperes.term_reference_days is None:
            return None

        semaines, jours = calculer_age_depuis_dpa(
            dpa,
            date_reference,
            terme_reference_jours=reperes.term_reference_days,
        )

    return semaines * 7 + jours

def construire_timeline(
    reperes: PregnancyJourney | None,
    date_reference: date,
    *,
    chemin: Path = CHEMIN_TIMELINE,
) -> tuple[dict, ...]:
    jours_sa = calculer_jours_sa_timeline(
        reperes,
        date_reference,
    )
    etapes = charger_etapes_affichables(chemin)

    etapes_triees = sorted(
        etapes,
        key=lambda etape: (
            etape["window"]["start"],
            etape["window"]["end"],
            etape["id"],
        ),
    )

    return tuple(
        {
            "etape": etape,
            "position": situer_fenetre_timeline(
                etape["window"],
                jours_sa,
            ),
        }
        for etape in etapes_triees
    )

