from datetime import date, timedelta

def estimer_prochaines_regles(
        dernieres_regles: date, duree_cycle: int,
) -> date:
    if duree_cycle <= 0:
        raise ValueError(
            "La durée du cycle doit être strictement positive."
        )
    return dernieres_regles + timedelta(days=duree_cycle)

def calculer_jour_cycle(
        dernieres_regles: date,
        date_reference: date,
) -> int:
    if dernieres_regles > date_reference:
        raise ValueError(
            "La date des dernières règles ne peut pas être postérieur à la date de référence."
        )
    return (date_reference - dernieres_regles).days + 1

def valider_durees_cycle(
    duree_cycle: int,
    duree_regles: int,
) -> None:
    if duree_cycle <= 0:
        raise ValueError("La durée du cycle doit être strictement positive.")

    if duree_regles <= 0:
        raise ValueError("La durée des règles doit être strictement positive.")

    if duree_regles > duree_cycle:
        raise ValueError(
            "La durée des règles ne peut pas dépasser la durée du cycle."
        )