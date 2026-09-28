import pytest
from datetime import date, datetime, timedelta, timezone
from dataclasses import FrozenInstanceError

from modeles import Journey, UserProfile, ConceptionJourney, PregnancyJourney, Appointment

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

def test_rendez_vous_en_preparation_sans_date():
    parcours = Journey(
        type="pregnancy",
        start_date=date(2026, 9, 27),
    )

    rendez_vous = Appointment(journey_id=parcours.id)

    assert rendez_vous.date is None
    assert rendez_vous.journey_id == parcours.id
    assert rendez_vous.appointment_type == "other"


def test_rendez_vous_avec_date_passee():
    parcours = Journey(
        type="pregnancy",
        start_date=date(2026, 1, 1),
    )

    rendez_vous = Appointment(
        journey_id=parcours.id,
        appointment_type="follow_up",
        date=date(2026, 2, 1),
    )

    assert rendez_vous.date == date(2026, 2, 1)


@pytest.mark.parametrize(
    "champs",
    [
        {"appointment_type": "inconnu"},
        {"date": "2026-10-01"},
        {"journey_id": ""},
        {"journey_id": None},
        {"id": "incorrect"},
    ],
)
def test_rendez_vous_refuse_champs_invalides(champs):
    parcours = Journey(
        type="pregnancy",
        start_date=date(2026, 9, 27),
    )

    donnees = {"journey_id": parcours.id, **champs}

    with pytest.raises(ValueError):
        Appointment(**donnees)

def test_fiche_rendez_vous_vide():
    parcours = Journey(
        type="pregnancy",
        start_date=date(2026, 9, 27),
    )
    fiche = Appointment(journey_id=parcours.id)

    assert fiche.notes == ""
    assert fiche.questions == ()


def test_fiche_rendez_vous_accepte_limites():
    parcours = Journey(
        type="pregnancy",
        start_date=date(2026, 9, 27),
    )
    fiche = Appointment(
        journey_id=parcours.id,
        notes="n" * 5000,
        questions=("q" * 500,) * 30,
    )

    assert len(fiche.notes) == 5000
    assert len(fiche.questions) == 30


def test_fiche_conserve_texte_et_ordre():
    parcours = Journey(
        type="pregnancy",
        start_date=date(2026, 9, 27),
    )
    notes = "Mes notes\nDeuxième ligne."
    questions = (
        "  Que dois-je apporter ?  ",
        "Comment préparer la consultation ?",
    )

    fiche = Appointment(
        journey_id=parcours.id,
        notes=notes,
        questions=questions,
    )

    assert fiche.notes == notes
    assert fiche.questions == questions


@pytest.mark.parametrize(
    "champs",
    [
        {"notes": None},
        {"notes": "n" * 5001},
        {"questions": []},
        {"questions": None},
        {"questions": ("Question ?",) * 31},
        {"questions": ("",)},
        {"questions": ("   ",)},
        {"questions": ("q" * 501,)},
        {"questions": (42,)},
    ],
)
def test_fiche_refuse_contenu_invalide(champs):
    parcours = Journey(
        type="pregnancy",
        start_date=date(2026, 9, 27),
    )

    with pytest.raises(ValueError):
        Appointment(journey_id=parcours.id, **champs)

def test_rendez_vous_sans_theme():
    parcours = Journey(
        type="pregnancy",
        start_date=date(2026, 9, 27),
    )

    assert Appointment(journey_id=parcours.id).topics == ()


def test_rendez_vous_conserve_ordre_themes():
    parcours = Journey(
        type="pregnancy",
        start_date=date(2026, 9, 27),
    )
    fiche = Appointment(
        journey_id=parcours.id,
        topics=("travel", "nutrition"),
    )

    assert fiche.topics == ("travel", "nutrition")


def test_rendez_vous_accepte_tous_les_themes_du_cadrage():
    parcours = Journey(
        type="pregnancy",
        start_date=date(2026, 9, 27),
    )
    themes = (
        "nutrition",
        "physical_activity",
        "symptoms",
        "medications",
        "tests",
        "work",
        "travel",
        "childbirth",
        "other",
    )

    fiche = Appointment(journey_id=parcours.id, topics=themes)

    assert fiche.topics == themes


@pytest.mark.parametrize(
    "themes",
    [
        [],
        None,
        ("inconnu",),
        (42,),
        ({"theme": "nutrition"},),
        ("nutrition", "nutrition"),
    ],
)
def test_rendez_vous_refuse_themes_invalides(themes):
    parcours = Journey(
        type="pregnancy",
        start_date=date(2026, 9, 27),
    )

    with pytest.raises(ValueError):
        Appointment(journey_id=parcours.id, topics=themes)

