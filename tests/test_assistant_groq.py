import json
from pathlib import Path

import pytest

import assistant_groq
from corpus_documentaire import charger_corpus


CHEMIN_CORPUS = (
    Path(__file__).resolve().parents[1]
    / "donnees"
    / "corpus_fictif.json"
)


def test_branchement_classification_puis_generation(monkeypatch):
    appels = []

    def faux_appel(messages, *, cle_api, modele):
        assert cle_api == "cle-fictive"
        assert modele == "modele-fictif"

        donnees = json.loads(messages[1]["content"])
        appels.append(donnees)

        if len(appels) == 1:
            assert donnees == {"question": "calendrier"}
            return "GENERAL_INFORMATION"

        assert len(appels) == 2
        assert donnees["question"] == "calendrier"
        assert [
            document["id"]
            for document in donnees["documents"]
        ] == ["calendrier"]

        return "Le calendrier présente les rendez-vous [calendrier]."

    monkeypatch.setattr(
        assistant_groq,
        "generer_reponse_groq",
        faux_appel,
    )

    resultat = assistant_groq.traiter_demande_groq(
        "calendrier",
        charger_corpus(CHEMIN_CORPUS),
        cle_api="cle-fictive",
        modele="modele-fictif",
    )

    assert len(appels) == 2
    assert resultat["statut"] == "references_controlees"
    assert [source["id"] for source in resultat["sources"]] == [
        "calendrier",
    ]


@pytest.mark.parametrize(
    "question, signalement, statut",
    [
        ("", True, "urgence_signalee"),
        (
            "C’est une urgence médicale pour moi.",
            False,
            "urgence_potentielle",
        ),
    ],
)
def test_branchement_urgence_sans_appel(
    monkeypatch,
    question,
    signalement,
    statut,
):
    def appel_interdit(*args, **kwargs):
        pytest.fail("Aucun appel distant ne doit être effectué.")

    monkeypatch.setattr(
        assistant_groq,
        "generer_reponse_groq",
        appel_interdit,
    )

    resultat = assistant_groq.traiter_demande_groq(
        question,
        (),
        cle_api="",
        modele="modele-fictif",
        urgence_signalee=signalement,
    )

    assert resultat["statut"] == statut
    assert resultat["sources"] == ()

@pytest.mark.parametrize("appel_en_echec", [1, 2])
@pytest.mark.parametrize(
    "type_erreur, statut",
    [
        (assistant_groq.RequeteGroqRefusee, "requete_refusee"),
        (
            assistant_groq.GenerationGroqInterrompue,
            "generation_interrompue",
        ),
        (assistant_groq.ReponseGroqVide, "reponse_vide"),
    ],
)
def test_erreur_fournisseur_interrompt_la_chaine(
    monkeypatch,
    appel_en_echec,
    type_erreur,
    statut,
):
    appels = []

    def faux_appel(messages, *, cle_api, modele):
        appels.append(messages)

        if len(appels) == appel_en_echec:
            raise type_erreur("Détail technique fictif")

        return "GENERAL_INFORMATION"

    monkeypatch.setattr(
        assistant_groq,
        "generer_reponse_groq",
        faux_appel,
    )

    resultat = assistant_groq.traiter_demande_groq(
        "calendrier",
        charger_corpus(CHEMIN_CORPUS),
        cle_api="cle-fictive",
        modele="modele-fictif",
    )

    assert len(appels) == appel_en_echec
    assert resultat["statut"] == statut
    assert resultat["sources"] == ()
    assert resultat["reponse"]
    assert "Détail technique fictif" not in resultat["reponse"]