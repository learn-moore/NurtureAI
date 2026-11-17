import json
from pathlib import Path

import streamlit as st

from assistant_documentaire import GenerationIndisponible
from fidelite_rendez_vous import (
    evaluer_controleur_fidelite,
    preparer_messages_fidelite,
)
from generation_groq import creer_appel_groq_rendez_vous


MODELE = "openai/gpt-oss-20b"
CHEMIN_CAS = (
    Path(__file__).resolve().parent
    / "donnees"
    / "evaluation_fidelite_rendez_vous.json"
)


st.title("Essai du contrôle de fidélité")
st.caption(f"Cas fictifs prédéfinis. Fournisseur : Groq. Modèle : {MODELE}.")

cas_par_id = {
    cas["id"]: cas
    for cas in json.loads(CHEMIN_CAS.read_text(encoding="utf-8"))
}
identifiant = st.selectbox("Cas de référence", list(cas_par_id))
cas = cas_par_id[identifiant]

with st.expander("Messages qui seront envoyés"):
    st.json(list(preparer_messages_fidelite(
        cas["contenu_selectionne"],
        tuple(cas["questions_proposees"]),
    )))

autorisation = st.checkbox(
    "J’autorise un appel à Groq pour ce cas fictif.",
    key=f"autorisation_{identifiant}",
)

if st.button("Évaluer le cas", disabled=not autorisation) and autorisation:
    try:
        cle = st.secrets["GROQ_API_KEY"]
    except (FileNotFoundError, KeyError):
        st.error("Le service IA n’est pas configuré.")
        st.stop()

    if not isinstance(cle, str) or not cle.strip():
        st.error("La configuration du service IA est invalide.")
        st.stop()

    controler = creer_appel_groq_rendez_vous(cle_api=cle, modele=MODELE)

    try:
        resultat = evaluer_controleur_fidelite(cas, controler=controler)
    except GenerationIndisponible:
        st.error("Le contrôle de fidélité est indisponible.")
    else:
        st.json(resultat)
        st.caption(cas["motif"])