def test_horodatages_initialises_a_la_creation():
    parcours = Journey(
        type="pregnancy",
        start_date=date(2026, 9, 27),
    )

    avant = datetime.now(timezone.utc)
    fiche = Appointment(journey_id=parcours.id)
    apres = datetime.now(timezone.utc)

    assert avant <= fiche.created_at <= apres
    assert fiche.created_at.utcoffset() == timedelta(0)
    assert fiche.updated_at == fiche.created_at


def test_horodatages_fournis_conserves():
    parcours = Journey(
        type="pregnancy",
        start_date=date(2026, 9, 27),
    )
    creation = datetime(2026, 9, 27, 10, tzinfo=timezone.utc)
    modification = datetime(
        2026, 9, 27, 13,
        tzinfo=timezone(timedelta(hours=2)),
    )

    fiche = Appointment(
        journey_id=parcours.id,
        created_at=creation,
        updated_at=modification,
    )

    assert fiche.created_at == creation
    assert fiche.updated_at == modification


@pytest.mark.parametrize(
    "champs",
    [
        {"created_at": datetime(2026, 9, 27)},
        {"updated_at": datetime(2026, 9, 27)},
        {"updated_at": datetime(2026, 9, 26, tzinfo=timezone.utc)},
        {"created_at": "2026-09-27T00:00:00Z"},
        {"updated_at": "2026-09-27T00:00:00Z"},
    ],
)
def test_horodatages_invalides_refuses(champs):
    parcours = Journey(
        type="pregnancy",
        start_date=date(2026, 9, 27),
    )
    donnees = {
        "journey_id": parcours.id,
        "created_at": datetime(2026, 9, 27, tzinfo=timezone.utc),
        **champs,
    }

    with pytest.raises(ValueError):
        Appointment(**donnees)

@pytest.fixture
def profil_grossesse_pour_rendez_vous():
    return UserProfile().demarrer_parcours(
        "pregnancy",
        date(2026, 9, 27),
    )


def test_ajouter_rendez_vous_preserve_profil_initial(
    profil_grossesse_pour_rendez_vous,
):
    profil = profil_grossesse_pour_rendez_vous
    premiere = Appointment(journey_id=profil.active_journey_id)
    seconde = Appointment(journey_id=profil.active_journey_id)

    intermediaire = profil.ajouter_rendez_vous(premiere)
    resultat = intermediaire.ajouter_rendez_vous(seconde)

    assert profil.appointments == ()
    assert intermediaire.appointments == (premiere,)
    assert resultat.appointments == (premiere, seconde)
    assert resultat.journeys == profil.journeys
    assert resultat.active_journey_id == profil.active_journey_id
    assert resultat.id == profil.id


def test_ajouter_rendez_vous_refuse_doublon(
    profil_grossesse_pour_rendez_vous,
):
    profil = profil_grossesse_pour_rendez_vous
    fiche = Appointment(journey_id=profil.active_journey_id)
    profil = profil.ajouter_rendez_vous(fiche)

    with pytest.raises(ValueError):
        profil.ajouter_rendez_vous(fiche)

    assert profil.appointments == (fiche,)


def test_ajouter_rendez_vous_refuse_parcours_absent(
    profil_grossesse_pour_rendez_vous,
):
    profil = profil_grossesse_pour_rendez_vous
    autre = Journey(
        type="conception",
        start_date=date(2026, 9, 27),
    )
    fiche = Appointment(journey_id=autre.id)

    with pytest.raises(ValueError):
        profil.ajouter_rendez_vous(fiche)

    assert profil.appointments == ()


@pytest.mark.parametrize("fiche", [None, "fiche"])
def test_ajouter_rendez_vous_refuse_mauvais_type(
    profil_grossesse_pour_rendez_vous, fiche
):
    with pytest.raises(ValueError):
        profil_grossesse_pour_rendez_vous.ajouter_rendez_vous(fiche)

def test_supprimer_rendez_vous_preserve_autres_donnees(
    profil_grossesse_pour_rendez_vous,
):
    profil = profil_grossesse_pour_rendez_vous
    premiere = Appointment(journey_id=profil.active_journey_id)
    seconde = Appointment(journey_id=profil.active_journey_id)
    profil = profil.ajouter_rendez_vous(premiere)
    profil = profil.ajouter_rendez_vous(seconde)

    resultat = profil.supprimer_rendez_vous(premiere.id)

    assert resultat.appointments == (seconde,)
    assert profil.appointments == (premiere, seconde)
    assert resultat.journeys == profil.journeys
    assert resultat.active_journey_id == profil.active_journey_id
    assert resultat.id == profil.id


