import json
from dataclasses import asdict
from datetime import date, datetime, timezone
from uuid import UUID

from modeles import UserProfile, ConceptionJourney, PregnancyJourney, Journey

def convertir_date(valeur):
    if isinstance(valeur, date):
        return valeur.isoformat()

    raise TypeError(f"Type non pris en charge pour l'export : {type(valeur).__name__}")

def exporter_profil(profil: UserProfile) -> str:
    donnees = {
        "schema_version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "profil": asdict(profil),
    }

    return json.dumps(
        donnees,
        default=convertir_date,
        ensure_ascii=False,
        indent=2,
    )

def importer_profil(texte: str) -> UserProfile:
    export = lire_export(texte)
    donnees = export["profil"]

    champs_attendus = {
        "id",
        "journeys",
        "active_journey_id",
    }

    if set(donnees) != champs_attendus:
        raise ValueError("Les champs du profil sont incomplets ou inconnus.")

    if not isinstance(donnees["journeys"], list):
        raise ValueError("Les parcours doivent être une liste.")

    identifiant_actif = donnees["active_journey_id"]

    if identifiant_actif is not None:
        identifiant_actif = lire_identifiant(
            identifiant_actif,
            "active_journey_id",
        )

    parcours = tuple(
        lire_parcours(element)
        for element in donnees["journeys"]
    )

    return UserProfile(
        id=lire_identifiant(donnees["id"], "id"),
        journeys=parcours,
        active_journey_id=identifiant_actif,
    )

def lire_export(texte: str) -> dict:
    try:
        donnees = json.loads(texte)
    except json.JSONDecodeError as erreur:
        raise ValueError("Le fichier ne contient pas un JSON valide.") from erreur

    if not isinstance(donnees, dict):
        raise ValueError("L’export doit contenir un objet JSON.")

    version = donnees.get("schema_version")

    if type(version) is not int or version != 1:
        raise ValueError("Version d’export non prise en charge.")

    if not isinstance(donnees.get("profil"), dict):
        raise ValueError("Le profil est absent ou invalide.")

    if "exported_at" in donnees:
        horodatage = donnees["exported_at"]

        if not isinstance(horodatage, str):
            raise ValueError("La date d’export doit être du texte.")

        try:
            date_export = datetime.fromisoformat(horodatage)
        except ValueError as erreur:
            raise ValueError("La date d’export est invalide.") from erreur

        if date_export.tzinfo is None:
            raise ValueError("La date d’export doit préciser son fuseau horaire.")

    return donnees

def lire_date(valeur: object, nom_champ: str, obligatoire: bool = True,) -> date | None:
    if valeur is None:
        if obligatoire:
            raise ValueError(f"Le champ {nom_champ} est obligatoire.")
        return None

    if not isinstance(valeur, str):
        raise ValueError(
            f"Le champ {nom_champ} doit être une date au format YYYY-MM-DD."
        )

    try:
        resultat = date.fromisoformat(valeur)
    except ValueError as erreur:
        raise ValueError(
            f"Le champ {nom_champ} contient une date invalide."
        ) from erreur

    if resultat.isoformat() != valeur:
        raise ValueError(
            f"Le champ {nom_champ} doit respecter le format YYYY-MM-DD."
        )

    return resultat

def lire_reperes_conception(donnees: object) -> ConceptionJourney:
    if not isinstance(donnees, dict):
        raise ValueError("Les repères conception doivent être un objet JSON.")

    champs_attendus = {
        "last_period_date",
        "average_cycle_length",
        "period_length",
        "cycle_regularity",
    }

    if set(donnees) != champs_attendus:
        raise ValueError(
            "Les champs des repères conception sont incomplets ou inconnus."
        )

    for champ in ("average_cycle_length", "period_length"):
        if type(donnees[champ]) is not int:
            raise ValueError(f"Le champ {champ} doit être un entier.")

    if not isinstance(donnees["cycle_regularity"], str):
        raise ValueError("La régularité du cycle doit être du texte.")

    return ConceptionJourney(
        last_period_date=lire_date(
            donnees["last_period_date"],
            "last_period_date",
            obligatoire=False,
        ),
        average_cycle_length=donnees["average_cycle_length"],
        period_length=donnees["period_length"],
        cycle_regularity=donnees["cycle_regularity"], # type: ignore
    )

def lire_reperes_grossesse(donnees: object) -> PregnancyJourney:
    if not isinstance(donnees, dict):
        raise ValueError("Les repères grossesse doivent être un objet JSON.")

    champs_attendus = {
        "dating_method",
        "last_period_date",
        "estimated_due_date",
    }

    if set(donnees) != champs_attendus:
        raise ValueError(
            "Les champs des repères grossesse sont incomplets ou inconnus."
        )

    if not isinstance(donnees["dating_method"], str):
        raise ValueError("La méthode de datation doit être du texte.")

    return PregnancyJourney(
        dating_method=donnees["dating_method"], # type: ignore
        last_period_date=lire_date(
            donnees["last_period_date"],
            "last_period_date",
            obligatoire=False,
        ),
        estimated_due_date=lire_date(
            donnees["estimated_due_date"],
            "estimated_due_date",
            obligatoire=False,
        ),
    )

def lire_identifiant(valeur: object, nom_champ: str) -> str:
    if not isinstance(valeur, str):
        raise ValueError(f"Le champ {nom_champ} doit être un UUID.")

    try:
        identifiant = UUID(valeur)
    except ValueError as erreur:
        raise ValueError(
            f"Le champ {nom_champ} contient un UUID invalide."
        ) from erreur

    if str(identifiant) != valeur:
        raise ValueError(
            f"Le champ {nom_champ} doit utiliser le format UUID standard."
        )

    return valeur


def lire_parcours(donnees: object) -> Journey:
    if not isinstance(donnees, dict):
        raise ValueError("Un parcours doit être un objet JSON.")

    champs_attendus = {
        "id",
        "type",
        "status",
        "start_date",
        "end_date",
        "details",
    }

    if set(donnees) != champs_attendus:
        raise ValueError("Les champs du parcours sont incomplets ou inconnus.")

    if donnees["type"] not in ("conception", "pregnancy"):
        raise ValueError("Type de parcours inconnu.")

    if donnees["status"] not in ("active", "completed"):
        raise ValueError("Statut de parcours inconnu.")

    details = None

    if donnees["details"] is not None:
        if donnees["type"] == "conception":
            details = lire_reperes_conception(donnees["details"])
        else:
            details = lire_reperes_grossesse(donnees["details"])

    return Journey(
        id=lire_identifiant(donnees["id"], "id"),
        type=donnees["type"],
        status=donnees["status"],
        start_date=lire_date(donnees["start_date"], "start_date"), # type: ignore
        end_date=lire_date(
            donnees["end_date"],
            "end_date",
            obligatoire=False,
        ),
        details=details,
    )

