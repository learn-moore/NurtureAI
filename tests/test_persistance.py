import pytest
import json
from datetime import date, datetime, timezone
from dataclasses import asdict, replace

from modeles import UserProfile, ConceptionJourney, PregnancyJourney, Journey, Appointment
from persistance import exporter_profil, importer_profil, lire_export, lire_date, lire_reperes_conception, lire_reperes_grossesse, lire_parcours, convertir_date, lire_rendez_vous


def test_export_contient_parcours_et_reperes():
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 25),
    )
    profil = profil.renseigner_reperes_actifs(
        ConceptionJourney(
            last_period_date=date(2026, 9, 12),
            average_cycle_length=30,
        )
    )

    texte = exporter_profil(profil)
    donnees = json.loads(texte)

    assert donnees["schema_version"] == 3
    assert donnees["profil"]["id"] == profil.id
    assert donnees["profil"]["active_journey_id"] == profil.active_journey_id

    parcours = donnees["profil"]["journeys"][0]

    assert parcours["type"] == "conception"
    assert parcours["start_date"] == "2026-09-25"
    assert parcours["end_date"] is None
    assert parcours["details"]["last_period_date"] == "2026-09-12"
    assert parcours["details"]["average_cycle_length"] == 30

def test_lire_export_reconnait_un_export_du_projet():
    profil = UserProfile()
    texte = exporter_profil(profil)

    donnees = lire_export(texte)

    assert donnees["schema_version"] == 3
    assert donnees["profil"]["id"] == profil.id


@pytest.mark.parametrize(
    "texte",
    [
        "ceci n’est pas du JSON",
        "[]",
        '{"schema_version": 99, "profil": {}}',
        '{"schema_version": true, "profil": {}}',
        '{"schema_version": 1}',
        '{"schema_version": 1, "profil": []}',
    ],
)
def test_lire_export_refuse_une_enveloppe_invalide(texte):
    with pytest.raises(ValueError):
        lire_export(texte)

def test_lire_date_valide():
    assert lire_date("2028-02-29", "start_date") == date(2028, 2, 29)


def test_lire_date_facultative_absente():
    assert lire_date(None, "end_date", obligatoire=False) is None


@pytest.mark.parametrize(
    "valeur",
    [
        None,
        20260925,
        "25/09/2026",
        "2026-02-29",
        "20260925",
        "",
    ],
)
def test_lire_date_refuse_valeur_invalide(valeur):
    with pytest.raises(ValueError):
        lire_date(valeur, "start_date")

def test_lire_reperes_conception():
    donnees = {
        "last_period_date": "2026-09-12",
        "average_cycle_length": 30,
        "period_length": 5,
        "cycle_regularity": "regular",
    }

    reperes = lire_reperes_conception(donnees)

    assert reperes.last_period_date == date(2026, 9, 12)
    assert reperes.average_cycle_length == 30
    assert reperes.period_length == 5
    assert reperes.cycle_regularity == "regular"


@pytest.mark.parametrize(
    "modifications",
    [
        {"average_cycle_length": "28"},
        {"average_cycle_length": True},
        {"period_length": 5.5},
        {"period_length": 31},
        {"cycle_regularity": "inconnu"},
        {"champ_inattendu": "valeur"},
    ],
)
def test_lire_reperes_conception_refuse_donnees_invalides(modifications):
    donnees = {
        "last_period_date": None,
        "average_cycle_length": 30,
        "period_length": 5,
        "cycle_regularity": "unknown",
    }
    donnees.update(modifications)

    with pytest.raises(ValueError):
        lire_reperes_conception(donnees)


def test_lire_reperes_conception_refuse_champs_manquants():
    with pytest.raises(ValueError):
        lire_reperes_conception({})

@pytest.mark.parametrize(
    "methode, dernieres_regles, dpa",
    [
        ("last_period", "2026-07-20", None),
        ("due_date", None, "2027-04-26"),
    ],
)
def test_lire_reperes_grossesse(methode, dernieres_regles, dpa):
    reperes = lire_reperes_grossesse({
        "dating_method": methode,
        "last_period_date": dernieres_regles,
        "estimated_due_date": dpa,
    })

    assert reperes.dating_method == methode
    assert reperes.last_period_date == (
        date(2026, 7, 20) if dernieres_regles is not None else None
    )
    assert reperes.estimated_due_date == (
        date(2027, 4, 26) if dpa is not None else None
    )


@pytest.mark.parametrize(
    "modifications",
    [
        {"dating_method": 42},
        {"dating_method": "inconnue"},
        {"last_period_date": None},
        {"dating_method": "due_date"},
        {"last_period_date": "2026-02-29"},
        {"champ_inattendu": "valeur"},
    ],
)
def test_lire_reperes_grossesse_refuse_donnees_invalides(modifications):
    donnees = {
        "dating_method": "last_period",
        "last_period_date": "2026-07-20",
        "estimated_due_date": None,
    }
    donnees.update(modifications)

    with pytest.raises(ValueError):
        lire_reperes_grossesse(donnees)


