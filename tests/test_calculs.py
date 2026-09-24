import pytest
from datetime import date
from calculs import estimer_prochaines_regles, calculer_jour_cycle, valider_durees_cycle

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

@pytest.mark.parametrize(
    "duree_cycle, duree_regles",
    [(0, 5), (28, 0), (28, -1), (28, 29)],
)
def test_durees_invalides(duree_cycle, duree_regles):
    with pytest.raises(ValueError):
        valider_durees_cycle(duree_cycle, duree_regles)


def test_durees_valides():
    valider_durees_cycle(28, 5)


def test_duree_regles_egale_au_cycle():
    valider_durees_cycle(5, 5)

def test_prochaines_regles_annee_bissextile():
    resultat = estimer_prochaines_regles(
        date(2028, 2, 1),
        28,
    )

    assert resultat == date(2028, 2, 29)

def test_prochaines_regles_annee_non_bissextile():
    resultat = estimer_prochaines_regles(
        date(2027, 2, 1),
        28,
    )

    assert resultat == date(2027, 3, 1)

def test_jour_cycle_avec_29_fevrier():
    resultat = calculer_jour_cycle(
        date(2028, 2, 28),
        date(2028, 3, 1),
    )

    assert resultat == 3