from pathlib import Path

from corpus_documentaire import THEMES_CORPUS, charger_corpus
from recherche_documentaire import rechercher_corpus


CHEMIN_CORPUS = Path(__file__).resolve().parent / "donnees" / "corpus_fictif.json"


def main() -> None:
    print("Démonstration sur des textes fictifs, sans information médicale.")
    try:
        corpus = charger_corpus(CHEMIN_CORPUS)
    except ValueError as erreur:
        print(f"Chargement impossible : {erreur}")
        return

    while True:
        try:
            question = input("\nVotre recherche, ou /quitter : ").strip()
            if question == "/quitter":
                print("Fin de la démonstration.")
                return
            if not question:
                print("Saisissez une question non vide.")
                continue

            print("Thèmes :", ", ".join(sorted(THEMES_CORPUS)))
            theme = input("Thème, ou Entrée pour tous : ").strip() or None
            saisie_limite = input("Nombre de résultats, Entrée pour 3 : ").strip()
            try:
                limite = int(saisie_limite) if saisie_limite else 3
            except ValueError:
                print("Le nombre de résultats doit être un entier.")
                continue

            try:
                resultats = rechercher_corpus(question, corpus, limite, theme=theme)
            except ValueError as erreur:
                print(f"Recherche impossible : {erreur}")
                continue

            if not resultats:
                print("Aucun passage correspondant dans ce périmètre.")
                continue

            for rang, resultat in enumerate(resultats, start=1):
                passage = resultat["passage"]
                print(f"\n{rang}. {passage['title']}")
                print(f"Identifiant : {passage['id']}")
                print(f"Score lexical : {resultat['score']}")
                if "mots_communs" in resultat:
                    print("Mots communs :", ", ".join(resultat["mots_communs"]))
                print(passage["content"])
                print(f"Source fictive : {passage['url']}")
        except (EOFError, KeyboardInterrupt):
            print("\nFin de la démonstration.")
            return


if __name__ == "__main__":
    main()
