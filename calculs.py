from datetime import date, timedelta

def estimer_prochaines_regles(
        dernieres_regles: date, duree_cycle: int,
) -> date:
    return dernieres_regles + timedelta(days=duree_cycle)