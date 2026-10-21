import json
from pathlib import Path

import streamlit as st

from assistant_groq import traiter_demande_groq
from classification_intentions import CONSIGNES_CLASSIFICATION
from corpus_documentaire import charger_corpus
from intentions import MESSAGE_URGENCE, reperer_declaration_urgence
from messages_assistant import preparer_messages
from recherche_documentaire import rechercher_corpus


MODELE = "openai/gpt-oss-20b"
CHEMIN_CORPUS = (
    Path(__file__).resolve().parent
    / "donnees"
    / "corpus_fictif.json"
)

QUESTIONS = (
    "Que présente le calendrier de suivi de grossesse ?",
    "Quelle couleur utilise le calendrier de suivi de grossesse ?",
    "Peux-tu interpréter mon échographie ?",
    "Comment annuler mon dernier commit Git ?",
    "Et pour moi ?",
    "C’est une urgence médicale pour moi.",
)


def reinitialiser_autorisation():
    st.session_state["autorisation_assistant_groq"] = False


st.title("Essai distant de la chaîne documentaire")
st.info(
    "Questions prédéfinies et corpus fictif uniquement. Cet essai ne fournit pas de conseil médical."
)
st.caption(f"Fournisseur : Groq. Modèle : {MODELE}.")

question = st.selectbox(
    "Question fictive",
    QUESTIONS,
    key="question_assistant_groq",
    on_change=reinitialiser_autorisation,
)

# Ce contrôle précède le chargement du corpus et la lecture de la clé.
if reperer_declaration_urgence(question):
    st.warning(MESSAGE_URGENCE)
    st.caption("Traitement local : aucun appel distant.")
    st.stop()

try:
    corpus = charger_corpus(CHEMIN_CORPUS)
    resultats_apercu = rechercher_corpus(question, corpus)
    messages_generation = preparer_messages(
        question,
        resultats_apercu,
    )
except ValueError:
    st.error("Le corpus fictif ne peut pas être préparé.")
    st.stop()

messages_classification = (
    {
        "role": "system",
        "content": CONSIGNES_CLASSIFICATION,
    },
    {
        "role": "user",
        "content": json.dumps(
            {"question": question},
            ensure_ascii=False,
        ),
    },
)

with st.expander("Premier appel : classification"):
    st.json(list(messages_classification))

with st.expander("Second appel éventuel : génération"):
    if messages_generation:
        st.json(list(messages_generation))
    else:
        st.info(
            "Aucun contexte disponible : le second appel ne sera pas effectué."
        )

st.write(
    "Le premier appel transmet les consignes de classification et la question fictive. Si la demande est classée comme "
    "information générale et qu’un contexte est disponible, un second appel transmet les consignes documentaires, "
    "la question et les passages fictifs affichés."
)
st.caption(
    "L’aperçu est préparé localement. Il ne déclenche aucun appel. Aucun profil utilisateur n’est chargé."
)
st.markdown(
    "[Conditions de traitement des données par Groq](https://console.groq.com/docs/your-data)"
)

autorisation = st.checkbox(
    "J’autorise ces envois à Groq, jusqu’à deux appels.",
    key="autorisation_assistant_groq",
    value=False,
)

executer = st.button(
    "Exécuter la chaîne",
    key="executer_assistant_groq",
    disabled=not autorisation,
)

if executer and autorisation:
    try:
        cle = st.secrets["GROQ_API_KEY"]
    except (FileNotFoundError, KeyError):
        st.error(
            "Configurer GROQ_API_KEY dans .streamlit/secrets.toml."
        )
        st.stop()

    if not isinstance(cle, str) or not cle.strip():
        st.error("La clé API est absente ou invalide.")
        st.stop()

    with st.spinner("Traitement en cours…"):
        resultat = traiter_demande_groq(
            question,
            corpus,
            cle_api=cle,
            modele=MODELE,
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