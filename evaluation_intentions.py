from collections.abc import Callable

from intentions import Intention, autoriser_generation_documentaire, ClassificationIndisponible, ClassificationInvalide


def evaluer_classifieur(
    cas: list[dict],
    *,
    classer: Callable[[str], Intention | None],
) -> tuple[dict, ...]:
    """Compare les intentions obtenues aux attentes du jeu d’évaluation."""
    evaluations = []

    for exemple in cas:
        valeur_attendue = exemple["intention_attendue"]
        attendu = (
            None
            if valeur_attendue is None
            else Intention(valeur_attendue)
        )

        try:
            obtenu = classer(exemple["question"])
        except (
            ClassificationIndisponible,
            ClassificationInvalide,
        ) as erreur:
            evaluations.append(
                {
                    "id": exemple["id"],
                    "attendu": (
                        attendu.value if attendu is not None else None
                    ),
                    "obtenu": None,
                    "conforme": False,
                    "generation_indument_autorisee": False,
                    "erreur": (
                        "classification_indisponible"
                        if isinstance(erreur, ClassificationIndisponible)
                        else "classification_invalide"
                    ),
                }
            )
            continue

        if obtenu is not None and not isinstance(obtenu, Intention):
            raise ValueError("Le classifieur doit retourner une Intention ou None.")

        evaluations.append(
            {
                "id": exemple["id"],
                "attendu": attendu.value if attendu is not None else None,
                "obtenu": obtenu.value if obtenu is not None else None,
                "conforme": obtenu is attendu,
                "generation_indument_autorisee": (
                    autoriser_generation_documentaire(obtenu)
                    and not autoriser_generation_documentaire(attendu)
                ),
                "erreur": None,
            }
        )

    return tuple(evaluations)