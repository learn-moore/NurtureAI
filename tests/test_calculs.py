import pytest
from datetime import date, timedelta
from calculs import estimer_prochaines_regles, calculer_jour_cycle, valider_durees_cycle
from calculs import calculer_age_depuis_dernieres_regles, estimer_semaines_grossesse, calculer_age_depuis_dpa
from calculs import determiner_trimestre, calculer_progression_grossesse, estimer_dpa

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

@pytest.mark.parametrize(
    "date_reference, resultat_attendu",
    [
        (date(2026, 7, 20), (0, 0)),
        (date(2026, 7, 26), (0, 6)),
        (date(2026, 7, 27), (1, 0)),
        (date(2026, 9, 23), (9, 2)),
    ],
)
def test_age_depuis_dernieres_regles(date_reference, resultat_attendu):
    resultat = calculer_age_depuis_dernieres_regles(
        date(2026, 7, 20),
        date_reference,
    )

    assert resultat == resultat_attendu


def test_age_depuis_dernieres_regles_refuse_date_future():
    with pytest.raises(ValueError):
        calculer_age_depuis_dernieres_regles(
            date(2026, 9, 24),
            date(2026, 9, 23),
        )

@pytest.mark.parametrize(
    "jours_ecoules, attendu",
    [
        (0, None),
        (13, None),
        (14, (0, 0)),
        (20, (0, 6)),
        (21, (1, 0)),
        (65, (7, 2)),
    ],
)
def test_estimation_semaines_grossesse(jours_ecoules, attendu):
    dernieres_regles = date(2026, 7, 20)
    date_reference = dernieres_regles + timedelta(
        days=jours_ecoules
    )

    resultat = estimer_semaines_grossesse(
        dernieres_regles,
        date_reference,
    )

    assert resultat == attendu


def test_estimation_sg_refuse_date_future():
    with pytest.raises(ValueError):
        estimer_semaines_grossesse(
            date(2026, 9, 24),
            date(2026, 9, 23),
        )

@pytest.mark.parametrize(
    "jours_avant_dpa, attendu",
    [
        (287, (0, 0)),
        (286, (0, 1)),
        (222, (9, 2)),
        (0, (41, 0)),
        (-1, (41, 1)),
    ],
)
def test_age_depuis_dpa(jours_avant_dpa, attendu):
    dpa = date(2027, 4, 1)
    date_reference = dpa - timedelta(days=jours_avant_dpa)

    resultat = calculer_age_depuis_dpa(
        dpa,
        date_reference,
        terme_reference_jours=287,
    )

    assert resultat == attendu


def test_age_depuis_dpa_respecte_la_convention():
    dpa = date(2027, 4, 1)

    assert calculer_age_depuis_dpa(
        dpa,
        dpa,
        terme_reference_jours=280,
    ) == (40, 0)


def test_age_depuis_dpa_refuse_age_negatif():
    dpa = date(2027, 4, 1)

    with pytest.raises(ValueError):
        calculer_age_depuis_dpa(
            dpa,
            dpa - timedelta(days=288),
            terme_reference_jours=287,
        )


@pytest.mark.parametrize("duree", [0, -1, True, 280.0])
def test_age_depuis_dpa_refuse_duree_invalide(duree):
    with pytest.raises(ValueError):
        calculer_age_depuis_dpa(
            date(2027, 4, 1),
            date(2027, 4, 1),
            terme_reference_jours=duree,
        )

@pytest.mark.parametrize(
    "jours_sa, attendu",
    [
        (0, 1),
        (97, 1),    # 13 SA + 6 jours
        (98, 2),    # 14 SA
        (195, 2),   # 27 SA + 6 jours
        (196, 3),   # 28 SA
        (287, 3),   # Aucun quatrième trimestre automatique
    ],
)
def test_trimestre_limites(jours_sa, attendu):
    resultat = determiner_trimestre(
        jours_sa,
        debut_deuxieme=14 * 7,
        debut_troisieme=28 * 7,
    )

    assert resultat == attendu


@pytest.mark.parametrize(
    "age, deuxieme, troisieme",
    [
        (-1, 98, 196),
        (True, 98, 196),
        (98.0, 98, 196),
        (0, 0, 196),
        (0, 196, 98),
        (0, 98, 98),
        (0, "98", 196),
    ],
)
def test_trimestre_refuse_entrees_invalides(age, deuxieme, troisieme):
    with pytest.raises(ValueError):
        determiner_trimestre(
            age,
            debut_deuxieme=deuxieme,
            debut_troisieme=troisieme,
        )

@pytest.mark.parametrize(
    "jours_sa, terme, attendu",
    [
        (0, 280, 0.0),
        (140, 280, 0.5),
        (280, 280, 1.0),
        (290, 280, 1.0),
        (140, 287, 140 / 287),
    ],
)
def test_progression_grossesse_bornee(jours_sa, terme, attendu):
    resultat = calculer_progression_grossesse(
        jours_sa,
        terme_reference_jours=terme,
    )

    assert resultat == pytest.approx(attendu)


@pytest.mark.parametrize(
    "jours_sa, terme",
    [
        (-1, 280),
        (10, 0),
        (10, -280),
        (True, 280),
        (10, True),
        (10.5, 280),
        (10, "280"),
    ],
)
def test_progression_grossesse_refuse_entrees_invalides(jours_sa, terme):
    with pytest.raises(ValueError):
        calculer_progression_grossesse(
            jours_sa,
            terme_reference_jours=terme,
        )

@pytest.mark.parametrize(
    "dernieres_regles, terme, attendu",
    [
        (date(2026, 1, 1), 280, date(2026, 10, 8)),
        (date(2026, 1, 1), 287, date(2026, 10, 15)),
        (date(2027, 12, 1), 280, date(2028, 9, 6)),
    ],
)
def test_estimation_dpa(dernieres_regles, terme, attendu):
    resultat = estimer_dpa(
        dernieres_regles,
        terme_reference_jours=terme,
    )

    assert resultat == attendu


@pytest.mark.parametrize("terme", [0, -1, True, 280.0, "280"])
def test_estimation_dpa_refuse_duree_invalide(terme):
    with pytest.raises(ValueError):
        estimer_dpa(
            date(2026, 1, 1),
            terme_reference_jours=terme,
        )


@pytest.mark.parametrize("terme", [280, 287])
def test_dpa_estimee_et_age_sa_coherents(terme):
    dernieres_regles = date(2026, 1, 1)

    dpa = estimer_dpa(
        dernieres_regles,
        terme_reference_jours=terme,
    )

    age_sa = calculer_age_depuis_dpa(
        dpa,
        date(2026, 3, 7),
        terme_reference_jours=terme,
    )

    assert age_sa == (9, 2)

