from groq import APIConnectionError, APIStatusError, Groq

from assistant_documentaire import GenerationIndisponible


class RequeteGroqRefusee(ValueError):
    """Signale un refus de la requête par le fournisseur."""


class GenerationGroqInterrompue(ValueError):
    """Signale une génération qui ne s’est pas terminée normalement."""

    def __init__(self, message: str, *, raison: str = "autre"):
        super().__init__(message)
        self.raison = (
            raison
            if raison in {"length", "tool_calls", "content_filter"}
            else "autre"
        )


class ReponseGroqVide(ValueError):
    """Signale une absence de réponse textuelle exploitable."""

def generer_reponse_groq(
    messages: tuple[dict[str, str], ...],
    *,
    cle_api: str,
    modele: str,
) -> str:
    """Appelle Groq et retourne une réponse textuelle complète."""
    if not messages:
        raise ValueError("La génération nécessite des messages.")

    if not isinstance(cle_api, str) or not cle_api.strip():
        raise ValueError("La clé API Groq est absente.")

    if not isinstance(modele, str) or not modele.strip():
        raise ValueError("Le modèle Groq doit être renseigné.")

    try:
        with Groq(
            api_key=cle_api,
            timeout=20.0,
            max_retries=0,
        ) as client:
            resultat = client.chat.completions.create(
                model=modele,
                messages=list(messages), # type: ignore
                max_completion_tokens=1024,
                stream=False,
            ) # type: ignore
    except APIConnectionError:
        raise GenerationIndisponible(
            "Connexion à Groq indisponible."
        ) from None
    except APIStatusError as erreur:
        if erreur.status_code in (408, 429) or erreur.status_code >= 500:
            raise GenerationIndisponible(
                "Service Groq temporairement indisponible."
            ) from None

        raise RequeteGroqRefusee(
            "La requête Groq a été refusée. Vérifier la configuration de la clé et du modèle."
        ) from None

    if not resultat.choices:
        raise ReponseGroqVide("Groq n’a retourné aucune réponse.")

    choix = resultat.choices[0]

    if choix.finish_reason != "stop":
        raise GenerationGroqInterrompue(
            "La génération ne s’est pas terminée normalement.",
            raison=choix.finish_reason,
        )

    texte = choix.message.content

    if not isinstance(texte, str) or not texte.strip():
        raise ReponseGroqVide("Groq n’a retourné aucun texte exploitable.")

    return texte