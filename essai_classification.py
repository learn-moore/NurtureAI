import json

from functools import partial
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

import streamlit as st

from classification_intentions import (
    VERSION_CLASSIFICATION,
    CONSIGNES_CLASSIFICATION,
    classer_demande_experimentale,
)
from evaluation_intentions import evaluer_classifieur
from generation_groq import (
    GenerationGroqInterrompue,
    ReponseGroqVide,
    RequeteGroqRefusee,
    generer_reponse_groq,
)


MODELE = "openai/gpt-oss-20b"
CHEMIN = (
    Path(__file__).resolve().parent
    / "donnees"
    / "evaluation_intentions.json"
)


def reinitialiser_autorisation():
    st.session_state["autorisation_classification"] = False


if "historique_classification" not in st.session_state:
    st.session_state["historique_classification"] = []

st.title("Évaluation expérimentale des intentions")
st.info("Questions fictives uniquement. Ce prototype n’est pas un dispositif d’orientation médicale.")

donnees = json.loads(CHEMIN.read_text(encoding="utf-8"))
cas_par_id = {cas["id"]: cas for cas in donnees["cas"]}

identifiant = st.selectbox(
    "Cas à évaluer",
    list(cas_par_id),
    key="cas_classification",
    on_change=reinitialiser_autorisation,
)
cas = cas_par_id[identifiant]

st.text(cas["question"])
st.caption(f"Fournisseur : Groq. \nModèle : {MODELE}.")

with st.expander("Contenu transmis au modèle"):
    st.text(CONSIGNES_CLASSIFICATION)
    st.json({"question": cas["question"]})

st.write(
    "Seules les consignes et la question fictive seront envoyées. La catégorie attendue et sa justification restent locales."
)
st.caption(
    "Les conditions de traitement sont celles de Groq, comme pour l’essai de génération."
)
st.markdown(
    "[Consulter les conditions de traitement des données](https://console.groq.com/docs/your-data)"
)

autorisation = st.checkbox(
    "J’autorise l’envoi de ce cas fictif à Groq.",
    value=False,
    key="autorisation_classification",
)
evaluer = st.button(
    "Évaluer ce cas",
    disabled=not autorisation,
)

if evaluer and autorisation:
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
    classer = partial(
        classer_demande_experimentale,
        generer=generer,
    )

    debut = datetime.now(timezone.utc).isoformat()

    try:
        with st.spinner("Classification en cours…"):
            evaluation = evaluer_classifieur(
                [cas],
                classer=classer,
            )[0]
    except ValueError as erreur:
        if isinstance(erreur, RequeteGroqRefusee):
            code_erreur = "requete_refusee"
        elif isinstance(erreur, GenerationGroqInterrompue):
            code_erreur = "generation_interrompue"
        elif isinstance(erreur, ReponseGroqVide):
            code_erreur = "reponse_vide"
        else:
            code_erreur = "evaluation_refusee"

        evaluation = {
            "id": cas["id"],
            "attendu": cas["intention_attendue"],
            "obtenu": None,
            "conforme": False,
            "generation_indument_autorisee": False,
            "erreur": code_erreur,
        }

    essai = {
        "id_essai": str(uuid4()),
        "debut_utc": debut,
        "fin_utc": datetime.now(timezone.utc).isoformat(),
        "fournisseur": "Groq",
        "modele": MODELE,
        "version_classification": VERSION_CLASSIFICATION,
        "consignes": CONSIGNES_CLASSIFICATION,
        "cas": dict(cas),
        "resultat": evaluation,
    }
    st.session_state["historique_classification"].append(essai)

    st.json(evaluation)

    messages_erreur = {
        "requete_refusee": (
            "La requête a été refusée par le fournisseur."
        ),
        "generation_interrompue": (
            "La génération ne s’est pas terminée normalement."
        ),
        "reponse_vide": (
            "Le fournisseur n’a retourné aucun texte exploitable."
        ),
        "classification_invalide": (
            "Le classifieur a retourné une catégorie non conforme."
        ),
        "classification_indisponible": (
            "Le service de classification est indisponible."
        ),
        "evaluation_refusee": (
            "L’évaluation a été refusée ; la cause reste à préciser."
        ),
    }

    if evaluation["erreur"]:
        message = messages_erreur.get(
            evaluation["erreur"],
            "Une erreur non identifiée a interrompu l’évaluation.",
        )
        st.error(f"{message} Cas non réussi.")
    elif evaluation["conforme"]:
        st.success("Catégorie conforme à l’attente de ce cas.")
    else:
        st.warning("Écart entre la catégorie attendue et obtenue.")

    if evaluation["generation_indument_autorisee"]:
        st.error("Ce classement autoriserait indûment la génération documentaire.")

    st.caption("Aucune réponse documentaire n’est générée dans cette page.")


st.subheader("Historique des essais")

historique = st.session_state["historique_classification"]

st.caption(
    "Cet historique est conservé pendant la session uniquement. Télécharge-le avant de fermer ou de recharger la page."
)

if historique:
    st.write(f"Nombre d’essais enregistrés : {len(historique)}")

    with st.expander("Consulter les essais"):
        st.json(historique)

    export = {
        "schema_version": 1,
        "essais": historique,
    }

    st.download_button(
        "Télécharger les essais en JSON",
        data=json.dumps(
            export,
            ensure_ascii=False,
            indent=2,
        ),
        file_name="essais_classification.json",
        mime="application/json",
        on_click="ignore",
    )
else:
    st.info("Aucun essai enregistré pendant cette session.")