def test_lire_reperes_grossesse_refuse_champs_manquants():
    with pytest.raises(ValueError):
        lire_reperes_grossesse({})

def test_lire_parcours_reconstruit_objet_exporte():
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 25),
    )
    profil = profil.renseigner_reperes_actifs(
        ConceptionJourney(last_period_date=date(2026, 9, 12))
    )

    donnees = json.loads(exporter_profil(profil))
    parcours = lire_parcours(donnees["profil"]["journeys"][0])

    assert parcours == profil.journeys[0]


@pytest.mark.parametrize(
    "modifications",
    [
        {"id": "identifiant-invalide"},
        {"type": "inconnu"},
        {"status": "completed"},
        {"end_date": "2026-09-26"},
        {"start_date": None},
        {"details": {}},
    ],
)
def test_lire_parcours_refuse_donnees_invalides(modifications):
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 25),
    )
    donnees = json.loads(exporter_profil(profil))
    parcours = donnees["profil"]["journeys"][0]
    parcours.update(modifications)

    with pytest.raises(ValueError):
        lire_parcours(parcours)

def test_export_import_restitue_profil_et_historique():
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 25),
    )
    profil = profil.renseigner_reperes_actifs(
        ConceptionJourney(
            last_period_date=date(2026, 9, 12),
            average_cycle_length=30,
        )
    )
    profil = profil.changer_parcours(
        "pregnancy",
        date(2026, 10, 15),
    )

    profil_restaure = importer_profil(exporter_profil(profil))

    assert profil_restaure == profil


def test_export_import_profil_vide():
    profil = UserProfile()

    assert importer_profil(exporter_profil(profil)) == profil


@pytest.mark.parametrize(
    "champ, valeur",
    [
        ("id", "invalide"),
        ("journeys", {}),
        ("active_journey_id", None),
    ],
)
def test_import_refuse_profil_invalide(champ, valeur):
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 25),
    )
    donnees = json.loads(exporter_profil(profil))
    donnees["profil"][champ] = valeur

    with pytest.raises(ValueError):
        importer_profil(json.dumps(donnees))


def test_import_refuse_parcours_dupliques():
    profil = UserProfile().demarrer_parcours(
        "conception",
        date(2026, 9, 25),
    )
    profil = profil.terminer_parcours_actif(date(2026, 9, 26))

    donnees = json.loads(exporter_profil(profil))
    parcours = donnees["profil"]["journeys"][0]
    donnees["profil"]["journeys"].append(parcours.copy())

    with pytest.raises(ValueError):
        importer_profil(json.dumps(donnees))

def test_export_contient_horodatage_utc():
    avant = datetime.now(timezone.utc)

    donnees = json.loads(exporter_profil(UserProfile()))

    apres = datetime.now(timezone.utc)
    date_export = datetime.fromisoformat(donnees["exported_at"])

    assert avant <= date_export <= apres
    assert date_export.utcoffset().total_seconds() == 0 # type: ignore


@pytest.mark.parametrize(
    "horodatage",
    [
        123,
        "date-invalide",
        "2026-09-25T12:00:00",
    ],
)
def test_import_refuse_horodatage_invalide(horodatage):
    donnees = json.loads(exporter_profil(UserProfile()))
    donnees["exported_at"] = horodatage

    with pytest.raises(ValueError):
        importer_profil(json.dumps(donnees))


def test_import_accepte_ancien_export_sans_horodatage():
    profil = UserProfile()
    donnees = json.loads(exporter_profil(profil))
    del donnees["exported_at"]

    profil_restaure = importer_profil(json.dumps(donnees))

    assert profil_restaure == profil

def test_import_version_1_preserve_grossesse():
    ancien_export = {
        "schema_version": 1,
        "profil": {
            "id": "11111111-1111-4111-8111-111111111111",
            "active_journey_id": "22222222-2222-4222-8222-222222222222",
            "journeys": [
                {
                    "id": "22222222-2222-4222-8222-222222222222",
                    "type": "pregnancy",
                    "status": "active",
                    "start_date": "2026-09-25",
                    "end_date": None,
                    "details": {
                        "dating_method": "due_date",
                        "last_period_date": None,
                        "estimated_due_date": "2027-04-01",
                    },
                }
            ],
        },
    }

    profil = importer_profil(json.dumps(ancien_export))

    assert profil.id == ancien_export["profil"]["id"]
    assert (
        profil.active_journey_id
        == ancien_export["profil"]["active_journey_id"]
    )
    assert profil.journeys[0].details == PregnancyJourney(
        dating_method="due_date",
        estimated_due_date=date(2027, 4, 1),
    )

    nouvel_export = exporter_profil(profil)

    assert json.loads(nouvel_export)["schema_version"] == 3
    assert importer_profil(nouvel_export) == profil

