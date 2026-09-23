from datetime import date
from calculs import estimer_prochaines_regles

def test_prochaines_regles_changement_annee():
    resultat = estimer_prochaines_regles(
        date(2026, 12, 20),
        28,
    )

    assert resultat == date(2027, 1, 17)