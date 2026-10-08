def construire_rapport_recherche(question: str, resultats: tuple[dict, ...]) -> str:
    """Produit un rapport texte à partir de résultats déjà contrôlés."""
    lignes = [
        "RAPPORT DE RECHERCHE DOCUMENTAIRE",
        "Démonstration sur corpus fictif. Aucune réponse médicale générée.",
        "",
        f"Question : {question}",
    ]
    if not resultats:
        lignes.extend(["", "Aucun passage correspondant."])
    else:
        for numero, resultat in enumerate(resultats, start=1):
            passage = resultat["passage"]
            lignes.extend([
                "",
                f"[{numero}] {passage['title']}",
                f"Identifiant : {passage['id']}",
                f"Score lexical : {resultat['score']}",
                "Mots communs : " + ", ".join(resultat["mots_communs"]),
                passage["content"],
                f"Source : {passage['source']}",
                f"URL : {passage['url']}",
                f"Consultée le : {passage['retrieved_at']}",
            ])
    return "\n".join(lignes) + "\n"
