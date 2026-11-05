# Recette V1 de NurtureAI

## Objet

Suivre la réalisation et la vérification du périmètre défini dans le cadrage fonctionnel. Ce document ne remplace pas le cadrage et ne réduit pas son périmètre.

## États utilisés

* À réaliser : fonctionnalité absente.
* Partiel : certains composants existent, mais le parcours reste incomplet.
* À vérifier : fonctionnalité implémentée, recette finale à effectuer.
* Validé : critères vérifiés, avec preuve et environnement consignés.

Un test automatisé réussi ne remplace pas une recette navigateur ni une revue du contenu médical.

## Suivi des lots

| Lot | État initial | Critères concernés | Travail restant |
| --- | --- | --- | --- |
| Accueil et navigation | Partiel | CA-01, CA-25 | Finaliser les écrans, À propos et la navigation accessible. |
| Conception | Partiel | CA-03, CA-04 | Définir les conventions et réaliser les estimations d’ovulation et de fenêtre fertile. |
| Repères grossesse | À vérifier | CA-05, CA-06 | Finaliser les conventions et vérifier les changements de datation. |
| Transitions et historique | Partiel | CA-07 à CA-11 | Vérifier la sauvegarde confirmée, les annulations et les échecs. |
| Persistance et échanges | Partiel | CA-02, CA-12 à CA-14, CA-23, CA-24 | Compléter les limites d’import et la recette réelle du stockage. |
| Calendrier et contenus | Partiel | EF-04 | Compléter les événements, la timeline et les fiches selon la couverture retenue. |
| Assistant documentaire | Partiel | CA-15, CA-16, CA-21, CA-22 | Compléter la couverture et les réserves du corpus, puis intégrer le parcours documentaire dans l’application de suivi. |
| Intentions et sécurité | Partiel | CA-17 à CA-19 | Classifier, orienter et fournir des réponses locales adaptées. |
| Préparation IA des rendez-vous | Partiel | CA-20 | Ajouter les propositions IA avec conservation des notes et validation manuelle. |
| Accessibilité et déploiement | À réaliser | CA-25, ENF-04, ENF-06, ENF-09 | Tester les navigateurs, les petits écrans, les performances et l’hébergement. |

## Décisions à finaliser

* Couverture minimale des fiches hebdomadaires et de la timeline.
* Questions effectivement couvertes par chacun des six thèmes du corpus.
* Conventions de calcul destinées à la V1.
* Stratégie de classification et traitement des demandes ambiguës.
* Hébergement de démonstration et conditions d’utilisation des données.

Toute réduction du périmètre doit être explicitement décidée, puis reportée dans le cadrage.

## Prochain lot : orientation des demandes

Résultats attendus :

* Les quatre catégories disposent de cas de référence.
* Les demandes ambiguës peuvent rester indéterminées.
* Les demandes mixtes ne libèrent pas une réponse personnalisée.
* Une urgence potentielle suit un parcours local prioritaire,
  sans attendre la recherche documentaire ou une API.
* Les intentions non autorisées n’appellent pas le générateur.
* Une erreur de classification ne déclenche pas de génération libre.

### État au 20 octobre 2026

Un classifieur distant expérimental et des réponses prédéfinies existent pour les urgences potentielles, les situations médicales personnelles, les demandes hors périmètre et les demandes indéterminées.

Un signalement explicite d’urgence interrompt le traitement avant la classification. Une règle locale reconnaît également certaines déclarations contenant « vis », « vit » ou « vivre une urgence médicale ». Lorsqu’elle correspond, ni le classifieur distant, ni la recherche, ni le générateur ne sont appelés.

L’application propose une aide d’urgence consultable sans passer par le chat, y compris pendant la lecture du profil.

### Vérifications et limites

Les tests automatisés vérifient la priorité du signalement, le blocage des appels, les réponses prédéfinies et l’accès à l’aide pendant le chargement du profil.

La règle locale ne constitue pas une détection clinique des urgences. Elle peut manquer d’autres formulations et déclencher une alerte pour certaines négations ou citations. Une absence de correspondance ne signifie pas une absence de danger.

Le classifieur distant reste expérimental. L’assistant complet n’est pas encore intégré à l’application. Le critère CA-18 reste partiellement couvert ; les critères CA-17 à CA-19 ne sont pas déclarés validés.

## Preuves de validation

Pour chaque scénario exécuté, consigner :

* Identifiant du critère et scénario.
* Commit testé.
* Date et environnement.
* Données fictives utilisées.
* Résultat attendu et résultat observé.
* Verdict : conforme, non conforme ou non vérifié.
* Limites de la vérification.

## Point documentaire au 5 novembre 2026

Le corpus médical contient seize passages, dont quinze utilisables et un brouillon exclu de la recherche. Les six thèmes sont représentés, sans être intégralement couverts.

Sur les douze questions de couverture :
* Sept sont vérifiées sur les cas prévus.
* Trois sont évaluées avec réserves.
* Deux restent en revue.

Les essais distants ont porté sur des questions prédéfinies, sans profil utilisateur transmis. Les réponses ont été comparées aux passages et leurs écarts consignés dans REVUE_SOURCES.md.

Les références conservent les versions des sources et, lorsqu’elle existe, une mention de réutilisation ou d’adaptation. Des tests simulés vérifient le transport et l’affichage de cette mention.

Les réserves portent notamment sur la recherche lexicale, l’attribution des citations et la fidélité de certaines formulations. La revue du moteur de recherche reste reportée.

L’assistant demeure dans une page expérimentale distincte. Ces résultats ne valident pas encore les critères de l’assistant intégré à l’application de suivi.

## Condition de fin

La V1 peut être déclarée terminée lorsque les critères retenus sont vérifiés, les écarts bloquants corrigés et les limites documentées.

Les résultats expérimentaux du laboratoire ne valent pas validation de l’assistant médical intégré.