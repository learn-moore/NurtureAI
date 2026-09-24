import streamlit as st


def initialiser_session():
    if "suivi_conception" not in st.session_state:
        st.session_state["suivi_conception"] = None

    if "suivi_grossesse" not in st.session_state:
        st.session_state["suivi_grossesse"] = None

def effacer_reperes_conception():
    st.session_state["suivi_conception"] = None
    st.session_state["conception_dernieres_regles"] = None
    st.session_state["conception_duree_cycle"] = 28
    st.session_state["conception_duree_regles"] = 5
    st.session_state["conception_regularite"] = "Je ne sais pas"
    st.session_state["confirmer_effacement_conception"] = False

def effacer_reperes_grossesse():
    st.session_state["suivi_grossesse"] = None
    st.session_state["methode_datation_grossesse"] = "dernieres_regles"
    st.session_state["date_regles_grossesse"] = None
    st.session_state["date_accouchement_grossesse"] = None
    st.session_state["confirmer_effacement_grossesse"] = False