@pytest.mark.parametrize("duree", [None, 280, 287])
def test_export_import_conserve_convention_grossesse(duree):
    reperes = PregnancyJourney(
        dating_method="due_date",
        estimated_due_date=date(2027, 4, 1),
        term_reference_days=duree,
        dating_rule_version=(
            "sa-reference-v1" if duree is not None else None
        ),
    )

    profil = UserProfile().demarrer_parcours(
        "pregnancy",
        date(2026, 9, 27),
    )
    profil = profil.renseigner_reperes_actifs(reperes)

    assert importer_profil(exporter_profil(profil)) == profil


@pytest.fixture
def donnees_rendez_vous():
    parcours = Journey(
        type="pregnancy",
        start_date=date(2026, 9, 27),
    )
    fiche = Appointment(
        journey_id=parcours.id,
        notes="Questions à préparer",
        questions=("Que dois-je apporter ?",),
        topics=("nutrition",),
        created_at=datetime(2026, 9, 27, tzinfo=timezone.utc),
    )

    return json.loads(
        json.dumps(asdict(fiche), default=convertir_date)
    )


def test_lecture_rendez_vous_preserve_export(donnees_rendez_vous):
    fiche = lire_rendez_vous(donnees_rendez_vous)

    assert fiche.questions == ("Que dois-je apporter ?",)
    assert fiche.topics == ("nutrition",)
    assert fiche.date is None

    assert json.loads(
        json.dumps(asdict(fiche), default=convertir_date)
    ) == donnees_rendez_vous


@pytest.mark.parametrize(
    "champs",
    [
        {"questions": "Question ?"},
        {"topics": "nutrition"},
        {"created_at": None},
        {"updated_at": "invalide"},
        {"created_at": "2026-09-27T00:00:00"},
        {"updated_at": "2026-09-26T00:00:00+00:00"},
        {"date": "2026-02-30"},
        {"champ_inconnu": True},
    ],
)
def test_lecture_rendez_vous_refuse_export_invalide(
    donnees_rendez_vous, champs
):
    with pytest.raises(ValueError):
        lire_rendez_vous({**donnees_rendez_vous, **champs})


def test_lecture_rendez_vous_refuse_champ_manquant(
    donnees_rendez_vous,
):
    del donnees_rendez_vous["updated_at"]

    with pytest.raises(ValueError):
        lire_rendez_vous(donnees_rendez_vous)

@pytest.fixture
def profil_avec_rendez_vous():
    profil = UserProfile().demarrer_parcours(
        "pregnancy",
        date(2026, 9, 27),
    )
    fiche = Appointment(
        journey_id=profil.active_journey_id, # type: ignore
        notes="Mes notes",
        questions=("Que dois-je apporter ?",),
        topics=("nutrition",),
    )

    return replace(profil, appointments=(fiche,))


def test_export_import_profil_avec_rendez_vous(
    profil_avec_rendez_vous,
):
    texte = exporter_profil(profil_avec_rendez_vous)

    assert json.loads(texte)["schema_version"] == 3
    assert importer_profil(texte) == profil_avec_rendez_vous


@pytest.mark.parametrize("version", [1, 2])
def test_ancien_export_sans_rendez_vous(version):
    donnees = json.loads(exporter_profil(UserProfile()))
    donnees["schema_version"] = version
    del donnees["profil"]["appointments"]

    assert importer_profil(json.dumps(donnees)).appointments == ()


@pytest.mark.parametrize(
    "anomalie",
    ["absent", "doublon", "orphelin", "liste_invalide"],
)
def test_import_refuse_rendez_vous_incoherents(
    profil_avec_rendez_vous, anomalie
):
    donnees = json.loads(exporter_profil(profil_avec_rendez_vous))
    profil = donnees["profil"]

    if anomalie == "absent":
        del profil["appointments"]
    elif anomalie == "doublon":
        profil["appointments"] *= 2
    elif anomalie == "orphelin":
        profil["appointments"][0]["journey_id"] = (
            "11111111-1111-4111-8111-111111111111"
        )
    else:
        profil["appointments"] = None

    with pytest.raises(ValueError):
        importer_profil(json.dumps(donnees))


def test_transition_conserve_rendez_vous_archives(
    profil_avec_rendez_vous,
):
    nouveau = profil_avec_rendez_vous.changer_parcours(
        "conception",
        date(2026, 9, 28),
    )

    assert nouveau.appointments == profil_avec_rendez_vous.appointments
    assert nouveau.appointments[0].journey_id != nouveau.active_journey_id
    assert importer_profil(exporter_profil(nouveau)) == nouveau

