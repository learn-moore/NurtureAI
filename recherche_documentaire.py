import re
import unicodedata

from corpus_documentaire import THEMES_CORPUS, valider_corpus

MOTS_IGNORES = frozenset({
    "a", "au", "aux",
    "d", "de", "des", "du",
    "l", "la", "le", "les",
    "un", "une",
    "et",
})

def extraire_mots(texte: str) -> set[str]:
    if not isinstance(texte, str):
        raise ValueError("Le texte doit être une chaîne de caractères.")

    texte = texte.casefold()
    texte = texte.replace("œ", "oe").replace("æ", "ae")

    caracteres = unicodedata.normalize("NFD", texte)
    sans_accents = "".join(
        caractere
        for caractere in caracteres
        if not unicodedata.combining(caractere)
    )

    return set(re.findall(r"[a-z0-9]+", sans_accents))

def extraire_mots_recherche(texte: str) -> set[str]:
    return extraire_mots(texte) - MOTS_IGNORES

def calculer_score_lexical(question: str, passage: str) -> int:
    mots_question = extraire_mots_recherche(question)
    mots_passage = extraire_mots_recherche(passage)

    mots_communs = mots_question & mots_passage

    return len(mots_communs)

def rechercher_passages(
    question: str,
    passages: tuple[dict, ...],
    limite: int = 3,
) -> tuple[dict, ...]:
    """Classe des passages déjà validés selon leurs mots communs."""
    if type(limite) is not int or limite < 1:
        raise ValueError("La limite doit être un entier strictement positif.")

    mots_question = extraire_mots_recherche(question)

    if not mots_question:
        return ()

    resultats = []

    for passage in passages:
        texte_recherche = (
            f"{passage.get('title', '')}\n{passage['content']}"
        )
        mots_commun = mots_question & extraire_mots_recherche(texte_recherche)
        score = len(mots_commun)

        if score > 0:
            resultats.append({
                "passage": passage,
                "score": score,
                "mots_communs": tuple(sorted(mots_commun)),
            })

    resultats.sort(key=lambda resultat: resultat["score"], reverse=True)

    return tuple(resultats[:limite])

def rechercher_corpus(
    question: str,
    corpus: tuple[dict, ...],
    limite: int = 3,
    *,
    theme: str | None = None,
) -> tuple[dict, ...]:
    """Valide le corpus et recherche parmi les passages autorisés."""
    if theme is not None:
        if not isinstance(theme, str) or theme not in THEMES_CORPUS:
            raise ValueError("Thème de recherche non pris en charge.")

    if not isinstance(corpus, tuple):
        raise ValueError("Le corpus de recherche doit être un tuple.")

    corpus = valider_corpus(list(corpus))

    passages_autorises = tuple(
        passage
        for passage in corpus
        if passage["editorial_status"] == "approved"
        and passage["reuse_status"] == "approved"
        and passage["usage"] == "rag"
        and (theme is None or passage["topic"] == theme)
    )

    return rechercher_passages(
        question,
        passages_autorises,
        limite=limite,
    )

