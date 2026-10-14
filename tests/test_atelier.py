from copy import deepcopy
from pathlib import Path

import pytest
import json

from corpus_documentaire import charger_corpus
from recherche_documentaire import rechercher_corpus
from rapport_recherche import construire_rapport_recherche
from contexte_documentaire import construire_contexte
from citations_documentaires import trouver_citations_inconnues, retrouver_sources_citees
from messages_assistant import preparer_messages
from generation_simulee import generer_reponse_simulee

import assistant_documentaire


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

@pytest.mark.parametrize(
    "theme, identifiant_attendu",
    [
        ("suivi_grossesse", "calendrier"),
        ("conception", "export"),
    ],
)
def test_generation_simulee_utilise_document_transmis(
    corpus,
    theme,
    identifiant_attendu,
):
    resultats = rechercher_corpus("profil", corpus, theme=theme)
    messages = preparer_messages("profil", resultats)

    reponse = generer_reponse_simulee(messages)

    donnees = json.loads(messages[1]["content"])
    contexte_transmis = json.dumps(
        donnees["documents"],
        ensure_ascii=False,
    )
    sources = retrouver_sources_citees(reponse, contexte_transmis)

    assert "Démonstration sur un corpus fictif." in reponse
    assert resultats[0]["passage"]["content"] in reponse
    assert [source["id"] for source in sources] == [
        identifiant_attendu,
    ]
    assert sources[0]["url"] == (
        f"https://example.org/{identifiant_attendu}"
    )


def test_generation_simulee_refuse_messages_vides():
    with pytest.raises(ValueError, match="nécessite des messages"):
        generer_reponse_simulee(())

@pytest.mark.parametrize(
    "question, budget",
    [
        ("banane", 6000),
        ("profil", 2),
    ],
)
def test_assistant_ne_genere_pas_sans_contexte(
    corpus,
    monkeypatch,
    question,
    budget,
):
    resultats = rechercher_corpus(question, corpus)

    def generation_interdite(messages):
        pytest.fail("Le générateur ne devait pas être appelé.")

    monkeypatch.setattr(
        assistant_documentaire,
        "generer_reponse_simulee",
        generation_interdite,
    )

    resultat = assistant_documentaire.preparer_reponse_simulee(
        question,
        resultats,
        max_caracteres=budget,
    )

    assert resultat["statut"] == "sans_contexte"
    assert resultat["sources"] == ()
    assert "Aucun passage disponible" in resultat["reponse"]


def test_assistant_refuse_reference_inventee(corpus, monkeypatch):
    resultats = rechercher_corpus("profil", corpus)
    appels = []

    def generation_invalide(messages):
        appels.append(messages)
        return "Une information fictive [invente]."

    monkeypatch.setattr(
        assistant_documentaire,
        "generer_reponse_simulee",
        generation_invalide,
    )

    with pytest.raises(ValueError, match="invente"):
        assistant_documentaire.preparer_reponse_simulee(
            "profil",
            resultats,
        )

    assert len(appels) == 1

@pytest.mark.parametrize("reponse", ["", "   ", None, 42])
def test_assistant_refuse_generation_inexploitable(
    corpus,
    monkeypatch,
    reponse,
):
    resultats = rechercher_corpus("profil", corpus)

    def generation_inexploitable(messages):
        return reponse

    monkeypatch.setattr(
        assistant_documentaire,
        "generer_reponse_simulee",
        generation_inexploitable,
    )

    with pytest.raises(ValueError, match="texte non vide"):
        assistant_documentaire.preparer_reponse_simulee(
            "profil",
            resultats,
        )

@pytest.mark.parametrize(
    "reponse",
    [
        "Les documents sont insuffisants pour répondre.",
        "Le calendrier présente les rendez-vous.",
    ],
)
def test_assistant_signale_absence_de_citation(
    corpus,
    monkeypatch,
    reponse,
):
    resultats = rechercher_corpus("profil", corpus)

    def generation_sans_citation(messages):
        return reponse

    monkeypatch.setattr(
        assistant_documentaire,
        "generer_reponse_simulee",
        generation_sans_citation,
    )

    resultat = assistant_documentaire.preparer_reponse_simulee(
        "profil",
        resultats,
    )

    assert resultat["statut"] == "sans_citation"
    assert resultat["reponse"] == reponse
    assert resultat["sources"] == ()

def test_assistant_utilise_generateur_fourni(corpus):
    resultats = rechercher_corpus("profil", corpus)
    appels = []

    def autre_generateur(messages):
        appels.append(messages)
        return "Le profil est conservé dans le navigateur [sauvegarde]."

    resultat = assistant_documentaire.preparer_reponse(
        "profil",
        resultats,
        generer=autre_generateur,
    )

    assert len(appels) == 1

    messages_recus = appels[0]
    assert [message["role"] for message in messages_recus] == [
        "system",
        "user",
    ]

    donnees = json.loads(messages_recus[1]["content"])
    assert donnees["question"] == "profil"
    assert [document["id"] for document in donnees["documents"]] == [
        "calendrier",
        "sauvegarde",
        "export",
    ]

    assert resultat["statut"] == "references_controlees"
    assert resultat["reponse"] == (
        "Le profil est conservé dans le navigateur [sauvegarde]."
    )
    assert [source["id"] for source in resultat["sources"]] == [
        "sauvegarde",
    ]
    assert resultat["sources"][0]["url"] == (
        "https://example.org/sauvegarde"
    )

def test_assistant_transmet_indisponibilite_generateur(corpus):
    resultats = rechercher_corpus("profil", corpus)
    appels = []

    def generateur_indisponible(messages):
        appels.append(messages)
        raise assistant_documentaire.GenerationIndisponible(
            "Indisponibilité simulée"
        )

    with pytest.raises(
        assistant_documentaire.GenerationIndisponible,
        match="Indisponibilité simulée",
    ):
        assistant_documentaire.preparer_reponse(
            "profil",
            resultats,
            generer=generateur_indisponible,
        )

    assert len(appels) == 1

