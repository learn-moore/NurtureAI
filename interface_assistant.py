import json
import streamlit as st

from pathlib import Path
from datetime import datetime, timezone

from corpus_documentaire import charger_corpus
from intentions import MESSAGE_URGENCE, reperer_declaration_urgence
from messages_assistant import preparer_messages
from recherche_documentaire import rechercher_corpus
from classification_intentions import CONSIGNES_CLASSIFICATION
from assistant_groq import traiter_demande_groq
from fiches_rendez_vous import PreparationRendezVousUrgente
from messages_assistant import preparer_messages_rendez_vous
from preparation_rendez_vous import enregistrer_questions_relues, controler_et_proposer_questions
from securite_rendez_vous import preparer_controle_rendez_vous
from generation_groq import creer_appel_groq_rendez_vous
from fidelite_rendez_vous import CONSIGNES_FIDELITE_RENDEZ_VOUS
from preparation_rendez_vous import controler_proposer_et_verifier_questions


CHEMIN_CORPUS = (
    Path(__file__).resolve().parent
    / "donnees"
    / "corpus_medical.json"
)
MODELE = "openai/gpt-oss-20b"


def effacer_apercu_assistant():
    st.session_state.pop("assistant_apercu", None)
    st.session_state.pop("assistant_resultat", None)
    st.session_state["assistant_autorisation"] = False


def executer_apercu_assistant(apercu, *, cle_api):
    messages_attendus = preparer_messages(
        apercu["question"],
        rechercher_corpus(
            apercu["question"],
            apercu["corpus"],
        ),
        mode="medical",
    )

    if (
        messages_attendus != apercu["messages"]
        or apercu["consignes_classification"] != CONSIGNES_CLASSIFICATION
        or apercu["modele"] != MODELE
    ):
        raise ValueError(
            "L’aperçu ne correspond plus à la configuration courante."
        )

    return traiter_demande_groq(
        apercu["question"],
        apercu["corpus"],
        cle_api=cle_api,
        modele=apercu["modele"],
        mode="medical",
    )


def afficher_assistant():
    st.subheader("Assistant documentaire")
    st.caption(
        "Informations générales sur la conception et la grossesse. Cet assistant ne peut pas évaluer une situation médicale personnelle."
    )

    with st.expander("Préparer une question"):
        st.info(
            "Cette étape prépare uniquement un aperçu local. Aucune donnée n’est envoyée à un fournisseur IA."
        )
        st.caption(
            "Utilisez des questions fictives pour cette démonstration. Le profil et les rendez-vous ne sont pas ajoutés à la question."
        )

        question = st.text_area(
            "Votre question générale",
            max_chars=2000,
            key="assistant_question",
            on_change=effacer_apercu_assistant,
        )
        preparer = st.button(
            "Préparer un aperçu local",
            key="assistant_preparer",
            on_click=effacer_apercu_assistant,
        )

        if preparer:
            if not question.strip():
                st.warning("Saisissez une question pour préparer l’aperçu.")
                return

            if reperer_declaration_urgence(question):
                st.warning(MESSAGE_URGENCE)
                return

            try:
                corpus = charger_corpus(CHEMIN_CORPUS)
                resultats = rechercher_corpus(question, corpus)
                messages = preparer_messages(
                    question,
                    resultats,
                    mode="medical",
                )
            except ValueError:
                st.error("L’aperçu documentaire ne peut pas être préparé.")
                return

            if not messages:
                st.info(
                    "Aucun contexte documentaire ne peut être préparé pour cette question."
                )
                return

            st.session_state["assistant_apercu"] = {
                "question": question.strip(),
                "messages": messages,
                "corpus": corpus,
                "consignes_classification": CONSIGNES_CLASSIFICATION,
                "modele": MODELE,
            }

        apercu = st.session_state.get("assistant_apercu")

        if apercu is None:
            return

        if apercu["question"] != question.strip():
            effacer_apercu_assistant()
            return

        st.caption(
            "Documents proposés par la recherche locale. Leur présence ne garantit pas qu’ils répondent à la question. "
            "Cet aperçu ne constitue pas une réponse médicale."
        )
        st.json(list(apercu["messages"]))

        with st.expander("Consignes de classification"):
            st.code(
                apercu["consignes_classification"],
                language="text",
            )

        st.write(
            "Le traitement distant prévu utilise Groq. Un premier appel transmet les consignes de classification "
            "et votre question. Si la demande est autorisée, un second appel peut transmettre les consignes documentaires, "
            "votre question et les passages présentés dans l’aperçu."
        )
        st.caption(
            "Le profil et les rendez-vous ne sont pas ajoutés automatiquement. Les informations personnelles que vous "
            "écrivez dans la question feraient partie de l’envoi."
        )
        st.markdown(
            "[Conditions de traitement des données par Groq](https://console.groq.com/docs/your-data)"
        )

        st.caption(f"Modèle : {apercu['modele']}.")

        autorisation = st.checkbox(
            "J’autorise l’envoi de cette question et des passages présentés à Groq, jusqu’à deux appels par clic d’envoi.",
            key="assistant_autorisation",
        )
        envoyer = st.button(
            "Envoyer à Groq",
            key="assistant_envoyer",
            disabled=not autorisation,
        )
        st.caption(
            "Cocher l’autorisation ne déclenche aucun appel. Chaque clic d’envoi autorisé peut déclencher jusqu’à deux appels."
        )

        if envoyer and autorisation:
            st.session_state.pop("assistant_resultat", None)

            try:
                cle = st.secrets["GROQ_API_KEY"]
            except (FileNotFoundError, KeyError):
                st.error("Le service IA n’est pas configuré.")
                return

            if not isinstance(cle, str) or not cle.strip():
                st.error("La configuration du service IA est invalide.")
                return

            try:
                with st.spinner("Traitement en cours…"):
                    resultat = executer_apercu_assistant(
                        apercu,
                        cle_api=cle,
                    )
            except ValueError:
                st.error(
                    "La demande ne peut pas être envoyée. Préparez un nouvel aperçu avant de réessayer."
                )
                return

            st.session_state["assistant_resultat"] = resultat

        resultat = st.session_state.get("assistant_resultat")

        if resultat is None:
            return

        st.caption(f"Statut : {resultat['statut']}")
        st.markdown(resultat["reponse"], unsafe_allow_html=False)

        if resultat["statut"] == "references_controlees":
            st.caption(
                "Information générale issue des documents cités. Elle ne permet pas d’interpréter une situation personnelle "
                "et ne remplace pas une consultation."
            )

        for source in resultat["sources"]:
            st.text(f"[{source['id']}] {source['title']}")
            st.text(source["source"])

            if "source_version" in source:
                st.text(source["source_version"])

            st.text(source["url"])

            if "reuse_notice" in source:
                st.text(source["reuse_notice"])

        if resultat["sources"]:
            st.caption(
                "La présence des références ne prouve pas que chaque affirmation est étayée."
            )

