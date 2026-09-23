# NurtureAI

Prototype pédagogique de suivi du projet de conception et de la grossesse, développé avec Python et Streamlit.

L’application fournit des informations générales et des estimations. Elle ne fournit ni diagnostic ni recommandation médicale personnalisée.

## État actuel

Le prototype permet de :

* Choisir entre les parcours conception et grossesse.
* Saisir la date des dernières règles et la durée moyenne du cycle.
* Calculer une estimation de la date des prochaines règles.

Le parcours grossesse affiche actuellement un message. La persistance des données et l’assistant IA ne sont pas encore implémentés.

## Installation sur macOS

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
* `tests/` : tests automatisés.
* `requirements.txt` : dépendances Python.

## Limites

Les dates calculées sont indicatives. Elles ne confirment ni une ovulation ni une grossesse et ne constituent pas une méthode contraceptive.

Ce projet est en cours de développement.