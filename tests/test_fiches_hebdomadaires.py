import pytest
import json
from copy import deepcopy

from fiches_hebdomadaires import selectionner_fiche_semaine, fiche_hebdomadaire_affichable, charger_fiches_hebdomadaires


@pytest.mark.parametrize(
    "jours_sa, identifiant_attendu",
    [
        (None, None),
        (62, None),
        (63, "semaine_9"),
        (69, "semaine_9"),
        (70, None),
        (77, "semaine_11"),
        (83, "semaine_11"),
        (84, None),
    ],
)
def test_selection_semaine_exacte(jours_sa, identifiant_attendu):
    fiches = (
        {"id": "semaine_9", "week_sa": 9},
        {"id": "semaine_11", "week_sa": 11},
    )

    resultat = selectionner_fiche_semaine(fiches, jours_sa)

    if identifiant_attendu is None:
        assert resultat is None
    else:
        assert resultat is not None
        assert resultat["id"] == identifiant_attendu


@pytest.mark.parametrize(
    "jours_sa",
    [-1, True, False, 63.5, "63"],
)
def test_selection_refuse_age_invalide(jours_sa):
    with pytest.raises(ValueError):
        selectionner_fiche_semaine((), jours_sa)


def test_selection_refuse_semaine_ambigue():
    fiches = (
        {"week_sa": 9},
        {"week_sa": 9},
    )

    with pytest.raises(ValueError):
        selectionner_fiche_semaine(fiches, 63)

@pytest.fixture
def fiche_semaine():
    return {
        "id": "semaine_test",
        "week_sa": 9,
        "title": "Fiche fictive",
        "body": "Contenu de test.",
        "editorial_status": "approved",
        "reviewed_at": "2026-10-04",
        "source": {
            "name": "Source fictive",
            "title": "Document de test",
            "url": "https://example.org/document",
            "section": "Test",
            "publication_date": None,
            "displayed_date": None,
            "retrieved_at": "2026-10-04",
            "reuse_status": "approved",
        },
    }


@pytest.mark.parametrize(
    "statut", ["draft", "approved", "rejected"]
)
@pytest.mark.parametrize(
    "reutilisation", ["to_review", "approved", "rejected"]
)
@pytest.mark.parametrize("revue", [None, "2026-10-04"])
def test_conditions_affichage(
    fiche_semaine, statut, reutilisation, revue
):
    fiche_semaine["editorial_status"] = statut
    fiche_semaine["source"]["reuse_status"] = reutilisation
    fiche_semaine["reviewed_at"] = revue

    attendu = (
        statut == "approved"
        and reutilisation == "approved"
        and revue is not None
    )

    assert fiche_hebdomadaire_affichable(fiche_semaine) == attendu


@pytest.mark.parametrize(
    "champ, valeur",
    [
        ("week_sa", True),
        ("week_sa", -1),
        ("week_sa", 9.5),
        ("id", " test"),
        ("title", ""),
        ("body", " "),
        ("source", None),
    ],
)
def test_fiche_hebdomadaire_invalide(
    fiche_semaine, champ, valeur
):
    fiche_semaine[champ] = valeur

    with pytest.raises(ValueError):
        fiche_hebdomadaire_affichable(fiche_semaine)

def ecrire_fiches(tmp_path, fiches):
    chemin = tmp_path / "fiches.json"
    chemin.write_text(
        json.dumps({
            "schema_version": 1,
            "content_version": "2026-10-04",
            "fiches": fiches,
        }),
        encoding="utf-8",
    )
    return chemin


def test_charger_fiches_vide_independant_du_dossier(
    tmp_path, monkeypatch
):
    chemin = ecrire_fiches(tmp_path, [])

    monkeypatch.chdir(tmp_path)

    assert charger_fiches_hebdomadaires(chemin) == ()


def test_charger_fiches_filtre_et_trie(tmp_path, fiche_semaine):
    suivante = deepcopy(fiche_semaine)
    suivante.update(id="semaine_11", week_sa=11)

    brouillon = deepcopy(fiche_semaine)
    brouillon.update(
        id="semaine_10",
        week_sa=10,
        editorial_status="draft",
    )

    chemin = ecrire_fiches(
        tmp_path, [suivante, brouillon, fiche_semaine]
    )

    assert charger_fiches_hebdomadaires(chemin) == (
        fiche_semaine, suivante
    )


@pytest.mark.parametrize("champ", ["id", "week_sa"])
def test_charger_fiches_refuse_doublon(
    tmp_path, fiche_semaine, champ
):
    autre = deepcopy(fiche_semaine)
    autre.update(
        id="autre", week_sa=10, editorial_status="draft"
    )
    autre[champ] = fiche_semaine[champ]

    chemin = ecrire_fiches(tmp_path, [fiche_semaine, autre])

    with pytest.raises(ValueError):
        charger_fiches_hebdomadaires(chemin)


@pytest.mark.parametrize(
    "champ, valeur",
    [
        ("schema_version", True),
        ("schema_version", 2),
        ("content_version", "2026-02-30"),
        ("fiches", {}),
        ("fiches", [None]),
    ],
)
def test_charger_fiches_refuse_structure(
    tmp_path, champ, valeur
):
    chemin = ecrire_fiches(tmp_path, [])
    donnees = json.loads(chemin.read_text(encoding="utf-8"))
    donnees[champ] = valeur
    chemin.write_text(json.dumps(donnees), encoding="utf-8")

    with pytest.raises(ValueError):
        charger_fiches_hebdomadaires(chemin)


@pytest.mark.parametrize(
    "contenu", [None, b"{", b"[]", b"\xff"]
)
def test_charger_fiches_refuse_fichier_illisible(
    tmp_path, contenu
):
    chemin = tmp_path / "fiches.json"

    if contenu is not None:
        chemin.write_bytes(contenu)

    with pytest.raises(ValueError):
        charger_fiches_hebdomadaires(chemin)

def test_fiche_reelle_9_sa_affichee_aux_bonnes_dates(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    fiches = charger_fiches_hebdomadaires()

    for jours in (63, 69):
        fiche = selectionner_fiche_semaine(fiches, jours)

        assert fiche is not None
        assert fiche["id"] == "developpement_9_sa"
        assert fiche["attribution"]["mode"] == "reference"
        assert fiche["reviewed_at"] == "2026-10-05"

    for jours in (62, 70):
        assert selectionner_fiche_semaine(fiches, jours) is None

@pytest.mark.parametrize("mode", ["licence", "reference"])
def test_fiche_accepte_attribution(fiche_semaine, mode):
    fiche_semaine["attribution"] = {
        "mode": mode,
        "text": "Mention de test.",
        "url": "https://example.org/conditions",
    }

    assert fiche_hebdomadaire_affichable(fiche_semaine) is True


@pytest.mark.parametrize(
    "attribution",
    [
        None,
        {},
        {
            "mode": "inconnu",
            "text": "Mention de test.",
            "url": "https://example.org/licence",
        },
        {
            "mode": "licence",
            "text": " ",
            "url": "https://example.org/licence",
        },
        {
            "mode": "licence",
            "text": "Mention de test.",
            "url": "http://example.org/licence",
        },
        {
            "mode": "licence",
            "text": "Mention de test.",
            "url": "https://utilisateur:secret@example.org/licence",
        },
    ],
)
def test_fiche_refuse_attribution_invalide(
    fiche_semaine, attribution
):
    fiche_semaine["attribution"] = attribution

    with pytest.raises(ValueError):
        fiche_hebdomadaire_affichable(fiche_semaine)

