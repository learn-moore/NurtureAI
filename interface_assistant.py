from pathlib import Path

import streamlit as st

from corpus_documentaire import charger_corpus
from intentions import MESSAGE_URGENCE, reperer_declaration_urgence
from messages_assistant import preparer_messages
from recherche_documentaire import rechercher_corpus
from classification_intentions import CONSIGNES_CLASSIFICATION
from assistant_groq import traiter_demande_groq


CHEMIN_CORPUS = (
    Path(__file__).resolve().parent
    / "donnees"
    / "corpus_medical.json"
)
MODELE = "openai/gpt-oss-20b"


def effacer_apercu_assistant():
    st.session_state.pop("assistant_apercu", None)
    st.session_state.pop("assistant_resultat", None)
    st.session_state["assistant_autorisation"] = False


def executer_apercu_assistant(apercu, *, cle_api):
    messages_attendus = preparer_messages(
        apercu["question"],
        rechercher_corpus(
            apercu["question"],
            apercu["corpus"],
        ),
        mode="medical",
    )

    if (
        messages_attendus != apercu["messages"]
        or apercu["consignes_classification"] != CONSIGNES_CLASSIFICATION
        or apercu["modele"] != MODELE
    ):
        raise ValueError(
            "L’aperçu ne correspond plus à la configuration courante."
        )

    return traiter_demande_groq(
        apercu["question"],
        apercu["corpus"],
        cle_api=cle_api,
        modele=apercu["modele"],
        mode="medical",
    )


def afficher_assistant():
    st.subheader("Assistant documentaire")
    st.caption(
        "Informations générales sur la conception et la grossesse. Cet assistant ne peut pas évaluer une situation médicale personnelle."
    )

    with st.expander("Préparer une question"):
        st.info(
            "Cette étape prépare uniquement un aperçu local. Aucune donnée n’est envoyée à un fournisseur IA."
        )
        st.caption(
            "Utilisez des questions fictives pour cette démonstration. Le profil et les rendez-vous ne sont pas ajoutés à la question."
        )

        question = st.text_area(
            "Votre question générale",
            max_chars=2000,
            key="assistant_question",
            on_change=effacer_apercu_assistant,
        )
        preparer = st.button(
            "Préparer un aperçu local",
            key="assistant_preparer",
            on_click=effacer_apercu_assistant,
        )

        if preparer:
            if not question.strip():
                st.warning("Saisissez une question pour préparer l’aperçu.")
                return

            if reperer_declaration_urgence(question):
                st.warning(MESSAGE_URGENCE)
                return

            try:
                corpus = charger_corpus(CHEMIN_CORPUS)
                resultats = rechercher_corpus(question, corpus)
                messages = preparer_messages(
                    question,
                    resultats,
                    mode="medical",
                )
            except ValueError:
                st.error("L’aperçu documentaire ne peut pas être préparé.")
                return

            if not messages:
                st.info(
                    "Aucun contexte documentaire ne peut être préparé pour cette question."
                )
                return

            st.session_state["assistant_apercu"] = {
                "question": question.strip(),
                "messages": messages,
                "corpus": corpus,
                "consignes_classification": CONSIGNES_CLASSIFICATION,
                "modele": MODELE,
            }

        apercu = st.session_state.get("assistant_apercu")

        if apercu is None:
            return

        if apercu["question"] != question.strip():
            effacer_apercu_assistant()
            return

        st.caption(
            "Documents proposés par la recherche locale. Leur présence ne garantit pas qu’ils répondent à la question. "
            "Cet aperçu ne constitue pas une réponse médicale."
        )
        st.json(list(apercu["messages"]))

        with st.expander("Consignes de classification"):
            st.code(
                apercu["consignes_classification"],
                language="text",
            )

        st.write(
            "Le traitement distant prévu utilise Groq. Un premier appel transmet les consignes de classification "
            "et votre question. Si la demande est autorisée, un second appel peut transmettre les consignes documentaires, "
            "votre question et les passages présentés dans l’aperçu."
        )
        st.caption(
            "Le profil et les rendez-vous ne sont pas ajoutés automatiquement. Les informations personnelles que vous "
            "écrivez dans la question feraient partie de l’envoi."
        )
        st.markdown(
            "[Conditions de traitement des données par Groq](https://console.groq.com/docs/your-data)"
        )

        st.caption(f"Modèle : {apercu['modele']}.")

        autorisation = st.checkbox(
            "J’autorise l’envoi de cette question et des passages présentés à Groq, jusqu’à deux appels par clic d’envoi.",
            key="assistant_autorisation",
        )
        envoyer = st.button(
            "Envoyer à Groq",
            key="assistant_envoyer",
            disabled=not autorisation,
        )
        st.caption(
            "Cocher l’autorisation ne déclenche aucun appel. Chaque clic d’envoi autorisé peut déclencher jusqu’à deux appels."
        )

        if envoyer and autorisation:
            st.session_state.pop("assistant_resultat", None)

            try:
                cle = st.secrets["GROQ_API_KEY"]
            except (FileNotFoundError, KeyError):
                st.error("Le service IA n’est pas configuré.")
                return

            if not isinstance(cle, str) or not cle.strip():
                st.error("La configuration du service IA est invalide.")
                return

            try:
                with st.spinner("Traitement en cours…"):
                    resultat = executer_apercu_assistant(
                        apercu,
                        cle_api=cle,
                    )
            except ValueError:
                st.error(
                    "La demande ne peut pas être envoyée. Préparez un nouvel aperçu avant de réessayer."
                )
                return

            st.session_state["assistant_resultat"] = resultat

        resultat = st.session_state.get("assistant_resultat")

        if resultat is None:
            return

        st.caption(f"Statut : {resultat['statut']}")
        st.markdown(resultat["reponse"], unsafe_allow_html=False)

        if resultat["statut"] == "references_controlees":
            st.caption(
                "Information générale issue des documents cités. Elle ne permet pas d’interpréter une situation personnelle "
                "et ne remplace pas une consultation."
            )

        for source in resultat["sources"]:
            st.text(f"[{source['id']}] {source['title']}")
            st.text(source["source"])

            if "source_version" in source:
                st.text(source["source_version"])

            st.text(source["url"])

            if "reuse_notice" in source:
                st.text(source["reuse_notice"])

        if resultat["sources"]:
            st.caption(
                "La présence des références ne prouve pas que chaque affirmation est étayée."
            )