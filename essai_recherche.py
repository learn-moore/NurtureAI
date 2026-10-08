from corpus_documentaire import valider_corpus
from recherche_documentaire import rechercher_corpus


def main() -> None:
    base = {
        "topic": "suivi_grossesse",
        "source": "Source fictive de démonstration",
        "url": "https://example.org/document",
        "country": "FR",
        "publication_date": None,
        "retrieved_at": "2026-10-05",
        "reviewed_at": "2026-10-05",
        "editorial_status": "approved",
        "reuse_status": "approved",
        "usage": "rag",
    }

    corpus = valider_corpus([
        {
            **base,
            "id": "calendrier",
            "title": "Calendrier fictif",
            "content": "Le calendrier présente les rendez-vous du profil.",
        },
        {
            **base,
            "id": "sauvegarde",
            "title": "Sauvegarde fictive",
            "content": "La sauvegarde conserve le profil dans le navigateur.",
        },
        {
            **base,
            "id": "export",
            "title": "Export fictif",
            "content": "Un export JSON permet de télécharger le profil.",
        },
    ])

    print("Démonstration sur des textes fictifs, sans information médicale.")
    question = input("Votre recherche : ")

    resultats = rechercher_corpus(question, corpus)

    if not resultats:
        print("Aucun passage correspondant.")
        return

    for rang, resultat in enumerate(resultats, start=1):
        passage = resultat["passage"]

        print(f"\n{rang}. {passage['title']}")
        print(f"Identifiant : {passage['id']}")
        print(f"Score lexical : {resultat['score']}")
        print(passage["content"])


if __name__ == "__main__":
    main()