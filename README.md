# NurtureAI

Prototype pédagogique de suivi du projet de conception et de la grossesse, développé avec Python et Streamlit.

L’application fournit des informations générales et des estimations. Elle ne fournit ni diagnostic ni recommandation médicale personnalisée.

## État actuel

Le prototype permet de :

* Créer un parcours conception ou grossesse, le terminer et démarrer un autre parcours.
* Conserver l’historique et les repères des parcours terminés.
* Renseigner les repères du cycle et calculer le jour du cycle ainsi que les prochaines règles estimées.
* Saisir une référence de grossesse : dernières règles ou DPA connue.
* Calculer les semaines d’aménorrhée depuis les dernières règles.
* Enregistrer les repères dans le parcours actif et les reprendre dans les formulaires.
* Exporter et importer le profil au format JSON, avec validation et confirmation du remplacement.
* Sauvegarder manuellement le profil dans le navigateur et le restaurer après confirmation.
* Effacer uniquement les données de session, ou supprimer la sauvegarde locale et la session après confirmation.
* Restaurer automatiquement une sauvegarde valide au démarrage et sauvegarder automatiquement les modifications du profil lorsque le stockage est disponible et sans conflit.

La reprise au démarrage et la sauvegarde des modifications du profil sont automatiques. Les saisies temporaires des formulaires restent exclues.

Une erreur ou un conflit suspend les tentatives automatiques. Un remplacement par un profil d’identifiant différent nécessite un enregistrement manuel.

Les écritures et suppressions utilisent un verrou partagé entre les onglets de l’application et vérifient que la sauvegarde n’a pas changé depuis sa lecture. Si ce verrou est indisponible, aucune modification du stockage n’est effectuée ; l’export JSON reste disponible.

Le calcul depuis une DPA, les SG, le trimestre, le calendrier, la timeline, les rendez-vous et l’assistant IA ne sont pas encore implémentés.

Des tests automatisés vérifient les calculs, les modèles, les imports et les interactions Python. Le stockage du navigateur est simulé dans ces tests ; son fonctionnement réel nécessite une vérification dans le navigateur.

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

Le profil contient les parcours et leurs repères enregistrés. Les saisies temporaires des formulaires ne sont pas incluses dans les sauvegardes et les exports.

Avant de sauvegarder, valider les repères du formulaire puis les enregistrer dans le parcours actif.

### Sauvegarde dans le navigateur

Au démarrage, l’application attend la lecture du navigateur. Une sauvegarde valide est restaurée automatiquement avec son parcours actif. En cas de lecture impossible ou de données invalides, une session temporaire peut être ouverte sans supprimer la sauvegarde.

La création d’un parcours et les modifications enregistrées dans le profil déclenchent une sauvegarde automatique lorsque les conditions le permettent. Les saisies temporaires des formulaires ne sont pas sauvegardées.

Dans « Mes données », la section « Sauvegarde dans ce navigateur » indique si le profil correspond à la dernière sauvegarde confirmée. Attendre cette confirmation avant de fermer ou de recharger la page.

Le bouton « Enregistrer le profil dans ce navigateur » reste disponible pour un enregistrement manuel. La restauration manuelle reste également accessible après confirmation du remplacement du profil de session.

Si un autre onglet a modifié la sauvegarde depuis sa lecture, l’opération est refusée. Exporter les modifications de session à conserver avant de recharger la page.

Les données sont propres au navigateur, à son profil utilisateur et à l’adresse du site. Elles ne sont pas synchronisées entre appareils. La suppression des données du navigateur peut les faire disparaître.

### Export et import JSON

L’export permet de télécharger une copie du profil dans un fichier JSON.

Pour restaurer un fichier :

1. Sélectionner un export dans « Importer mes données ».
2. Vérifier l’aperçu.
3. Confirmer le remplacement.
4. Cliquer sur « Remplacer mon profil ».

L’import et la restauration locale remplacent entièrement le profil de session et réinitialisent les saisies temporaires. Ils ne fusionnent pas les historiques. Un fichier importé invalide est refusé sans remplacer le profil actuel.

Après un import provenant d’un profil d’identifiant différent, un enregistrement manuel est nécessaire pour remplacer la sauvegarde locale. Vérifier l’indicateur de sauvegarde avant de quitter.

### Effacement

« Effacer toutes mes données de session » réinitialise uniquement la session et conserve la sauvegarde locale.

« Effacer la sauvegarde et la session » demande une confirmation, supprime la sauvegarde du navigateur, puis réinitialise la session après réception du signal de réussite. Si la suppression locale échoue, la session est conservée.

Les fichiers JSON déjà téléchargés ne sont pas supprimés.

### Confidentialité

La sauvegarde locale et les exports ne sont pas chiffrés par NurtureAI. Une personne ayant accès au même navigateur peut accéder au suivi.

Le stockage local ne signifie pas que tous les traitements restent sur l’appareil : Streamlit traite les données nécessaires dans la session du serveur.

Conserver les exports dans un emplacement privé et ne pas les ajouter au dépôt Git. Utiliser des données fictives pour les démonstrations du projet.

## Organisation

* `app.py` : interface Streamlit.
* `calculs.py` : calculs indépendants de l’interface.
* `tests/` : tests des calculs et des interactions avec l'interface.
* `requirements.txt` : dépendances Python.
* `etat_session.py` : initialisation et effacement des données de session.
* `modeles.py` : profils, parcours, repères et règles de cohérence.
* `persistance.py` : export JSON et validation des données importées.
* `stockage_navigateur.py` : composant de lecture, sauvegarde et effacement dans le navigateur.

## Limites

Les dates calculées sont indicatives. Elles ne confirment ni une ovulation ni une grossesse et ne constituent pas une méthode contraceptive.

Ce projet est en cours de développement.