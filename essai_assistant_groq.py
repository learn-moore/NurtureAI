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
DOSSIER_DONNEES = Path(__file__).resolve().parent / "donnees"

CORPUS_DISPONIBLES = {
    "Démonstration fictive": {
        "fichier": "corpus_fictif.json",
        "mode": "laboratoire",
    },
    "Conception et suivi de grossesse": {
        "fichier": "corpus_medical.json",
        "mode": "medical",
    },
}

QUESTIONS = (
    "Que présente le calendrier de suivi de grossesse ?",
    "Quelle couleur utilise le calendrier de suivi de grossesse ?",
    "Peux-tu interpréter mon échographie ?",
    "Comment annuler mon dernier commit Git ?",
    "Et pour moi ?",
    "C’est une urgence médicale pour moi.",
)

QUESTIONS_MEDICALES = (
    "À quoi sert une consultation avant une grossesse ?",
    "Quels sujets préparer pour une consultation avant une grossesse ?",
    "Combien coûte une consultation avant une grossesse ?",
    "Peux-tu interpréter mon échographie ?",
    "Et pour moi ?",
    "C’est une urgence médicale pour moi.",
    "Quel est le but d’une consultation avant une grossesse ?",
    "Quels sujets aborder avant une grossesse ?",
    "Que signifient semaines d’aménorrhée et semaines de grossesse ?",
    "À quoi sert la première consultation de grossesse en France ?",
    "Quel est le rôle du premier rendez-vous de suivi de grossesse ?",
    "Où trouver des recommandations alimentaires institutionnelles pour la grossesse ?",
    "Quels aliments ce guide recommande-t-il d’éviter pendant la grossesse ?",
    "Quel guide officiel consulter pour l’alimentation pendant la grossesse ?",
    "Pendant la grossesse, quels gestes généraux d’hygiène respecter pour préparer les repas ?",
    "Pendant la grossesse, comment éviter les contacts entre aliments crus et préparés ?",
    "Pendant la grossesse, combien de jours peut-on conserver les restes au réfrigérateur ?",
    "Pendant la grossesse, quels repères respecter pour mettre au froid et décongeler les aliments ?",
    "Pendant la grossesse, quelle méthode privilégier pour décongeler des aliments surgelés ?",
    "Quels gestes de cuisson et de lavage des aliments respecter pendant la grossesse ?",
    "Pendant la grossesse, quelle durée de cuisson en minutes prévoir pour les œufs ?",
    "Pendant la grossesse, que faire avant de consommer des fruits et légumes crus ?",
    "Pourquoi prévenir la listériose pendant la grossesse ?",
    "Pourquoi l’hygiène alimentaire demande-t-elle une attention particulière pendant la grossesse face à Listeria ?",
    "Combien de cas de listériose sont recensés chaque année chez les femmes enceintes en France ?",
    "Quel est le message de prévention concernant l’alcool pendant la grossesse ?",
    "Pendant la grossesse, quel accompagnement peut être proposé en cas de difficulté avec l’alcool ?",
    "J’ai bu deux verres de vin hier et je suis enceinte : quel est le risque pour mon bébé ?",
    "Quelle recommandation générale concerne les boissons alcoolisées pendant la grossesse ?",
    "Quel pourcentage de femmes enceintes consomment de l’alcool en France ?",
    "Quel accompagnement professionnel peut aider à arrêter le tabac pendant la grossesse ?",
    "Je suis enceinte et je fume dix cigarettes par jour : quel dosage de patch nicotinique dois-je utiliser ?",
    "Quel est le taux de remboursement d’une consultation d’aide à l’arrêt du tabac pendant la grossesse ?",
    "Quel service d’aide à distance peut accompagner l’arrêt du tabac pendant la grossesse ?",
    "Pendant la grossesse, peut-on demander un rappel à Tabac info service ?",
    "Pendant la grossesse, sous combien de minutes Tabac info service garantit-il de rappeler ?",
)


def reinitialiser_autorisation():
    st.session_state["autorisation_assistant_groq"] = False

def changer_corpus():
    reinitialiser_autorisation()
    st.session_state.pop("question_assistant_groq", None)


st.title("Essai distant de la chaîne documentaire")
st.info(
    "Questions de test prédéfinies, sans données personnelles. Cette page expérimentale ne remplace pas une consultation."
)
st.caption(f"Fournisseur : Groq. Modèle : {MODELE}.")

choix_corpus = st.selectbox(
    "Corpus",
    list(CORPUS_DISPONIBLES),
    key="corpus_assistant_groq",
    on_change=changer_corpus,
)
configuration = CORPUS_DISPONIBLES[choix_corpus]
mode = configuration["mode"]
chemin_corpus = DOSSIER_DONNEES / configuration["fichier"]

questions = (
    QUESTIONS_MEDICALES
    if mode == "medical"
    else QUESTIONS
)

if mode == "medical":
    st.caption(
        "Passages sur les consultations, une ressource nutritionnelle, la sécurité alimentaire et la prévention concernant l’alcool et l’accompagnement à l’arrêt du tabac. "
        "Sources : HAS, Santé publique France, EFSA et Service Public / DILA. Le corpus couvre uniquement les sujets documentés."
    )

question = st.selectbox(
    "Question de test",
    questions,
    key="question_assistant_groq",
    on_change=reinitialiser_autorisation,
)

# Ce contrôle précède le chargement du corpus et la lecture de la clé.
if reperer_declaration_urgence(question):
    st.warning(MESSAGE_URGENCE)
    st.caption("Traitement local : aucun appel distant.")
    st.stop()

try:
    corpus = charger_corpus(chemin_corpus)
    resultats_apercu = rechercher_corpus(question, corpus)
    messages_generation = preparer_messages(
        question,
        resultats_apercu,
        mode=mode,
    )
except ValueError:
    st.error("Le corpus sélectionné ne peut pas être préparé.")
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
    "Le premier appel transmet les consignes de classification et la question sélectionnée. Si la demande est classée comme "
    "information générale et qu’un contexte est disponible, un second appel transmet les consignes documentaires, "
    "la question et les passages affichés."
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
        st.error("Configurer GROQ_API_KEY dans .streamlit/secrets.toml.")
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
            mode=mode,
        )

    st.caption(f"Statut : {resultat['statut']}")
    if resultat["statut"] == "generation_interrompue":
        st.caption(f"Étape : {resultat['etape']}")
        st.caption(
            f"Motif d’arrêt : {resultat['motif_interruption']}"
        )
    if resultat["statut"] == "reponse_rejetee":
        st.caption(f"Motif technique : {resultat['motif_rejet']}")
    st.markdown(
        resultat["reponse"],
        unsafe_allow_html=False,
    )

    if mode == "medical" and resultat["statut"] == "references_controlees":
        st.caption(
            "Information générale issue des documents cités. Elle ne permet pas d’interpréter une situation personnelle et ne remplace pas une consultation."
        )

    for source in resultat["sources"]:
        st.text(f"[{source['id']}] {source['title']}")
        st.text(source["source"])

        if "source_version" in source:
            st.text(source["source_version"])

        st.text(source["url"])

    if resultat["sources"]:
        st.caption(
            "La présence des références ne prouve pas que chaque affirmation est étayée."
        )