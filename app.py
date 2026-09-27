import streamlit as st
from datetime import date, datetime, timezone

from etat_session import initialiser_session, effacer_reperes_grossesse, effacer_reperes_conception, terminer_parcours_actif, changer_parcours_actif 
from etat_session import reprendre_reperes_conception, reprendre_reperes_grossesse, annuler_confirmation_import, appliquer_import, effacer_profil_complet
from etat_session import demarrer_nouveau_parcours, restaurer_profil_local, finaliser_effacement_global, remplacer_profil_session
from calculs import estimer_prochaines_regles, calculer_jour_cycle, valider_durees_cycle, calculer_age_depuis_dernieres_regles, estimer_semaines_grossesse
from calculs import calculer_age_depuis_dpa, convertir_sa_en_sg, determiner_trimestre, calculer_progression_grossesse, estimer_dpa
from modeles import ConceptionJourney, PregnancyJourney
from persistance import exporter_profil, importer_profil, lire_export, sauvegarde_automatique_necessaire
from stockage_navigateur import afficher_stockage_navigateur, lire_sauvegarde_initiale

st.title("NurtureAI")
st.write("Votre compagnon d'information sur la conception et la grossesse.")

st.info(
    "NurtureAI fournit des informations générales et des estimations. Il ne remplace pas une professionnel de santé."
)

if "profil" not in st.session_state:
    lecture_initiale = lire_sauvegarde_initiale()

    if lecture_initiale is None:
        st.info("Lecture de votre sauvegarde locale…")
        st.stop()

    st.session_state["lecture_initiale_stockage"] = (
        lecture_initiale.copy()
    )

    probleme_lecture = None

    if lecture_initiale["lecture"] == "erreur":
        probleme_lecture = "Le stockage du navigateur est inaccessible."
    elif lecture_initiale["texte"] != "":
        try:
            profil_sauvegarde = importer_profil(
                lecture_initiale["texte"]
            )
        except (ValueError, RecursionError):
            probleme_lecture = (
                "La sauvegarde locale ne peut pas être restaurée."
            )
        else:
            remplacer_profil_session(profil_sauvegarde)

    if probleme_lecture:
        st.error(probleme_lecture)
        st.caption(
            "Vous pouvez continuer dans une session temporaire. "
            "La sauvegarde existante ne sera pas supprimée."
        )

        if not st.button(
            "Continuer sans restauration",
            key="continuer_sans_restauration",
        ):
            st.stop()

        st.session_state["mode_temporaire"] = True

initialiser_session()

if st.session_state.get("mode_temporaire", False):
    st.warning(
        "Session ouverte sans restauration. Exportez votre travail avant de quitter. Un enregistrement manuel remplacera la sauvegarde locale existante."
    )

message_effacement = st.session_state.pop("message_effacement", None)

if message_effacement:
    st.success(message_effacement)

parcours = st.radio(
    "Quel écran souhaitez-vous consulter ?",
    ["Projet de conception", "Grossesse en cours"],
    key = "ecran_consulte",
)

