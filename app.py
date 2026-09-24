import streamlit as st
from datetime import date
from calculs import estimer_prochaines_regles, calculer_jour_cycle, valider_durees_cycle

st.title("NurtureAI")
st.write("Votre compagnon d'ionformation sur la conception et la grossesse.")

st.info(
    "NurtureAI fournit des informations générales et des estimations. Il ne remplace pas une professionnel de santé."
)

if "suivi_conception" not in st.session_state:
    st.session_state["suivi_conception"] = None

parcours = st.radio(
    "Quel suivi souhaitez-vous commencer ?",
    ["Projet de conception", "Grossesse en cours"]
)

if parcours == "Projet de conception":
    suivi = st.session_state["suivi_conception"]
    choix_regularite = ["Je ne sais pas", "Régulier", "Irrégulier"]

    with st.form("formulaire_conception"):
        dernieres_regles = st.date_input(
            "Premier jour de vos dernières règles",
            value = suivi["dernieres_regles"] if suivi is not None else None,
            max_value = date.today(),
            format = "DD/MM/YYYY",
        )
        duree_cycle = st.number_input(
            "Durée moyenne de votre cycle, en jours",
            min_value = 1,
            value = suivi["duree_cycle"] if suivi is not None else 28,
            step = 1,
            help = "28 jours est une valeur proposée. Adaptez-la à votre cycle.",
        )
        duree_regles = st.number_input(
            "Durée moyenne de vos règles, en jours",
            min_value = 1,
            value = suivi.get("duree_regles", 5) if suivi is not None else 5,
            step = 1,
        )
        regularite_cycle = st.radio(
            "Votre cycle est-il généralement régulier ?",
            choix_regularite,
            index=(
                choix_regularite.index(suivi["regularite_cycle"]) if suivi is not None else 0
            ),
        )

        formulaire_envoye = st.form_submit_button("Calculer mes repères")

    if formulaire_envoye:
        if dernieres_regles is None:
            st.error("Renseignez le premier jour de vos dernières règles.")
        else:
            try:
                valider_durees_cycle(duree_cycle, duree_regles)
            except ValueError as erreur:
                st.error(str(erreur))
            else:
                st.session_state["suivi_conception"] = {
                    "dernieres_regles": dernieres_regles,
                    "duree_cycle": duree_cycle,
                    "duree_regles": duree_regles,
                    "regularite_cycle": regularite_cycle,
                }

    suivi = st.session_state["suivi_conception"]

    if suivi is not None:
        jour_cycle = calculer_jour_cycle(
            suivi["dernieres_regles"], date.today(),
        )
        st.metric("Jour du cycle", jour_cycle)

        prochaines_regles = estimer_prochaines_regles(
            suivi["dernieres_regles"], suivi["duree_cycle"],
        )

        st.write(
            "Prochaine règles estimées : ",
            prochaines_regles.strftime("%d/%m/%Y"),
        )

        if prochaines_regles < date.today():
            st.info(
                "La date estimée des prochaines règles est passée. Si de nouvelles règles ont commencé, actualiser leur date de " \
                "début dans le formulaire. Sinon, conservez les informations actuelles. Cette estimation ne permet pas de conclure" \
                "à une grossesse ou à un problème de santé."
            )

        if suivi["regularite_cycle"] == "Régulier":
            st.caption(
                "Cette date est une estimation basée sur les informations reneignées. La durée réelle du cycle peut varier."
            )
        else:
            st.warning(
                "Laa régularité de votre cycle est inconnue ou vous avez indiqué un cycle irrégulier. " \
                "La date estimée des prochaines règles est donc à interpréter avec davantage de prudence."
            )
else:
    st.write("Vous avez choisi le suivi grossesse.")