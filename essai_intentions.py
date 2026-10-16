import json
from pathlib import Path

from evaluation_intentions import evaluer_classifieur
from intentions import Intention


CHEMIN = (
    Path(__file__).resolve().parent
    / "donnees"
    / "evaluation_intentions.json"
)


def toujours_indetermine(question: str) -> Intention | None:
    """Référence de comparaison sans classification ni appel réseau."""
    return None


def main():
    donnees = json.loads(CHEMIN.read_text(encoding="utf-8"))
    evaluations = evaluer_classifieur(
        donnees["cas"],
        classer=toujours_indetermine,
    )

    print("Référence de comparaison : toujours indéterminé")
    print("Aucun appel API.\n")

    for evaluation in evaluations:
        attendu = evaluation["attendu"] or "INDETERMINE"
        obtenu = evaluation["obtenu"] or "INDETERMINE"
        verdict = "CONFORME" if evaluation["conforme"] else "ECART"

        print(
            f"{evaluation['id']} | {verdict} | "
            f"attendu={attendu} | obtenu={obtenu}"
        )

        if evaluation["erreur"]:
            print(f"  Erreur : {evaluation['erreur']}")

    conformes = sum(e["conforme"] for e in evaluations)
    ouvertures_indues = sum(
        e["generation_indument_autorisee"]
        for e in evaluations
    )
    indisponibilites = sum(
        e["erreur"] is not None
        for e in evaluations
    )

    print(f"\nClassements conformes : {conformes}/{len(evaluations)}")
    print(f"Autorisations indues : {ouvertures_indues}")
    print(f"Indisponibilités : {indisponibilites}")


if __name__ == "__main__":
    main()