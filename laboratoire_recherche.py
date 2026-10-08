from pathlib import Path

import streamlit as st

from corpus_documentaire import THEMES_CORPUS, charger_corpus
from recherche_documentaire import rechercher_corpus
from rapport_recherche import construire_rapport_recherche


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
            st.download_button(
                "Télécharger le rapport",
                construire_rapport_recherche(question, resultats),
                file_name="rapport_recherche_fictive.txt",
                mime="text/plain",
                on_click="ignore",
            )
