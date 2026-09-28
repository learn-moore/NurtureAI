from modeles import Appointment


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