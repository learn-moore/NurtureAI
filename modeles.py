from dataclasses import dataclass, field, replace
from datetime import date, datetime, timezone
from typing import Literal
from uuid import uuid4, UUID

from calculs import valider_durees_cycle

@dataclass(frozen=True)
class ConceptionJourney:
    last_period_date: date | None = None
    average_cycle_length: int = 28
    period_length: int = 5
    cycle_regularity: Literal["regular", "irregular", "unknown"] = "unknown"

    def __post_init__(self):
        valider_durees_cycle(
            self.average_cycle_length,
            self.period_length,
        )

        if self.cycle_regularity not in (
            "regular",
            "irregular",
            "unknown",
        ):
            raise ValueError("Régularité du cycle inconnue.")

@dataclass(frozen=True)
class PregnancyJourney:
    dating_method: Literal["last_period", "due_date"]
    last_period_date: date | None = None
    estimated_due_date: date | None = None
    term_reference_days: int | None = None
    dating_rule_version: str | None = None

    def __post_init__(self):
        if self.dating_method not in ("last_period", "due_date"):
            raise ValueError("Méthode de datation inconnue.")

        if (
            self.dating_method == "last_period"
            and self.last_period_date is None
        ):
            raise ValueError(
                "La date des dernières règles est requise."
            )

        if (
            self.dating_method == "due_date"
            and self.estimated_due_date is None
        ):
            raise ValueError(
                "La date prévue d’accouchement est requise."
            )

        if self.term_reference_days is None:
            if self.dating_rule_version is not None:
                raise ValueError("Une version de règle nécessite une durée de référence.")
        else:
            if (
                type(self.term_reference_days) is not int
                or self.term_reference_days not in (280, 287)
            ):
                raise ValueError("La durée de référence doit être 280 ou 287 jours.")

            if self.dating_rule_version != "sa-reference-v1":
                raise ValueError(
                    "Version de convention de datation non prise en charge."
                )

@dataclass(frozen=True)
class Journey:
    type: Literal["conception", "pregnancy"]
    start_date: date
    id: str = field(default_factory=lambda: str(uuid4()))
    status: Literal["active", "completed"] = "active"
    end_date: date | None = None
    details: ConceptionJourney | PregnancyJourney | None = None

    def __post_init__(self):
        if self.type not in ("conception", "pregnancy"):
            raise ValueError("Type de parcours inconnu.")

        if self.status not in ("active", "completed"):
            raise ValueError("Statut de parcours inconnu.")

        if self.status == "active" and self.end_date is not None:
            raise ValueError(
                "Un parcours actif ne peut pas avoir de date de fin."
            )

        if self.status == "completed" and self.end_date is None:
            raise ValueError(
                "Un parcours terminé doit avoir une date de fin."
            )

        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError(
                "La date de fin ne peut pas précéder la date de début."
            )

        if self.details is not None:
            if self.type == "conception":
                if not isinstance(self.details, ConceptionJourney):
                    raise ValueError(
                        "Un parcours conception nécessite des repères conception."
                    )
            else:
                if not isinstance(self.details, PregnancyJourney):
                    raise ValueError(
                        "Un parcours grossesse nécessite des repères grossesse."
                    )

    def terminer(self, end_date: date) -> "Journey":
        if self.status != "active":
            raise ValueError("Ce parcours est déjà terminé.")

        return replace(
            self,
            status="completed",
            end_date=end_date,
        )

    def renseigner_reperes(self, details: ConceptionJourney | PregnancyJourney,) -> "Journey":
        if self.status != "active":
            raise ValueError(
                "Les repères d’un parcours terminé ne sont pas modifiables."
            )

        if details is None:
            raise ValueError("Les repères sont requis.")

        return replace(self, details=details)