def effacer_apercu_rendez_vous(identifiant):
    cles = {
        f"preparation_rdv_apercu_{identifiant}",
        f"preparation_rdv_resultat_{identifiant}",
        f"preparation_rdv_autorisation_{identifiant}",
    }
    prefixe_relecture = f"preparation_rdv_relecture_{identifiant}_"

    for cle in list(st.session_state):
        if cle in cles or cle.startswith(prefixe_relecture): # type: ignore
            del st.session_state[cle]


def afficher_preparation_rendez_vous(
    fiche,
    *,
    profil=None,
    generer=None,
    controler=None,
    activer_groq=False,
    verifier_fidelite=None,
    activer_fidelite_groq=False,
):
    cle_apercu = f"preparation_rdv_apercu_{fiche.id}"
    apercu = st.session_state.get(cle_apercu)

    simuler_fidelite = not activer_groq and verifier_fidelite is not None

    fidelite_groq = activer_groq and activer_fidelite_groq
    verifier_proposition = simuler_fidelite or fidelite_groq
    consignes_fidelite = (
        CONSIGNES_FIDELITE_RENDEZ_VOUS if verifier_proposition else None
    )

    if apercu is not None and (
        apercu["fiche"] != fiche
        or "messages_controle" not in apercu
        or apercu.get("modele") != MODELE
        or apercu.get("simuler_fidelite", False) != simuler_fidelite
        or apercu.get("activer_groq") != activer_groq
        or apercu.get("fidelite_groq", False) != fidelite_groq
        or apercu.get("consignes_fidelite") != consignes_fidelite
    ):
        effacer_apercu_rendez_vous(fiche.id)

    st.write("**Préparer mes questions**")
    st.caption(
        "Sélectionnez les champs à utiliser. Cette étape prépare uniquement un aperçu local, sans envoi IA."
    )

    inclure_notes = st.checkbox(
        "Utiliser les notes de cette fiche",
        key=f"preparation_rdv_notes_{fiche.id}",
        disabled=not fiche.notes.strip(),
        on_change=effacer_apercu_rendez_vous,
        args=(fiche.id,),
    )
    inclure_questions = st.checkbox(
        "Utiliser les questions de cette fiche",
        key=f"preparation_rdv_questions_{fiche.id}",
        disabled=not fiche.questions,
        on_change=effacer_apercu_rendez_vous,
        args=(fiche.id,),
    )

    preparer = st.button(
        "Préparer l’aperçu des questions",
        key=f"preparation_rdv_preparer_{fiche.id}",
        on_click=effacer_apercu_rendez_vous,
        args=(fiche.id,),
    )

    if preparer:
        try:
            messages_controle = preparer_controle_rendez_vous(
                fiche,
                inclure_notes=inclure_notes,
                inclure_questions=inclure_questions,
            )

            messages = preparer_messages_rendez_vous(
                fiche,
                inclure_notes=inclure_notes,
                inclure_questions=inclure_questions,
            )
        except PreparationRendezVousUrgente:
            st.warning(MESSAGE_URGENCE)
            return
        except ValueError:
            st.warning(
                "Sélectionnez au moins un champ non vide à préparer."
            )
            return

        st.session_state[cle_apercu] = {
            "fiche": fiche,
            "messages": messages,
            "messages_controle": messages_controle,
            "inclure_notes": inclure_notes,
            "inclure_questions": inclure_questions,
            "modele": MODELE,
            "simuler_fidelite": simuler_fidelite,
            "activer_groq": activer_groq,
            "fidelite_groq": fidelite_groq,
            "consignes_fidelite": consignes_fidelite,
        }

    apercu = st.session_state.get(cle_apercu)

    if apercu is None:
        return None

    st.caption("Premier appel éventuel : contrôle préalable.")
    st.code(
        json.dumps(
            list(apercu["messages_controle"]),
            ensure_ascii=False,
            indent=2,
        ),
        language="json",
    )

    st.caption("Second appel éventuel : reformulation.")
    st.json(list(apercu["messages"]))

    st.caption(f"Fournisseur : Groq. Modèle : {apercu['modele']}.")
    st.write(
        "Un premier appel transmet les consignes de contrôle et les champs sélectionnés. Si le contrôle autorise la préparation, "
        "un second appel transmet les consignes de reformulation et ces mêmes champs."
    )
    st.caption(
        "Les notes et questions sélectionnées peuvent contenir des données personnelles. Les autres champs de la fiche et "
        "le reste du profil ne sont pas ajoutés."
    )
    st.markdown(
        "[Conditions de traitement des données par Groq](https://console.groq.com/docs/your-data)"
    )

    libelle_autorisation = (
        "J’autorise ces envois à Groq, jusqu’à deux appels par clic de proposition."
    )

    if simuler_fidelite:
        st.caption(
            "Simulation sans envoi distant. Si une proposition valide est produite, le troisième contrôle reçoit les champs sélectionnés "
            "et les questions générées. Ces questions ne sont pas encore disponibles dans l’aperçu."
        )
        st.code(CONSIGNES_FIDELITE_RENDEZ_VOUS, language="text")
        libelle_autorisation = "J’autorise la simulation des trois étapes."

    if fidelite_groq:
        st.caption(
            "Si la reformulation produit une proposition valide, un troisième appel transmet à Groq les champs sélectionnés "
            "et les questions générées pour vérifier leur fidélité. Ces questions n’existent pas encore au moment de l’aperçu."
        )
        st.code(apercu["consignes_fidelite"], language="text")
        libelle_autorisation = (
            "J’autorise ces envois à Groq, jusqu’à trois appels par clic de proposition."
        )

    autorisation = st.checkbox(
        libelle_autorisation,
        key=f"preparation_rdv_autorisation_{fiche.id}",
    )

    proposition_disponible = activer_groq or (
        generer is not None and controler is not None
    )

    proposer = st.button(
        "Proposer des questions",
        key=f"preparation_rdv_proposer_{fiche.id}",
        disabled=not proposition_disponible or not autorisation,
    )

    if not proposition_disponible:
        st.caption(
            "La proposition automatique n’est pas disponible pour le moment. Vous pouvez continuer à préparer la fiche manuellement."
        )
        return None

    cle_resultat = f"preparation_rdv_resultat_{fiche.id}"

    if proposer and autorisation:
        st.session_state.pop(cle_resultat, None)

        prefixe = f"preparation_rdv_relecture_{fiche.id}_"
        for cle in list(st.session_state):
            if cle.startswith(prefixe): # type: ignore
                del st.session_state[cle]

        if activer_groq:
            try:
                cle = st.secrets["GROQ_API_KEY"]
            except (FileNotFoundError, KeyError):
                st.error("Le service de préparation IA n’est pas configuré.")
                return None

            if not isinstance(cle, str) or not cle.strip():
                st.error("La configuration du service IA est invalide.")
                return None

            appel = creer_appel_groq_rendez_vous(
                cle_api=cle,
                modele=apercu["modele"],
            )
            controler = appel
            generer = appel
            if fidelite_groq:
                verifier_fidelite = appel

        def controler_apercu_verifie(messages):
            if messages != apercu["messages_controle"]:
                raise ValueError("L’aperçu doit être préparé à nouveau.")
            return controler(messages) # type: ignore

        def generer_apercu_verifie(messages):
            if messages != apercu["messages"]:
                raise ValueError("L’aperçu doit être préparé à nouveau.")
            return generer(messages) # type: ignore

        try:
            options = {
                "controler": controler_apercu_verifie,
                "generer": generer_apercu_verifie,
                "inclure_notes": apercu["inclure_notes"],
                "inclure_questions": apercu["inclure_questions"],
            }

            if verifier_proposition:
                resultat = controler_proposer_et_verifier_questions(
                    apercu["fiche"],
                    verifier_fidelite=verifier_fidelite, # type: ignore
                    **options,
                )
            else:
                resultat = controler_et_proposer_questions(
                    apercu["fiche"],
                    **options,
                )
        except ValueError:
            st.error("Préparez un nouvel aperçu avant de réessayer.")
            return None

        st.session_state[cle_resultat] = resultat

    resultat = st.session_state.get(cle_resultat)

    if resultat is None:
        return None

    st.caption(f"Statut : {resultat['statut']}")

    if resultat["statut"] in ("urgence_locale", "urgence_detectee"):
        st.warning(resultat["message"])
        return None

    st.info(resultat["message"])

    if (
        resultat["statut"] == "proposition_disponible"
        and profil is not None
    ):
        return afficher_relecture_rendez_vous(
            profil,
            apercu["fiche"],
            resultat["questions"],
            contenu_selectionne=json.loads(
                apercu["messages"][1]["content"]
            )["contenu_selectionne"],
        )

    return None

