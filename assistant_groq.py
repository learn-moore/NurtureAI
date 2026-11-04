from functools import partial

from assistant_documentaire import traiter_demande
from classification_intentions import classer_demande_experimentale
from generation_groq import (
    GenerationGroqInterrompue,
    ReponseGroqVide,
    RequeteGroqRefusee,
    generer_reponse_groq,
)


def traiter_demande_groq(
    question: str,
    corpus: tuple[dict, ...],
    *,
    cle_api: str,
    modele: str,
    urgence_signalee: bool = False,
    mode: str = "laboratoire",
) -> dict:
    """Relie la chaîne documentaire aux adaptateurs distants."""
    appel_distant = partial(
        generer_reponse_groq,
        cle_api=cle_api,
        modele=modele,
    )

    etape = "classification"

    def generer(messages):
        nonlocal etape
        etape = "generation_documentaire"
        return appel_distant(messages)

    classer = partial(
        classer_demande_experimentale,
        generer=appel_distant,
    )

    try:
        return traiter_demande(
            question,
            corpus,
            classer=classer,
            generer=generer,
            urgence_signalee=urgence_signalee,
            mode=mode,
        )
    except RequeteGroqRefusee:
        return {
            "statut": "requete_refusee",
            "reponse": (
                "Le fournisseur a refusé la requête. Vérifiez la configuration de l’essai."
            ),
            "sources": (),
        }
    except GenerationGroqInterrompue as erreur:
        return {
            "statut": "generation_interrompue",
            "etape": etape,
            "motif_interruption": erreur.raison,
            "reponse": (
                "Le traitement distant ne s’est pas terminé normalement. Aucun texte partiel n’est affiché."
            ),
            "sources": (),
        }
    except ReponseGroqVide:
        return {
            "statut": "reponse_vide",
            "reponse": (
                "Le fournisseur n’a retourné aucun texte exploitable."
            ),
            "sources": (),
        }