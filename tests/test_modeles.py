import pytest
from datetime import date
from dataclasses import FrozenInstanceError

from modeles import Journey, UserProfile, ConceptionJourney, PregnancyJourney

def test_nouveau_parcours_actif_sans_date_fin():
    parcours = Journey(
        type="conception",
        start_date=date(2026, 9, 24),
    )

    assert parcours.type == "conception"
    assert parcours.start_date == date(2026, 9, 24)
    assert parcours.status == "active"
    assert parcours.end_date is None


def test_deux_parcours_ont_des_identifiants_distincts():
    premier = Journey(
        type="conception",
        start_date=date(2026, 9, 24),
    )
    second = Journey(
        type="pregnancy",
        start_date=date(2026, 10, 15),
    )

    assert premier.id != second.id

@pytest.mark.parametrize(
    "modifications",
    [
        {"type": "inconnu"},
        {"status": "inconnu"},
        {"end_date": date(2026, 9, 25)},
        {"status": "completed"},
        {
            "status": "completed",
            "end_date": date(2026, 9, 23),
        },
    ],
)
def test_parcours_incoherent_refuse(modifications):
    donnees = {
        "type": "conception",
        "start_date": date(2026, 9, 24),
    }
    donnees.update(modifications)

    with pytest.raises(ValueError):
        Journey(**donnees)


def test_parcours_termine_le_jour_de_son_debut():
    parcours = Journey(
        type="conception",
        start_date=date(2026, 9, 24),
        status="completed",
        end_date=date(2026, 9, 24),
    )

    assert parcours.status == "completed"
    assert parcours.end_date == parcours.start_date

def test_modification_directe_interdite():
    parcours = Journey(
        type="conception",
        start_date=date(2026, 9, 24),
    )

    with pytest.raises(FrozenInstanceError):
        parcours.status = "completed" # type: ignore


def test_terminer_conserve_identifiant_et_objet_initial():
    parcours = Journey(
        type="conception",
        start_date=date(2026, 9, 24),
    )

    parcours_termine = parcours.terminer(date(2026, 10, 15))

    assert parcours_termine.id == parcours.id
    assert parcours_termine.status == "completed"
    assert parcours_termine.end_date == date(2026, 10, 15)
    assert parcours.status == "active"
    assert parcours.end_date is None


def test_terminer_refuse_date_anterieure():
    parcours = Journey(
        type="conception",
        start_date=date(2026, 9, 24),
    )

    with pytest.raises(ValueError):
        parcours.terminer(date(2026, 9, 23))


def test_terminer_refuse_parcours_deja_termine():
    parcours = Journey(
        type="conception",
        start_date=date(2026, 9, 24),
    ).terminer(date(2026, 10, 15))

    with pytest.raises(ValueError):
        parcours.terminer(date(2026, 10, 16))

def test_profil_vide():
    profil = UserProfile()

    assert profil.journeys == ()
    assert profil.active_journey_id is None


def test_profil_avec_un_parcours_actif():
    parcours = Journey(
        type="conception",
        start_date=date(2026, 9, 24),
    )

    profil = UserProfile(
        journeys=(parcours,),
        active_journey_id=parcours.id,
    )

    assert profil.active_journey_id == parcours.id


def test_profil_refuse_deux_parcours_actifs():
    conception = Journey(
        type="conception",
        start_date=date(2026, 9, 24),
    )
    grossesse = Journey(
        type="pregnancy",
        start_date=date(2026, 10, 15),
    )

    with pytest.raises(ValueError):
        UserProfile(
            journeys=(conception, grossesse),
            active_journey_id=grossesse.id,
        )


def test_profil_refuse_identifiant_actif_inconnu():
    with pytest.raises(ValueError):
        UserProfile(active_journey_id="inconnu")


def test_profil_refuse_parcours_actif_sans_identifiant_actif():
    parcours = Journey(
        type="conception",
        start_date=date(2026, 9, 24),
    )

    with pytest.raises(ValueError):
        UserProfile(journeys=(parcours,))


def test_profil_refuse_identifiants_dupliques():
    parcours = Journey(
        type="conception",
        start_date=date(2026, 9, 24),
    ).terminer(date(2026, 9, 25))

    with pytest.raises(ValueError):
        UserProfile(journeys=(parcours, parcours))


def test_demarrer_parcours_renseigne_identifiant_actif():
    profil = UserProfile()

    nouveau_profil = profil.demarrer_parcours(
        "conception",
        date(2026, 9, 24),
    )

    assert len(nouveau_profil.journeys) == 1

    parcours = nouveau_profil.journeys[0]

    assert parcours.type == "conception"
    assert parcours.status == "active"
    assert nouveau_profil.active_journey_id == parcours.id
    assert nouveau_profil.id == profil.id

    # Le profil initial reste inchangé.
    assert profil.journeys == ()
    assert profil.active_journey_id is None


