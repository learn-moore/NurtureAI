from copy import deepcopy
from pathlib import Path

import pytest
import json

from corpus_documentaire import charger_corpus
from recherche_documentaire import rechercher_corpus
from rapport_recherche import construire_rapport_recherche
from contexte_documentaire import construire_contexte
from citations_documentaires import trouver_citations_inconnues
from messages_assistant import preparer_messages


CHEMIN = Path(__file__).resolve().parents[1] / "donnees" / "corpus_fictif.json"


@pytest.fixture
def corpus():
    return charger_corpus(CHEMIN)


@pytest.mark.parametrize(
    "question, theme, attendus",
    [
        ("profil", None, ["calendrier", "sauvegarde", "export"]),
        ("profil", "conception", ["export"]),
        ("profil", "nutrition", []),
        ("calendrier rendez-vous", None, ["calendrier"]),
        ("sauvegarde navigateur", None, ["sauvegarde"]),
        ("exporter", None, []),
        ("banane", None, []),
    ],
)
def test_atelier_classement(corpus, question, theme, attendus):
    resultats = rechercher_corpus(question, corpus, theme=theme)
    assert [r["passage"]["id"] for r in resultats] == attendus


def test_atelier_mots_expliquent_score(corpus):
    resultats = rechercher_corpus("calendrier calendrier rendez-vous", corpus)
    assert len(resultats) == 1
    assert resultats[0]["mots_communs"] == ("calendrier", "rendez", "vous")
    assert resultats[0]["score"] == len(resultats[0]["mots_communs"])


def test_atelier_recherche_ne_modifie_pas_corpus(corpus):
    avant = deepcopy(corpus)
    rechercher_corpus("profil", corpus)
    assert corpus == avant


def test_atelier_rapport_sans_resultat():
    texte = construire_rapport_recherche("banane", ())
    assert "Question : banane" in texte
    assert "Aucun passage correspondant." in texte
    assert "URL :" not in texte


def test_atelier_rapport_conserve_passages_et_sources(corpus):
    resultats = rechercher_corpus("profil", corpus)
    texte = construire_rapport_recherche("profil", resultats)
    for numero, resultat in enumerate(resultats, start=1):
        passage = resultat["passage"]
        assert f"[{numero}] {passage['title']}" in texte
        assert passage["content"] in texte
        assert f"URL : {passage['url']}" in texte
    assert "https://example.org/brouillon" not in texte
    assert "https://example.org/recoupement" not in texte
    assert "https://example.org/droits" not in texte


def test_atelier_chargement_independant_du_dossier(corpus, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert charger_corpus(CHEMIN) == corpus


def test_contexte_depuis_recherche_sur_corpus(corpus):
    resultats = rechercher_corpus("profil", corpus)

    contexte = construire_contexte(resultats)
    documents = json.loads(contexte)

    assert [document["id"] for document in documents] == [
        "calendrier",
        "sauvegarde",
        "export",
    ]
    assert [document["url"] for document in documents] == [
        resultat["passage"]["url"]
        for resultat in resultats
    ]


def test_contexte_limite_depuis_recherche_sur_corpus(corpus):
    resultats = rechercher_corpus("profil", corpus)

    contexte_premier_resultat = construire_contexte(resultats[:1])
    budget = len(contexte_premier_resultat)

    contexte = construire_contexte(
        resultats,
        max_caracteres=budget,
    )
    documents = json.loads(contexte)

    assert len(contexte) <= budget
    assert [document["id"] for document in documents] == [
        "calendrier",
    ]
    assert documents[0]["url"] == "https://example.org/calendrier"

def test_citations_limitees_aux_documents_transmis(corpus):
    resultats = rechercher_corpus("profil", corpus)

    assert [resultat["passage"]["id"] for resultat in resultats] == [
        "calendrier",
        "sauvegarde",
        "export",
    ]

    budget = len(construire_contexte(resultats[:1]))
    messages = preparer_messages(
        "profil",
        resultats,
        max_caracteres=budget,
    )

    donnees_transmises = json.loads(messages[1]["content"])
    documents_transmis = donnees_transmises["documents"]

    assert [document["id"] for document in documents_transmis] == [
        "calendrier",
    ]

    contexte_transmis = json.dumps(
        documents_transmis,
        ensure_ascii=False,
    )
    reponse = (
        "Les rendez-vous figurent dans le calendrier [calendrier]. "
        "Le profil est conservé dans le navigateur [sauvegarde]."
    )

    assert trouver_citations_inconnues(
        reponse,
        contexte_transmis,
    ) == ("sauvegarde",)

