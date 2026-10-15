from functools import partial
from pathlib import Path

import streamlit as st

from assistant_documentaire import (
    GenerationIndisponible,
    preparer_reponse,
)
from corpus_documentaire import charger_corpus
from generation_groq import generer_reponse_groq
from messages_assistant import preparer_messages
from recherche_documentaire import rechercher_corpus


MODELE = "openai/gpt-oss-20b"
QUESTION = "Que présente le calendrier ?"
CHEMIN = Path(__file__).resolve().parent / "donnees" / "corpus_fictif.json"

st.title("Premier essai Groq")
st.info("Démonstration technique sur des documents fictifs.")
st.text(f"Modèle : {MODELE}")
st.text(f"Question : {QUESTION}")

try:
    corpus = charger_corpus(CHEMIN)
    resultats = rechercher_corpus(QUESTION, corpus)
    messages = preparer_messages(QUESTION, resultats)
except ValueError as erreur:
    st.error(str(erreur))
    st.stop()

with st.expander("Voir les messages qui seront envoyés"):
    st.json(list(messages))

st.write(
    "Un clic enverra à Groq les consignes, cette question fixe et les passages fictifs affichés ci-dessus. "
    "Aucun profil utilisateur n’est chargé."
)
st.caption(
    "Groq indique ne pas conserver les entrées et sorties par défaut, avec des exceptions pour la fiabilité et la surveillance des abus "
    "pouvant aller jusqu’à 30 jours, sauf obligation légale."
)
st.markdown(
    "[Conditions de traitement des données]"
    "(https://console.groq.com/docs/your-data)"
)

autorisation = st.checkbox(
    "J’autorise l’envoi de ces messages fictifs à Groq.",
    value=False,
)

envoyer = st.button(
    "Envoyer un appel à Groq",
    disabled=not autorisation or not messages,
)

if envoyer and autorisation and messages:
    try:
        cle = st.secrets["GROQ_API_KEY"]
    except (FileNotFoundError, KeyError):
        st.error("Configurer GROQ_API_KEY dans .streamlit/secrets.toml.")
        st.stop()

    generer = partial(
        generer_reponse_groq,
        cle_api=cle,
        modele=MODELE,
    )

    try:
        with st.spinner("Génération en cours…"):
            resultat = preparer_reponse(
                QUESTION,
                resultats,
                generer=generer,
            )
    except GenerationIndisponible:
        st.error("Groq est indisponible ou le quota est atteint.")
    except ValueError as erreur:
        st.error(str(erreur))
    else:
        if resultat["statut"] == "sans_contexte":
            st.info(resultat["reponse"])
        else:
            if resultat["statut"] == "sans_citation":
                st.warning("Réponse sans citation : sources non vérifiées.")

            st.text(resultat["reponse"])

            for source in resultat["sources"]:
                st.text(f"[{source['id']}] {source['title']}")
                st.text(source["url"])

            st.caption(
                "La présence des références ne prouve pas que chaque affirmation est étayée."
            )