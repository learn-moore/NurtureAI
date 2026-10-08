import pytest
import json

from recherche_documentaire import extraire_mots, extraire_mots_recherche, calculer_score_lexical, rechercher_passages, rechercher_corpus
from corpus_documentaire import charger_corpus


@pytest.fixture
def passage_valide():
    return {
        "id": "test",
        "topic": "suivi_grossesse",
        "title": "Document fictif",
        "content": "Calendrier.",
        "source": "Source fictive",
        "url": "https://example.org/document",
        "country": "FR",
        "publication_date": None,
        "retrieved_at": "2026-10-05",
        "reviewed_at": "2026-10-05",
        "editorial_status": "approved",
        "reuse_status": "approved",
        "usage": "rag",
    }

@pytest.mark.parametrize(
    "texte, attendu",
    [
        ("ÉCHOGRAPHIE échographie", {"echographie"}),
        ("préparer un rendez-vous", {"preparer", "un", "rendez", "vous"}),
        ("L’échographie à 9 SA", {"l", "echographie", "a", "9", "sa"}),
        ("cœur", {"coeur"}),
        ("", set()),
        ("   ?! ", set()),
    ],
)
def test_extraire_mots(texte, attendu):
    assert extraire_mots(texte) == attendu


@pytest.mark.parametrize("texte", [None, 42, ["échographie"]])
def test_extraire_mots_refuse_type_invalide(texte):
    with pytest.raises(ValueError):
        extraire_mots(texte)

@pytest.mark.parametrize(
    "question, passage, attendu",
    [
        ("calendrier rendez-vous", "Le calendrier présente les rendez-vous.", 3),
        ("export profil", "Exporter le profil.", 1),
        ("calendrier", "calendrier calendrier calendrier", 1),
        ("ÉCHOGRAPHIE", "échographie", 1),
        ("calendrier", "Sauvegarde locale.", 0),
        ("", "Calendrier des rendez-vous.", 0),
        ("profil", "", 0),
    ],
)
def test_calculer_score_lexical(question, passage, attendu):
    assert calculer_score_lexical(question, passage) == attendu

def test_rechercher_passages_classe_et_limite():
    passages = (
        {"id": "court", "content": "Calendrier."},
        {"id": "hors_sujet", "content": "Sauvegarde locale."},
        {"id": "complet", "content": "Calendrier des rendez-vous."},
        {"id": "autre", "content": "Rendez-vous."},
    )

    resultats = rechercher_passages(
        "calendrier rendez-vous",
        passages,
        limite=2,
    )

    assert [
        (resultat["passage"]["id"], resultat["score"])
        for resultat in resultats
    ] == [
        ("complet", 3),
        ("autre", 2),
    ]


def test_rechercher_passages_conserve_ordre_des_egalites():
    passages = (
        {"id": "premier", "content": "Profil local."},
        {"id": "second", "content": "Profil exporté."},
    )

    resultats = rechercher_passages("profil", passages)

    assert [
        resultat["passage"]["id"] for resultat in resultats
    ] == ["premier", "second"]


@pytest.mark.parametrize("question", ["", "?!", "échographie"])
def test_rechercher_passages_sans_correspondance(question):
    passages = (
        {"id": "profil", "content": "Sauvegarde locale."},
    )

    assert rechercher_passages(question, passages) == ()


def test_rechercher_passages_corpus_vide():
    assert rechercher_passages("profil", ()) == ()


@pytest.mark.parametrize("limite", [0, -1, True, 1.5, "3"])
def test_rechercher_passages_refuse_limite_invalide(limite):
    with pytest.raises(ValueError):
        rechercher_passages("profil", (), limite=limite)

def test_mots_recherche_retire_articles():
    assert extraire_mots_recherche(
        "Le calendrier des rendez-vous"
    ) == {"calendrier", "rendez", "vous"}


def test_mots_recherche_conserve_negation_et_age():
    assert extraire_mots_recherche(
        "pas de mouvement à 9 SA"
    ) == {"pas", "mouvement", "9", "sa"}


def test_score_ignore_correspondance_sur_article():
    assert calculer_score_lexical(
        "le calendrier", "le profil"
    ) == 0


@pytest.mark.parametrize("question", ["le calendrier", "le de la"])
def test_recherche_ne_retient_pas_les_articles(question):
    passages = (
        {"id": "profil", "content": "Le profil de la personne."},
    )

    assert rechercher_passages(question, passages) == ()

def test_rechercher_corpus_filtre_avant_classement(passage_valide):
    corpus = (
        {
            **passage_valide,
            "id": "brouillon",
            "content": "Calendrier rendez-vous profil.",
            "editorial_status": "draft",
            "reviewed_at": None,
        },
        {
            **passage_valide,
            "id": "retenu",
        },
    )

    resultats = rechercher_corpus(
        "calendrier rendez-vous profil",
        corpus,
        limite=1,
    )

    assert [
        resultat["passage"]["id"] for resultat in resultats
    ] == ["retenu"]