@dataclass(frozen=True)
class UserProfile:
    id: str = field(default_factory=lambda: str(uuid4()))
    journeys: tuple[Journey, ...] = ()
    active_journey_id: str | None = None
    appointments: "tuple[Appointment, ...]" = ()

    def __post_init__(self):
        identifiants = [parcours.id for parcours in self.journeys]

        if len(identifiants) != len(set(identifiants)):
            raise ValueError("Les identifiants des parcours doivent être uniques.")

        actifs = [parcours for parcours in self.journeys if parcours.status == "active"]

        if len(actifs) > 1:
            raise ValueError("Un seul parcours peut être actif.")

        if not actifs:
            if self.active_journey_id is not None:
                raise ValueError(
                    "Aucun parcours actif ne correspond à l'identifiant indiqué."
                )
        elif self.active_journey_id != actifs[0].id:
            raise ValueError(
                "L'identifiant actif doit désigner le parcours actif."
            )
        
        if not isinstance(self.appointments, tuple) or any(
            not isinstance(fiche, Appointment)
            for fiche in self.appointments
        ):
            raise ValueError(
                "Les rendez-vous doivent être un tuple de fiches."
            )

        ids_rendez_vous = [fiche.id for fiche in self.appointments]

        if len(ids_rendez_vous) != len(set(ids_rendez_vous)):
            raise ValueError(
                "Les identifiants des rendez-vous doivent être uniques."
            )

        if any(
            fiche.journey_id not in identifiants
            for fiche in self.appointments
        ):
            raise ValueError(
                "Chaque rendez-vous doit référencer un parcours existant."
            )

    def ajouter_rendez_vous(self, fiche: "Appointment") -> "UserProfile":
        return replace(
            self,
            appointments=self.appointments + (fiche,),
        )

    def demarrer_parcours(self, type_parcours: Literal["conception", "pregnancy"], start_date: date,) -> "UserProfile":
        if self.active_journey_id is not None:
            raise ValueError("Un parcours est déjà actif.")

        parcours = Journey(
            type=type_parcours,
            start_date=start_date,
        )

        return replace(
            self,
            journeys=self.journeys + (parcours,),
            active_journey_id=parcours.id,
        )

    def terminer_parcours_actif(self, end_date: date) -> "UserProfile":
        if self.active_journey_id is None:
            raise ValueError("Aucun parcours actif à terminer.")

        parcours_mis_a_jour = tuple(
            parcours.terminer(end_date)
            if parcours.id == self.active_journey_id
            else parcours
            for parcours in self.journeys
        )

        return replace(
            self,
            journeys=parcours_mis_a_jour,
            active_journey_id=None,
        )

    def changer_parcours(self, nouveau_type: Literal["conception", "pregnancy"], date_transition: date,) -> "UserProfile":
        profil_sans_parcours_actif = self.terminer_parcours_actif(date_transition)

        return profil_sans_parcours_actif.demarrer_parcours(
            nouveau_type,
            date_transition,
        )

    def renseigner_reperes_actifs(self, details: ConceptionJourney | PregnancyJourney,) -> "UserProfile":
        if self.active_journey_id is None:
            raise ValueError("Aucun parcours actif à renseigner.")

        parcours_mis_a_jour = tuple(
            parcours.renseigner_reperes(details)
            if parcours.id == self.active_journey_id
            else parcours
            for parcours in self.journeys
        )

        return replace(
            self,
            journeys=parcours_mis_a_jour,
        )

THEMES_RENDEZ_VOUS = (
    "nutrition",
    "physical_activity",
    "symptoms",
    "medications",
    "tests",
    "work",
    "travel",
    "childbirth",
    "other",
)

@dataclass(frozen=True)
class Appointment:
    journey_id: str
    appointment_type: Literal[
        "preconception",
        "follow_up",
        "ultrasound",
        "birth_preparation",
        "other",
    ] = "other"
    date: "date | None" = None
    id: str = field(default_factory=lambda: str(uuid4()))
    notes: str = ""
    questions: tuple[str, ...] = ()
    topics: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None

    def __post_init__(self):
        if self.appointment_type not in (
            "preconception",
            "follow_up",
            "ultrasound",
            "birth_preparation",
            "other",
        ):
            raise ValueError("Type de rendez-vous inconnu.")

        if self.date is not None and type(self.date) is not date:
            raise ValueError("La date du rendez-vous doit être une date ou None.")

        for identifiant in (self.id, self.journey_id):
            if not isinstance(identifiant, str):
                raise ValueError("Les identifiants doivent être des UUID textuels.")

            try:
                valide = str(UUID(identifiant)) == identifiant
            except ValueError:
                valide = False

            if not valide:
                raise ValueError("Les identifiants doivent être des UUID canoniques.")

        if not isinstance(self.notes, str) or len(self.notes) > 5000:
            raise ValueError(
                "Les notes doivent être un texte de 5 000 caractères maximum."
            )

        if not isinstance(self.questions, tuple) or len(self.questions) > 30:
            raise ValueError(
                "Les questions doivent être un tuple de 30 éléments maximum."
            )

        for question in self.questions:
            if (
                not isinstance(question, str)
                or not question.strip()
                or len(question) > 500
            ):
                raise ValueError(
                    "Chaque question doit être un texte non vide de 500 caractères maximum."
                )

        if not isinstance(self.topics, tuple):
            raise ValueError("Les thèmes doivent être un tuple.")

        if any(
            not isinstance(theme, str) or theme not in THEMES_RENDEZ_VOUS
            for theme in self.topics
        ):
            raise ValueError("Thème de rendez-vous inconnu.")

        if len(set(self.topics)) != len(self.topics):
            raise ValueError("Un thème ne peut être sélectionné qu’une seule fois.")

        if self.updated_at is None:
            object.__setattr__(self, "updated_at", self.created_at)

        for instant in (self.created_at, self.updated_at):
            if not isinstance(instant, datetime) or instant.utcoffset() is None:
                raise ValueError(
                    "Les horodatages doivent inclure un fuseau horaire."
                )

        if self.updated_at < self.created_at: # type: ignore
            raise ValueError(
                "La modification ne peut pas précéder la création."
            )

        