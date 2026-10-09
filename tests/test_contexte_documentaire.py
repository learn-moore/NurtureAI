import json

import pytest

from contexte_documentaire import construire_contexte


@pytest.fixture
def resultats():
    return (
        {
            "passage": {
                "id": "premier",
                "title": "Calendrier",
                "content": "Les rendez-vous sont présentés ici.",
                "source": "Source fictive",
                "url": "https://example.org/calendrier",
            },
            "score": 2,
        },
        {
            "passage": {
                "id": "second",
                "title": "Profil",
                "content": "Le profil est enregistré.",
                "source": "Source fictive",
                "url": "https://example.org/profil",
            },
            "score": 1,
        },
    )


def test_contexte_conserve_ordre_contenu_et_sources(resultats):
    documents = json.loads(construire_contexte(resultats))

    assert documents == [
        resultat["passage"] for resultat in resultats
    ]


def test_contexte_accepte_taille_exacte(resultats):
    complet = construire_contexte(resultats)

    assert construire_contexte(
        resultats,
        max_caracteres=len(complet),
    ) == complet


def test_contexte_retire_passage_entier_si_budget_depasse(resultats):
    complet = construire_contexte(resultats)
    limite = len(complet) - 1

    contexte = construire_contexte(resultats, max_caracteres=limite)

    assert len(contexte) <= limite
    assert json.loads(contexte) == [resultats[0]["passage"]]


def test_contexte_vide_si_premier_passage_trop_long(resultats):
    assert construire_contexte(resultats, max_caracteres=2) == "[]"


def test_contexte_sans_resultat():
    assert construire_contexte(()) == "[]"


@pytest.mark.parametrize("limite", [0, 1, -1, True, 3.5, "6000"])
def test_contexte_refuse_budget_invalide(limite):
    with pytest.raises(ValueError):
        construire_contexte((), max_caracteres=limite)