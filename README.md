# NurtureAI

Prototype pédagogique de suivi du projet de conception et de la grossesse, développé avec Python et Streamlit.

L’application fournit des informations générales et des estimations. Elle ne fournit ni diagnostic ni recommandation médicale personnalisée.

## État actuel

Le prototype permet de :

* Créer un parcours conception ou grossesse, le terminer et démarrer un autre parcours.
* Conserver l’historique et les repères des parcours terminés.
* Renseigner les repères du cycle et calculer le jour du cycle ainsi que les prochaines règles estimées.
* Saisir une référence de grossesse : dernières règles ou DPA connue.
* Calculer les semaines d’aménorrhée depuis les dernières règles, ou depuis une DPA lorsque la durée de référence du terme est renseignée.
* Présenter les semaines de grossesse approximatives, le trimestre et les repères de progression lorsque les données nécessaires sont disponibles.
* Créer, modifier et supprimer des fiches de rendez-vous avec date facultative, thèmes, notes et questions.
* Télécharger une fiche de rendez-vous au format texte.
* Consulter un calendrier mensuel des rendez-vous et des repères du parcours, en distinguant les dates déclarées des estimations.
* Consulter trois fiches sourcées consacrées aux échographies de grossesse.
* Consulter une fiche hebdomadaire autour de 9 SA, sélectionnée à partir des repères enregistrés, avec référence documentaire et attribution.
* Identifier la période actuelle ou la prochaine période parmi les fiches disponibles, à partir des repères enregistrés.
* Enregistrer les repères dans le parcours actif et les reprendre dans les formulaires.
* Exporter et importer le profil au format JSON, avec validation et confirmation du remplacement.
* Sauvegarder manuellement le profil dans le navigateur et le restaurer après confirmation.
* Effacer uniquement les données de session, ou supprimer la sauvegarde locale et la session après confirmation.
* Restaurer automatiquement une sauvegarde valide au démarrage et sauvegarder automatiquement les modifications du profil lorsque le stockage est disponible et sans conflit.

La reprise au démarrage et la sauvegarde des modifications du profil sont automatiques. Les saisies temporaires des formulaires restent exclues.

Une erreur ou un conflit suspend les tentatives automatiques. Un remplacement par un profil d’identifiant différent nécessite un enregistrement manuel.

Les écritures et suppressions utilisent un verrou partagé entre les onglets de l’application et vérifient que la sauvegarde n’a pas changé depuis sa lecture. Si ce verrou est indisponible, aucune modification du stockage n’est effectuée ; l’export JSON reste disponible.

La timeline couvre actuellement les trois échographies. Elle ne représente pas encore l’ensemble du suivi de grossesse. Une période passée ne signifie pas qu’un examen a été réalisé.

Une première fiche hebdomadaire est disponible entre 9 SA et 9 SA + 6 jours. Pour les semaines sans contenu approuvé, l’application indique qu’aucune fiche n’est disponible. Les repères décrits sont généraux et ne permettent pas d’interpréter une échographie individuelle.

Un premier moteur de recherche documentaire est développé et testé sur des passages fictifs. Il valide les fichiers JSON et les métadonnées, exclut les passages non autorisés pour le RAG et classe les résultats selon les mots communs avec leur titre et leur contenu.

Le moteur est accessible dans un laboratoire Streamlit indépendant de l’application de suivi. Le corpus médical destiné au RAG, la classification des intentions et la génération par LLM ne sont pas encore intégrés. La préparation des rendez-vous repose sur les informations saisies par l’utilisateur.

La démonstration documentaire charge un corpus fictif depuis JSON. Le moteur valide les métadonnées, les dates, les statuts et l’unicité des identifiants avant de filtrer les autorisations et, si demandé, le thème. Il classe les passages par mots communs dans leur titre et leur contenu, avec une explication du score. Un rapport texte peut être produit à partir des résultats retenus. Aucun LLM ni service externe n’est utilisé dans cette démonstration.

