import streamlit as st
from datetime import date, datetime, timezone

from etat_session import (
    initialiser_session, effacer_reperes_grossesse, effacer_reperes_conception, terminer_parcours_actif, changer_parcours_actif,
    reprendre_reperes_conception, reprendre_reperes_grossesse, annuler_confirmation_import, appliquer_import, effacer_profil_complet,
    demarrer_nouveau_parcours, restaurer_profil_local, finaliser_effacement_global, remplacer_profil_session, changer_mois_calendrier
)
from calculs import (
    estimer_prochaines_regles, calculer_jour_cycle, valider_durees_cycle, calculer_age_depuis_dernieres_regles, estimer_semaines_grossesse,
    calculer_age_depuis_dpa, convertir_sa_en_sg, determiner_trimestre, calculer_progression_grossesse, estimer_dpa
)
from modeles import ConceptionJourney, PregnancyJourney, Appointment, THEMES_RENDEZ_VOUS
from persistance import exporter_profil, importer_profil, lire_export, sauvegarde_automatique_necessaire
from stockage_navigateur import afficher_stockage_navigateur, lire_sauvegarde_initiale
from fiches_rendez_vous import exporter_fiche_texte, LIBELLES_TYPES as types_rdv, LIBELLES_THEMES as libelles_themes_rdv
from calendrier import rendez_vous_du_mois, construire_grille_mois, regles_du_mois, dpa_du_mois, prochaines_regles_du_mois
from timeline import construire_timeline, choisir_etape_a_mettre_en_avant, calculer_jours_sa_timeline
from fiches_hebdomadaires import charger_fiches_hebdomadaires, selectionner_fiche_semaine


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
        lecture_initiale.copy() # type: ignore
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

        st.caption("Cette action remplace la méthode et les champs du formulaire par les repères du parcours actif.")

    st.subheader("Les étapes de mon suivi grossesse")

    profil_timeline = st.session_state["profil"]
    grossesse_active = next(
        (
            journey for journey in profil_timeline.journeys
            if journey.id == profil_timeline.active_journey_id
            and journey.type == "pregnancy"
        ),
        None,
    )

    if grossesse_active is None:
        st.info("Démarrez un parcours grossesse pour consulter ses étapes de suivi.")
    else:
        st.caption(
            "Les étapes utilisent les repères enregistrés du parcours actif. Une période passée ne signifie pas qu’un examen a été réalisé."
        )

        try:
            elements_timeline = construire_timeline(
                grossesse_active.details,
                date.today(),
            )
        except ValueError:
            st.warning(
                "Les étapes de suivi sont indisponibles. Vérifiez les repères enregistrés ; si le problème persiste, le contenu doit être vérifié."
            )
        else:
            if not elements_timeline:
                st.info("Aucune fiche de suivi disponible pour le moment.")

            repere = choisir_etape_a_mettre_en_avant(elements_timeline)

            if repere is not None:
                titre_repere = (
                    "Repère actuel"
                    if repere["position"] == "current"
                    else "Prochaine période disponible"
                )

                st.write(f"**{titre_repere}**")
                st.text(repere["etape"]["title"])
                st.caption("Repère parmi les fiches disponibles. Consultez le détail et les sources ci-dessous.")

            elif elements_timeline:
                if any(
                    element["position"] == "unknown"
                    for element in elements_timeline
                ):
                    st.info("Complétez les repères de datation enregistrés pour situer les étapes de suivi.")
                else:
                    st.info("Aucune prochaine période dans les fiches disponibles. Cela ne signifie pas que le suivi est terminé.")

            libelles_positions = {
                "upcoming": "Période à venir",
                "current": "Période en cours",
                "past": "Période passée",
                "unknown": "Position indéterminée",
            }

            for element in elements_timeline:
                etape = element["etape"]
                position = element["position"]

                with st.expander(etape["title"]):
                    st.caption(libelles_positions[position])

                    if position == "unknown":
                        st.info("Les repères enregistrés ne permettent pas de situer cette étape dans le temps.")

                    for champ, titre in (
                        ("when", "Quand ?"),
                        ("why", "Pourquoi ?"),
                        ("how", "Comment cela se déroule généralement ?"),
                    ):
                        st.write(f"**{titre}**")
                        st.text(etape[champ])

                    st.write("**Questions possibles**")

                    for numero, question in enumerate(
                        etape["questions"],
                        start=1,
                    ):
                        st.text(f"{numero}. {question}")

                    source = etape["source"]
                    st.text(source["title"])
                    st.caption(
                        f"Source : {source['name']} ; "
                        f"consultée le {source['retrieved_at']}."
                    )
                    st.link_button(
                        "Consulter la source",
                        source["url"],
                    )
                    for secondaire in etape.get(
                        "secondary_sources", []
                    ):
                        st.write("**Source secondaire**")
                        st.text(secondaire["title"])
                        st.caption(
                            f"{secondaire['name']} ; "
                            f"consultée le {secondaire['retrieved_at']}. "
                            "Référence de recoupement ; "
                            "son texte n’est pas reproduit."
                        )
                        st.link_button(
                            "Consulter la référence secondaire",
                            secondaire["url"],
                        )
                        st.link_button(
                            "Conditions de réutilisation",
                            secondaire["terms_url"],
                        )

    st.subheader("Ma fiche de la semaine")

    if grossesse_active is None:
        st.info("Démarrez un parcours grossesse pour consulter les fiches hebdomadaires.")
    else:
        st.caption("Cette fiche utilise les repères enregistrés du parcours actif.")

        try:
            jours_fiche = calculer_jours_sa_timeline(
                grossesse_active.details,
                date.today(),
            )

            fiche_semaine = None

            if jours_fiche is not None:
                fiche_semaine = selectionner_fiche_semaine(
                    charger_fiches_hebdomadaires(),
                    jours_fiche,
                )
        except ValueError:
            st.warning("La fiche hebdomadaire est indisponible : les repères ou le contenu doivent être vérifiés.")
        else:
            if jours_fiche is None:
                st.info("Complétez les repères enregistrés pour déterminer la semaine SA.")
            elif fiche_semaine is None:
                st.info(f"Aucune fiche disponible pour {jours_fiche // 7} SA révolues.")
            else:
                st.caption(f"{jours_fiche // 7} SA révolues.")
                st.text(fiche_semaine["title"])
                st.text(fiche_semaine["body"])

                attribution = fiche_semaine.get("attribution")
                mode = attribution["mode"] if attribution is not None else None

                if mode == "licence":
                    st.text(attribution["text"]) # type: ignore
                    st.link_button(
                        "Licence de la fiche hebdomadaire",
                        attribution["url"], # type: ignore
                    )
                else:
                    source = fiche_semaine["source"]
                    st.text(source["title"])
                    st.caption(
                        f"Source : {source['name']} ; "
                        f"consultée le {source['retrieved_at']}."
                    )
                    st.link_button(
                        "Source de la fiche hebdomadaire",
                        source["url"],
                    )

                    if mode == "reference":
                        st.link_button(
                            attribution["text"], # type: ignore
                            attribution["url"], # type: ignore
                        )

                secondaires = fiche_semaine.get("secondary_sources", [])

                if secondaires:
                    with st.expander("Références complémentaires"):
                        st.caption("Documents utilisés pour recouper les informations de cette fiche.")

                        for secondaire in secondaires:
                            st.text(secondaire["title"])
                            st.caption(
                                f"{secondaire['name']} ; "
                                f"consultée le {secondaire['retrieved_at']}."
                            )
                            st.link_button(
                                f"Consulter : {secondaire['title']}",
                                secondaire["url"],
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

            if journey.status == "completed":
                st.write("Rendez-vous de ce parcours")
                st.caption("Fiches archivées en lecture seule.")

                fiches_archivees = sorted(
                    (
                        fiche for fiche in profil.appointments
                        if fiche.journey_id == journey.id
                    ),
                    key=lambda fiche: (
                        fiche.date is None,
                        fiche.date or date.max,
                    ),
                )

                if not fiches_archivees:
                    st.caption(
                        "Aucune fiche de rendez-vous pour ce parcours."
                    )

                for fiche_archivee in fiches_archivees:
                    st.text(exporter_fiche_texte(fiche_archivee))

                    st.download_button(
                        label="Télécharger cette fiche archivée (.txt)",
                        data=exporter_fiche_texte(
                            fiche_archivee
                        ).encode("utf-8"),
                        file_name=(
                            f"nurtureai-rendez-vous-{fiche_archivee.id}.txt"
                        ),
                        mime="text/plain; charset=utf-8",
                        key=f"telecharger_archive_rdv_{fiche_archivee.id}",
                        on_click="ignore",
                    )

st.subheader("Mes rendez-vous")

message_modification = st.session_state.pop(
    "message_modification_rdv",
    None,
)

if message_modification:
    st.success(message_modification)

message_suppression = st.session_state.pop(
    "message_suppression_rdv",
    None,
)

if message_suppression:
    st.success(message_suppression)

profil = st.session_state["profil"]
parcours_rdv = next(
    (
        journey for journey in profil.journeys
        if journey.id == profil.active_journey_id
    ),
    None,
)

if parcours_rdv is None:
    st.info("Démarrez un parcours pour créer une fiche de rendez-vous.")
else:
    st.caption(f"Nouvelle fiche pour le parcours actif : {libelles_parcours[parcours_rdv.type]}.")

    if st.session_state.pop(f"vider_rdv_{parcours_rdv.id}", False):
        st.session_state[f"type_rdv_{parcours_rdv.id}"] = "other"
        st.session_state[f"date_rdv_{parcours_rdv.id}"] = None
        st.session_state[f"themes_rdv_{parcours_rdv.id}"] = []
        st.session_state[f"notes_rdv_{parcours_rdv.id}"] = ""
        st.session_state[f"questions_rdv_{parcours_rdv.id}"] = ""
        st.success("Fiche ajoutée au profil.")

    with st.form(f"nouveau_rdv_{parcours_rdv.id}"):
        type_rdv = st.selectbox(
            "Type de rendez-vous",
            options=list(types_rdv),
            index=4,
            format_func=lambda valeur: types_rdv[valeur],
            key=f"type_rdv_{parcours_rdv.id}",
        )

        date_rdv = st.date_input(
            "Date du rendez-vous, si connue",
            value=None,
            format="DD/MM/YYYY",
            key=f"date_rdv_{parcours_rdv.id}",
        )

        themes_rdv = st.multiselect(
            "Thèmes à aborder",
            options=THEMES_RENDEZ_VOUS,
            format_func=lambda valeur: libelles_themes_rdv[valeur],
            help="Facultatif. Vous pouvez sélectionner plusieurs thèmes.",
            key=f"themes_rdv_{parcours_rdv.id}",
        )

        notes_rdv = st.text_area(
            "Notes pour le rendez-vous",
            max_chars=5000,
            help=("Facultatif, 5 000 caractères maximum. Ces notes restent telles que vous les saisissez."),
            key=f"notes_rdv_{parcours_rdv.id}",
        )

        questions_rdv = st.text_area(
            "Questions à poser",
            help=("Facultatif. Une question par ligne, 30 questions maximum et 500 caractères par question. Les lignes vides sont ignorées."),
            key=f"questions_rdv_{parcours_rdv.id}",
        )        

        creer_rdv = st.form_submit_button(
            "Créer la fiche",
            key="creer_rendez_vous",
        )

    if creer_rdv:
        try:
            fiche = Appointment(
                journey_id=parcours_rdv.id,
                appointment_type=type_rdv, # type: ignore
                date=date_rdv,
                notes=notes_rdv,
                topics=tuple(themes_rdv),
                questions=tuple(
                    ligne for ligne in questions_rdv.splitlines()
                    if ligne.strip()
                ),
            )
            profil = profil.ajouter_rendez_vous(fiche)
        except ValueError as erreur:
            st.error(str(erreur))
        else:
            st.session_state["profil"] = profil
            st.session_state[f"vider_rdv_{parcours_rdv.id}"] = True
            st.rerun()

    fiches_parcours = sorted(
        (
            fiche for fiche in profil.appointments
            if fiche.journey_id == parcours_rdv.id
        ),
        key=lambda fiche: (
            fiche.date is None,
            fiche.date or date.max,
        ),
    )

    st.write(f"Fiches du parcours actif : {len(fiches_parcours)}")

    if not fiches_parcours:
        st.info("Aucune fiche de rendez-vous pour ce parcours.")

    for numero, fiche in enumerate(fiches_parcours, start=1):
        date_affichee = (
            fiche.date.strftime("%d/%m/%Y")
            if fiche.date is not None
            else "Date à définir"
        )

        with st.expander(
            f"Fiche {numero} : "
            f"{types_rdv[fiche.appointment_type]} ({date_affichee})"
        ):
            st.write(f"Type : {types_rdv[fiche.appointment_type]}")
            st.write(f"Date : {date_affichee}")
            if fiche.topics:
                themes_affiches = ", ".join(
                    libelles_themes_rdv[theme]
                    for theme in fiche.topics
                )
                st.write(f"Thèmes : {themes_affiches}")
            else:
                st.caption("Aucun thème sélectionné.")
            
            st.write("Notes")
            if fiche.notes:
                st.text(fiche.notes)
            else:
                st.caption("Aucune note renseignée.")
            
            st.write("Questions")
            if fiche.questions:
                for numero_question, question in enumerate(
                    fiche.questions, start=1
                ):
                    st.text(f"{numero_question}. {question}")
            else:
                st.caption("Aucune question renseignée.")
            
            st.download_button(
                label="Télécharger la fiche (.txt)",
                data=exporter_fiche_texte(fiche).encode("utf-8"),
                file_name=f"nurtureai-rendez-vous-{fiche.id}.txt",
                mime="text/plain; charset=utf-8",
                key=f"telecharger_rdv_{fiche.id}",
                on_click="ignore",
            )

            cle_edition = (
                f"edition_rdv_{fiche.id}_{fiche.updated_at.isoformat()}"
            )

            if st.checkbox(
                "Modifier cette fiche",
                key=cle_edition,
                help="Décochez pour abandonner les modifications non enregistrées.",
            ):
                with st.form(f"formulaire_{cle_edition}"):
                    type_modifie = st.selectbox(
                        "Type",
                        options=list(types_rdv),
                        index=list(types_rdv).index(fiche.appointment_type),
                        format_func=lambda valeur: types_rdv[valeur],
                        key=f"type_{cle_edition}",
                    )

                    date_modifiee = st.date_input(
                        "Date, si connue",
                        value=fiche.date,
                        format="DD/MM/YYYY",
                        key=f"date_{cle_edition}",
                    )

                    themes_modifies = st.multiselect(
                        "Thèmes",
                        options=THEMES_RENDEZ_VOUS,
                        default=list(fiche.topics),
                        format_func=lambda valeur: libelles_themes_rdv[valeur],
                        key=f"themes_{cle_edition}",
                    )

                    notes_modifiees = st.text_area(
                        "Notes, 5 000 caractères maximum",
                        value=fiche.notes,
                        max_chars=5000,
                        key=f"notes_{cle_edition}",
                    )

                    questions_modifiees = st.text_area(
                        "Questions, une par ligne",
                        value="\n".join(fiche.questions),
                        help=(
                            "30 questions maximum, 500 caractères chacune. "
                            "Les lignes vides sont ignorées."
                        ),
                        key=f"questions_{cle_edition}",
                    )

                    enregistrer_modification = st.form_submit_button(
                        "Enregistrer les modifications",
                        key=f"enregistrer_{cle_edition}",
                    )

                if enregistrer_modification:
                    try:
                        profil = st.session_state["profil"].modifier_rendez_vous(
                            fiche.id,
                            appointment_type=type_modifie,
                            date=date_modifiee,
                            notes=notes_modifiees,
                            questions=tuple(
                                ligne
                                for ligne in questions_modifiees.splitlines()
                                if ligne.strip()
                            ),
                            topics=tuple(themes_modifies),
                            modifie_le=datetime.now(timezone.utc),
                        )
                    except ValueError as erreur:
                        st.error(str(erreur))
                    else:
                        st.session_state["profil"] = profil
                        st.session_state["message_modification_rdv"] = (
                            "Fiche modifiée dans le profil."
                        )
                        st.rerun()

            confirmation_suppression = st.checkbox(
                "Je confirme vouloir supprimer cette fiche et son contenu.",
                key=f"confirmer_suppression_rdv_{fiche.id}",
            )

            if st.button(
                "Supprimer cette fiche",
                key=f"supprimer_rdv_{fiche.id}",
                disabled=not confirmation_suppression,
            ) and confirmation_suppression:
                try:
                    profil = st.session_state["profil"].supprimer_rendez_vous(
                        fiche.id
                    )
                except ValueError as erreur:
                    st.error(str(erreur))
                else:
                    st.session_state["profil"] = profil
                    st.session_state["message_suppression_rdv"] = (
                        "Fiche supprimée du profil."
                    )
                    st.rerun()

st.subheader("Calendrier du parcours")

profil_calendrier = st.session_state["profil"]

if not profil_calendrier.journeys:
    st.info("Aucun parcours disponible pour le calendrier.")
else:
    parcours_calendrier = {
        journey.id: journey
        for journey in profil_calendrier.journeys
    }
    ids_calendrier = list(parcours_calendrier)

    choix_initial = (
        ids_calendrier.index(profil_calendrier.active_journey_id)
        if profil_calendrier.active_journey_id is not None
        else len(ids_calendrier) - 1
    )

    id_consulte = st.selectbox(
        "Parcours à consulter",
        options=ids_calendrier,
        index=choix_initial,
        format_func=lambda identifiant: (
            f"{libelles_parcours[parcours_calendrier[identifiant].type]} "
            f"du {parcours_calendrier[identifiant].start_date:%d/%m/%Y} "
            f"({'En cours' if parcours_calendrier[identifiant].status == 'active' else 'Terminé'})"
        ),
        key="calendrier_parcours",
    )

    mois_consulte = st.date_input(
        "Date du mois à consulter",
        value=date.today(),
        min_value=date.min,
        max_value=date.max,
        format="DD/MM/YYYY",
        help="Tous les rendez-vous du mois choisi sont affichés.",
        key="calendrier_mois",
    )

    precedent, suivant = st.columns(2)

    with precedent:
        st.button(
            "Mois précédent",
            key="calendrier_precedent",
            disabled=(
                mois_consulte is None
                or (mois_consulte.year, mois_consulte.month) == (1, 1)
            ),
            on_click=changer_mois_calendrier,
            args=(-1,),
        )

    with suivant:
        st.button(
            "Mois suivant",
            key="calendrier_suivant",
            disabled=(
                mois_consulte is None
                or (mois_consulte.year, mois_consulte.month) == (9999, 12)
            ),
            on_click=changer_mois_calendrier,
            args=(1,),
        )

    st.caption(
        "Rendez-vous saisis et repères de conception et de grossesse. Les fiches sans date restent dans Mes rendez-vous ou dans l’historique. "
        "Consulter un parcours ne le réactive pas."
    )

    if mois_consulte is None:
        st.info("Choisissez une date pour consulter son mois.")
    else:
        fiches_mois = rendez_vous_du_mois(
            profil_calendrier,
            id_consulte, # type: ignore
            annee=mois_consulte.year,
            mois=mois_consulte.month,
        )

        parcours_consulte = parcours_calendrier[id_consulte]
        evenements_suivi = ()

        if isinstance(parcours_consulte.details, ConceptionJourney):
            evenements_suivi = regles_du_mois(
                parcours_consulte.details,
                annee=mois_consulte.year,
                mois=mois_consulte.month,
            ) + prochaines_regles_du_mois(
                parcours_consulte.details,
                annee=mois_consulte.year,
                mois=mois_consulte.month,
            )
        elif isinstance(parcours_consulte.details, PregnancyJourney):
            evenements_suivi = dpa_du_mois(
                parcours_consulte.details,
                annee=mois_consulte.year,
                mois=mois_consulte.month,
            )

        evenements_par_jour = {
            evenement.jour: evenement
            for evenement in evenements_suivi
        }

        if not fiches_mois and not evenements_suivi:
            st.info("Aucun événement pour ce mois et ce parcours.")

        noms_mois = (
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
        )

        st.write(
            f"**{noms_mois[mois_consulte.month - 1]} "
            f"{mois_consulte.year}**"
        )

        rendez_vous_par_jour = {}

        for fiche_mois in fiches_mois:
            jour = fiche_mois.date
            rendez_vous_par_jour[jour] = (
                rendez_vous_par_jour.get(jour, 0) + 1
            )

        jours_semaine = (
            "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"
        )
        lignes_grille = []

        for semaine in construire_grille_mois(
            mois_consulte.year,
            mois_consulte.month,
        ):
            ligne = {}

            for libelle, jour in zip(jours_semaine, semaine):
                if jour is None:
                    ligne[libelle] = ""
                else:
                    nombre = rendez_vous_par_jour.get(jour, 0)
                    ligne[libelle] = (
                        f"{jour.day} ({nombre} RDV)"
                        if nombre
                        else str(jour.day)
                    )

                    evenement = evenements_par_jour.get(jour)
                    if evenement is not None:
                        ligne[libelle] += f" ; {evenement.libelle}"

            lignes_grille.append(ligne)

        st.table(lignes_grille)

        st.caption("RDV : rendez-vous saisis. Le nombre entre parenthèses indique combien de rendez-vous sont prévus ce jour-là.")
        if isinstance(parcours_consulte.details, ConceptionJourney):
            st.caption(
                "Seul le début des dernières règles est déclaré. Les jours suivants et le début des prochaines règles sont estimés à partir des durées renseignées. "
                "Ces estimations ne constituent pas des observations. Les dates réelles peuvent différer, notamment si les cycles sont irréguliers ou leur régularité inconnue."
            )
        elif isinstance(parcours_consulte.details, PregnancyJourney):
            st.caption(
                "DPA renseignée : date saisie dans le parcours. DPA estimée : date calculée à partir des dernières règles et du terme de référence choisi. "
                "Ces repères ne constituent pas une date de naissance certaine."
            )
        st.write("Détail des rendez-vous du mois")

        if not fiches_mois:
            st.info("Aucun rendez-vous daté pour ce mois et ce parcours.")

        for fiche_mois in fiches_mois:
            st.write(
                f"{fiche_mois.date:%d/%m/%Y} : "
                f"{types_rdv[fiche_mois.appointment_type]}"
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
        "Enregistrez une copie de votre profil, de ses parcours, de leurs repères et de vos fiches de rendez-vous dans ce navigateur."
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
            st.write(
                f"Nombre de rendez-vous sauvegardés : "
                f"{len(profil_local.appointments)}"
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
        "L’export contient vos parcours, leurs repères et toutes vos fiches de rendez-vous, y compris celles des parcours archivés."
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
                st.write(
                    f"Nombre de rendez-vous : "
                    f"{len(profil_importe.appointments)}"
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

