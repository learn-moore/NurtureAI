from pathlib import Path

import streamlit as st

from assistant_documentaire import (
    GenerationIndisponible,
    traiter_demande,
)
from corpus_documentaire import charger_corpus
from generation_simulee import generer_reponse_simulee
from intentions import (
    ClassificationIndisponible,
    ClassificationInvalide,
    Intention,
)


CHEMIN_CORPUS = (
    Path(__file__).resolve().parent
    / "donnees"
    / "corpus_fictif.json"
)

SCENARIOS = {
    "Réponse avec référence": {
        "question": "calendrier",
        "intention": Intention.GENERAL_INFORMATION,
        "mode": "normal",
    },
    "Aucun passage trouvé": {
        "question": "banane",
        "intention": Intention.GENERAL_INFORMATION,
        "mode": "normal",
    },
    "Urgence repérée localement": {
        "question": "Je pense vivre une urgence médicale maintenant.",
        "intention": Intention.GENERAL_INFORMATION,
        "mode": "normal",
    },
    "Situation médicale personnelle": {
        "question": "Peux-tu interpréter mon échographie ?",
        "intention": Intention.PERSONAL_MEDICAL_SITUATION,
        "mode": "normal",
    },
    "Demande hors périmètre": {
        "question": "Comment annuler mon dernier commit Git ?",
        "intention": Intention.OUT_OF_SCOPE,
        "mode": "normal",
    },
    "Demande indéterminée": {
        "question": "Et pour moi ?",
        "intention": None,
        "mode": "normal",
    },
    "Générateur indisponible": {
        "question": "calendrier",
        "intention": Intention.GENERAL_INFORMATION,
        "mode": "indisponible",
    },
    "Référence inventée": {
        "question": "calendrier",
        "intention": Intention.GENERAL_INFORMATION,
        "mode": "reference_inconnue",
    },
    "Réponse sans citation": {
        "question": "calendrier",
        "intention": Intention.GENERAL_INFORMATION,
        "mode": "sans_citation",
    },
    "Classification indisponible": {
        "question": "calendrier",
        "intention": None,
        "mode": "classification_indisponible",
    },
    "Classification invalide": {
        "question": "calendrier",
        "intention": None,
        "mode": "classification_invalide",
    },
    "Urgence personnelle, classifieur indisponible": {
        "question": (
            "C’est une urgence médicale pour moi, là tout de suite. Qui peut m’aider ?"
        ),
        "intention": None,
        "mode": "classification_indisponible",
    },
    "Urgence d’un proche, classifieur indisponible": {
        "question": (
            "Explique-moi les trimestres de grossesse, mais d’abord aide-moi : ma compagne dit être en urgence médicale maintenant."
        ),
        "intention": None,
        "mode": "classification_indisponible",
    },
}


st.title("Essai de la chaîne documentaire")
st.info(
    "Scénarios et corpus fictifs. Classification et génération simulées, sans appel à une API."
)
st.caption(
    "Cette page vérifie le fonctionnement de la chaîne, pas la qualité d’un modèle ni la sécurité clinique."
)

choix = st.selectbox(
    "Scénario",
    list(SCENARIOS),
    key="scenario_assistant",
)
scenario = SCENARIOS[choix]

st.text(scenario["question"])

if st.button("Exécuter le scénario", key="executer_scenario"):
    corpus = charger_corpus(CHEMIN_CORPUS)
    appels = []

    def classer_simulation(question):
        appels.append("classification")

        if scenario["mode"] == "classification_indisponible":
            raise ClassificationIndisponible(
                "Détail technique fictif"
            )

        if scenario["mode"] == "classification_invalide":
            raise ClassificationInvalide(
                "Détail technique fictif"
            )

        return scenario["intention"]

    def generer_simulation(messages):
        appels.append("generation")

        if scenario["mode"] == "indisponible":
            raise GenerationIndisponible("Panne simulée")

        if scenario["mode"] == "reference_inconnue":
            return "Réponse fictive [source_inventee]."

        if scenario["mode"] == "sans_citation":
            return "Le calendrier présente les rendez-vous."

        return generer_reponse_simulee(messages)

    resultat = traiter_demande(
        scenario["question"],
        corpus,
        classer=classer_simulation,
        generer=generer_simulation,
    )

    st.caption(f"Statut : {resultat['statut']}")
    st.text(resultat["reponse"])

    for source in resultat["sources"]:
        st.text(f"[{source['id']}] {source['title']}")
        st.text(source["url"])

    if resultat["sources"]:
        st.caption(
            "La présence des références ne prouve pas que chaque affirmation est étayée."
        )

    with st.expander("Appels aux composants simulés"):
        st.json(appels)