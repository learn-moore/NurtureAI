import re
import unicodedata

from enum import StrEnum


VERSION_MESSAGE_URGENCE = "urgence-v1"

MESSAGE_URGENCE = (
    "Si vous pensez vivre une urgence médicale, contactez les services d’urgence sans attendre une réponse de l’application. "
    "En France, appelez le 15 ou le 112. Le 114 est accessible notamment par SMS, application ou internet "
    "aux personnes sourdes, sourdaveugles, malentendantes ou aphasiques. Hors de France, contactez les services d’urgence locaux."
)

MESSAGE_SITUATION_PERSONNELLE = (
    "Cette application ne peut pas interpréter votre situation médicale ni décider d’un traitement. Vous pouvez préparer une question "
    "à poser à un professionnel de santé : « Que signifie cette situation pour moi et quelle conduite me conseillez-vous ? »"
)

MESSAGE_HORS_PERIMETRE = (
    "Cet assistant traite des informations générales sur la conception, la grossesse et la préparation de leur suivi. "
    "Votre demande sort de ce périmètre."
)

MESSAGE_DEMANDE_INDETERMINEE = (
    "Votre demande ne permet pas de déterminer le type d’aide attendu. Pouvez-vous préciser le sujet de votre question, "
    "sans ajouter de données personnelles inutiles ?"
)

class ClassificationIndisponible(RuntimeError):
    """Signale une indisponibilité attendue du classifieur."""

class Intention(StrEnum):
    GENERAL_INFORMATION = "GENERAL_INFORMATION"
    PERSONAL_MEDICAL_SITUATION = "PERSONAL_MEDICAL_SITUATION"
    POTENTIAL_EMERGENCY = "POTENTIAL_EMERGENCY"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


def autoriser_generation_documentaire(
    intention: Intention | None,
) -> bool:
    """Autorise la génération uniquement pour une information générale."""
    return intention is Intention.GENERAL_INFORMATION

def convertir_intention(valeur: object) -> Intention | None:
    """Convertit une catégorie reconnue, sinon retourne une intention inconnue."""
    if not isinstance(valeur, str):
        return None

    try:
        return Intention(valeur)
    except ValueError:
        return None


def reperer_declaration_urgence(question: str) -> bool:
    """Repère certaines formulations explicites, sans analyse clinique."""
    texte = unicodedata.normalize("NFD", question.casefold())
    texte = "".join(
        caractere
        for caractere in texte
        if not unicodedata.combining(caractere)
    )
    texte = " ".join(texte.split())

    return re.search(
        r"\b(?:vis|vit|vivre)\s+une\s+urgence\s+medicale\b",
        texte,
    ) is not None

