from dataclasses import dataclass, field, replace
from datetime import date
from typing import Literal
from uuid import uuid4


@dataclass(frozen=True)
class Journey:
    type: Literal["conception", "pregnancy"]
    start_date: date
    id: str = field(default_factory=lambda: str(uuid4()))
    status: Literal["active", "completed"] = "active"
    end_date: date | None = None

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

    def terminer(self, end_date: date) -> "Journey":
        if self.status != "active":
            raise ValueError("Ce parcours est déjà terminé.")

        return replace(
            self,
            status="completed",
            end_date=end_date,
        )

@dataclass(frozen=True)
class UserProfile:
    id: str = field(default_factory=lambda: str(uuid4()))
    journeys: tuple[Journey, ...] = ()
    active_journey_id: str | None = None

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
