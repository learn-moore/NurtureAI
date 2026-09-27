from datetime import date, timedelta

def estimer_prochaines_regles(
        dernieres_regles: date, duree_cycle: int,
) -> date:
    if duree_cycle <= 0:
        raise ValueError(
            "La durée du cycle doit être strictement positive."
        )
    return dernieres_regles + timedelta(days=duree_cycle)

def calculer_jour_cycle(
        dernieres_regles: date,
        date_reference: date,
) -> int:
    if dernieres_regles > date_reference:
        raise ValueError(
            "La date des dernières règles ne peut pas être postérieur à la date de référence."
        )
    return (date_reference - dernieres_regles).days + 1

def valider_durees_cycle(
    duree_cycle: int,
    duree_regles: int,
) -> None:
    if duree_cycle <= 0:
        raise ValueError("La durée du cycle doit être strictement positive.")

    if duree_regles <= 0:
        raise ValueError("La durée des règles doit être strictement positive.")

    if duree_regles > duree_cycle:
        raise ValueError(
            "La durée des règles ne peut pas dépasser la durée du cycle."
        )

def calculer_age_depuis_dernieres_regles(
    dernieres_regles: date,
    date_reference: date,
) -> tuple[int, int]:
    if dernieres_regles > date_reference:
        raise ValueError(
            "La date des dernières règles ne peut pas être postérieure à la date de référence."
        )

    jours_ecoules = (date_reference - dernieres_regles).days

    return divmod(jours_ecoules, 7)

def estimer_semaines_grossesse(dernieres_regles: date, date_reference: date,) -> tuple[int, int] | None:
    """Estime les SG conventionnelles depuis les dernières règles."""
    semaines_sa, jours_sa = calculer_age_depuis_dernieres_regles(
        dernieres_regles,
        date_reference,
    )

    return convertir_sa_en_sg(semaines_sa, jours_sa)

def calculer_age_depuis_dpa(
    dpa: date,
    date_reference: date,
    *,
    terme_reference_jours: int,
) -> tuple[int, int]:
    """Calcule les SA selon une durée de référence explicite."""
    if (
        type(terme_reference_jours) is not int
        or terme_reference_jours <= 0
    ):
        raise ValueError("La durée de référence doit être un entier strictement positif.")

    jours_sa = terme_reference_jours + (date_reference - dpa).days

    if jours_sa < 0:
        raise ValueError("La DPA est trop éloignée pour la convention de calcul choisie.")

    return divmod(jours_sa, 7)

def convertir_sa_en_sg(semaines_sa: int,jours_sa: int,) -> tuple[int, int] | None:
    """Convertit les SA en SG conventionnelles, avec 14 jours d’écart."""
    if (
        type(semaines_sa) is not int
        or type(jours_sa) is not int
        or semaines_sa < 0
        or not 0 <= jours_sa <= 6
    ):
        raise ValueError("L’âge en SA doit avoir des semaines positives ou nulles et de 0 à 6 jours.")

    jours_sg = semaines_sa * 7 + jours_sa - 14

    if jours_sg < 0:
        return None

    return divmod(jours_sg, 7)

def determiner_trimestre(
    jours_sa: int,
    *,
    debut_deuxieme: int,
    debut_troisieme: int,
) -> int:
    """Classe un âge en jours SA selon deux seuils explicites."""
    valeurs = (jours_sa, debut_deuxieme, debut_troisieme)

    if any(type(valeur) is not int for valeur in valeurs):
        raise ValueError("Les durées doivent être des entiers.")

    if jours_sa < 0:
        raise ValueError("L’âge en jours SA ne peut pas être négatif.")

    if not 0 < debut_deuxieme < debut_troisieme:
        raise ValueError("Les seuils doivent être positifs et croissants.")

    if jours_sa < debut_deuxieme:
        return 1

    if jours_sa < debut_troisieme:
        return 2

    return 3

def calculer_progression_grossesse(
    jours_sa: int,
    *,
    terme_reference_jours: int,
) -> float:
    """Renvoie une proportion chronologique comprise entre 0 et 1."""
    if type(jours_sa) is not int or type(terme_reference_jours) is not int:
        raise ValueError("Les durées doivent être des entiers.")

    if jours_sa < 0:
        raise ValueError("L’âge en jours SA ne peut pas être négatif.")

    if terme_reference_jours <= 0:
        raise ValueError("La durée de référence doit être strictement positive.")

    return min(jours_sa / terme_reference_jours, 1.0)

