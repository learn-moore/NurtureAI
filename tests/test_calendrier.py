from datetime import date

import pytest

from calendrier import rendez_vous_du_mois, decaler_mois, construire_grille_mois, regles_du_mois, dpa_du_mois
from modeles import Appointment, Journey, UserProfile, ConceptionJourney, PregnancyJourney


@pytest.fixture
def profil_pour_calendrier():
    archive = Journey(
        type="conception",
        start_date=date(2026, 9, 1),
        status="completed",
        end_date=date(2026, 9, 28),
    )
    actif = Journey(
        type="pregnancy",
        start_date=date(2026, 9, 28),
    )

    fiches = tuple(
        Appointment(journey_id=archive.id, date=jour)
        for jour in (
            date(2026, 10, 31),
            date(2026, 9, 30),
            date(2026, 10, 1),
            date(2026, 11, 1),
            None,
            date(2025, 10, 15),
        )
    )
    autre = Appointment(
        journey_id=actif.id,
        date=date(2026, 10, 15),
    )

    profil = UserProfile(
        journeys=(archive, actif),
        active_journey_id=actif.id,
        appointments=fiches + (autre,),
    )

    return profil, archive.id


def test_calendrier_filtre_et_trie_sans_reactiver_archive(
    profil_pour_calendrier,
):
    profil, identifiant = profil_pour_calendrier

    resultat = rendez_vous_du_mois(
        profil,
        identifiant,
        annee=2026,
        mois=10,
    )

    assert resultat == (
        profil.appointments[2],
        profil.appointments[0],
    )
    assert profil.journeys[0].status == "completed"
    assert profil.active_journey_id == profil.journeys[1].id
    assert len(profil.appointments) == 7


def test_calendrier_mois_vide(profil_pour_calendrier):
    profil, identifiant = profil_pour_calendrier

    assert rendez_vous_du_mois(
        profil,
        identifiant,
        annee=2027,
        mois=1,
    ) == ()


@pytest.mark.parametrize(
    "annee, mois",
    [
        (2026, 0),
        (2026, 13),
        (2026, True),
        ("2026", 10),
        (0, 10),
    ],
)
def test_calendrier_refuse_mois_invalide(
    profil_pour_calendrier, annee, mois
):
    profil, identifiant = profil_pour_calendrier

    with pytest.raises(ValueError):
        rendez_vous_du_mois(
            profil,
            identifiant,
            annee=annee,
            mois=mois,
        )


def test_calendrier_refuse_parcours_absent(profil_pour_calendrier):
    profil, _ = profil_pour_calendrier

    with pytest.raises(ValueError, match="Parcours introuvable"):
        rendez_vous_du_mois(
            profil,
            "absent",
            annee=2026,
            mois=10,
        )

@pytest.mark.parametrize(
    "reference, decalage, attendu",
    [
        (date(2026, 12, 31), 1, date(2027, 1, 1)),
        (date(2027, 1, 31), -1, date(2026, 12, 1)),
        (date(2026, 1, 31), 1, date(2026, 2, 1)),
        (date(2028, 2, 29), 0, date(2028, 2, 1)),
    ],
)
def test_decaler_mois(reference, decalage, attendu):
    assert decaler_mois(reference, decalage) == attendu


@pytest.mark.parametrize(
    "reference, decalage",
    [
        (None, 1),
        (date(2026, 9, 1), True),
        (date(2026, 9, 1), 1.5),
        (date(2026, 9, 1), "1"),
    ],
)
def test_decaler_mois_refuse_entrees_invalides(reference, decalage):
    with pytest.raises(ValueError):
        decaler_mois(reference, decalage)


@pytest.mark.parametrize(
    "reference, decalage",
    [
        (date.min, -1),
        (date.max, 1),
    ],
)
def test_decaler_mois_refuse_depassement(reference, decalage):
    with pytest.raises(ValueError, match="dépasse"):
        decaler_mois(reference, decalage)

@pytest.mark.parametrize(
    "annee, mois, nombre_jours, nombre_semaines",
    [
        (2021, 2, 28, 4),
        (2028, 2, 29, 5),
        (2026, 8, 31, 6),
    ],
)
def test_grille_mois_complete_et_alignee(
    annee, mois, nombre_jours, nombre_semaines
):
    grille = construire_grille_mois(annee, mois)

    assert len(grille) == nombre_semaines
    assert all(len(semaine) == 7 for semaine in grille)

    jours = [
        jour
        for semaine in grille
        for jour in semaine
        if jour is not None
    ]

    assert jours == [
        date(annee, mois, numero)
        for numero in range(1, nombre_jours + 1)
    ]

    for semaine in grille:
        for colonne, jour in enumerate(semaine):
            if jour is not None:
                assert jour.weekday() == colonne


