import streamlit as st
from datetime import date
from calculs import estimer_prochaines_regles, calculer_jour_cycle

st.title("NurtureAI")
st.write("Votre compagnon d'ionformation sur la conception et la grossesse.")

st.info(
    "NurtureAI fournit des informations générales et des estimations."
    "Il ne remplace pas une professionnel de santé."
)

parcours = st.radio(
    "Quel suivi souhaitez-vous commencer ?",
    ["Projet de conception", "Grossesse en cours"]
)

if parcours == "Projet de conception":
    dernieres_regles = st.date_input(
        "Premier jour de vos dernières règles",
        value = None,
        max_value = date.today(),
        format = "DD/MM/YYYY",
    )
    duree_cycle = st.number_input(
        "Durée moyenne de votre cycle, en jours",
        min_value = 1,
        value = 28,
        step = 1,
        help = "28 jours est une valeur proposée. Adaptez-la à votre cycle.",
    )
    if dernieres_regles is not None:
        jour_cycle = calculer_jour_cycle(
            dernieres_regles,
            date.today(),
        )
        st.metric("Jour du cycle", jour_cycle)

        prochaines_regles = estimer_prochaines_regles(
            dernieres_regles, duree_cycle
        )

        st.write(
            "Prochaine règles estimées : ",
            prochaines_regles.strftime("%d/%m/%Y"),
        )

        st.caption(
            "Cette date est une estimation basée sur les informations reneignées. La durée réelle du cycle peut varier."
        )
else:
    st.write("Vous avez choisi le suivi grossesse.")