def retirer_confirmation_rendez_vous(cle):
    st.session_state[cle] = False


def afficher_relecture_rendez_vous(
    profil,
    fiche_reference,
    questions_proposees,
    *,
    contenu_selectionne=None,
):
    """Retourne un nouveau profil après ajout explicitement confirmé."""
    base = f"preparation_rdv_relecture_{fiche_reference.id}"
    cle_texte = f"{base}_texte"
    cle_confirmation = f"{base}_confirmation"
    cle_reference = f"{base}_reference"

    reference = (fiche_reference, questions_proposees)

    if st.session_state.get(cle_reference) != reference:
        st.session_state[cle_reference] = reference
        st.session_state[cle_texte] = "\n".join(questions_proposees)
        st.session_state[cle_confirmation] = False

    st.write("**Relire la proposition**")
    if contenu_selectionne:
        st.caption("Texte sélectionné pour cette proposition")

        if "notes" in contenu_selectionne:
            st.write("**Notes sélectionnées**")
            st.text(contenu_selectionne["notes"])

        if "questions" in contenu_selectionne:
            st.write("**Questions sélectionnées**")
            for question in contenu_selectionne["questions"]:
                st.text(question)

        st.caption(
            "Comparez les questions proposées à ce texte. Modifiez ou retirez tout détail que vous ne souhaitez pas aborder."
        )
    st.caption(
        "Modifiez ou retirez les questions proposées avant de confirmer. L’ajout conserve vos notes et vos questions déjà enregistrées."
    )

    texte = st.text_area(
        "Questions proposées, une par ligne",
        key=cle_texte,
        max_chars=15030,
        on_change=retirer_confirmation_rendez_vous,
        args=(cle_confirmation,),
    )
    confirmation = st.checkbox(
        "J’ai relu ces questions et je souhaite les ajouter à ma fiche.",
        key=cle_confirmation,
    )
    ajouter = st.button(
        "Ajouter les questions relues",
        key=f"{base}_ajouter",
        disabled=not confirmation,
    )

    if not ajouter or not confirmation:
        return None

    questions = tuple(
        ligne.strip()
        for ligne in texte.splitlines()
        if ligne.strip()
    )

    if not questions:
        st.warning("Conservez au moins une question à ajouter.")
        return None

    try:
        return enregistrer_questions_relues(
            profil,
            fiche_reference,
            questions,
            modifie_le=datetime.now(timezone.utc),
            confirmer=True,
        )
    except ValueError as erreur:
        st.error(str(erreur))
        return None