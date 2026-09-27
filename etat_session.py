import streamlit as st
from datetime import date

from modeles import UserProfile, ConceptionJourney, PregnancyJourney


def initialiser_session():
    if "suivi_conception" not in st.session_state:
        st.session_state["suivi_conception"] = None

    if "suivi_grossesse" not in st.session_state:
        st.session_state["suivi_grossesse"] = None

    if "profil" not in st.session_state:
        st.session_state["profil"] = UserProfile()

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
    st.session_state["terme_reference_grossesse"] = None

def terminer_parcours_actif():
    profil = st.session_state["profil"]

    st.session_state["profil"] = profil.terminer_parcours_actif(
        date.today()
    )

    st.session_state["confirmer_fin_parcours"] = False

def changer_parcours_actif():
    profil = st.session_state["profil"]

    parcours_actif = next(
        journey
        for journey in profil.journeys
        if journey.id == profil.active_journey_id
    )

    nouveau_type = (
        "pregnancy"
        if parcours_actif.type == "conception"
        else "conception"
    )

    st.session_state["profil"] = profil.changer_parcours(
        nouveau_type,
        date.today(),
    )

    effacer_reperes_conception()
    effacer_reperes_grossesse()

    st.session_state["confirmer_changement_parcours"] = False
    st.session_state["confirmer_fin_parcours"] = False

    st.session_state["ecran_consulte"] = (
        "Grossesse en cours"
        if nouveau_type == "pregnancy"
        else "Projet de conception"
    )

def reprendre_reperes_conception():
    profil = st.session_state["profil"]

    parcours_actif = next(
        (
            journey
            for journey in profil.journeys
            if journey.id == profil.active_journey_id
        ),
        None,
    )

    if parcours_actif is None:
        return

    reperes = parcours_actif.details

    if not isinstance(reperes, ConceptionJourney):
        return

    regularites = {
        "regular": "Régulier",
        "irregular": "Irrégulier",
        "unknown": "Je ne sais pas",
    }

    st.session_state["conception_dernieres_regles"] = reperes.last_period_date
    st.session_state["conception_duree_cycle"] = reperes.average_cycle_length
    st.session_state["conception_duree_regles"] = reperes.period_length
    st.session_state["conception_regularite"] = regularites[
        reperes.cycle_regularity
    ]

    st.session_state["suivi_conception"] = None


def reprendre_reperes_grossesse():
    profil = st.session_state["profil"]

    parcours_actif = next(
        (
            journey
            for journey in profil.journeys
            if journey.id == profil.active_journey_id
        ),
        None,
    )

    if parcours_actif is None:
        return

    reperes = parcours_actif.details

    if not isinstance(reperes, PregnancyJourney):
        return

    st.session_state["terme_reference_grossesse"] = (
        reperes.term_reference_days
    )

    # Vider les deux champs avant de restaurer la référence enregistrée.
    st.session_state["date_regles_grossesse"] = None
    st.session_state["date_accouchement_grossesse"] = None

    if reperes.dating_method == "last_period":
        st.session_state["methode_datation_grossesse"] = "dernieres_regles"
        st.session_state["date_regles_grossesse"] = reperes.last_period_date
    else:
        st.session_state["methode_datation_grossesse"] = "dpa"
        st.session_state["date_accouchement_grossesse"] = (
            reperes.estimated_due_date
        )

    st.session_state["suivi_grossesse"] = None

def annuler_confirmation_import():
    st.session_state["confirmer_import"] = False
    st.session_state["message_import"] = None


def remplacer_profil_session(profil: UserProfile):
    effacer_reperes_conception()
    effacer_reperes_grossesse()

    st.session_state["profil"] = profil
    st.session_state["confirmer_fin_parcours"] = False
    st.session_state["confirmer_changement_parcours"] = False
    st.session_state["confirmer_import"] = False
    st.session_state["confirmer_restauration_locale"] = False

    parcours_actif = next(
        (
            journey
            for journey in profil.journeys
            if journey.id == profil.active_journey_id
        ),
        None,
    )

    st.session_state["ecran_consulte"] = (
        "Grossesse en cours"
        if parcours_actif is not None and parcours_actif.type == "pregnancy"
        else "Projet de conception"
    )


def appliquer_import(profil_importe: UserProfile):
    if not st.session_state.get("confirmer_import", False):
        return

    remplacer_profil_session(profil_importe)
    st.session_state["message_import"] = "Le profil a été remplacé."


def restaurer_profil_local(profil_local: UserProfile):
    if not st.session_state.get("confirmer_restauration_locale", False):
        return

    remplacer_profil_session(profil_local)
    st.session_state["message_import"] = None
    st.session_state["message_restauration_locale"] = (
        "La sauvegarde locale a été restaurée."
    )

def effacer_profil_complet():
    if not st.session_state.get("confirmer_effacement_total", False):
        return

    st.session_state.clear()
    initialiser_session()

    st.session_state["message_effacement"] = (
        "Le profil et les saisies de cette session ont été effacés."
    )

def demarrer_nouveau_parcours(type_parcours: str):
    profil = st.session_state["profil"]

    nouveau_profil = profil.demarrer_parcours(
        type_parcours,
        date.today(),
    )

    effacer_reperes_conception()
    effacer_reperes_grossesse()

    st.session_state["profil"] = nouveau_profil
    st.session_state["confirmer_fin_parcours"] = False
    st.session_state["confirmer_changement_parcours"] = False

def finaliser_effacement_global():
    etat_stockage = st.session_state.get("stockage_profil", {})

    if etat_stockage.get("effacement") is not True:
        return

    st.session_state.clear()
    initialiser_session()

    st.session_state["message_effacement"] = (
        "La sauvegarde locale et les données de session ont été effacées."
    )