@pytest.mark.parametrize("annee, mois", [(1, 1), (9999, 12)])
def test_grille_supporte_dates_limites(annee, mois):
    grille = construire_grille_mois(annee, mois)

    jours = [
        jour
        for semaine in grille
        for jour in semaine
        if jour is not None
    ]

    assert jours[0] == date(annee, mois, 1)
    assert jours[-1] == date(annee, mois, 31)
    assert len(jours) == 31


@pytest.mark.parametrize(
    "annee, mois",
    [
        (True, 1),
        (2026, 0),
        (2026, 13),
        (0, 1),
    ],
)
def test_grille_refuse_periode_invalide(annee, mois):
    with pytest.raises(ValueError):
        construire_grille_mois(annee, mois)

@pytest.mark.parametrize(
    "mois, jours, natures",
    [
        (9, [30], ["declared"]),
        (10, [1, 2, 3, 4], ["estimated"] * 4),
    ],
)
def test_regles_reparties_sur_deux_mois(mois, jours, natures):
    reperes = ConceptionJourney(
        last_period_date=date(2026, 9, 30),
        period_length=5,
    )

    resultat = regles_du_mois(reperes, annee=2026, mois=mois)

    assert [e.jour for e in resultat] == [
        date(2026, mois, jour) for jour in jours
    ]
    assert [e.nature for e in resultat] == natures
    assert [e.libelle for e in resultat] == [
        "Début des règles déclaré"
        if nature == "declared"
        else "Jour de règles estimé"
        for nature in natures
    ]


def test_regles_sans_date_ne_produisent_aucun_evenement():
    assert regles_du_mois(
        ConceptionJourney(),
        annee=2026,
        mois=10,
    ) == ()


def test_regles_annee_bissextile():
    reperes = ConceptionJourney(
        last_period_date=date(2028, 2, 28),
        period_length=3,
    )

    resultat = regles_du_mois(reperes, annee=2028, mois=2)

    assert [e.jour for e in resultat] == [
        date(2028, 2, 28),
        date(2028, 2, 29),
    ]

    mars = regles_du_mois(reperes, annee=2028, mois=3)

    assert len(mars) == 1
    assert mars[0].jour == date(2028, 3, 1)
    assert mars[0].nature == "estimated"


def test_regles_ne_creent_pas_de_cycle_suivant():
    reperes = ConceptionJourney(
        last_period_date=date(2026, 9, 1),
        period_length=5,
    )

    assert regles_du_mois(
        reperes,
        annee=2026,
        mois=10,
    ) == ()

@pytest.mark.parametrize("terme", [None, 280, 287])
def test_calendrier_dpa_renseignee_prioritaire(terme):
    reperes = PregnancyJourney(
        dating_method="due_date",
        estimated_due_date=date(2026, 10, 20),
        last_period_date=date(2026, 1, 1),
        term_reference_days=terme,
        dating_rule_version=(
            "sa-reference-v1" if terme is not None else None
        ),
    )

    resultat = dpa_du_mois(reperes, annee=2026, mois=10)

    assert len(resultat) == 1
    assert resultat[0].jour == date(2026, 10, 20)
    assert resultat[0].libelle == "DPA renseignée"
    assert resultat[0].nature == "declared"
    assert reperes.estimated_due_date == date(2026, 10, 20)


@pytest.mark.parametrize("terme, jour", [(280, 8), (287, 15)])
def test_calendrier_dpa_estimee_selon_convention(terme, jour):
    reperes = PregnancyJourney(
        dating_method="last_period",
        last_period_date=date(2026, 1, 1),
        term_reference_days=terme,
        dating_rule_version="sa-reference-v1",
    )

    resultat = dpa_du_mois(reperes, annee=2026, mois=10)

    assert len(resultat) == 1
    assert resultat[0].jour == date(2026, 10, jour)
    assert resultat[0].libelle == "DPA estimée"
    assert resultat[0].nature == "estimated"
    assert reperes.estimated_due_date is None


def test_calendrier_dpa_non_estimee_sans_convention():
    reperes = PregnancyJourney(
        dating_method="last_period",
        last_period_date=date(2026, 1, 1),
    )

    assert dpa_du_mois(reperes, annee=2026, mois=10) == ()


def test_calendrier_dpa_hors_mois():
    reperes = PregnancyJourney(
        dating_method="due_date",
        estimated_due_date=date(2026, 10, 20),
    )

    assert dpa_du_mois(reperes, annee=2026, mois=11) == ()
    assert dpa_du_mois(reperes, annee=2027, mois=10) == ()

