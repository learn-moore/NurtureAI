# Couverture du corpus documentaire

## Objet

Relier les questions générales visées aux passages documentaires et aux preuves de leur couverture.

Cette liste constitue une proposition de travail pour le MVP. Elle ne signifie pas que les réponses sont déjà disponibles. Les six thèmes du cadrage restent dans le périmètre.

## États

* À documenter : question retenue, aucun passage approuvé.
* En revue : sources et contenu en cours de vérification.
* Prêt pour essai : contenu et réutilisation examinés, passage préparé.
* Vérifié sur les cas prévus : recherche et réponse contrôlées sur des questions de référence et leurs variantes.
* Évalué avec réserves : essais réalisés et relus, avec des écarts ou des vérifications complémentaires consignés dans la revue.

Un classement favorable ou une citation reconnue ne suffit pas à déclarer une question couverte.

## Questions de référence

| ID | Thème | Question générale | État |
| --- | --- | --- | --- |
| COR-01 | conception | À quoi sert une consultation avant une grossesse ? | Vérifié sur les cas prévus |
| COR-02 | conception | Quels sujets peut-on préparer pour cette consultation ? | Évalué avec réserves |
| COR-03 | suivi_grossesse | Que signifient semaines d’aménorrhée et semaines de grossesse ? | En revue |
| COR-04 | suivi_grossesse | À quoi sert la première consultation de grossesse en France ? | Vérifié sur les cas prévus |
| COR-05 | nutrition | Où trouver des recommandations alimentaires institutionnelles pour la grossesse ? | Vérifié sur les cas prévus |
| COR-06 | nutrition | Quelles précautions alimentaires générales sont recommandées pendant la grossesse ? | En revue |
| COR-07 | habitudes_de_vie | Quels sont les messages généraux de prévention concernant l’alcool pendant la grossesse ? | Évalué avec réserves |
| COR-08 | habitudes_de_vie | Quels accompagnements sont proposés pour arrêter le tabac pendant la grossesse ? | Évalué avec réserves |
| COR-09 | medicaments | Pourquoi signaler un projet de grossesse lors d’une discussion sur les médicaments ? | À documenter |
| COR-10 | medicaments | Quelles informations préparer pour discuter de ses médicaments avec un professionnel ? | À documenter |
| COR-11 | signes_alerte | Où trouver une information institutionnelle sur les signes nécessitant un avis pendant la grossesse ? | À documenter |
| COR-12 | signes_alerte | Quelles limites présente une liste générale de signes d’alerte ? | À documenter |

COR-01 et COR-02 ont fait l’objet d’essais sur les questions initiales et leurs variantes. Les résultats couvrent plusieurs versions des consignes et du format de sortie. Des réserves d’attribution des citations subsistent dans les observations consignées. Une vérification finale avec la configuration actuelle reste à effectuer.

Pour COR-04, la vérification porte sur la question de référence et une reformulation. Trois tentatives ont produit une interruption et deux réponses conformes aux passages transmis. Ce statut ne constitue pas une validation clinique ni une garantie de répétabilité.

Pour COR-06, les passages nutrition_hygiene_preparation, nutrition_mise_au_froid_decongelation et nutrition_cuisson_lavage ont chacun été examinés sur une question principale, une reformulation et une question non couverte. Les résultats et leurs limites sont consignés dans REVUE_SOURCES.md. La couverture reste partielle ; COR-06 conserve l’état En revue.

Le passage nutrition_listeriose_prevention a également été examiné sur une question principale, une reformulation et une question chiffrée non couverte. Les deux réponses documentaires présentent des réserves de formulation ; l’insuffisance est correctement signalée pour la question chiffrée. COR-06 conserve l’état En revue.

## Premier lot proposé

Commencer par COR-01 à COR-04.

Ce lot permet de travailler les informations générales de conception et de suivi. Il ne réduit pas le périmètre final aux deux premiers thèmes.

## Dossier attendu pour chaque question

* Document précis, organisme, URL et section utilisée.
* Date de publication ou de mise à jour, si disponible.
* Date de consultation et recherche de mises à jour.
* Pays et limites de transposition.
* Conditions de réutilisation et décision documentée.
* Identifiants des passages associés.
* Éléments que la réponse peut affirmer.
* Éléments non couverts, à ne pas déduire.
* Question de référence et variantes de formulation.
* Question voisine sans réponse dans les passages.
* Résultats de recherche et vérification des affirmations produites.

Les décisions détaillées sur les sources restent consignées dans REVUE_SOURCES.md.

## Limites de sécurité

Les questions de ce document sont générales. Une formulation personnelle, une demande de décision thérapeutique ou un signal d’urgence doit suivre les contrôles de sécurité avant le RAG.

Les passages sur les signes d’alerte ne remplacent pas le contrôle local et ne doivent pas devenir une condition d’accès à l’aide urgente.

Les passages non approuvés restent exclus de la recherche utilisée pour répondre à l’utilisateur.

## Cas de recherche du premier lot

| Question | Passage attendu en première position |
| --- | --- |
| À quoi sert une consultation avant une grossesse ? | conception_consultation_objectif |
| Quels sujets peut-on préparer pour cette consultation ? | conception_consultation_preparation |
| Quels sujets aborder avant une grossesse ? | conception_consultation_preparation |

Les passages sont désormais retenus pour les essais du prototype. Les tests de recherche utilisent directement le corpus enregistré. Les réponses générées restent à vérifier.

### Question voisine non couverte

Question : Combien coûte une consultation avant une grossesse ?

Les passages ne contiennent aucune information tarifaire. La recherche lexicale retourne néanmoins des résultats en raison des mots communs.

Comportement attendu pour la réponse : signaler que le corpus ne permet pas de répondre, sans inventer un prix ou une prise en charge. Une citation valide ne suffirait pas à justifier une affirmation tarifaire.

## Vérification complémentaire de COR-01 et COR-02

Quatre essais ont été réalisés avec la configuration actuelle, sans modification des consignes entre les exécutions.

COR-01 : la question initiale et sa reformulation produisent des réponses fidèles à conception_consultation_objectif, correctement citées et sans confusion avec le suivi de grossesse.
Verdict : vérifié sur les deux cas examinés.

COR-02 : la question initiale produit une liste fidèle, sans exemple ajouté. La variante reprend également les catégories et les limites du passage sur la préparation.

Une réserve persiste dans la variante : « échanger sur ces sujets » renvoie à la liste issue du passage sur la préparation, mais cite uniquement conception_consultation_objectif. Le contenu est présent dans le corpus ; son attribution reste imparfaitement délimitée.

Verdict COR-02 : évalué avec réserves. Ces essais ne démontrent pas une fiabilité systématique.