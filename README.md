# NurtureAI

Prototype pédagogique de suivi du projet de conception et de la grossesse, développé avec Python et Streamlit.

L’application fournit des informations générales et des estimations. Elle ne fournit ni diagnostic ni recommandation médicale personnalisée.

## État actuel

Le prototype permet de :

## État actuel

Le prototype permet de :

* Choisir entre les parcours conception et grossesse.
* Renseigner les dernières règles, la durée moyenne du cycle, la durée des règles et la régularité du cycle.
* Calculer le jour du cycle et la date estimée des prochaines règles.
* Saisir une référence de grossesse : dernières règles ou DPA connue.
* Calculer les semaines d’aménorrhée depuis les dernières règles.
* Conserver les dernières saisies validées pendant la session et les retrouver après un changement de parcours.

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

## Organisation

* `app.py` : interface Streamlit.
* `calculs.py` : calculs indépendants de l’interface.
* `tests/` : tests des calculs et des interactions avec l'interface.
* `requirements.txt` : dépendances Python.

## Limites

Les dates calculées sont indicatives. Elles ne confirment ni une ovulation ni une grossesse et ne constituent pas une méthode contraceptive.

Ce projet est en cours de développement.