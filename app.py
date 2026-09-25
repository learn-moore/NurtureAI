import streamlit as st
from datetime import date

from etat_session import initialiser_session, effacer_reperes_grossesse, effacer_reperes_conception, terminer_parcours_actif, changer_parcours_actif 
from etat_session import reprendre_reperes_conception, reprendre_reperes_grossesse, annuler_confirmation_import, appliquer_import
from calculs import estimer_prochaines_regles, calculer_jour_cycle, valider_durees_cycle, calculer_age_depuis_dernieres_regles
from modeles import ConceptionJourney, PregnancyJourney
from persistance import exporter_profil, importer_profil

st.title("NurtureAI")
st.write("Votre compagnon d'information sur la conception et la grossesse.")

st.info(
    "NurtureAI fournit des informations générales et des estimations. Il ne remplace pas une professionnel de santé."
)

initialiser_session()

parcours = st.radio(
    "Quel écran souhaitez-vous consulter ?",
    ["Projet de conception", "Grossesse en cours"],
    key = "ecran_consulte",
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
            key="conception_dernieres_regles",
        )
        duree_cycle = st.number_input(
            "Durée moyenne de votre cycle, en jours",
            min_value = 1,
            value = suivi["duree_cycle"] if suivi is not None else 28,
            step = 1,
            help = "28 jours est une valeur proposée. Adaptez-la à votre cycle.",
            key="conception_duree_cycle",
        )
        duree_regles = st.number_input(
            "Durée moyenne de vos règles, en jours",
            min_value = 1,
            value = suivi.get("duree_regles", 5) if suivi is not None else 5,
            step = 1,
            key="conception_duree_regles",
        )
        regularite_cycle = st.radio(
            "Votre cycle est-il généralement régulier ?",
            choix_regularite,
            index=(
                choix_regularite.index(suivi["regularite_cycle"]) if suivi is not None else 0
            ),
            key="conception_regularite",
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

    profil = st.session_state["profil"]

    parcours_actif = next(
        (
            journey
            for journey in profil.journeys
            if journey.id == profil.active_journey_id
        ),
        None,
    )

    if (
        suivi is not None
        and parcours_actif is not None
        and parcours_actif.type == "conception"
    ):
        if st.button(
            "Enregistrer les repères validés dans le parcours actif",
            key="enregistrer_reperes_conception",
        ):
            regularites = {
                "Régulier": "regular",
                "Irrégulier": "irregular",
                "Je ne sais pas": "unknown",
            }

            try:
                reperes = ConceptionJourney(
                    last_period_date=suivi["dernieres_regles"],
                    average_cycle_length=suivi["duree_cycle"],
                    period_length=suivi["duree_regles"],
                    cycle_regularity=regularites[suivi["regularite_cycle"]], # type: ignore
                )

                nouveau_profil = profil.renseigner_reperes_actifs(reperes)

            except ValueError as erreur:
                st.error(str(erreur))
            else:
                st.session_state["profil"] = nouveau_profil
                st.success("Repères enregistrés dans le parcours actif.")

    if (
        parcours_actif is not None
        and isinstance(parcours_actif.details, ConceptionJourney)
    ):
        st.button(
            "Reprendre les repères enregistrés",
            key="reprendre_reperes_conception",
            on_click=reprendre_reperes_conception,
        )

        st.caption("Cette action remplace les champs du formulaire par les repères du parcours actif.")

    with st.expander("Réinitialiser la saisie conception"):
        confirmation_effacement = st.checkbox(
            "Je confirme vouloir vider la saisie temporaire. Les repères enregistrés dans les parcours seront conservés.",
            key="confirmer_effacement_conception",
        )

        st.button(
            "Réinitialiser la saisie conception",
            disabled=not confirmation_effacement,
            key="effacer_reperes_conception",
            on_click=effacer_reperes_conception,
        )
else:
    suivi_grossesse = st.session_state["suivi_grossesse"]

    libelles_datation = {
        "dernieres_regles": "Date des dernières règles",
        "dpa": "Date prévue d'accouchement connue",
    }

    if suivi_grossesse is not None and "methode_datation_grossesse" not in st.session_state:

        st.session_state["methode_datation_grossesse"] = suivi_grossesse["methode_datation"]

        if suivi_grossesse["methode_datation"] == "dernieres_regles":
            cle_date = "date_regles_grossesse"
        else:
            cle_date = "date_accouchement_grossesse"

        st.session_state[cle_date] = suivi_grossesse["date_reference"]
        

    methode_datation = st.radio(
        "Quel repère souhaitez-vous utiliser ?",
        options = list(libelles_datation),
        format_func = lambda identifiant: libelles_datation[identifiant],
        key = "methode_datation_grossesse",
    )

    for cle in ["date_regles_grossesse", "date_accouchement_grossesse"]:
        if cle not in st.session_state:
            st.session_state[cle] = None

    with st.form("formulaire_grossesse"):
        if methode_datation == "dernieres_regles":
            date_reference = st.date_input(
                "Premier jour de vos dernières règles",
                max_value = date.today(),
                format = "DD/MM/YYYY",
                key = "date_regles_grossesse",
            )
        else:
            date_reference = st.date_input(
                "Date prévue d'accouchement",
                format = "DD/MM/YYYY",
                key = "date_accouchement_grossesse",
            )

        grossesse_envoyee = st.form_submit_button("Valider mes repères")

    if grossesse_envoyee:
        if date_reference is None:
            st.error("Renseignez une date pour continuer.")
        else:
            st.session_state["suivi_grossesse"] = {
                "methode_datation": methode_datation,
                "date_reference": date_reference,
            }

    suivi_grossesse = st.session_state["suivi_grossesse"]

    if suivi_grossesse is not None:
        st.caption("Repères issus de la dernières saisie validée.")
        st.write(
            "Repère choisi :", 
            libelles_datation[suivi_grossesse["methode_datation"]],
            )
        st.write(
            "Date renseignée :", 
            suivi_grossesse["date_reference"].strftime("%d/%m/%Y"),
            )           

        if suivi_grossesse["methode_datation"] == "dernieres_regles":
            semaines, jours = calculer_age_depuis_dernieres_regles(
                suivi_grossesse["date_reference"], date.today(),
            )

            st.metric(
                "Âge estimé depuis les dernières règles",
                f"{semaines} SA + {jours} jours",
            )

            st.caption(
                "SA signifie semaines d'aménorrhée. Ce repère est calculé depuis la date renseignée et ne confirme pas la datation médicale."
            )
        else:
            st.info("Le calcul à parti d'un DPA sera ajouté après définition de la convention de datation.")

        with st.expander("Réinitialiser la saisie grossesse"):
            confirmation_effacement = st.checkbox(
                "Je confirme vouloir vider la saisie temporaire. Les repères enregistrés dans les parcours seront conservés.",
                key = "confirmer_effacement_grossesse",
            )

            st.button(
                "Réinitialiser la saisie grossesse",
                disabled = not confirmation_effacement,
                key = "effacer_reperes_grossesse",
                on_click = effacer_reperes_grossesse,
            )

    profil = st.session_state["profil"]

    parcours_actif = next(
        (
            journey
            for journey in profil.journeys
            if journey.id == profil.active_journey_id
        ),
        None,
    )

    if (
        suivi_grossesse is not None
        and parcours_actif is not None
        and parcours_actif.type == "pregnancy"
    ):
        if st.button(
            "Enregistrer les repères validés dans le parcours actif",
            key="enregistrer_reperes_grossesse",
        ):
            try:
                if suivi_grossesse["methode_datation"] == "dernieres_regles":
                    reperes = PregnancyJourney(
                        dating_method="last_period",
                        last_period_date=suivi_grossesse["date_reference"],
                    )
                else:
                    reperes = PregnancyJourney(
                        dating_method="due_date",
                        estimated_due_date=suivi_grossesse["date_reference"],
                    )

                nouveau_profil = profil.renseigner_reperes_actifs(reperes)
            except ValueError as erreur:
                st.error(str(erreur))
            else:
                st.session_state["profil"] = nouveau_profil
                st.success("Repères enregistrés dans le parcours actif.")

    if (
        parcours_actif is not None
        and isinstance(parcours_actif.details, PregnancyJourney)
    ):
        st.button(
            "Reprendre les repères grossesse enregistrés",
            key="reprendre_reperes_grossesse",
            on_click=reprendre_reperes_grossesse,
        )

        st.caption(
            "Cette action remplace la méthode et les champs du formulaire "
            "par les repères du parcours actif."
        )

st.subheader("Mon parcours actif")

profil = st.session_state["profil"]

types_parcours = {
    "Projet de conception": "conception",
    "Grossesse en cours": "pregnancy",
}

if profil.active_journey_id is None:
    st.write("Aucun parcours actif.")

    if st.button(
        f"Démarrer le parcours : {parcours}",
        key="demarrer_parcours",
    ):
        st.session_state["profil"] = profil.demarrer_parcours(
            types_parcours[parcours],
            date.today(),
        )
        st.rerun()
else:
    for journey in profil.journeys:
        if journey.id == profil.active_journey_id:
            libelle = (
                "Projet de conception"
                if journey.type == "conception"
                else "Grossesse en cours"
            )

            st.write("Parcours actif :", libelle)
            st.write(
                "Suivi commencé le :",
                journey.start_date.strftime("%d/%m/%Y"),
            )

            with st.expander("Terminer ce parcours"):
                confirmation_fin = st.checkbox(
                    "Je confirme vouloir terminer ce parcours. Il restera dans mon historique.",
                    key="confirmer_fin_parcours",
                )

                st.button(
                    "Terminer mon parcours",
                    disabled=not confirmation_fin,
                    key="terminer_parcours_actif",
                    on_click=terminer_parcours_actif,
                )

            destination = (
                "grossesse"
                if journey.type == "conception"
                else "conception"
            )

            with st.expander("Changer de parcours"):
                confirmation_changement = st.checkbox(
                    f"Je confirme vouloir terminer le parcours actuel et démarrer un parcours {destination}. L’ancien parcours restera dans mon historique.",
                    key="confirmer_changement_parcours",
                )

                st.button(
                    f"Passer au parcours {destination}",
                    disabled=not confirmation_changement,
                    key="changer_parcours_actif",
                    on_click=changer_parcours_actif,
                )

st.subheader("Mes données")

st.write(
    "L’export contient vos parcours et les repères enregistrés dans chacun. Les saisies temporaires des formulaires ne sont pas incluses."
)

st.caption(
    "Le fichier contient des données personnelles non chiffrées. Conservez-le dans un emplacement privé."
)

contenu_export = exporter_profil(st.session_state["profil"])

st.download_button(
    label="Exporter mes données",
    data=contenu_export,
    file_name="nurtureai-export.json",
    mime="application/json",
    key="exporter_profil",
    on_click="ignore",
)

st.subheader("Historique des parcours")

profil = st.session_state["profil"]

libelles_parcours = {
    "conception": "Projet de conception",
    "pregnancy": "Grossesse",
}

if not profil.journeys:
    st.write("Aucun parcours enregistré.")
else:
    for numero, journey in enumerate(profil.journeys, start=1):
        with st.expander(
            f"Parcours {numero} : {libelles_parcours[journey.type]}"
        ):
            st.write(
                "Début du suivi :",
                journey.start_date.strftime("%d/%m/%Y"),
            )

            if journey.status == "active":
                st.write("Statut : en cours")
            else:
                st.write("Statut : terminé")
                st.write(
                    "Fin du suivi :",
                    journey.end_date.strftime("%d/%m/%Y"),
                )

            if isinstance(journey.details, ConceptionJourney):
                if journey.details.last_period_date is not None:
                    st.write(
                        "Dernières règles renseignées :",
                        journey.details.last_period_date.strftime("%d/%m/%Y"),
                    )

                st.write(
                    "Durée moyenne du cycle :",
                    journey.details.average_cycle_length,
                    "jours",
                )
            elif isinstance(journey.details, PregnancyJourney):
                if journey.details.dating_method == "last_period":
                    st.write(
                        "Dernières règles renseignées :",
                        journey.details.last_period_date.strftime("%d/%m/%Y"), # type: ignore
                    )
                else:
                    st.write(
                        "DPA renseignée :",
                        journey.details.estimated_due_date.strftime("%d/%m/%Y"), # type: ignore
                    )

st.subheader("Prévisualiser un import")

message_import = st.session_state.pop("message_import", None)

if message_import:
    st.success(message_import)

fichier_import = st.file_uploader(
    "Choisir un export NurtureAI",
    type=["json"],
    max_upload_size=1,
    key="fichier_import",
    on_change=annuler_confirmation_import,
)

if fichier_import is not None:
    if fichier_import.size > 1_048_576:
        st.error("Le fichier dépasse la limite de 1 Mio.")
    else:
        try:
            texte = fichier_import.getvalue().decode("utf-8")
            profil_importe = importer_profil(texte)
        except UnicodeDecodeError:
            st.error("Le fichier doit être encodé en UTF-8.")
        except ValueError as erreur:
            st.error(str(erreur))
        except RecursionError:
            st.error("La structure du fichier est trop complexe.")
        else:
            st.success("Le fichier respecte les contrôles d’import actuels.")

            st.write(
                "Nombre de parcours :",
                len(profil_importe.journeys),
            )

            parcours_importe_actif = next(
                (
                    journey
                    for journey in profil_importe.journeys
                    if journey.id == profil_importe.active_journey_id
                ),
                None,
            )

            if parcours_importe_actif is None:
                st.write("Parcours actif : aucun")
            else:
                st.write(
                    "Parcours actif :",
                    libelles_parcours[parcours_importe_actif.type],
                )

            st.warning(
                "L’import remplacera entièrement le profil actuel et videra les saisies temporaires. " \
                "Exportez d’abord votre profil actuel si vous souhaitez le conserver."
            )

            confirmation_import = st.checkbox(
                "Je confirme vouloir remplacer mon profil par cet export.",
                key="confirmer_import",
            )

            st.button(
                "Remplacer mon profil",
                key="appliquer_import",
                disabled=not confirmation_import,
                on_click=appliquer_import,
                args=(profil_importe,),
            )

