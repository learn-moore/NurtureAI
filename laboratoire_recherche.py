from pathlib import Path

import streamlit as st

from corpus_documentaire import THEMES_CORPUS, charger_corpus
from recherche_documentaire import rechercher_corpus
from rapport_recherche import construire_rapport_recherche
from contexte_documentaire import construire_contexte
from messages_assistant import preparer_messages
from citations_documentaires import retrouver_sources_citees
from assistant_documentaire import preparer_reponse_simulee


CHEMIN_CORPUS = Path(__file__).resolve().parent / "donnees" / "corpus_fictif.json"

st.title("Laboratoire de recherche documentaire")
st.info("Données fictives. Cet écran ne fournit aucune information médicale.")

try:
    corpus = charger_corpus(CHEMIN_CORPUS)
except ValueError as erreur:
    st.error(str(erreur))
    st.stop()

with st.form("Recherche"):
    question = st.text_input("Question", key="question_recherche")
    choix = st.selectbox("Thème", ["Tous les thèmes", *sorted(THEMES_CORPUS)])
    limite = st.number_input("Nombre de résultats", min_value=1, max_value=10, value=3)
    reponse_fictive = st.text_area(
        "Réponse fictive à contrôler (facultatif)",
        key="reponse_fictive",
        help="Exemple : Les rendez-vous sont affichés [calendrier].",
    )
    soumettre = st.form_submit_button("Rechercher")

if soumettre:
    if not question.strip():
        st.warning("Saisissez une question non vide.")
    else:
        theme = None if choix == "Tous les thèmes" else choix
        try:
            resultats = rechercher_corpus(question, corpus, int(limite), theme=theme)
        except ValueError as erreur:
            st.error(str(erreur))
        else:
            if not resultats:
                st.info("Aucun passage correspondant dans ce périmètre.")
            for numero, resultat in enumerate(resultats, start=1):
                passage = resultat["passage"]
                st.subheader(f"{numero}. {passage['title']}")
                st.caption(f"Score lexical : {resultat['score']}")
                st.text("Mots communs : " + ", ".join(resultat["mots_communs"]))
                st.text(passage["content"])
                st.caption(f"Source fictive : {passage['source']}")
                st.text(passage["url"])

            contexte = construire_contexte(resultats)

            with st.expander("Voir le contexte documentaire"):
                st.caption(
                    f"{len(contexte)} caractères sur un maximum de 6 000."
                )
                st.code(contexte, language="json")
                st.caption("Ce contexte contient les passages retenus et leurs sources. Aucun appel à un modèle IA n’est effectué.")

            messages = preparer_messages(question, resultats)

            with st.expander("Voir les messages préparés"):
                if not messages:
                    st.info("Aucun document disponible dans le contexte. Aucun message à envoyer au modèle.")
                else:
                    for message in messages:
                        st.text(f"Rôle : {message['role']}")
                        st.code(
                            message["content"],
                            language=(
                                "json"
                                if message["role"] == "user"
                                else "text"
                            ),
                        )

                    st.caption("Aperçu uniquement : aucun appel API.")

            if reponse_fictive.strip():
                with st.expander(
                    "Contrôle des références de la réponse fictive",
                    expanded=True,
                ):
                    try:
                        sources = retrouver_sources_citees(
                            reponse_fictive,
                            contexte,
                        )
                    except ValueError as erreur:
                        st.error(str(erreur))
                    else:
                        if not sources:
                            st.warning(
                                "Aucune citation détectée. Ce contrôle ne permet pas de conclure que la réponse est suffisamment sourcée."
                            )
                        else:
                            st.success(
                                "Toutes les références détectées figurent dans le contexte."
                            )
                            for source in sources:
                                st.text(
                                    f"[{source['id']}] {source['title']}"
                                )
                                st.caption(source["source"])
                                st.text(source["url"])

                            st.caption(
                                "La présence des références ne garantit pas que les passages soutiennent les affirmations."
                            )

            with st.expander("Réponse simulée", expanded=True):
                st.caption(
                    "Simulation déterministe : reprise du premier passage. Aucun modèle IA ni service externe n’est appelé."
                )

                try:
                    simulation = preparer_reponse_simulee(
                        question,
                        resultats,
                    )
                except ValueError as erreur:
                    st.error(f"La simulation n’a pas pu aboutir : {erreur}")
                else:
                    if simulation["statut"] == "sans_contexte":
                        st.info(simulation["reponse"])
                    elif simulation["statut"] == "sans_citation":
                        st.warning("Aucune citation détectée. La réponse n’est pas validée comme sourcée.")
                        st.text(simulation["reponse"])
                    else:
                        st.text(simulation["reponse"])

                        for source in simulation["sources"]:
                            st.text(
                                f"[{source['id']}] {source['title']}"
                            )
                            st.caption(source["source"])
                            st.text(source["url"])

                        st.caption("Les références appartiennent au contexte. Ce contrôle ne valide pas le sens de la réponse.")

            st.download_button(
                "Télécharger le rapport",
                construire_rapport_recherche(question, resultats),
                file_name="rapport_recherche_fictive.txt",
                mime="text/plain",
                on_click="ignore",
            )
