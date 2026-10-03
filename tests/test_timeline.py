import json
import pytest
from datetime import date
from copy import deepcopy

from timeline import charger_timeline, charger_etapes_affichables, situer_fenetre_timeline, calculer_jours_sa_timeline, construire_timeline, choisir_etape_a_mettre_en_avant
from modeles import PregnancyJourney

def donnees_timeline_test():
    donnees = charger_timeline()
    etape = donnees["etapes"][0]
    donnees["etapes"] = [etape]
    etape["secondary_sources"] = []

    etape["editorial_status"] = "draft"
    etape["reviewed_at"] = None
    etape["source"]["retrieved_at"] = "2026-10-02"
    etape["source"]["publication_date"] = None
    etape["source"]["displayed_date"] = "2026-07-14"
    etape["source"]["reuse_status"] = "to_review"

    return donnees

def test_charger_timeline_independamment_du_dossier_courant(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    donnees = charger_timeline()

    assert donnees["schema_version"] == 1
    assert donnees["etapes"][0]["id"] == (
        "echographie_premier_trimestre"
    )
    assert donnees["etapes"][0]["editorial_status"] == "approved"


@pytest.mark.parametrize(
    "champ, valeur",
    [
        ("schema_version", True),
        ("schema_version", 2),
        ("content_version", "2026-02-30"),
        ("content_version", "20261002"),
        ("etapes", {}),
        ("etapes", ["fiche"]),
    ],
)
def test_charger_timeline_refuse_enveloppe_invalide(
    tmp_path, champ, valeur
):
    donnees = {
        "schema_version": 1,
        "content_version": "2026-10-02",
        "etapes": [],
    }
    donnees[champ] = valeur

    chemin = tmp_path / "timeline.json"
    chemin.write_text(
        json.dumps(donnees),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        charger_timeline(chemin)


@pytest.mark.parametrize(
    "contenu",
    [None, "{invalide", "[]"],
)
def test_charger_timeline_refuse_fichier_inexploitable(
    tmp_path, contenu
):
    chemin = tmp_path / "timeline.json"

    if contenu is not None:
        chemin.write_text(contenu, encoding="utf-8")

    with pytest.raises(ValueError):
        charger_timeline(chemin)

@pytest.mark.parametrize(
    "fenetre",
    [
        None,
        {},
        {"unit": "weeks_sa", "start": 77, "end": 97, "bounds": "inclusive"},
        {"unit": "days_sa", "start": 77, "end": 97, "bounds": "exclusive"},
        {"unit": "days_sa", "start": True, "end": 97, "bounds": "inclusive"},
        {"unit": "days_sa", "start": 77, "end": False, "bounds": "inclusive"},
        {"unit": "days_sa", "start": 77.0, "end": 97, "bounds": "inclusive"},
        {"unit": "days_sa", "start": 77, "end": "97", "bounds": "inclusive"},
        {"unit": "days_sa", "start": -1, "end": 97, "bounds": "inclusive"},
        {"unit": "days_sa", "start": 98, "end": 97, "bounds": "inclusive"},
    ],
)
def test_charger_timeline_refuse_fenetre_invalide(
    tmp_path, fenetre
):
    donnees = donnees_timeline_test()
    donnees["etapes"][0]["window"] = fenetre

    chemin = tmp_path / "timeline.json"
    chemin.write_text(
        json.dumps(donnees),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="fenêtre"):
        charger_timeline(chemin)


@pytest.mark.parametrize(
    "debut, fin",
    [(0, 0), (77, 97)],
)
def test_charger_timeline_accepte_fenetre_inclusive(
    tmp_path, debut, fin
):
    donnees = donnees_timeline_test()
    donnees["etapes"][0]["window"]["start"] = debut
    donnees["etapes"][0]["window"]["end"] = fin

    chemin = tmp_path / "timeline.json"
    chemin.write_text(
        json.dumps(donnees),
        encoding="utf-8",
    )

    assert charger_timeline(chemin) == donnees

@pytest.mark.parametrize(
    "champ, valeur",
    [
        ("id", " fiche "),
        ("title", "   "),
        ("when", ""),
        ("why", None),
        ("how", 123),
        ("questions", "Une question ?"),
        ("questions", []),
        ("questions", ["   "]),
        ("questions", [123]),
    ],
)
def test_charger_timeline_refuse_texte_invalide(
    tmp_path, champ, valeur
):
    donnees = donnees_timeline_test()
    donnees["etapes"][0][champ] = valeur

    chemin = tmp_path / "timeline.json"
    chemin.write_text(
        json.dumps(donnees),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        charger_timeline(chemin)


def test_charger_timeline_refuse_identifiants_dupliques(
    tmp_path,
):
    donnees = donnees_timeline_test()

    copie = donnees["etapes"][0].copy()
    copie["title"] = "Une autre fiche"
    donnees["etapes"].append(copie)

    chemin = tmp_path / "timeline.json"
    chemin.write_text(
        json.dumps(donnees),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Identifiant de timeline dupliqué",
    ):
        charger_timeline(chemin)

@pytest.mark.parametrize(
    "champ, valeur",
    [
        ("name", " "),
        ("url", "http://www.ameli.fr/page"),
        ("url", "https:///page"),
        ("url", "https://utilisateur@www.ameli.fr/page"),
        ("url", "https://www.ameli.fr/une page"),
        ("reuse_status", "inconnu"),
        ("retrieved_at", None),
        ("retrieved_at", "2026-02-30"),
        ("retrieved_at", "20261002"),
        ("publication_date", "2026-10-03"),
        ("displayed_date", "2026-10-03"),
    ],
)
def test_timeline_refuse_source_invalide(
    tmp_path, champ, valeur
):
    donnees = donnees_timeline_test()
    donnees["etapes"][0]["source"][champ] = valeur

    chemin = tmp_path / "timeline.json"
    chemin.write_text(
        json.dumps(donnees),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        charger_timeline(chemin)


@pytest.mark.parametrize(
    "revue",
    [
        None,
        "2026-10-02",
        "2026-10-03",
        "2026-10-01",
        "2026-02-30",
    ],
)
def test_timeline_date_revue(tmp_path, revue):
    donnees = donnees_timeline_test()
    donnees["etapes"][0]["reviewed_at"] = revue

    chemin = tmp_path / "timeline.json"
    chemin.write_text(
        json.dumps(donnees),
        encoding="utf-8",
    )

    if revue in (None, "2026-10-02", "2026-10-03"):
        assert charger_timeline(chemin) == donnees
    else:
        with pytest.raises(ValueError):
            charger_timeline(chemin)

@pytest.mark.parametrize(
    "statut, reutilisation, revue, affichee",
    [
        ("draft", "to_review", None, False),
        ("draft", "approved", "2026-10-02", False),
        ("rejected", "approved", "2026-10-02", False),
        ("approved", "to_review", "2026-10-02", False),
        ("approved", "rejected", "2026-10-02", False),
        ("approved", "approved", None, False),
        ("approved", "approved", "2026-10-02", True),
    ],
)
def test_timeline_selection_editoriale(
    tmp_path, statut, reutilisation, revue, affichee
):
    donnees = donnees_timeline_test()
    etape = donnees["etapes"][0]

    etape["editorial_status"] = statut
    etape["source"]["reuse_status"] = reutilisation
    etape["reviewed_at"] = revue

    chemin = tmp_path / "timeline.json"
    texte = json.dumps(donnees)
    chemin.write_text(texte, encoding="utf-8")

    resultat = charger_etapes_affichables(chemin)

    assert resultat == ((etape,) if affichee else ())
    assert chemin.read_text(encoding="utf-8") == texte


@pytest.mark.parametrize("statut", [None, "publie", True])
def test_timeline_refuse_statut_editorial_inconnu(
    tmp_path, statut
):
    donnees = donnees_timeline_test()
    donnees["etapes"][0]["editorial_status"] = statut

    chemin = tmp_path / "timeline.json"
    chemin.write_text(
        json.dumps(donnees),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Statut éditorial"):
        charger_etapes_affichables(chemin)

@pytest.mark.parametrize(
    "jours_sa, attendu",
    [
        (76, "upcoming"),
        (77, "current"),
        (97, "current"),
        (98, "past"),
        (None, "unknown"),
    ],
)
def test_situer_fenetre_timeline_aux_bornes(
    jours_sa, attendu
):
    fenetre = {
        "unit": "days_sa",
        "start": 77,
        "end": 97,
        "bounds": "inclusive",
    }
    avant = fenetre.copy()

    assert situer_fenetre_timeline(
        fenetre, jours_sa
    ) == attendu

    assert fenetre == avant


@pytest.mark.parametrize(
    "jours_sa",
    [-1, True, 77.0, "77"],
)
def test_situer_fenetre_timeline_refuse_age_invalide(
    jours_sa,
):
    fenetre = {
        "unit": "days_sa",
        "start": 77,
        "end": 97,
        "bounds": "inclusive",
    }

    with pytest.raises(ValueError, match="jours SA"):
        situer_fenetre_timeline(fenetre, jours_sa)


@pytest.mark.parametrize(
    "jours_sa, attendu",
    [
        (76, "upcoming"),
        (77, "current"),
        (78, "past"),
    ],
)
def test_situer_fenetre_timeline_un_seul_jour(
    jours_sa, attendu
):
    fenetre = {
        "unit": "days_sa",
        "start": 77,
        "end": 77,
        "bounds": "inclusive",
    }

    assert situer_fenetre_timeline(
        fenetre, jours_sa
    ) == attendu

@pytest.mark.parametrize(
    "methode, terme, attendu",
    [
        ("last_period", None, 77),
        ("last_period", 280, 77),
        ("due_date", 280, 63),
        ("due_date", 287, 70),
        ("due_date", None, None),
    ],
)
def test_jours_sa_timeline_respecte_methode(
    methode, terme, attendu
):
    reperes = PregnancyJourney(
        dating_method=methode,
        last_period_date=date(2026, 1, 1),
        estimated_due_date=date(2026, 10, 22),
        term_reference_days=terme,
        dating_rule_version=(
            "sa-reference-v1" if terme is not None else None
        ),
    )

    assert calculer_jours_sa_timeline(
        reperes,
        date(2026, 3, 19),
    ) == attendu


def test_jours_sa_timeline_sans_reperes():
    assert calculer_jours_sa_timeline(
        None,
        date(2026, 3, 19),
    ) is None


@pytest.mark.parametrize(
    "methode",
    ["last_period", "due_date"],
)
def test_jours_sa_timeline_refuse_age_negatif(methode):
    reperes = PregnancyJourney(
        dating_method=methode,
        last_period_date=date(2026, 1, 1),
        estimated_due_date=date(2026, 10, 22),
        term_reference_days=280,
        dating_rule_version="sa-reference-v1",
    )

    with pytest.raises(ValueError):
        calculer_jours_sa_timeline(
            reperes,
            date(2025, 12, 31),
        )

@pytest.mark.parametrize("reperes_connus", [False, True])
def test_construire_timeline_trie_filtre_et_positionne(
    tmp_path, reperes_connus
):
    donnees = donnees_timeline_test()
    modele = donnees["etapes"][0]
    donnees["etapes"] = []

    for identifiant, debut, fin, statut in [
        ("apres", 100, 120, "approved"),
        ("brouillon", 50, 60, "draft"),
        ("pendant", 77, 97, "approved"),
        ("avant", 0, 10, "approved"),
    ]:
        etape = deepcopy(modele)
        etape["id"] = identifiant
        etape["when"] = "Fenêtre fictive pour le test."
        etape["window"]["start"] = debut
        etape["window"]["end"] = fin
        etape["editorial_status"] = statut
        etape["source"]["reuse_status"] = "approved"
        etape["reviewed_at"] = "2026-10-02"
        donnees["etapes"].append(etape)

    chemin = tmp_path / "timeline.json"
    texte = json.dumps(donnees)
    chemin.write_text(texte, encoding="utf-8")

    reperes = (
        PregnancyJourney(
            dating_method="last_period",
            last_period_date=date(2026, 1, 1),
        )
        if reperes_connus
        else None
    )

    resultat = construire_timeline(
        reperes,
        date(2026, 3, 19),
        chemin=chemin,
    )

    assert [
        element["etape"]["id"] for element in resultat
    ] == ["avant", "pendant", "apres"]

    assert [
        element["position"] for element in resultat
    ] == (
        ["past", "current", "upcoming"]
        if reperes_connus
        else ["unknown"] * 3
    )

    assert chemin.read_text(encoding="utf-8") == texte


def test_construire_timeline_sans_fiche_affichable(tmp_path):
    chemin = tmp_path / "timeline.json"
    chemin.write_text(
        json.dumps({
            "schema_version": 1,
            "content_version": "2026-10-02",
            "etapes": [],
        }),
        encoding="utf-8",
    )

    assert construire_timeline(
        None,
        date(2026, 3, 19),
        chemin=chemin,
    ) == ()

def source_secondaire_test():
    source = deepcopy(
        donnees_timeline_test()["etapes"][0]["source"]
    )
    source.update({
        "role": "secondary",
        "usage": "cross_check",
        "url": "https://example.org/reference",
        "terms_url": "https://example.org/conditions",
    })
    return source


@pytest.mark.parametrize("principal_approuve", [False, True])
@pytest.mark.parametrize(
    "reutilisation",
    ["to_review", "approved", "rejected"],
)
def test_secondaire_ne_decide_pas_affichage(
    tmp_path, principal_approuve, reutilisation
):
    donnees = donnees_timeline_test()
    etape = donnees["etapes"][0]

    etape["editorial_status"] = "approved"
    etape["reviewed_at"] = "2026-10-02"
    etape["source"]["reuse_status"] = (
        "approved" if principal_approuve else "to_review"
    )

    secondaire = source_secondaire_test()
    secondaire["reuse_status"] = reutilisation
    etape["secondary_sources"] = [secondaire]

    chemin = tmp_path / "timeline.json"
    chemin.write_text(
        json.dumps(donnees),
        encoding="utf-8",
    )

    assert bool(
        charger_etapes_affichables(chemin)
    ) == principal_approuve


@pytest.mark.parametrize(
    "champ, valeur",
    [
        ("role", "primary"),
        ("usage", "rag"),
        ("terms_url", "javascript:alert(1)"),
        ("retrieved_at", "2026-02-30"),
    ],
)
def test_timeline_refuse_secondaire_invalide(
    tmp_path, champ, valeur
):
    donnees = donnees_timeline_test()
    secondaire = source_secondaire_test()
    secondaire[champ] = valeur
    donnees["etapes"][0]["secondary_sources"] = [secondaire]

    chemin = tmp_path / "timeline.json"
    chemin.write_text(
        json.dumps(donnees),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        charger_timeline(chemin)

@pytest.mark.parametrize(
    "positions, index_attendu",
    [
        ((), None),
        (("past",), None),
        (("unknown",), None),
        (("past", "upcoming", "upcoming"), 1),
        (("upcoming", "current"), 1),
        (("current", "current", "upcoming"), 0),
    ],
)
def test_choisir_etape_a_mettre_en_avant(
    positions, index_attendu
):
    elements = tuple(
        {
            "etape": {"id": f"etape_{index}"},
            "position": position,
        }
        for index, position in enumerate(positions)
    )
    avant = deepcopy(elements)

    resultat = choisir_etape_a_mettre_en_avant(elements)

    if index_attendu is None:
        assert resultat is None
    else:
        assert resultat == elements[index_attendu]

    assert elements == avant

@pytest.mark.parametrize(
    "jours_sa, positions, identifiant_attendu",
    [
        (97, ("current", "upcoming"), "echographie_premier_trimestre"),
        (98, ("past", "upcoming"), "echographie_deuxieme_trimestre"),
        (139, ("past", "upcoming"), "echographie_deuxieme_trimestre"),
        (140, ("past", "current"), "echographie_deuxieme_trimestre"),
        (174, ("past", "current"), "echographie_deuxieme_trimestre"),
        (175, ("past", "past"), None),
    ],
)
def test_timeline_reelle_selectionne_la_bonne_fiche(
    jours_sa, positions, identifiant_attendu
):
    from datetime import timedelta

    origine = date(2026, 1, 1)
    reperes = PregnancyJourney(
        dating_method="last_period",
        last_period_date=origine,
    )
    elements = construire_timeline(
        reperes,
        origine + timedelta(days=jours_sa),
    )

    assert tuple(element["etape"]["id"] for element in elements) == (
        "echographie_premier_trimestre",
        "echographie_deuxieme_trimestre",
    )
    assert tuple(element["position"] for element in elements) == positions

    repere = choisir_etape_a_mettre_en_avant(elements)

    if identifiant_attendu is None:
        assert repere is None
    else:
        assert repere is not None
        assert repere["etape"]["id"] == identifiant_attendu

