import pytest
from datetime import date
from calculs import estimer_prochaines_regles, calculer_jour_cycle

def test_prochaines_regles_changement_annee():
    resultat = estimer_prochaines_regles(
        date(2026, 12, 20),
        28,
    )

    assert resultat == date(2027, 1, 17)

def test_premier_jour_cycle():
    resultat = calculer_jour_cycle(
        date(2026, 9, 12),
        date(2026, 9, 12),
    )

    assert resultat == 1


def test_jour_cycle_apres_plusieurs_jours():
    resultat = calculer_jour_cycle(
        date(2026, 9, 12),
        date(2026, 9, 23),
    )

    assert resultat == 12

def test_jour_cycle_refuse_une_date_future():
    with pytest.raises(ValueError):
        calculer_jour_cycle(
            date(2026, 9, 24),
            date(2026, 9, 23),
        )

@pytest.mark.parametrize("duree_cycle", [0, -1, -28])
def test_prochaines_regles_refuse_duree_non_positive(duree_cycle):
    with pytest.raises(ValueError):
        estimer_prochaines_regles(
            date(2026, 9, 12),
            duree_cycle,
        )