def test_supprimer_derniere_fiche_conserve_parcours(
    profil_grossesse_pour_rendez_vous,
):
    profil = profil_grossesse_pour_rendez_vous
    fiche = Appointment(journey_id=profil.active_journey_id)
    profil = profil.ajouter_rendez_vous(fiche)

    resultat = profil.supprimer_rendez_vous(fiche.id)

    assert resultat.appointments == ()
    assert resultat.journeys == profil.journeys
    assert resultat.active_journey_id == profil.active_journey_id


@pytest.mark.parametrize(
    "identifiant",
    [
        "",
        None,
        "11111111-1111-4111-8111-111111111111",
    ],
)
def test_supprimer_rendez_vous_absent_refuse(
    profil_grossesse_pour_rendez_vous, identifiant
):
    profil = profil_grossesse_pour_rendez_vous
    fiche = Appointment(journey_id=profil.active_journey_id)
    profil = profil.ajouter_rendez_vous(fiche)

    with pytest.raises(ValueError, match="Rendez-vous introuvable"):
        profil.supprimer_rendez_vous(identifiant)

    assert profil.appointments == (fiche,)

@pytest.fixture
def modification_rendez_vous():
    profil = UserProfile().demarrer_parcours(
        "pregnancy",
        date(2026, 9, 28),
    )
    creation = datetime(2026, 9, 28, 10, tzinfo=timezone.utc)

    fiche = Appointment(
        journey_id=profil.active_journey_id, # type: ignore
        created_at=creation,
    )
    autre = Appointment(
        journey_id=profil.active_journey_id, # type: ignore
        created_at=creation,
    )
    profil = profil.ajouter_rendez_vous(fiche)
    profil = profil.ajouter_rendez_vous(autre)

    changements = {
        "appointment_type": "follow_up",
        "date": date(2026, 10, 15),
        "notes": "Notes modifiées",
        "questions": ("Nouvelle question ?",),
        "topics": ("travel",),
        "modifie_le": datetime(2026, 9, 28, 11, tzinfo=timezone.utc),
    }

    return profil, fiche, autre, changements


def test_modifier_rendez_vous_preserve_identite(
    modification_rendez_vous,
):
    profil, fiche, autre, changements = modification_rendez_vous

    resultat = profil.modifier_rendez_vous(fiche.id, **changements)
    modifiee = resultat.appointments[0]

    assert modifiee.id == fiche.id
    assert modifiee.journey_id == fiche.journey_id
    assert modifiee.created_at == fiche.created_at
    assert modifiee.updated_at == changements["modifie_le"]

    for champ in ("appointment_type", "date", "notes", "questions", "topics"):
        assert getattr(modifiee, champ) == changements[champ]

    assert resultat.appointments[1] == autre
    assert resultat.journeys == profil.journeys
    assert resultat.id == profil.id
    assert resultat.active_journey_id == profil.active_journey_id
    assert profil.appointments == (fiche, autre)


@pytest.mark.parametrize(
    "invalide",
    [
        {"notes": "n" * 5001},
        {"questions": ("",)},
        {"topics": ("inconnu",)},
        {"modifie_le": None},
        {"modifie_le": datetime(2026, 9, 28, 11)},
    ],
)
def test_modifier_rendez_vous_refuse_donnees_invalides(
    modification_rendez_vous, invalide
):
    profil, fiche, autre, changements = modification_rendez_vous

    with pytest.raises(ValueError):
        profil.modifier_rendez_vous(
            fiche.id,
            **{**changements, **invalide},
        )

    assert profil.appointments == (fiche, autre)


def test_modifier_rendez_vous_refuse_retour_en_arriere(
    modification_rendez_vous,
):
    profil, fiche, _, changements = modification_rendez_vous
    profil = profil.modifier_rendez_vous(fiche.id, **changements)

    changements["modifie_le"] = datetime(
        2026, 9, 28, 10, 30, tzinfo=timezone.utc
    )

    with pytest.raises(ValueError, match="précédente"):
        profil.modifier_rendez_vous(fiche.id, **changements)


def test_modifier_rendez_vous_absent(modification_rendez_vous):
    profil, _, _, changements = modification_rendez_vous

    with pytest.raises(ValueError, match="introuvable"):
        profil.modifier_rendez_vous("absent", **changements)

