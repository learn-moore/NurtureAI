# NurtureAI

Prototype pédagogique de suivi du projet de conception et de la grossesse, développé avec Python et Streamlit.

L’application fournit des informations générales et des estimations. Elle ne fournit ni diagnostic ni recommandation médicale personnalisée.

## État actuel

Le prototype permet de :

* Choisir entre les parcours conception et grossesse.
* Renseigner les dernières règles, la durée moyenne du cycle, la durée des règles et la régularité du cycle.
* Calculer le jour du cycle et la date estimée des prochaines règles.
* Saisir une référence de grossesse : dernières règles ou DPA connue.
* Calculer les semaines d’aménorrhée depuis les dernières règles.
* Conserver les dernières saisies validées pendant la session et les retrouver après un changement de parcours.
* Effacer les repères conception ou grossesse après confirmation, sans supprimer ceux de l’autre suivi.

Des tests automatisés vérifient les calculs, les validations et plusieurs interactions avec l’interface.

Le calcul depuis une DPA, la sauvegarde durable dans le navigateur, l’historique des parcours et l’assistant IA restent à développer.

Un rechargement de la page peut entraîner la perte des données de session.

## Installation sur Linux / macOS

Prérequis : Python 3.12.

Depuis la racine du projet :

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Lancer l’application

Avec l’environnement virtuel activé :

```bash
python -m streamlit run app.py
```

Ouvrir l’adresse locale indiquée dans le terminal.

Pour arrêter l’application : Ctrl + C.

## Exécuter les tests

Depuis la racine du projet, avec l’environnement activé :

```bash
python -m pytest
```

## Sauvegarder et restaurer ses données

Les données restent en mémoire pendant la session.
Un rechargement de la page ou un redémarrage de l’application
peut les faire perdre.

Pour conserver son suivi :

1. Valider les repères dans le formulaire.
2. Les enregistrer dans le parcours actif.
3. Cliquer sur « Exporter mes données ».
4. Conserver le fichier JSON dans un emplacement privé.

L’export contient le profil, ses parcours et leurs repères enregistrés.
Les saisies temporaires des formulaires ne sont pas incluses.

Pour restaurer un export :

1. Sélectionner le fichier JSON dans la section d’import.
2. Vérifier l’aperçu.
3. Confirmer le remplacement du profil.
4. Cliquer sur « Remplacer mon profil ».

L’import remplace entièrement le profil actuel et réinitialise
les saisies temporaires. Il ne fusionne pas les historiques.

Les fichiers invalides sont refusés sans remplacer le profil actuel.

Le fichier exporté n’est pas chiffré et peut contenir des informations
sensibles. Il ne doit pas être ajouté au dépôt Git.

La sauvegarde automatique dans le navigateur n’est pas encore implémentée.

## Organisation

* `app.py` : interface Streamlit.
* `calculs.py` : calculs indépendants de l’interface.
* `tests/` : tests des calculs et des interactions avec l'interface.
* `requirements.txt` : dépendances Python.
* `etat_session.py` : initialisation et effacement des données de session.
* `modeles.py` : profils, parcours, repères et règles de cohérence.
* `persistance.py` : export JSON et validation des données importées.

## Limites

Les dates calculées sont indicatives. Elles ne confirment ni une ovulation ni une grossesse et ne constituent pas une méthode contraceptive.

Ce projet est en cours de développement.