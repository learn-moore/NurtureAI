import json

from dataclasses import replace

from modeles import Appointment
from intentions import MESSAGE_URGENCE, reperer_declaration_urgence


LIBELLES_TYPES = {
    "preconception": "Consultation préconceptionnelle",
    "follow_up": "Consultation de suivi",
    "ultrasound": "Échographie",
    "birth_preparation": "Préparation à la naissance",
    "other": "Autre",
}

LIBELLES_THEMES = {
    "nutrition": "Alimentation",
    "physical_activity": "Activité physique",
    "symptoms": "Symptômes",
    "medications": "Médicaments",
    "tests": "Examens",
    "work": "Travail",
    "travel": "Voyage",
    "childbirth": "Accouchement",
    "other": "Autre",
}


def exporter_fiche_texte(fiche: Appointment) -> str:
    date_affichee = (
        fiche.date.strftime("%d/%m/%Y")
        if fiche.date is not None
        else "Date à définir"
    )

    themes = ", ".join(
        LIBELLES_THEMES[theme] for theme in fiche.topics
    )

    questions = "\n".join(
        f"{numero}. {question}"
        for numero, question in enumerate(fiche.questions, start=1)
    )

    return "\n".join([
        "NurtureAI : préparation de rendez-vous",
        f"Type : {LIBELLES_TYPES[fiche.appointment_type]}",
        f"Date : {date_affichee}",
        f"Thèmes : {themes or 'Aucun thème sélectionné.'}",
        "",
        "Notes",
        fiche.notes or "Aucune note renseignée.",
        "",
        "Questions",
        questions or "Aucune question renseignée.",
        "",
        "Fiche personnelle de préparation, ne remplaçant pas un avis médical.",
        "",
    ])

class PreparationRendezVousUrgente(ValueError):
    """Interrompt la préparation lorsqu’un signal local est reconnu."""


def preparer_contenu_ia(
    fiche: Appointment,
    *,
    inclure_notes: bool = False,
    inclure_questions: bool = False,
) -> dict:
    """Prépare uniquement les champs explicitement sélectionnés."""
    if not isinstance(fiche, Appointment):
        raise ValueError("Une fiche de rendez-vous est nécessaire.")

    if (
        type(inclure_notes) is not bool
        or type(inclure_questions) is not bool
    ):
        raise ValueError("Les choix de transmission doivent être booléens.")

    contenu = {}

    if inclure_notes and fiche.notes.strip():
        contenu["notes"] = fiche.notes

    if inclure_questions and fiche.questions:
        contenu["questions"] = list(fiche.questions)

    if not contenu:
        raise ValueError(
            "Sélectionnez au moins un champ non vide à préparer."
        )

    textes_selectionnes = []

    if "notes" in contenu:
        textes_selectionnes.append(contenu["notes"])

    if "questions" in contenu:
        textes_selectionnes.extend(contenu["questions"])

    if any(
        reperer_declaration_urgence(texte)
        for texte in textes_selectionnes
    ):
        raise PreparationRendezVousUrgente(MESSAGE_URGENCE)

    return contenu

def lire_proposition_questions(sortie: str) -> tuple[str, ...]:
    """Valide une proposition sans modifier de fiche."""
    if not isinstance(sortie, str) or not sortie.strip():
        raise ValueError("La proposition doit être un texte JSON non vide.")

    def refuser_cles_dupliquees(paires):
        objet = {}

        for cle, valeur in paires:
            if cle in objet:
                raise ValueError("Clé JSON dupliquée.")
            objet[cle] = valeur

        return objet

    try:
        proposition = json.loads(
            sortie,
            object_pairs_hook=refuser_cles_dupliquees,
        )
    except (ValueError, RecursionError):
        raise ValueError("Le JSON de la proposition est invalide.") from None

    if (
        not isinstance(proposition, dict)
        or set(proposition) != {"questions"}
    ):
        raise ValueError(
            "La proposition doit contenir uniquement la clé questions."
        )

    questions = proposition["questions"]

    if not isinstance(questions, list) or len(questions) > 30:
        raise ValueError(
            "La proposition doit contenir une liste de 30 questions maximum."
        )

    for question in questions:
        if (
            not isinstance(question, str)
            or not question.strip()
            or len(question) > 500
        ):
            raise ValueError(
                "Chaque question doit être un texte non vide de 500 caractères maximum."
            )

    return tuple(question.strip() for question in questions)

def fusionner_questions_rendez_vous(
    fiche: Appointment,
    proposition: tuple[str, ...],
) -> tuple[str, ...]:
    """Prépare les questions fusionnées sans enregistrer la fiche."""
    if not isinstance(fiche, Appointment):
        raise ValueError("Une fiche de rendez-vous est nécessaire.")

    # Réutiliser la validation du modèle pour les questions proposées.
    fiche_proposee = replace(
        fiche,
        questions=proposition,
    )

    questions = tuple(dict.fromkeys(
        (*fiche.questions, *fiche_proposee.questions)
    ))

    # Vérifier aussi les limites après fusion avec les questions existantes.
    fiche_fusionnee = replace(
        fiche,
        questions=questions,
    )

    return fiche_fusionnee.questions