def test_demarrer_refuse_un_second_parcours_actif():
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 24),
    )

    with pytest.raises(ValueError):
        profil.demarrer_parcours(
            "pregnancy",
            date(2026, 10, 15),
        )

def test_terminer_parcours_actif_conserve_historique():
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 24),
    )

    profil_termine = profil.terminer_parcours_actif(date(2026, 10, 15))

    assert profil_termine.active_journey_id is None
    assert len(profil_termine.journeys) == 1

    parcours = profil_termine.journeys[0]

    assert parcours.id == profil.active_journey_id
    assert parcours.status == "completed"
    assert parcours.end_date == date(2026, 10, 15)

    # La version initiale n'a pas été modifiée.
    assert profil.journeys[0].status == "active"


def test_terminer_sans_parcours_actif_est_refuse():
    profil = UserProfile()

    with pytest.raises(ValueError):
        profil.terminer_parcours_actif(date(2026, 10, 15))


def test_terminer_parcours_actif_refuse_date_anterieure():
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 24),
    )

    with pytest.raises(ValueError):
        profil.terminer_parcours_actif(date(2026, 9, 23))

@pytest.mark.parametrize(
    "ancien_type, nouveau_type",
    [
        ("conception", "pregnancy"),
        ("pregnancy", "conception"),
    ],
)
def test_changement_parcours_conserve_historique(
    ancien_type,
    nouveau_type,
):
    profil = UserProfile().demarrer_parcours(
        ancien_type,
        date(2026, 9, 24),
    )
    ancien_identifiant = profil.active_journey_id

    nouveau_profil = profil.changer_parcours(
        nouveau_type,
        date(2026, 10, 15),
    )

    assert len(nouveau_profil.journeys) == 2

    ancien, nouveau = nouveau_profil.journeys

    assert ancien.id == ancien_identifiant
    assert ancien.status == "completed"
    assert ancien.end_date == date(2026, 10, 15)

    assert nouveau.type == nouveau_type
    assert nouveau.status == "active"
    assert nouveau.start_date == date(2026, 10, 15)
    assert nouveau.id != ancien.id
    assert nouveau_profil.active_journey_id == nouveau.id

    assert profil.id == nouveau_profil.id
    assert len(profil.journeys) == 1
    assert profil.journeys[0].status == "active"


def test_changement_invalide_preserve_profil_initial():
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 24),
    )

    with pytest.raises(ValueError):
        profil.changer_parcours(
            "inconnu", # type: ignore
            date(2026, 10, 15),
        )

    assert len(profil.journeys) == 1
    assert profil.journeys[0].status == "active"
    assert profil.active_journey_id == profil.journeys[0].id

def test_transitions_successives_conservent_tous_les_parcours():
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 24),
    )

    profil = profil.changer_parcours(
        "pregnancy",
        date(2026, 10, 15),
    )

    profil = profil.changer_parcours(
        "conception",
        date(2027, 7, 1),
    )

    assert len(profil.journeys) == 3

    premiere_conception, grossesse, nouvelle_conception = profil.journeys

    assert premiere_conception.type == "conception"
    assert premiere_conception.status == "completed"
    assert premiere_conception.end_date == date(2026, 10, 15)

    assert grossesse.type == "pregnancy"
    assert grossesse.status == "completed"
    assert grossesse.end_date == date(2027, 7, 1)

    assert nouvelle_conception.type == "conception"
    assert nouvelle_conception.status == "active"
    assert nouvelle_conception.end_date is None

    assert profil.active_journey_id == nouvelle_conception.id
    assert len({parcours.id for parcours in profil.journeys}) == 3

def test_reprise_apres_cloture_conserve_ancien_parcours():
    profil = UserProfile().demarrer_parcours(
        "pregnancy",
        date(2026, 9, 24),
    )

    profil = profil.terminer_parcours_actif(date(2027, 6, 1))

    assert profil.active_journey_id is None

    profil = profil.demarrer_parcours(
        "conception",
        date(2027, 7, 1),
    )

    assert len(profil.journeys) == 2
    assert profil.journeys[0].status == "completed"
    assert profil.journeys[0].end_date == date(2027, 6, 1)
    assert profil.journeys[1].status == "active"
    assert profil.journeys[1].start_date == date(2027, 7, 1)
    assert profil.active_journey_id == profil.journeys[1].id

def test_reperes_conception_sans_date():
    reperes = ConceptionJourney()

    assert reperes.last_period_date is None
    assert reperes.average_cycle_length == 28
    assert reperes.period_length == 5
    assert reperes.cycle_regularity == "unknown"