libelles_parcours = {
    "conception": "Projet de conception",
    "pregnancy": "Grossesse",
}

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

    if "terme_reference_grossesse" not in st.session_state:
        st.session_state["terme_reference_grossesse"] = (
            suivi_grossesse.get("term_reference_days")
            if suivi_grossesse is not None
            else None
        )

    with st.form("formulaire_grossesse"):
        if methode_datation == "dernieres_regles":
            date_reference = st.date_input(
                "Premier jour de vos dernières règles",
                max_value=date.today(),
                format="DD/MM/YYYY",
                key="date_regles_grossesse",
            )
        else:
            date_reference = st.date_input(
                "Date prévue d'accouchement",
                format="DD/MM/YYYY",
                key="date_accouchement_grossesse",
            )

        duree_reference = st.selectbox(
            "Durée de référence du terme, si connue",
            options=[None, 280, 287],
            format_func=lambda valeur: {
                None: "Je ne sais pas",
                280: "40 SA",
                287: "41 SA",
            }[valeur],
            key="terme_reference_grossesse",
            help=(
                "Renseignez la convention indiquée pour votre suivi. Si elle est inconnue, conservez « Je ne sais pas » sans choisir au hasard."
            ),
        )

        grossesse_envoyee = st.form_submit_button("Valider mes repères")

    if grossesse_envoyee:
        if date_reference is None:
            st.error("Renseignez une date pour continuer.")
        else:
            st.session_state["suivi_grossesse"] = {
                "methode_datation": methode_datation,
                "date_reference": date_reference,
                "term_reference_days": duree_reference,
            }

    suivi_grossesse = st.session_state["suivi_grossesse"]

    if suivi_grossesse is not None:
        age_sa_jours = None
        dpa_affichee = None

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

            age_sa_jours = semaines * 7 + jours

            st.metric(
                "Âge estimé depuis les dernières règles",
                f"{semaines} SA + {jours} jours",
            )

            terme_dpa = suivi_grossesse.get("term_reference_days")

            if terme_dpa is not None:
                dpa_estimee = estimer_dpa(
                    suivi_grossesse["date_reference"],
                    terme_reference_jours=terme_dpa,
                )

                dpa_affichee = dpa_estimee

                st.write(f"DPA estimée : {dpa_estimee:%d/%m/%Y}")

                st.caption(
                    f"Estimation depuis les dernières règles avec une durée de {terme_dpa // 7} SA. Elle ne remplace pas une datation médicale."
                )
            else:
                st.info("DPA non estimée : aucune durée de référence renseignée.")

            age_sg = estimer_semaines_grossesse(
                suivi_grossesse["date_reference"],
                date.today(),
            )

            if age_sg is None:
                st.info("Estimation en SG non affichable avant 2 SA.")
            else:
                semaines_sg, jours_sg = age_sg

                st.metric(
                    "Semaines de grossesse estimées",
                    f"{semaines_sg} SG + {jours_sg} jours",
                )

            st.caption(
                "SA : semaines d’aménorrhée, comptées depuis le premier jour des dernières règles. SG : semaines de grossesse estimées ici en retirant 14 jours. " \
                "Ce décalage conventionnel peut ne pas correspondre à la date réelle de fécondation et ne remplace pas une datation médicale. "
                "[Source : Assurance Maladie] (https://www.ameli.fr/assure/sante/devenir-parent/grossesse/grossesse-en-bonne-sante/grossesse/premiers-symptomes-grossesse)"
            )
        else:
            dpa_affichee = suivi_grossesse["date_reference"]
            duree_validee = suivi_grossesse.get("term_reference_days")

            if duree_validee is None:
                st.info("DPA conservée. Le calcul des SA nécessite une convention renseignée.")
            else:
                try:
                    semaines, jours = calculer_age_depuis_dpa(
                        suivi_grossesse["date_reference"],
                        date.today(),
                        terme_reference_jours=duree_validee,
                    )
                except ValueError as erreur:
                    st.warning(str(erreur))
                else:
                    age_sa_jours = semaines * 7 + jours

                    st.metric(
                        "Âge estimé à partir de la DPA",
                        f"{semaines} SA + {jours} jours",
                    )

                    age_sg = convertir_sa_en_sg(semaines, jours)

                    if age_sg is None:
                        st.info("Estimation en SG non affichable avant 2 SA.")
                    else:
                        semaines_sg, jours_sg = age_sg

                        st.metric(
                            "Semaines de grossesse estimées",
                            f"{semaines_sg} SG + {jours_sg} jours",
                        )

                    st.caption(
                        f"Convention renseignée : {duree_validee // 7} SA. Les SG sont estimées en retirant 14 jours aux SA. "
                        "Ce calcul ne détermine pas la date réelle de fécondation, ne modifie pas votre DPA et ne remplace pas une datation médicale."
                    )

        if dpa_affichee is not None and dpa_affichee < date.today():
            st.info(
                "La DPA affichée est passée. Ce repère de calendrier ne permet pas de conclure à un accouchement ou à un problème de santé. "
                "Votre parcours reste inchangé."
            )

        if age_sa_jours is not None:
            trimestre = determiner_trimestre(
                age_sa_jours,
                debut_deuxieme=14 * 7,
                debut_troisieme=28 * 7,
            )

            st.write(f"Trimestre estimé : {trimestre}")

            st.caption(
                "Repère pédagogique : deuxième trimestre à 14 SA, troisième à 28 SA. Ces seuils ne définissent pas le calendrier de vos examens. "
                "[Source : ACOG](https://www.acog.org/womens-health/faqs/how-your-fetus-grows-during-pregnancy)"
            )

        duree_progression = suivi_grossesse.get("term_reference_days")

        if age_sa_jours is not None and duree_progression is not None:
            progression = calculer_progression_grossesse(
                age_sa_jours,
                terme_reference_jours=duree_progression,
            )

            st.progress(
                progression,
                text=f"Progression chronologique indicative : {progression:.0%}",
            )

            st.caption(
                "Cette proportion compare l’âge estimé à la durée de référence renseignée. Elle ne représente ni un état de santé ni une probabilité d’accouchement. "
                "Atteindre 100 % ne termine pas votre parcours."
            )
        
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
                        term_reference_days=suivi_grossesse.get(
                            "term_reference_days"
                        ),
                        dating_rule_version=(
                            "sa-reference-v1"
                            if suivi_grossesse.get("term_reference_days") is not None
                            else None
                        ),
                    )
                else:
                    reperes = PregnancyJourney(
                        dating_method="due_date",
                        estimated_due_date=suivi_grossesse["date_reference"],
                        term_reference_days=suivi_grossesse.get(
                            "term_reference_days"
                        ),
                        dating_rule_version=(
                            "sa-reference-v1"
                            if suivi_grossesse.get("term_reference_days")
                            is not None
                            else None
                        ),
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

    st.caption(
        "Le démarrage réinitialise les saisies temporaires des formulaires. Les parcours déjà enregistrés restent dans l’historique."
    )

    st.button(
        f"Démarrer le parcours : {parcours}",
        key="demarrer_parcours",
        on_click=demarrer_nouveau_parcours,
        args=(types_parcours[parcours],),
    )
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
                st.caption(
                    "Les saisies temporaires seront réinitialisées. Enregistrez les repères à conserver dans le parcours actuel avant de confirmer."
                )
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

st.subheader("Historique des parcours")

profil = st.session_state["profil"]

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

st.subheader("Mes données")

with st.expander("Sauvegarde dans ce navigateur"):
    message_restauration = st.session_state.pop(
        "message_restauration_locale",
        None,
    )

    if message_restauration:
        st.success(message_restauration)

    st.write(
        "Enregistrez une copie de votre profil, de ses parcours et de leurs repères dans ce navigateur. Les saisies temporaires des formulaires ne sont pas incluses."
    )

    st.caption(
        "Les modifications enregistrées dans les parcours sont sauvegardées automatiquement lorsque le stockage est disponible et sans conflit. "
        "Après une erreur ou pour remplacer un autre profil, un enregistrement manuel reste nécessaire."
    )

    etat_connu = st.session_state.get(
        "stockage_profil",
        st.session_state.get("lecture_initiale_stockage", {}),
    )

    sauvegarde_auto = sauvegarde_automatique_necessaire(
        st.session_state["profil"],
        etat_connu,
        mode_temporaire=st.session_state.get(
            "mode_temporaire",
            False,
        ),
    )

    resultat_stockage = afficher_stockage_navigateur(
        exporter_profil(st.session_state["profil"]),
        cle_stockage="nurtureai:profil:v1",
        key="stockage_profil",
        on_effacement=finaliser_effacement_global,
        sauvegarde_auto=sauvegarde_auto,
    )

    lecture_locale = resultat_stockage.get("lecture")
    texte_local = resultat_stockage.get("texte")
    erreur_locale = resultat_stockage.get("erreur_operation")

    if texte_local != st.session_state.get("sauvegarde_locale_previsualisee"):
        st.session_state["sauvegarde_locale_previsualisee"] = texte_local
        st.session_state["confirmer_restauration_locale"] = False

    if erreur_locale:
        st.error(erreur_locale)

    if lecture_locale == "erreur":
        st.error("Impossible de lire la sauvegarde locale. Rechargez la page après avoir rétabli l’accès au stockage.")
    elif lecture_locale is None or texte_local is None:
        st.info("Lecture de la sauvegarde locale en cours.")
    elif texte_local == "":
        st.info("Aucune sauvegarde locale disponible.")
    else:
        try:
            profil_local = importer_profil(texte_local)
        except (ValueError, RecursionError):
            st.error("La sauvegarde locale ne respecte pas le format attendu. Elle n’a pas été appliquée au profil actuel.")
        else:
            if erreur_locale:
                st.warning(
                    "La dernière opération a échoué. L’état actuel du stockage ne peut pas être confirmé."
                )
            elif profil_local == st.session_state["profil"]:
                st.success(
                    "Le profil de session correspond à la dernière sauvegarde locale lue ou enregistrée."
                )
            else:
                st.warning(
                    "Le profil de session diffère de la dernière sauvegarde confirmée. Attendez la confirmation de sauvegarde avant de quitter. "
                    "En cas d’erreur, exportez vos données."
                )
            
            st.write(
                "Nombre de parcours sauvegardés :",
                len(profil_local.journeys),
            )
            parcours_local_actif = next(
                (
                    journey
                    for journey in profil_local.journeys
                    if journey.id == profil_local.active_journey_id
                ),
                None,
            )

            st.write(
                "Parcours actif sauvegardé :",
                libelles_parcours[parcours_local_actif.type]
                if parcours_local_actif is not None
                else "Aucun",
            )

            st.warning(
                "La restauration remplacera le profil actuel et videra les saisies temporaires. Exportez d’abord votre profil actuel si vous souhaitez le conserver."
            )

            confirmation_restauration = st.checkbox(
                "Je confirme vouloir remplacer mon profil par cette sauvegarde.",
                key="confirmer_restauration_locale",
            )

            st.button(
                "Restaurer cette sauvegarde",
                key="restaurer_profil_local",
                disabled=not confirmation_restauration,
                on_click=restaurer_profil_local,
                args=(profil_local,),
            )

    st.caption(
        "L’effacement confirmé supprime la sauvegarde locale et toutes les données de session. Les fichiers JSON téléchargés restent sur votre appareil."
    )

with st.expander("Exporter mes données"):
    # Textes explicatifs et bouton de téléchargement existants.
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

with st.expander("Importer mes données"):
    # Sélection du fichier, aperçu et confirmation existants.
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
                donnees_export = lire_export(texte)
            except UnicodeDecodeError:
                st.error("Le fichier doit être encodé en UTF-8.")
            except ValueError as erreur:
                st.error(str(erreur))
            except RecursionError:
                st.error("La structure du fichier est trop complexe.")
            else:
                st.success("Le fichier respecte les contrôles d’import actuels.")

                horodatage = donnees_export.get("exported_at")

                if horodatage is None:
                    st.write("Date d’export : non disponible dans ce fichier.")
                else:
                    date_export = datetime.fromisoformat(horodatage)
                    date_export_utc = date_export.astimezone(timezone.utc)

                    st.write(
                        "Export créé le :",
                        date_export_utc.strftime("%d/%m/%Y à %H:%M:%S UTC"),
                    )

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

with st.expander("Effacer toutes mes données de session"):
    # Avertissement, confirmation et bouton existants.
    st.warning(
        "Cette action supprime le profil actuel, tous ses parcours, leurs repères et les saisies temporaires. " \
        "Exportez d’abord vos données si vous souhaitez les conserver."
    )

    st.caption(
        "Cette action efface uniquement la session. Pour supprimer également la sauvegarde du navigateur, utilisez « Effacer la sauvegarde et la session » " \
        "dans la section de sauvegarde. Les fichiers JSON téléchargés restent sur votre appareil."
    )

    confirmation_totale = st.checkbox(
        "Je confirme vouloir effacer toutes les données de cette session.",
        key="confirmer_effacement_total",
    )

    st.button(
        "Effacer toutes mes données de session",
        key="effacer_profil_complet",
        disabled=not confirmation_totale,
        on_click=effacer_profil_complet,
    )

