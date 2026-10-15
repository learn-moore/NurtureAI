from enum import StrEnum


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


