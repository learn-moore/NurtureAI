from pathlib import Path
from copy import deepcopy


import pytest

from corpus_documentaire import charger_corpus
from recherche_documentaire import (
    rechercher_corpus,
    rechercher_passages,
)


CHEMIN = (
    Path(__file__).resolve().parents[1]
    / "donnees"
    / "corpus_medical.json"
)


def test_corpus_medical_charge_les_passages_retenus():
    corpus = charger_corpus(CHEMIN)

    attendus = {
        "conception_consultation_objectif",
        "conception_consultation_preparation",
    }
    passages = {
        passage["id"]: passage
        for passage in corpus
    }

    assert attendus <= passages.keys()

    for identifiant in attendus:
        passage = passages[identifiant]
        assert passage["editorial_status"] == "approved"
        assert passage["reuse_status"] == "approved"
        assert passage["reviewed_at"] == "2026-10-22"


@pytest.mark.parametrize(
    "question",
    [
        "À quoi sert une consultation avant une grossesse ?",
        "Quels sujets préparer pour cette consultation ?",
    ],
)
def test_brouillons_medicaux_exclus_de_la_recherche(question):
    corpus = charger_corpus(CHEMIN)

    corpus = deepcopy(corpus)

    for passage in corpus:
        passage["editorial_status"] = "draft"
        passage["reviewed_at"] = None

    # Le texte correspond bien à la recherche lexicale.
    assert rechercher_passages(question, corpus)

    # Les statuts interdisent néanmoins son utilisation.
    assert rechercher_corpus(question, corpus) == ()

def test_version_source_conservee_dans_contexte_et_reference():
    import json

    from contexte_documentaire import construire_contexte
    from citations_documentaires import retrouver_sources_citees

    passage = charger_corpus(CHEMIN)[0]

    # Vérification de la transformation des données uniquement.
    # Aucun modèle n’est appelé.
    contexte = construire_contexte(
        ({"passage": passage, "score": 1},)
    )
    documents = json.loads(contexte)

    assert documents[0]["source_version"] == passage["source_version"]

    sources = retrouver_sources_citees(
        f"Référence de test [{passage['id']}].",
        contexte,
    )

    assert sources[0]["source"] == passage["source"]
    assert sources[0]["source_version"] == passage["source_version"]
    assert sources[0]["url"] == passage["url"]

@pytest.mark.parametrize(
    "question, premier_attendu",
    [
        (
            "À quoi sert une consultation avant une grossesse ?",
            "conception_consultation_objectif",
        ),
        (
            "Quels sujets peut-on préparer pour cette consultation ?",
            "conception_consultation_preparation",
        ),
        (
            "Quels sujets aborder avant une grossesse ?",
            "conception_consultation_preparation",
        ),
        (
            "À quoi sert la première consultation de grossesse en France ?",
            "grossesse_premiere_consultation_objectif",
        ),
        (
            "Où trouver des recommandations alimentaires institutionnelles pour la grossesse ?",
            "nutrition_guide_institutionnel",
        ),
        (
            "Quel guide officiel consulter pour l’alimentation pendant la grossesse ?",
            "nutrition_guide_institutionnel",
        ),
        (
            "Quels gestes d’hygiène respecter pour préparer les repas ?",
            "nutrition_hygiene_preparation",
        ),
        (
            "Comment éviter les contacts entre aliments crus et préparés ?",
            "nutrition_hygiene_preparation",
        ),
        (
            "Pendant la grossesse, quels repères respecter pour mettre au froid et décongeler les aliments ?",
            "nutrition_mise_au_froid_decongelation",
        ),
        (
            "Quels gestes de cuisson et de lavage des aliments respecter pendant la grossesse ?",
            "nutrition_cuisson_lavage",
        ),
        (
            "Pourquoi prévenir la listériose pendant la grossesse ?",
            "nutrition_listeriose_prevention",
        ),
        (
            "Quel est le message de prévention concernant l’alcool pendant la grossesse ?",
            "habitudes_alcool_prevention",
        ),
        (
            "Quels sont les messages généraux de prévention concernant l’alcool pendant la grossesse ?",
            "habitudes_alcool_prevention",
        ),
        (
            "Quel accompagnement professionnel peut aider à arrêter le tabac pendant la grossesse ?",
            "habitudes_tabac_accompagnement",
        ),
        (
            "Quel service d’aide à distance peut accompagner l’arrêt du tabac pendant la grossesse ?",
            "habitudes_tabac_aide_distance",
        ),
        (
            "Pendant la grossesse, peut-on demander un rappel à Tabac info service ?",
            "habitudes_tabac_aide_distance",
        ),
        (
            "Pourquoi signaler un projet de grossesse lors d’une discussion sur les médicaments ?",
            "medicaments_projet_grossesse",
        ),
        (
            "Quelles informations préparer pour discuter de ses médicaments avec un professionnel dans un projet de grossesse ?",
            "medicaments_preparer_discussion",
        ),
        (
            "Où trouver une information institutionnelle sur les signes nécessitant un avis pendant la grossesse ?",
            "alerte_carnet_maternite_ressource",
        ),
        (
            "Quelles limites présente une liste générale de signes d’alerte pendant la grossesse ?",
            "alerte_limites_liste",
        ),
    ],
)
def test_recherche_sur_corpus_retenu(
    question,
    premier_attendu,
):
    corpus = charger_corpus(CHEMIN)
    resultats = rechercher_corpus(question, corpus)

    assert resultats
    assert resultats[0]["passage"]["id"] == premier_attendu

def test_passage_sa_sg_provisoire_exclu():
    corpus = charger_corpus(CHEMIN)
    identifiant = "grossesse_definitions_sa_sg"
    passage = next(
        passage
        for passage in corpus
        if passage["id"] == identifiant
    )

    assert passage["editorial_status"] == "draft"
    assert passage["reuse_status"] == "to_review"
    assert passage["usage"] == "cross_check"

    question = "Que signifient semaines d’aménorrhée et semaines de grossesse ?"

    # Le passage correspond à la question.
    assert rechercher_passages(question, (passage,))

    # Il reste exclu des résultats utilisables par l’assistant.
    resultats = rechercher_corpus(question, corpus)
    assert identifiant not in {
        resultat["passage"]["id"]
        for resultat in resultats
    }