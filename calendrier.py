from datetime import date
from calendar import Calendar
from dataclasses import dataclass
from typing import Literal

from modeles import Appointment, UserProfile, ConceptionJourney, PregnancyJourney
from calculs import estimer_dpa


def rendez_vous_du_mois(
    profil: UserProfile,
    journey_id: str,
    *,
    annee: int,
    mois: int,
) -> tuple[Appointment, ...]:
    if type(annee) is not int or type(mois) is not int:
        raise ValueError("L’année et le mois doivent être des entiers.")

    date(annee, mois, 1)

    if not any(
        journey.id == journey_id
        for journey in profil.journeys
    ):
        raise ValueError("Parcours introuvable.")

    return tuple(sorted(
        (
            fiche for fiche in profil.appointments
            if fiche.journey_id == journey_id
            and fiche.date is not None
            and fiche.date.year == annee
            and fiche.date.month == mois
        ),
        key=lambda fiche: fiche.date, # type: ignore
    )) # type: ignore

def decaler_mois(reference: date, decalage: int) -> date:
    """Renvoie le premier jour du mois obtenu après le décalage."""
    if type(reference) is not date:
        raise ValueError("La référence doit être une date.")

    if type(decalage) is not int:
        raise ValueError("Le décalage doit être un entier.")

    numero_mois = (
        (reference.year - 1) * 12
        + reference.month - 1
        + decalage
    )

    if not 0 <= numero_mois < 9999 * 12:
        raise ValueError(
            "Le mois demandé dépasse les dates prises en charge."
        )

    annee, mois = divmod(numero_mois, 12)

    return date(annee + 1, mois + 1, 1)

def construire_grille_mois(
    annee: int,
    mois: int,
) -> tuple[tuple[date | None, ...], ...]:
    """Construit des semaines du lundi au dimanche, sans dates hors mois."""
    if type(annee) is not int or type(mois) is not int:
        raise ValueError("L’année et le mois doivent être des entiers.")

    date(annee, mois, 1)

    semaines = Calendar(firstweekday=0).monthdayscalendar(
        annee,
        mois,
    )

    return tuple(
        tuple(
            date(annee, mois, jour) if jour != 0 else None
            for jour in semaine
        )
        for semaine in semaines
    )

@dataclass(frozen=True)
class EvenementCalendrier:
    jour: date
    libelle: str
    nature: Literal["declared", "estimated"]


def regles_du_mois(
    reperes: ConceptionJourney,
    *,
    annee: int,
    mois: int,
) -> tuple[EvenementCalendrier, ...]:
    grille = construire_grille_mois(annee, mois)

    if reperes.last_period_date is None:
        return ()

    evenements = []

    for semaine in grille:
        for jour in semaine:
            if jour is None:
                continue

            ecart = (jour - reperes.last_period_date).days

            if 0 <= ecart < reperes.period_length:
                evenements.append(
                    EvenementCalendrier(
                        jour=jour,
                        libelle=(
                            "Début des règles déclaré"
                            if ecart == 0
                            else "Jour de règles estimé"
                        ),
                        nature=(
                            "declared" if ecart == 0 else "estimated"
                        ),
                    )
                )

    return tuple(evenements)

def dpa_du_mois(
    reperes: PregnancyJourney,
    *,
    annee: int,
    mois: int,
) -> tuple[EvenementCalendrier, ...]:
    if type(annee) is not int or type(mois) is not int:
        raise ValueError("L’année et le mois doivent être des entiers.")

    date(annee, mois, 1)

    if reperes.dating_method == "due_date":
        dpa = reperes.estimated_due_date
        libelle = "DPA renseignée"
        nature = "declared"
    else:
        if (
            reperes.last_period_date is None
            or reperes.term_reference_days is None
        ):
            return ()

        dpa = estimer_dpa(
            reperes.last_period_date,
            terme_reference_jours=reperes.term_reference_days,
        )
        libelle = "DPA estimée"
        nature = "estimated"

    if dpa is None or (dpa.year, dpa.month) != (annee, mois):
        return ()

    return (
        EvenementCalendrier(
            jour=dpa,
            libelle=libelle,
            nature=nature,
        ),
    )