@pytest.mark.parametrize(
    "modifications",
    [
        {"average_cycle_length": 0},
        {"period_length": 0},
        {"average_cycle_length": 28, "period_length": 29},
        {"cycle_regularity": "inconnu"},
    ],
)
def test_reperes_conception_invalides_refuses(modifications):
    with pytest.raises(ValueError):
        ConceptionJourney(**modifications)

def test_grossesse_datee_par_dernieres_regles():
    reperes = PregnancyJourney(
        dating_method="last_period",
        last_period_date=date(2026, 7, 20),
    )

    assert reperes.last_period_date == date(2026, 7, 20)
    assert reperes.estimated_due_date is None


def test_grossesse_datee_par_dpa():
    reperes = PregnancyJourney(
        dating_method="due_date",
        estimated_due_date=date(2027, 4, 26),
    )

    assert reperes.estimated_due_date == date(2027, 4, 26)
    assert reperes.last_period_date is None


@pytest.mark.parametrize(
    "donnees",
    [
        {"dating_method": "inconnue"},
        {"dating_method": "last_period"},
        {"dating_method": "due_date"},
    ],
)
def test_reperes_grossesse_invalides_refuses(donnees):
    with pytest.raises(ValueError):
        PregnancyJourney(**donnees)

def test_renseigner_reperes_conception():
    parcours = Journey(
        type="conception",
        start_date=date(2026, 9, 24),
    )
    reperes = ConceptionJourney(
        last_period_date=date(2026, 9, 12),
        average_cycle_length=30,
    )

    nouveau = parcours.renseigner_reperes(reperes)

    assert nouveau.id == parcours.id
    assert nouveau.details == reperes
    assert parcours.details is None


def test_refuser_reperes_du_mauvais_type():
    parcours = Journey(
        type="conception",
        start_date=date(2026, 9, 24),
    )
    reperes = PregnancyJourney(
        dating_method="last_period",
        last_period_date=date(2026, 7, 20),
    )

    with pytest.raises(ValueError):
        parcours.renseigner_reperes(reperes)


def test_cloture_conserve_reperes():
    reperes = ConceptionJourney(
        last_period_date=date(2026, 9, 12),
    )
    parcours = Journey(
        type="conception",
        start_date=date(2026, 9, 24),
        details=reperes,
    )

    termine = parcours.terminer(date(2026, 10, 15))

    assert termine.details == reperes

    with pytest.raises(ValueError):
        termine.renseigner_reperes(
            ConceptionJourney(last_period_date=date(2026, 10, 1))
        )

def test_renseigner_reperes_actifs_preserve_historique():
    anciens_reperes = ConceptionJourney(
        last_period_date=date(2026, 9, 12),
    )

    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 24),
    )
    profil = profil.renseigner_reperes_actifs(anciens_reperes)
    profil = profil.changer_parcours(
        "pregnancy",
        date(2026, 10, 15),
    )

    nouveaux_reperes = PregnancyJourney(
        dating_method="last_period",
        last_period_date=date(2026, 9, 12),
    )

    nouveau_profil = profil.renseigner_reperes_actifs(nouveaux_reperes)

    assert nouveau_profil.id == profil.id
    assert nouveau_profil.active_journey_id == profil.active_journey_id

    assert nouveau_profil.journeys[0] == profil.journeys[0]
    assert nouveau_profil.journeys[0].details == anciens_reperes
    assert nouveau_profil.journeys[1].details == nouveaux_reperes

    # Le profil initial reste inchangé.
    assert profil.journeys[1].details is None


def test_renseigner_reperes_sans_parcours_actif_est_refuse():
    profil = UserProfile()

    with pytest.raises(ValueError):
        profil.renseigner_reperes_actifs(ConceptionJourney())


def test_renseigner_reperes_actifs_refuse_mauvais_type():
    profil = UserProfile().demarrer_parcours(
        "pregnancy",
        date(2026, 9, 24),
    )

    with pytest.raises(ValueError):
        profil.renseigner_reperes_actifs(ConceptionJourney())

    assert profil.journeys[0].details is None

@pytest.mark.parametrize(
    "duree, version",
    [
        (0, "sa-reference-v1"),
        (True, "sa-reference-v1"),
        (280.0, "sa-reference-v1"),
        (287, None),
        (None, "sa-reference-v1"),
        (287, "inconnue"),
    ],
)
def test_grossesse_refuse_convention_invalide(duree, version):
    with pytest.raises(ValueError):
        PregnancyJourney(
            dating_method="due_date",
            estimated_due_date=date(2027, 4, 1),
            term_reference_days=duree,
            dating_rule_version=version,
        )


