import pytest
import json

from corpus_documentaire import valider_passage, valider_corpus, charger_corpus


@pytest.fixture
def passage():
    return {
        "id": "document_test",
        "topic": "suivi_grossesse",
        "title": "Document fictif",
        "content": "Texte réservé aux tests.",
        "source": "Source fictive",
        "url": "https://example.org/document",
        "country": "FR",
        "publication_date": None,
        "retrieved_at": "2026-10-05",
        "reviewed_at": None,
        "editorial_status": "draft",
        "reuse_status": "to_review",
        "usage": "rag",
    }


def test_valider_passage_accepte_champs_textuels(passage):
    assert valider_passage(passage) is None


@pytest.mark.parametrize("valeur", [None, [], "texte"])
def test_valider_passage_refuse_autre_chose_qu_un_objet(valeur):
    with pytest.raises(ValueError, match="Un passage doit être un objet"):
        valider_passage(valeur)


@pytest.mark.parametrize(
    "champ",
    ["id", "topic", "title", "content", "source", "url", "country"],
)
def test_valider_passage_refuse_champ_manquant(passage, champ):
    del passage[champ]

    with pytest.raises(ValueError, match=champ):
        valider_passage(passage)


@pytest.mark.parametrize("valeur", ["", "   ", None, 42])
def test_valider_passage_refuse_contenu_invalide(passage, valeur):
    passage["content"] = valeur

    with pytest.raises(ValueError, match="content"):
        valider_passage(passage)


def test_valider_passage_refuse_identifiant_avec_espaces(passage):
    passage["id"] = " document_test "

    with pytest.raises(ValueError, match="identifiant"):
        valider_passage(passage)

@pytest.mark.parametrize(
    "url",
    [
        "http://example.org/document",
        "/document",
        "https:///document",
        "https://utilisateur:secret@example.org/document",
        "https://example.org/un document",
        "https://example.org/\ndocument",
        "https://example.org:abc/document",
        "https://example.org:70000/document",
        "https://example.org:0/document",
        "https://[adresse-invalide/document",
    ],
)
def test_valider_passage_refuse_url_invalide(passage, url):
    passage["url"] = url

    with pytest.raises(ValueError, match="URL"):
        valider_passage(passage)


def test_valider_passage_accepte_url_avec_ancre(passage):
    passage["url"] = "https://example.org/document#section"

    assert valider_passage(passage) is None

@pytest.mark.parametrize(
    "champ",
    ["publication_date", "retrieved_at", "reviewed_at"],
)
def test_valider_passage_refuse_date_manquante(passage, champ):
    del passage[champ]

    with pytest.raises(ValueError, match=champ):
        valider_passage(passage)


@pytest.mark.parametrize(
    "champ, valeur",
    [
        ("retrieved_at", None),
        ("retrieved_at", "20261005"),
        ("retrieved_at", "2026-02-30"),
        ("publication_date", "octobre 2026"),
        ("reviewed_at", "2026-10-05T12:00:00"),
        ("reviewed_at", 20261005),
    ],
)
def test_valider_passage_refuse_date_invalide(passage, champ, valeur):
    passage[champ] = valeur

    with pytest.raises(ValueError, match=champ):
        valider_passage(passage)


@pytest.mark.parametrize(
    "champ, valeur, message",
    [
        ("publication_date", "2026-10-06", "publication"),
        ("reviewed_at", "2026-10-04", "revue"),
    ],
)
def test_valider_passage_refuse_chronologie_incoherente(
    passage, champ, valeur, message
):
    passage[champ] = valeur

    with pytest.raises(ValueError, match=message):
        valider_passage(passage)


def test_valider_passage_accepte_dates_identiques(passage):
    passage["publication_date"] = "2026-10-05"
    passage["reviewed_at"] = "2026-10-05"

    assert valider_passage(passage) is None

@pytest.mark.parametrize(
    "champ",
    ["editorial_status", "reuse_status", "usage"],
)
@pytest.mark.parametrize("valeur", [None, "", "inconnu", True, []])
def test_valider_passage_refuse_statut_invalide(passage, champ, valeur):
    passage[champ] = valeur

    with pytest.raises(ValueError, match=champ):
        valider_passage(passage)


@pytest.mark.parametrize(
    "champ",
    ["editorial_status", "reuse_status", "usage"],
)
def test_valider_passage_refuse_statut_manquant(passage, champ):
    del passage[champ]

    with pytest.raises(ValueError, match=champ):
        valider_passage(passage)


def test_valider_passage_refuse_approbation_sans_revue(passage):
    passage["editorial_status"] = "approved"

    with pytest.raises(ValueError, match="reviewed_at"):
        valider_passage(passage)


def test_valider_passage_accepte_approbation_avec_revue(passage):
    passage["editorial_status"] = "approved"
    passage["reviewed_at"] = "2026-10-05"

    assert valider_passage(passage) is None


def test_valider_passage_accepte_reference_de_recoupement(passage):
    passage["usage"] = "cross_check"

    assert valider_passage(passage) is None

def test_valider_corpus_accepte_corpus_vide():
    assert valider_corpus([]) == ()


def test_valider_corpus_conserve_ordre_et_brouillons(passage):
    autre = {
        **passage,
        "id": "autre_document",
        "content": "Autre contenu fictif.",
    }

    assert valider_corpus([passage, autre]) == (passage, autre)


@pytest.mark.parametrize("valeur", [None, {}, "texte", ()])
def test_valider_corpus_refuse_autre_chose_qu_une_liste(valeur):
    with pytest.raises(ValueError, match="liste"):
        valider_corpus(valeur)


def test_valider_corpus_refuse_identifiant_duplique(passage):
    approuve = {
        **passage,
        "editorial_status": "approved",
        "reviewed_at": "2026-10-05",
    }

    with pytest.raises(ValueError, match="en double"):
        valider_corpus([approuve, passage])


def test_valider_corpus_refuse_passage_invalide(passage):
    invalide = {
        **passage,
        "id": "document_invalide",
        "content": "",
    }

    with pytest.raises(ValueError, match="content"):
        valider_corpus([passage, invalide])

def test_charger_corpus_lit_et_valide(tmp_path, passage):
    chemin = tmp_path / "corpus.json"
    chemin.write_text(
        json.dumps({
            "schema_version": 1,
            "passages": [passage],
        }),
        encoding="utf-8",
    )

    assert charger_corpus(chemin) == (passage,)


@pytest.mark.parametrize(
    "contenu",
    [
        b"{",
        b"\xff",
        b"[]",
        b'{"schema_version": true, "passages": []}',
        b'{"schema_version": 2, "passages": []}',
        b'{"schema_version": 1, "passages": {}}',
        b'{"schema_version": 1}',
    ],
)
def test_charger_corpus_refuse_fichier_invalide(tmp_path, contenu):
    chemin = tmp_path / "corpus.json"
    chemin.write_bytes(contenu)

    with pytest.raises(ValueError):
        charger_corpus(chemin)


def test_charger_corpus_refuse_fichier_absent(tmp_path):
    with pytest.raises(ValueError, match="Impossible de lire"):
        charger_corpus(tmp_path / "absent.json")


def test_charger_corpus_refuse_passage_invalide(tmp_path, passage):
    passage["content"] = ""
    chemin = tmp_path / "corpus.json"
    chemin.write_text(
        json.dumps({
            "schema_version": 1,
            "passages": [passage],
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="content"):
        charger_corpus(chemin)

