import argparse
from pathlib import Path

from corpus_documentaire import charger_corpus
from recherche_documentaire import rechercher_corpus
from rapport_recherche import construire_rapport_recherche

def main() -> None:
    arguments = argparse.ArgumentParser(
        description="Exporter une recherche sur le corpus fictif."
    )
    arguments.add_argument("destination", type=Path, help="Chemin du rapport texte.")
    options = arguments.parse_args()

    racine = Path(__file__).resolve().parent
    try:
        corpus = charger_corpus(racine / "donnees" / "corpus_fictif.json")
        resultats = rechercher_corpus("profil", corpus)
        rapport = construire_rapport_recherche("profil", resultats)
        options.destination.write_text(rapport, encoding="utf-8")
    except (ValueError, OSError) as erreur:
        arguments.exit(1, f"Export impossible : {erreur}\n")

    print(f"Rapport enregistré : {options.destination}")


if __name__ == "__main__":
    main()