La recherche reste lexicale : elle ne comprend pas les négations, les synonymes ou toutes les variations grammaticales. Le score ne mesure ni fiabilité médicale ni capacité à répondre à une question.

Les sources, les conditions de réutilisation et les décisions éditoriales des fiches sont documentées dans [la revue des sources](donnees/REVUE_SOURCES.md).
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

## Essayer la recherche documentaire

Depuis la racine du projet, avec l’environnement virtuel activé :

```bash
python essai_recherche.py
```

L’essai charge `donnees/corpus_fictif.json`. Il permet plusieurs recherches, un filtre de thème et une limite de résultats. Saisir `/quitter` pour terminer.

Pour ouvrir le laboratoire graphique indépendant :

```bash
python -m streamlit run laboratoire_recherche.py
```

Le laboratoire affiche les passages retenus, leurs scores et les mots communs, et permet de télécharger un rapport texte. Les données sont fictives et ne sont pas utilisées par l’application de suivi.

Deux sections dépliables présentent le contexte documentaire et les messages préparés pour un futur modèle. Le contexte conserve les passages entiers, dans leur ordre de classement, jusqu’à une limite de 6 000 caractères. Cette limite ne comprend ni la question ni les consignes et ne correspond pas à un nombre de tokens.

Les consignes sont séparées de la question et des documents. Si aucun passage ne tient dans le contexte, aucun message n’est préparé. Aucun appel API n’est effectué.

Un champ facultatif permet de saisir une réponse fictive pour contrôler ses références entre crochets. Les identifiants cités sont comparés aux documents du contexte. Une référence inconnue empêche l’affichage de la liste des sources ; une absence de citation produit un avertissement.

Les titres et les URL des sources citées proviennent des métadonnées du contexte. Ce contrôle vérifie la présence des références, pas que les passages soutiennent chaque affirmation.

Une simulation automatique reprend le premier passage du contexte et ajoute son identifiant comme citation. Elle ne comprend pas la question et ne réalise aucune synthèse.

La coordination accepte une fonction de génération interchangeable. Le laboratoire utilise toujours la simulation locale ; aucun fournisseur externe n’est configuré.

Une indisponibilité signalée par le générateur affiche un message dédié, sans exposer le détail technique de l’erreur. Les passages documentaires restent visibles et le téléchargement du rapport reste accessible. La coordination ne relance pas automatiquement la génération.

Si le contexte est vide, le générateur n’est pas appelé. Une réponse vide ou contenant une référence inconnue provoque une erreur et n’est pas affichée. Une réponse sans citation reste visible dans le laboratoire avec un avertissement, sans être présentée comme sourcée.

Pour exporter l’exemple de recherche « profil » depuis le terminal :

```bash
python essai_rapport.py /tmp/nurtureai_rapport_profil.txt
```

Le chemin de destination est obligatoire ; un fichier existant à cet emplacement est remplacé. Aucun service externe ni LLM n’est appelé par ces démonstrations.

## Essayer la génération avec Groq

Le script `essai_groq.py` propose quatre questions prédéfinies sur le corpus fictif et utilise le modèle `openai/gpt-oss-20b` via Groq. Chaque changement de question réinitialise l’autorisation d’envoi. Lorsqu’aucun passage n’est trouvé, le bouton reste désactivé, même si l’autorisation est cochée.

Configurer localement `.streamlit/secrets.toml` :

```toml
GROQ_API_KEY = "votre-cle"
```

Ce fichier doit rester exclu de Git. Ne jamais publier une clé réelle.

Lancer depuis la racine du projet :

```bash
python -m streamlit run essai_groq.py
```

La page présente les messages avant envoi. L’appel nécessite une autorisation cochée puis un clic explicite. Aucun appel n’est effectué à l’ouverture.

L’adaptateur limite la génération à 512 tokens, configure un délai d’attente réseau de 20 secondes et désactive les nouvelles tentatives automatiques. Les réponses interrompues, vides ou contenant une référence inconnue sont refusées. Une réponse sans citation est accompagnée d’un avertissement.

