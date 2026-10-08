from pathlib import Path

from corpus_documentaire import charger_corpus
from recherche_documentaire import rechercher_corpus
from rapport_recherche import construire_rapport_recherche

racine = Path(__file__).resolve().parent
corpus = charger_corpus(racine / "donnees" / "corpus_fictif.json")
resultats = rechercher_corpus("profil", corpus)
rapport = construire_rapport_recherche("profil", resultats)

destination = Path.home() / "Portfolio" / "NurtureAI_Atelier_Hors_Ligne" / "rapport_profil.txt"
destination.write_text(rapport, encoding="utf-8")
print(f"Rapport enregistré : {destination}")