@pytest.mark.parametrize(
    "champ, valeur",
    [
        ("editorial_status", "draft"),
        ("editorial_status", "rejected"),
        ("reuse_status", "to_review"),
        ("reuse_status", "rejected"),
        ("usage", "cross_check"),
    ],
)
def test_rechercher_corpus_exclut_passage_non_autorise(
    passage_valide, champ, valeur
):
    passage_valide[champ] = valeur

    assert rechercher_corpus("calendrier", (passage_valide,)) == ()


@pytest.mark.parametrize(
    "champ",
    ["editorial_status", "reuse_status", "usage"],
)
def test_rechercher_corpus_refuse_autorisation_manquante(
    passage_valide, champ
):
    del passage_valide[champ]

    with pytest.raises(ValueError, match=champ):
        rechercher_corpus("calendrier", (passage_valide,))

def test_recherche_depuis_fichier_valide(tmp_path):
    base = {
        "topic": "suivi_grossesse",
        "title": "Document fictif",
        "source": "Source fictive",
        "url": "https://example.org/document",
        "country": "FR",
        "publication_date": None,
        "retrieved_at": "2026-10-05",
        "reviewed_at": "2026-10-05",
        "editorial_status": "approved",
        "reuse_status": "approved",
        "usage": "rag",
    }

    passages = [
        {
            **base,
            "id": "brouillon",
            "content": "Calendrier rendez-vous profil.",
            "editorial_status": "draft",
            "reviewed_at": None,
        },
        {
            **base,
            "id": "recoupement",
            "content": "Calendrier rendez-vous profil.",
            "usage": "cross_check",
        },
        {
            **base,
            "id": "droits_non_confirmes",
            "content": "Calendrier rendez-vous profil.",
            "reuse_status": "to_review",
        },
        {
            **base,
            "id": "retenu",
            "content": "Calendrier.",
        },
    ]

    chemin = tmp_path / "corpus.json"
    chemin.write_text(
        json.dumps({
            "schema_version": 1,
            "passages": passages,
        }),
        encoding="utf-8",
    )

    corpus = charger_corpus(chemin)
    resultats = rechercher_corpus(
        "calendrier rendez-vous profil",
        corpus,
        limite=1,
    )

    assert len(corpus) == 4
    assert len(resultats) == 1

    resultat = resultats[0]
    assert resultat["passage"]["id"] == "retenu"
    assert resultat["score"] == 1
    assert resultat["passage"]["url"] == "https://example.org/document"

    assert rechercher_corpus("banane", corpus) == ()

def test_recherche_trouve_mot_present_uniquement_dans_titre():
    passages = ({
        "id": "calendrier",
        "title": "Calendrier",
        "content": "Présentation des rendez-vous.",
    },)

    resultats = rechercher_passages("calendrier", passages)

    assert len(resultats) == 1
    assert resultats[0]["passage"]["id"] == "calendrier"
    assert resultats[0]["score"] == 1


def test_recherche_ne_compte_pas_deux_fois_le_meme_mot():
    passages = ({
        "id": "calendrier",
        "title": "Calendrier",
        "content": "Le calendrier présente les rendez-vous.",
    },)

    resultats = rechercher_passages("calendrier", passages)

    assert resultats[0]["score"] == 1


def test_recherche_ignore_mots_des_metadonnees():
    passages = ({
        "id": "calendrier",
        "title": "Document",
        "content": "Présentation du profil.",
        "source": "Calendrier",
        "url": "https://example.org/calendrier",
    },)

    assert rechercher_passages("calendrier", passages) == ()

@pytest.mark.parametrize("question", ["calendrier", ""])
def test_rechercher_corpus_refuse_approbation_sans_revue(
    passage_valide, question
):
    passage_valide["reviewed_at"] = None

    with pytest.raises(ValueError, match="reviewed_at"):
        rechercher_corpus(question, (passage_valide,))


def test_rechercher_corpus_refuse_doublons(passage_valide):
    with pytest.raises(ValueError, match="en double"):
        rechercher_corpus(
            "calendrier",
            (passage_valide, passage_valide.copy()),
        )

@pytest.mark.parametrize(
    "theme, identifiants",
    [
        (None, ["suivi", "nutrition"]),
        ("suivi_grossesse", ["suivi"]),
        ("nutrition", ["nutrition"]),
        ("conception", []),
    ],
)
def test_rechercher_corpus_filtre_par_theme(
    passage_valide, theme, identifiants
):
    corpus = (
        {
            **passage_valide,
            "id": "suivi",
            "topic": "suivi_grossesse",
        },
        {
            **passage_valide,
            "id": "nutrition",
            "topic": "nutrition",
        },
    )

    resultats = rechercher_corpus(
        "calendrier",
        corpus,
        theme=theme,
    )

    assert [
        resultat["passage"]["id"] for resultat in resultats
    ] == identifiants


@pytest.mark.parametrize("theme", ["inconnu", "", True, []])
def test_rechercher_corpus_refuse_filtre_theme_invalide(theme):
    with pytest.raises(ValueError, match="Thème"):
        rechercher_corpus("calendrier", (), theme=theme)


def test_filtre_theme_ne_masque_pas_un_passage_invalide(passage_valide):
    invalide = {
        **passage_valide,
        "topic": "nutrition",
        "content": "",
    }

    with pytest.raises(ValueError, match="content"):
        rechercher_corpus(
            "calendrier",
            (invalide,),
            theme="suivi_grossesse",
        )