Les premiers essais distinguent les observations du modèle et les vérifications automatisées de l’application :

| Cas | Vérification | Résultat |
| --- | --- | --- |
| Contenu du calendrier | Appel réel | Réponse conforme au passage, avec citation et URL attendues. |
| Sauvegarde du profil | Appel réel | Réponse indiquant le navigateur, avec la référence `sauvegarde`. |
| Couleur du calendrier | Appel réel | Le modèle indique que les documents ne permettent pas de répondre. |
| Recherche `banane` | Test automatisé sans réseau | Aucun contexte ; bouton d’envoi désactivé malgré l’autorisation. |
| Changement de question | Test automatisé sans réseau | Autorisation décochée ; aucun appel automatique. |
| Réponse sans citation | Test automatisé avec générateur fictif | Texte accompagné d’un avertissement, sans liste de sources ni mention de références présentes. |

Ces observations ponctuelles ne constituent pas une évaluation générale du modèle. Les tests avec un générateur fictif vérifient le comportement de l’application, pas la qualité des réponses du fournisseur.

L’application de suivi et le laboratoire simulé restent indépendants de cet essai. Aucun profil utilisateur n’est transmis.

## Organisation

* `app.py` : interface Streamlit.
* `calculs.py` : calculs indépendants de l’interface.
* `tests/` : tests des calculs et des interactions avec l'interface.
* `requirements.txt` : dépendances Python.
* `etat_session.py` : initialisation et effacement des données de session.
* `modeles.py` : profils, parcours, repères et règles de cohérence.
* `persistance.py` : export JSON et validation des données importées.
* `stockage_navigateur.py` : composant de lecture, sauvegarde et effacement dans le navigateur.
* `calendrier.py` : construction du calendrier et des événements du parcours.
* `fiches_rendez_vous.py` : préparation de l’export texte des fiches de rendez-vous.
* `timeline.py` : validation des fiches, positionnement temporel et sélection du repère à mettre en avant.
* `fiches_hebdomadaires.py` : validation, chargement des fiches approuvées et sélection selon la semaine SA.
* `donnees/timeline_grossesse.json` : contenu versionné des fiches de suivi.
* `donnees/fiches_hebdomadaires.json` : contenu versionné des fiches hebdomadaires et métadonnées d’attribution.
* `donnees/REVUE_SOURCES.md` : revue documentaire et décisions de réutilisation.
* `.github/workflows/tests.yml` : exécution des tests lors des push et des pull requests.
* `corpus_documentaire.py` : chargement JSON et validation des passages documentaires.
* `recherche_documentaire.py` : filtrage des autorisations et classement lexical.
* `essai_recherche.py` : démonstration en terminal sur un corpus fictif.
* `donnees/corpus_fictif.json` : passages et autorisations fictifs de démonstration.
* `rapport_recherche.py` : construction du rapport texte à partir des résultats.
* `essai_rapport.py` : export de l’exemple de recherche vers un fichier choisi.
* `laboratoire_recherche.py` : interface de démonstration indépendante de l’application de suivi.
* `contexte_documentaire.py` : construction d’un contexte JSON limité en caractères, avec passages complets et sources.
* `messages_assistant.py` : préparation des consignes et des données pour le laboratoire, sans appel à un modèle.
* `citations_documentaires.py` : extraction des citations, détection des références inconnues et récupération des métadonnées des sources citées.
* `generation_simulee.py` : production déterministe d’un texte à partir du premier passage transmis.
* `assistant_documentaire.py` : coordination de la préparation des messages, d’un générateur interchangeable et du contrôle des références.
* `generation_groq.py` : adaptateur Groq et traduction des erreurs du fournisseur.
* `essai_groq.py` : essais distants sur des questions prédéfinies et un corpus fictif, après autorisation explicite.


## Limites

Les dates calculées sont indicatives. Elles ne confirment ni une ovulation ni une grossesse et ne constituent pas une méthode contraceptive.

Ce projet est en cours de développement.
