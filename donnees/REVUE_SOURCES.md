# Revue des sources

## Échographie du premier trimestre

Date de revue : 2026-10-03.
Fiche concernée : `echographie_premier_trimestre`.

### Référence médicale

Organisme : Assurance Maladie.
Page : https://www.ameli.fr/assure/sante/devenir-parent/grossesse/grossesse-en-bonne-sante/grossesse/grossesse-soins-dentaires-dentiste-consultation
Section : Première échographie.
Date affichée sur la page : 2026-07-14.

### Vérification du contenu

La fenêtre indiquée correspond à 11 SA à 13 SA + 6 jours, soit 77 à 97 jours SA révolus, bornes incluses.
Le résumé sur la datation, le nombre de fœtus et la mesure de la clarté nucale correspond aux informations de la source.
Les questions proposées sont une rédaction de NurtureAI. Elles ne sont pas présentées comme des citations d’Ameli.
Cette comparaison documentaire ne constitue pas une validation clinique.

### Réutilisation

Conditions consultées : https://www.ameli.fr/node/24268

Les CGU réservent les droits sur les textes et prévoient une autorisation préalable pour leur reproduction.
Aucune autorisation spécifique ni licence ouverte applicable à cette fiche n’a été établie lors de cette revue.
La réutilisation de notre synthèse reste à clarifier. Ce constat ne signifie pas que les faits médicaux eux-mêmes sont interdits de réutilisation.

### Décision pour le prototype

Conserver la fiche en brouillon et son statut de réutilisation à examiner. Ne pas modifier les statuts pour simplement faire apparaître la fiche dans l’interface.
Pour avancer, rechercher une référence institutionnelle dont les conditions de réutilisation sont explicites et qui couvre toutes les informations de la fiche.

## Remplacement de la source par la HAS

Date : 2026-10-03.

La fiche utilise désormais les recommandations HAS sur le suivi et l’orientation des femmes enceintes, mises à jour en mai 2016. Le passage retenu figure en section 4.1, page imprimée 14.

Document : https://www.has-sante.fr/upload/docs/application/pdf/suivi_des_femmes_enceintes_-_recommandations_23-04-2008.pdf

Conditions de réutilisation : https://www.has-sante.fr/jcms/c_518191/fr/mentions-legales

La synthèse conserve le sens du passage utilisé. La source et la mise à jour sont affichées, sans logo ni charte graphique HAS.
Les points retenus concordent avec la page Ameli consultée en octobre 2026. Cette vérification ne constitue pas une actualisation de l’ensemble des recommandations de 2016.
La fiche est retenue pour le prototype après revue documentaire. Cette décision ne constitue ni une validation clinique ni une approbation de NurtureAI par la HAS.
La décision précédente concernant Ameli reste conservée comme historique ; elle ne s’applique pas à cette nouvelle source.

## Conservation d’Ameli comme source secondaire

Date : 2026-10-03.

Fiche concernée : `echographie_premier_trimestre`.

La HAS reste la source principale utilisée pour la rédaction et l’approbation de la fiche dans le prototype.

Ameli est conservée dans `secondary_sources` avec :
- `role` : `secondary` ;
- `usage` : `cross_check` ;
- `reuse_status` : `to_review`.

Cette référence permet de documenter le recoupement des informations. Son texte n’est pas intégré au corpus de l’application.
L’interface présente un lien vers la page Ameli et un lien vers ses conditions de réutilisation : https://www.ameli.fr/node/24268

La présence de ces liens ne constitue pas une autorisation de reproduction du contenu. Le statut de réutilisation de la source secondaire ne détermine
pas l’affichage de la fiche. Celui-ci dépend de l’approbation éditoriale, de la revue et de la source principale.
Le futur importateur RAG devra exclure de l’ingestion de contenu les références dont l’usage est `cross_check`.

Cette entrée complète les décisions précédentes sans les effacer.

## Deuxième échographie : fiche en préparation

Date : 2026-10-03.

Fiche concernée : `echographie_deuxieme_trimestre`.

Référence candidate : arrêté du 20 avril 2018, annexe II, version initiale publiée le 25 avril 2018. https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000036833452
La fenêtre candidate correspond aux jours SA 140 à 174 inclus. Avant approbation, vérifier l’actualité du passage et les conditions de réutilisation applicables.
La fiche reste en brouillon, avec une réutilisation à examiner et sans date de revue finalisée. Elle est exclue de l’affichage.

## Deuxième échographie : sélection pour le prototype

Date : 2026-10-03.

Fiche concernée : `echographie_deuxieme_trimestre`.

La synthèse et les bornes de 140 à 174 jours SA inclus reposent sur l’annexe II de l’arrêté du 20 avril 2018, version initiale. Le titre conserve cette précision. Le fonds JORF est publié sous licence ouverte : https://www.data.gouv.fr/datasets/jorf-les-donnees-de-l-edition-lois-et-decrets-du-journal-officiel

La réutilisation conserve la source, sa date et son sens. Elle ne suggère aucune approbation officielle de NurtureAI.
La page Ameli du 2 juin 2026 recoupe les objectifs de l’examen. Elle indique une période de 20 à 24 SA sans précision des jours :
elle ne confirme donc pas à elle seule la borne de 174 jours. Elle reste une référence secondaire, sans ingestion de son texte.
La fiche est retenue pour le prototype après revue documentaire. Cette sélection ne constitue ni une validation clinique ni une certification du statut juridique actuel de l’ensemble de l’arrêté.

## Troisième échographie : sélection pour le prototype

Date : 2026-10-04.

Fiche concernée : `echographie_troisieme_trimestre`.

Source principale : annexe II de l’arrêté du 20 avril 2018, version initiale. Les conditions de réutilisation du fonds JORF documentées précédemment s’appliquent à cette synthèse. https://www.legifrance.gouv.fr/jorf/article_jo/JORFARTI000036833467

Fenêtre retenue : 210 à 244 jours SA inclus, soit 30 SA à 34 SA + 6 jours. Ameli indique 30 à 35 SA. Cette formulation n’est pas considérée comme une confirmation exacte des bornes retenues. Le recoupement porte sur les objectifs et les observations de l’examen. La sélection concerne le prototype. Elle ne constitue pas une validation clinique ni une certification du statut juridique actuel de l’ensemble du texte. Aucun contenu Ameli n’est ingéré.

## Fiche à 9 SA : revue documentaire

Date : 2026-10-04.

Fiche concernée : `developpement_9_sa`, intitulée « À 9 SA : le développement se poursuit ».

La fiche porte sur le développement à 9 SA et les changements possibles à cette période. Elle remplace `preparer_suivi_9_sa`, consacrée à la préparation du suivi. La référence HAS associée à ce précédent contenu n’est pas retenue pour les repères de développement. Périmètre temporel : 9 SA + 0 à 9 SA + 6 jours, soit 63 à 69 jours SA inclus. Il ne s’agit pas de 9 semaines depuis la conception, ni de la neuvième semaine en cours au sens ordinal.

Document consulté : NHS, Angleterre, « Week 9 », sections « What does my baby look like? » et « Early pregnancy symptoms (at 9 weeks) » : https://www.nhs.uk/best-start-in-life/pregnancy/week-by-week-guide-to-pregnancy/1st-trimester/week-9/

La synthèse française retient des repères de développement et quelques changements possibles. L’ordre de grandeur de la taille n’est pas présenté comme une norme individuelle ou un seuil diagnostique. Les symptômes mentionnés ne sont pas propres à cette seule semaine. Aucune image, posologie ou organisation des soins anglaise n’est reprise. Aucune date de publication ou de mise à jour propre à cette page n’a été identifiée. Les champs `publication_date` et `displayed_date` sont renseignés à `null`.

Conditions applicables : https://www.nhs.uk/best-start-in-life/terms-and-conditions/

Best Start in Life figure parmi les sites exclus des conditions générales du NHS. La licence OGL mentionnée dans ces conditions générales ne constitue donc pas une autorisation de réutilisation pour cette fiche. Aucune autorisation spécifique d’adaptation n’est documentée.

Statut documentaire : `editorial_status: draft`, `reuse_status: to_review` et `reviewed_at: null`. La revue éditoriale et l’examen des conditions de réutilisation ne sont pas finalisés. La fiche est exclue de l’affichage et ne dispose pas d’une validation clinique.

## Fiche à 9 SA : conditions de réutilisation

Date : 2026-10-04.

Fiche concernée : `developpement_9_sa`.

Best Start in Life est explicitement exclu des conditions générales de réutilisation du NHS : https://www.nhs.uk/our-policies/terms-and-conditions/content-not-licensed-for-re-use/

Ses conditions propres réservent les droits sur les contenus, limitent les copies à un usage personnel et interdisent la modification des copies : https://www.nhs.uk/best-start-in-life/terms-and-conditions/

L’attribution OGL précédemment envisagée n’est pas retenue. La provenance documentaire est conservée, mais aucune autorisation de publication de l’adaptation française n’est établie. La fiche reste en brouillon, avec une réutilisation à examiner et sans date de revue finalisée. Elle est exclue de l’affichage.

## Fiche à 9 SA : référence complémentaire examinée

Date : 2026-10-05.

Document : Better Health Channel, « Pregnancy - week by week ». Organisme : Department of Health, État de Victoria, Australie. URL : https://www.betterhealth.vic.gov.au/health/HealthyLiving/pregnancy-week-by-week

Passages examinés : « Calculating pregnancy duration » et « Pregnancy week 9 ».
Le document compte la grossesse depuis le premier jour des dernières règles. Le passage consacré à la semaine 9 décrit la formation des yeux, de la bouche et de la langue, les premiers mouvements et la production de cellules sanguines par le foie.

Date de revue affichée : 2012-02-28.
Date de consultation : 2026-10-05.

Conditions : https://www.betterhealth.vic.gov.au/about/terms-of-use

Les conditions autorisent la rédaction d’un contenu original utilisant le site comme référence, avec la mention « Reference: www.betterhealth.vic.gov.au » accompagnée d’un lien vers ce site. Cette possibilité est distincte de l’adaptation ou de la traduction de leurs textes, soumise à autorisation.

La référence reste candidate en raison de l’ancienneté de la revue affichée. Le libellé hebdomadaire ne suffit pas, à lui seul, à établir des bornes biologiques précises entre 63 et 69 jours SA. Aucun changement du statut de publication de la fiche.

## Fiche à 9 SA : sélection pour le prototype

Date : 2026-10-05.

Fiche concernée : `developpement_9_sa`.
Titre : « Autour de 9 SA : visage et premiers mouvements ».

Le texte actuel remplace le brouillon fondé sur Best Start in Life. Il présente la formation du visage et les mouvements précoces. Il ne reprend ni estimation de taille ni liste de symptômes.

Référence principale : Better Health Channel, « Pregnancy - week by week », passage « Pregnancy week 9 ». La date de revue affichée, 2012-02-28, reste conservée. Le développement du visage et les mouvements sont recoupés avec « Pregnancy at week 9 », Pregnancy, Birth and Baby, revue en août 2023 : https://www.pregnancybirthbaby.org.au/pregnancy/pregnancy-stages/pregnancy-at-week-9

La distinction entre mouvements et perception maternelle est recoupée avec « Your baby's movements », NHS, revue le 2024-07-08 : https://www.nhs.uk/pregnancy/keeping-well/your-babys-movements/

Ces références servent au recoupement documentaire. Leurs textes ne sont pas intégrés au corpus RAG. Le contenu est rédigé pour NurtureAI à partir des faits examinés. L’usage retenu relève de la rédaction originale avec référence, prévue par les conditions de Better Health Channel : https://www.betterhealth.vic.gov.au/about/terms-of-use

La mention « Reference: www.betterhealth.vic.gov.au » est affichée sous forme de lien. Le document précis reste également accessible. La fenêtre de 63 à 69 jours SA inclus détermine l’affichage. Elle ne constitue pas une limite biologique des étapes décrites.

La fiche est retenue pour le prototype après revue documentaire. Cette sélection ne constitue pas une validation clinique.

## Consultation préconceptionnelle : COR-01 et COR-02

### Périmètre examiné

* COR-01 : objectif général d’une consultation avant une grossesse.
* COR-02 : sujets à préparer pour cette consultation.

La sélection reste limitée à l’information générale. Les prescriptions, doses, examens à décider individuellement et interprétations de résultats sont exclus de ces premiers passages.

### Sources candidates

HAS : Projet de grossesse : informations, messages de prévention, examens à proposer.
https://www.has-sante.fr/jcms/c_1360649/

La page indique une mise à jour du 15 février 2013. Les sections sur l’objectif et les professionnels concernés sont candidates pour COR-01.

Assurance Maladie : Consulter avant d’être enceinte : la consultation préconceptionnelle.
https://www.ameli.fr/assure/sante/devenir-parent/concevoir-un-enfant/consultation-et-mode-de-vie-en-vue-d-une-grossesse/avant-d-etre-enceinte-la-consultation-preconceptionnelle

Date affichée : 26 mai 2025.
La section consacrée aux échanges pendant la consultation est candidate pour le recoupement de COR-02.

### Actualité documentaire

Les recommandations HAS de juin 2026 sur la santé sexuelle et reproductive, volet 2, mentionnent une actualisation en cours du volet consacré à la consultation préconceptionnelle.

La disponibilité d’une version finalisée de ce volet reste à vérifier avant l’approbation des passages.

### Réutilisation

La consultation complète des conditions HAS n’a pas abouti lors de cette recherche. Leur vérification reste à terminer, notamment pour la synthèse, la diffusion et l’usage envisagé dans le corpus transmis au fournisseur.

La page Ameli sert à ce stade de référence de recoupement. Aucune nouvelle autorisation de réutilisation n’est établie ici.

### Décision

COR-01 et COR-02 passent à l’état En revue. Aucun passage médical n’est encore approuvé ni ajouté au corpus utilisé pour la génération.

## Consultation préconceptionnelle : brouillons des passages

Date de travail : 22 octobre 2026.
Statut : brouillons, exclus de la génération.

### Actualité

La recherche retrouve les recommandations HAS de juin 2026. Elles mentionnent encore le volet consacré à la consultation préconceptionnelle comme étant en préparation. Aucune version finalisée de ce volet n’a été identifiée lors de cette recherche.

Cette observation ne prouve pas l’absence de publication ailleurs.

### Réutilisation

La section sur la reproduction des travaux HAS a pu être consultée dans le contenu restitué par le moteur de recherche. Elle prévoit une réutilisation des informations publiques sous conditions, avec notamment attribution, date et respect du sens, et réserve les droits de tiers.

L’ouverture directe des mentions légales reste en échec. La vérification complète n’est donc pas clôturée. Aucun logo ni aucune présentation suggérant une validation de NurtureAI par la HAS ne sera utilisé.

### COR-01 : objectif de la consultation

Identifiant proposé : conception_consultation_objectif.

Texte proposé : Une consultation avant une grossesse permet d’échanger avec un professionnel de santé sur le projet de grossesse, de recevoir des informations de prévention et d’aborder les besoins d’accompagnement. Elle peut être menée par un médecin généraliste, un gynécologue ou une sage-femme.

Source candidate : https://www.has-sante.fr/jcms/c_1360649/

Sections : Définition et objectif ; Qui fait la consultation ?

Limites : Ce passage ne définit aucun bilan obligatoire et ne détermine pas les examens ou traitements adaptés à une personne.

### COR-02 : préparer les échanges

Identifiant proposé : conception_consultation_preparation.

Texte proposé : Pour préparer les échanges avant une grossesse, les sujets à aborder peuvent inclure les questions sur le projet de grossesse, les antécédents personnels et familiaux, les éventuelles grossesses précédentes et les habitudes de vie. Le professionnel adapte les échanges à la situation.

Source candidate : https://www.has-sante.fr/jcms/c_1360649/

Sections : À quelles occasions ? ; Principes ; Quelles informations recueillir ?

La liste proposée résume des sujets abordés par la source. Elle ne constitue pas un questionnaire médical exhaustif.

Limites : Cette préparation n’implique pas de saisir ces informations dans NurtureAI. Le passage ne propose pas d’interpréter les documents. La réutilisation de cette synthèse reste à examiner.

### Décision

COR-01 et COR-02 restent En revue. Les textes sont des propositions éditoriales, pas des passages approuvés. Aucun envoi à un modèle distant n’est effectué.

## Vérification complémentaire du 22 octobre 2026

Les mentions légales HAS et la page consacrée au projet de grossesse ont été téléchargées et lues directement. Les difficultés d’accès signalées précédemment sont résolues.

### Réutilisation

Les mentions légales prévoient la réutilisation des informations publiques HAS sous conditions, notamment attribution, indication de la dernière mise à jour et respect du sens, sous réserve des droits de tiers.

Le projet retient une synthèse attribuée, sans logo ni charte graphique HAS. La source, sa date et les limites du passage devront accompagner le contenu. La réponse produite par NurtureAI ne sera pas présentée comme une communication validée par la HAS.

### Relecture des brouillons

COR-01 correspond aux sections consacrées à l’objectif de la consultation et aux professionnels qui peuvent la mener.

COR-02 est recentré sur les sujets documentés par la HAS. La phrase sur les documents médicaux à apporter est retirée. Ameli reste une référence de recoupement, sans incorporation de son texte dans ces passages.

### Limites conservées

La source HAS est ancienne. Les passages restent limités à l’objectif général et aux sujets d’échange. Ils ne reprennent ni calendrier de dépistage, ni liste d’examens à réaliser, ni prescription ou dose.

Les deux questions restent En revue jusqu’à la vérification des passages structurés et de leur attribution.

## Décision éditoriale du 22 octobre 2026 : COR-01 et COR-02

Les passages conception_consultation_objectif et conception_consultation_preparation sont retenus pour les essais du prototype après revue documentaire et examen des conditions de réutilisation HAS.

Leur attribution conserve l’organisme, l’URL et la date de mise à jour de la source. Les textes restent limités à l’objectif général de la consultation et aux sujets d’échange.

Les statuts éditorial et de réutilisation passent à approved. Cette décision ne constitue ni une certification clinique, ni une validation de NurtureAI par la HAS.

La recherche a été vérifiée sur trois formulations. La qualité des réponses générées reste à évaluer, notamment sur la question tarifaire non couverte.

Les interfaces existantes continuent d’utiliser le corpus fictif.

## Premier essai distant des passages préconceptionnels

Interface : essai_assistant_groq.py.
Fournisseur : Groq.
Modèle : openai/gpt-oss-20b.

COR-01 : les affirmations observées correspondent au passage cité. L’organisme, la date de mise à jour et le lien sont affichés.

COR-02 : les sujets proposés et le complément sur l’objectif de la consultation correspondent aux deux passages cités. Le complément est secondaire par rapport à la question. La présentation des puces reste à améliorer.

Pour les deux réponses, le rappel de portée générale demandé dans les consignes est absent du texte généré. Un avertissement est toutefois présent dans l’interface.

Question tarifaire : le statut sans_citation a entraîné le masquage du texte généré. Son contenu n’a pas été inspecté ; aucune conclusion n’est tirée sur la capacité du modèle à s’abstenir ou sur une éventuelle invention tarifaire.

Ces observations portent sur une tentative par question. Elles ne démontrent pas la répétabilité ni une validation clinique.

## Affichage des réponses : complément du 22 octobre 2026

Le rappel de portée générale est désormais ajouté par l’interface aux réponses du mode médical avec références reconnues. Son affichage ne dépend plus du respect de cette consigne par le modèle.

Le texte est rendu en Markdown, avec le HTML désactivé. Les tests vérifient le composant utilisé et le rappel fixe. L’apparence finale des listes reste à contrôler dans le navigateur.

Ces modifications ne constituent pas un contrôle automatique de la validité médicale ou de l’adéquation des affirmations aux passages cités.

## Essais de reformulation des questions COR-01 et COR-02

Deux variantes ont été essayées avec le corpus préconceptionnel.

### Variante COR-01

Question : Quel est le but d’une consultation avant une grossesse ?

Statut obtenu : references_controlees.

La réponse reprend des informations présentes dans le corpus. Toutefois, la première puce associe les antécédents et les habitudes de vie au seul passage conception_consultation_objectif. Ces éléments relèvent du passage conception_consultation_preparation.

Le contrôle des identifiants de références réussit, mais l’attribution des affirmations aux passages reste imparfaite.

### Variante COR-02

Question : Quels sujets aborder avant une grossesse ?

Statut obtenu : references_controlees.

Les sujets énumérés correspondent au passage sur la préparation. Le complément sur l’objectif de la consultation est également sourcé. Sa présentation comme deuxième puce est maladroite.

### Affichage et limites

Le rappel fixe sur la portée générale de la réponse apparaît dans les deux essais. Un rappel généré produit un doublon.

Ces observations portent sur une exécution par variante. Elles ne démontrent pas la répétabilité des résultats.

## Nouveaux essais après précision des consignes de citation

Question : Quel est le but d’une consultation avant une grossesse ?

Les consignes demandent désormais de séparer les affirmations provenant de passages différents ou de placer les références nécessaires immédiatement après les informations concernées.

Deux exécutions ont été réalisées avec les mêmes consignes.

| Essai | Statut | Observation |
| --- | --- | --- |
| 1 | references_controlees | Informations présentes dans le corpus, mais les deux références sont regroupées à la fin du paragraphe L’association entre chaque phrase et son passage reste implicite. |
| 2 | references_controlees | Chaque puce est accompagnée du passage correspondant à son contenu. |

Le rappel fixe est affiché dans les deux cas.

Ces essais montrent une variabilité dans le placement des citations. Ils ne démontrent pas une attribution systématiquement correcte. Le contrôle automatique vérifie les références, pas le soutien de chaque affirmation par le passage cité.

## Essais sur les sujets à préparer après modification des consignes

Question : Quels sujets aborder avant une grossesse ?

Deux exécutions ont retourné le statut references_controlees.

Dans le premier essai, la réponse ajoute des exemples concernant le projet de grossesse et les habitudes de vie qui ne figurent pas dans les passages transmis.

Dans le second essai, la réponse ajoute également des exemples pour les habitudes de vie : alimentation, activité et substances.

Les grandes catégories et les objectifs de la consultation correspondent au corpus. En revanche, les précisions ajoutées ne sont pas justifiées par les passages cités.

Les deux essais ne satisfont donc pas le critère de fidélité exclusive aux documents transmis. Le contrôle des références ne détecte pas ces ajouts.

## Essais après interdiction explicite des exemples non documentés

Deux nouvelles exécutions de la question « Quels sujets aborder avant une grossesse ? » ont été réalisées.

Les deux réponses développent les habitudes de vie avec des exemples absents des passages transmis, malgré la nouvelle consigne.

Le second essai attribue également le caractère non exhaustif de la liste au passage sur l’objectif, alors que cette information figure dans celui sur la préparation.

Résultat : aucun des deux essais ne satisfait le critère de fidélité exclusive au corpus. Le statut references_controlees vérifie les références, sans détecter ces ajouts ni cette attribution incorrecte.

### Rectification sur les consignes utilisées

La vérification de l’aperçu a montré que la nouvelle consigne n’était pas chargée lors des essais précédents.

Les ajouts non documentés observés restent des défauts des réponses, mais ces essais ne permettent pas de conclure à l’inefficacité de la nouvelle consigne.

Sa présence dans le message system est désormais confirmée. Les prochains essais permettront d’évaluer cette version.

## Essais avec présence des nouvelles consignes confirmée

Question : Quels sujets aborder avant une grossesse ?

La présence de la nouvelle consigne dans le message system a été vérifiée avant les deux essais.

Aucune des deux réponses ne développe les habitudes de vie avec des exemples absents du corpus.

Premier essai : les catégories sont correctement référencées. La phrase finale introduit toutefois le terme « habituellement », non étayé, et cite un passage qui ne justifie pas cette affirmation.

Second essai : le contenu correspond au passage sur la préparation. La référence unique est placée après la liste et la phrase finale, ce qui rend son rattachement à l’ensemble moins explicite.

Ces deux observations ne suffisent pas à établir la fiabilité du comportement sur d’autres questions ou exécutions.

## Question tarifaire avec les nouvelles consignes chargées

Question : Combien coûte une consultation avant une grossesse ?

Trois essais ont été réalisés.

Le premier retourne references_controlees et indique explicitement que les documents ne contiennent aucune information tarifaire. Aucun prix ni remboursement n’est inventé dans la réponse affichée.

Les deuxième et troisième essais retournent sans_citation. Le texte généré étant masqué, son contenu ne peut pas être évalué.

Aucun tarif n’est affiché sur ces trois essais. Cela ne démontre pas trois abstentions correctes du modèle : seule la première est directement observable.

Le statut references_controlees ne distingue pas une réponse documentaire d’un constat d’insuffisance accompagné de références.

## Essais du format documentaire structuré

La présence des consignes de sortie JSON a été vérifiée dans l’aperçu avant les essais.

| Question | Statut obtenu | Observation |
| --- | --- | --- |
| Combien coûte une consultation avant une grossesse ? | information_insuffisante | Message fixe affiché, sans référence ni information tarifaire. |
| À quoi sert une consultation avant une grossesse ? | references_controlees | Réponse fidèle au passage conception_consultation_objectif, correctement cité. |

Le format JSON n’apparaît pas dans l’interface.

Ces deux essais vérifient un cas couvert et un cas non couvert. Ils ne démontrent pas une détection systématiquement correcte des informations insuffisantes ni une fidélité garantie des réponses.

Un essai complémentaire porte sur la question : « Quels sujets aborder avant une grossesse ? »

Le statut obtenu est references_controlees. La liste reprend les catégories du passage sur la préparation, sans exemples supplémentaires.

La seconde phrase reprend les objectifs de la consultation. Toutefois, l’expression « ces sujets » renvoie à la liste précédente sans citer également le passage sur la préparation.

Le contenu est présent dans le corpus, mais le rattachement des affirmations aux références reste perfectible.

## COR-03 : semaines d’aménorrhée et semaines de grossesse

État : en revue.

Question : Que signifient semaines d’aménorrhée et semaines de grossesse ?

### Source examinée

Organisme : Assurance Maladie.
Titre : Grossesse : premiers signes et déroulement.
Date affichée : 2 juin 2026.
Section : La première échographie de grossesse.

URL : https://www.ameli.fr/assure/sante/devenir-parent/grossesse/grossesse-en-bonne-sante/grossesse/premiers-symptomes-grossesse

### Périmètre du futur passage

Expliquer les deux points de départ du décompte. Préciser les conditions de la correspondance approximative entre les deux unités.

Ne pas transformer cette explication générale en datation individuelle ni en calcul de date d’accouchement.

### Vérifications restantes

Sélectionner une source dont les conditions de réutilisation permettent l’usage prévu et documenter cette décision. Conserver cette page comme source de comparaison à ce stade.

Préparer un passage limité aux définitions et à leurs limites, puis vérifier sa recherche sur plusieurs formulations.

### Proposition de contenu à examiner

Les semaines d’aménorrhée (SA) sont comptées depuis le premier jour des dernières règles. Les semaines de grossesse (SG) correspondent au temps estimé depuis la fécondation.

La correspondance d’environ deux semaines repose sur une fécondation estimée deux semaines après le début des dernières règles. Elle ne permet pas de déterminer une date individuelle de fécondation avec certitude.

État : brouillon documentaire, non intégré au corpus actif. La sélection de la source réutilisable reste à finaliser.

### Questions prévues pour les essais

| Question | Éléments attendus |
| --- | --- |
| Que signifient SA et SG ? | Définition des deux sigles et points de départ. |
| Pourquoi distingue-t-on semaines d’aménorrhée et semaines de grossesse ? | Différence entre les références temporelles. |
| L’écart entre SA et SG permet-il de connaître exactement la date de fécondation ? | Limite de la correspondance approximative. |

### Éléments exclus du passage

Le passage ne fournit pas de datation personnelle, de date d’accouchement, de seuil d’intervention ni de calendrier d’examens.

### Piste complémentaire examinée

Le site ivg.gouv.fr présente des correspondances entre SA et SG. Ces exemples ne couvrent pas seuls toutes les explications visées.

Les mentions légales présentent des conditions de réutilisation et une demande de contact. La réutilisation n’est pas marquée comme approuvée à ce stade.

### Essai avec le passage exclu du contexte autorisé

Question : Que signifient semaines d’aménorrhée et semaines de grossesse ?

Le passage grossesse_definitions_sa_sg reste en brouillon, avec une réutilisation à examiner et un usage de comparaison. Son exclusion de la recherche autorisée est vérifiée par les tests.

L’essai distant retourne information_insuffisante. L’interface affiche le message fixe, sans définition de SA ou SG.

Ce résultat correspond au comportement attendu pour le corpus actuellement autorisé. Il ne valide pas la couverture de COR-03 ni la capacité du modèle à s’abstenir systématiquement.

## COR-04 : objectif de la première consultation de grossesse

État : en revue.

Question : À quoi sert la première consultation de grossesse en France ?

### Source candidate

Organisme : Haute Autorité de santé.

Titre : Suivi et orientation des femmes enceintes en fonction des situations à risque identifiées.

URL : https://www.has-sante.fr/jcms/c_567727/en/suivi-et-orientation-des-femmes-enceintes-en-fonction-des-situations-a-risque-identifiees

### Périmètre envisagé

Expliquer les objectifs généraux de la consultation et l’organisation du suivi.

Le passage ne devra pas fournir une liste personnalisée d’examens, interpréter des résultats ni déterminer le niveau de risque d’une personne.

### Vérifications avant rédaction

Examiner la publication complète et sa date. Rechercher une actualisation ou un remplacement. Identifier les sections justifiant chaque affirmation. Vérifier les conditions de réutilisation applicables au document.

Aucun passage n’est encore approuvé pour le corpus.

### Document retenu pour préparer le passage

Titre : Suivi et orientation des femmes enceintes en fonction des situations à risque identifiées.
Document : synthèse des recommandations professionnelles.
Version : mise à jour de mai 2016.

https://www.has-sante.fr/upload/docs/application/pdf/suivi_orientation_femmes_enceintes_synthese.pdf

Sections examinées :
* Page 1 : objectifs du suivi et appréciation du niveau de risque.
* Page 2 : première consultation, information et prévention.

La recommandation de 2007, actualisée en 2016, est encore citée dans un document HAS de 2026 sur les maisons de naissance. Cette citation ne constitue pas une actualisation complète de son contenu.

### Proposition de passage

La première consultation de grossesse permet au professionnel de santé de confirmer la grossesse et d’en établir la datation. Elle comprend une information sur le suivi et des messages de prévention. Le professionnel recherche également les facteurs pouvant nécessiter une adaptation du suivi.

### Limites retenues

Le passage décrit des objectifs généraux. Il ne contient ni liste d’examens à réaliser, ni prescription, ni calendrier détaillé. Il ne permet pas à l’application d’évaluer le risque individuel.

### Réutilisation

Les conditions HAS prévoient la réutilisation de ses informations publiques, sous réserve des droits de tiers, du respect du sens, de la mention de la source et de sa dernière mise à jour.

La proposition est une synthèse rédactionnelle sans logo ni reprise de la mise en page. Elle ne suggère aucune approbation de NurtureAI par la HAS.

### Décision pour le prototype

Le passage grossesse_premiere_consultation_objectif est retenu pour les essais après examen de la synthèse HAS de mai 2016 et des conditions de réutilisation.

Cette décision porte uniquement sur les objectifs généraux décrits dans le passage. Elle ne constitue pas une validation clinique ni une approbation de NurtureAI par la HAS.

La réponse générée reste à évaluer.

### Essais distants du 4 novembre 2026

Question : À quoi sert la première consultation de grossesse en France ?

Première tentative : generation_interrompue. Aucun texte partiel affiché. La cause et l’étape de l’interruption ne sont pas identifiées ; le contenu n’est pas évaluable.

Deuxième tentative : references_controlees. La réponse reprend les trois objectifs du passage grossesse_premiere_consultation_objectif, sans information ajoutée. Chaque phrase cite ce passage. L’organisme, la version de mai 2016 et le lien sont correctement affichés.

Bilan : une réponse conforme sur deux tentatives. La répétabilité et les variantes de formulation restent à évaluer.

### Essai de reformulation du 4 novembre 2026

Question : Quel est le rôle du premier rendez-vous de suivi de grossesse ?

La recherche locale place le passage COR-04 en deuxième position, après un passage préconceptionnel.

Statut obtenu : references_controlees.

La réponse reprend les objectifs du passage grossesse_premiere_consultation_objectif, sans ajout ni confusion avec la consultation préconceptionnelle. La référence et sa version sont correctement affichées.

Bilan cumulé : trois tentatives, dont une interrompue et deux réponses conformes sur deux formulations différentes. Ces observations ne démontrent pas une fiabilité systématique.

## COR-05 : ressource institutionnelle sur l’alimentation

État : en revue.
Consultation de la fiche : 4 novembre 2026.

Question : Où trouver des recommandations alimentaires institutionnelles pour la grossesse ?

### Ressource identifiée

Organisme : Santé publique France.

Titre : De la grossesse à l’arrivée de bébé, avec sérénité : alimentation, activité physique et bien-être.

Année du guide : 2026.
Publication de la fiche : 10 juin 2026.
Mise à jour de la fiche : 30 octobre 2026.

https://www.santepubliquefrance.fr/nutrition-et-activite-physique/brochure/de-la-grossesse-a-larrivee-de-bebe-avec-serenite-alimentation-activite-physique-et-bien-etre

### Périmètre du passage envisagé

Identifier le guide, son organisme et les sujets qu’il aborde. Orienter vers sa fiche officielle.

Le passage ne fournira pas de régime personnalisé, de quantités alimentaires, de liste d’aliments à éviter ni de supplémentation.

### Vérifications restantes

Examiner le guide et ses mentions de droits. Distinguer la date de mise à jour de la fiche de la version du document téléchargeable. Définir le texte d’orientation et documenter son usage.

### Examen du document et des dates

Le sommaire du guide comporte des rubriques sur l’alimentation, les précautions alimentaires, l’activité physique et le bien-être.

La fiche officielle donne 2026 comme année de publication. Sa mise à jour du 30 octobre 2026 ne permet pas de dater une éventuelle révision du PDF.

### Proposition de notice d’orientation

Santé publique France propose le guide « De la grossesse à l’arrivée de bébé, avec sérénité ». Il aborde notamment l’alimentation pendant la grossesse, l’activité physique et le bien-être. Le guide est accessible depuis sa fiche sur le site officiel de Santé publique France.

### Usage retenu pour COR-05

La notice identifie une ressource et renvoie vers sa fiche. Elle ne reproduit ni recommandations alimentaires détaillées, ni illustrations, ni tableaux du guide.

Les mentions légales autorisent les liens directs sans autorisation préalable et demandent d’en informer le webmestre. Aucune notification n’a été envoyée dans le cadre de cette revue.

Cette décision ne vaut pas autorisation de reprendre ou d’adapter le contenu du guide pour COR-06.

### Décision pour le prototype

La notice nutrition_guide_institutionnel est retenue pour les essais. L’approbation porte sur l’identification bibliographique du guide, la description générale de ses sujets et le lien vers sa fiche.

Elle ne couvre pas la reproduction du guide, de ses illustrations ou de ses recommandations détaillées. La demande d’information du webmestre mentionnée dans les conditions reste consignée ; aucun message n’a été envoyé.

La réponse générée reste à évaluer.

### Premier essai distant

Question : Où trouver des recommandations alimentaires institutionnelles pour la grossesse ?

Statut obtenu : references_controlees.

La réponse oriente vers le guide de Santé publique France et sa fiche officielle. Elle cite nutrition_guide_institutionnel, sans ajouter de recommandations alimentaires détaillées.

L’organisme, l’année du guide, la date de mise à jour de la fiche et le lien sont correctement affichés.

Verdict : conforme pour cette exécution. La reformulation et une question dépassant le contenu de la notice restent à évaluer.

### Question dépassant le contenu de la notice

Question : Quels aliments ce guide recommande-t-il d’éviter pendant la grossesse ?

Statut obtenu : information_insuffisante.

L’application affiche le message fixe d’insuffisance. Aucune liste d’aliments ni recommandation détaillée n’est affichée.

Verdict : conforme pour cette exécution. La présence du lien vers le guide n’a pas conduit à une réponse dépassant le contenu de la notice transmise.

### Essais de reformulation

Question : Quel guide officiel consulter pour l’alimentation pendant la grossesse ?

Première tentative : reponse_rejetee. Aucun texte généré n’est affiché. Le statut ne permet pas d’identifier précisément le défaut de format ou de références.

Deuxième tentative : references_controlees. La réponse identifie le guide de Santé publique France, cite nutrition_guide_institutionnel et affiche le lien attendu. Aucun conseil alimentaire détaillé n’est ajouté.

Bilan cumulé de COR-05 : quatre tentatives. Deux réponses d’orientation conformes, une insuffisance documentaire conforme et une réponse rejetée non évaluable.

Les cas prévus ont été examinés. Le rejet observé reste une limite de fiabilité technique, malgré la réussite suivante.

## COR-06 : précautions alimentaires pendant la grossesse

État : en revue.

Question générale : Quelles précautions alimentaires générales sont recommandées pendant la grossesse ?

### Premier passage envisagé

Sujet : hygiène lors de la préparation des repas.

Source candidate : Anses.
Document : Hygiène dans la cuisine : 10 recommandations pour éviter les intoxications alimentaires.

https://www.anses.fr/fr/system/files/hygiene-cuisine-A4-PRINT.pdf

### Périmètre à documenter

Sélectionner les recommandations concernant le lavage des mains, les ustensiles et la prévention des contaminations entre aliments.

Distinguer les règles générales d’hygiène des recommandations spécifiquement destinées aux femmes enceintes.

### Limites

Ce premier passage ne couvrira pas l’ensemble de COR-06. Il ne permettra pas de dresser une liste exhaustive des aliments à éviter ni d’évaluer le risque après une consommation.

### Vérifications restantes

Lire les sections retenues dans leur contexte. Identifier la date ou la version du document. Rechercher une version plus récente. Vérifier les conditions de réutilisation applicables au document. Recouper les gestes retenus avec une source consacrée à la grossesse.

Aucun nouveau passage n’est encore intégré au corpus.

### Examen de l’article Anses

Titre : Conseils d’hygiène dans la cuisine : dix gestes simples pour prévenir les risques microbiologiques.

Date affichée : 24 décembre 2020.
Consultation : 4 novembre 2026.

https://www.anses.fr/fr/content/conseils-dhygiene-dans-la-cuisine

Les recommandations examinées portent sur :
* le lavage des mains à l’eau et au savon avant et pendant la préparation des repas ;
* l’utilisation de planches distinctes pour les viandes et poissons crus, et pour les produits cuits et légumes propres ;
* l’absence de réutilisation, pour les aliments cuits, des plats et ustensiles ayant transporté les aliments crus.

Ces règles sont générales. Elles ne constituent pas une liste exhaustive de précautions spécifiques à la grossesse.

### Recoupement

La page Ameli « Les aliments à éviter et les précautions d’hygiène pendant la grossesse », datée du 19 juin 2026, confirme plusieurs mesures de lavage, de nettoyage et de séparation des produits crus et prêts à consommer.

Ce recoupement ne constitue pas une autorisation de reproduire le texte Ameli.

### Conditions de réutilisation à clarifier

Les mentions légales Anses autorisent la réutilisation sous conditions d’attribution, de date et de respect du sens. Elles demandent également une reprise intégrale, sans modification ni ajout.

L’adaptation reformulée destinée au RAG n’est donc pas encore marquée comme approuvée. Aucun nouveau passage n’est activé.

La recherche réalisée n’a pas établi l’existence d’une version plus récente de cet article.

### Source retenue pour le premier passage

Organisme : Autorité européenne de sécurité des aliments (EFSA).
Titre : Manipulation appropriée des aliments.
Consultation : 4 novembre 2026.

https://www.efsa.europa.eu/fr/safe2eat/proper-food-handling

Sections examinées : Maintenir la propreté ; Séparer cru et cuit. Aucune date de publication ou de mise à jour n’est affichée dans le contenu consulté.

### Proposition de passage

Pour préparer les repas, les règles générales d’hygiène comprennent le lavage des mains avant de manipuler les aliments et pendant leur préparation, ainsi que le nettoyage et la désinfection des surfaces et du matériel utilisés.

Il faut séparer les viandes, volailles et fruits de mer crus des autres aliments, utiliser du matériel distinct pour les viandes crues et éviter les contacts entre aliments crus et préparés pendant leur conservation.

### Réutilisation

Les conditions EFSA autorisent la réutilisation avec attribution, sous réserve de conditions particulières propres aux documents. Aucune restriction particulière n’a été repérée pour les sections textuelles retenues. Aucun logo, visuel ou témoignage n’est repris.

https://www.efsa.europa.eu/en/legalnotice

### Portée et limites

Le passage concerne l’hygiène alimentaire générale. Les mesures retenues ont été recoupées avec les sources françaises examinées précédemment.

Il ne couvre ni une liste complète d’aliments à éviter pendant la grossesse, ni les températures de cuisson, ni les durées de conservation, ni l’évaluation d’une exposition individuelle.

Ce premier passage ne suffit pas à déclarer COR-06 entièrement couvert.

### Décision pour le premier passage

Le passage nutrition_hygiene_preparation est retenu pour les essais du prototype après examen du contenu EFSA, de ses conditions de réutilisation et du recoupement avec les sources françaises.

La phrase finale précise la limite éditoriale du passage. Aucune date de publication non affichée n’est inventée.

La réponse générée reste à évaluer. COR-06 reste en revue : ce passage couvre uniquement une partie du sujet.

### Essais de la question sans contexte de grossesse

Question : Quels gestes d’hygiène respecter pour préparer les repas ?

Trois tentatives retournent generation_non_autorisee avec le message hors périmètre. La génération documentaire n’est pas autorisée.

La question ne mentionne ni conception ni grossesse. Le classifieur reçoit uniquement cette question, sans le choix de corpus effectué dans l’interface.

Ces essais ne permettent pas d’évaluer la réponse documentaire. La question suivante précise le contexte de grossesse.

### Premier essai avec contexte de grossesse

Question : Pendant la grossesse, quels gestes généraux d’hygiène respecter pour préparer les repas ?

Statut : generation_interrompue.
Aucun texte partiel affiché. L’étape et la cause précise de l’interruption ne sont pas identifiées. La réponse documentaire n’est pas évaluable.

### Essais du premier passage d’hygiène alimentaire

La question initiale, sans mention de grossesse, a produit trois refus hors périmètre. Elle a été reformulée pour préciser ce contexte.

Question retenue : Pendant la grossesse, quels gestes généraux d’hygiène respecter pour préparer les repas ?

Deux tentatives ont été interrompues sans texte affiché. Un essai supplémentaire avec diagnostic a identifié l’étape generation_documentaire et le motif length, avec un plafond de 512 tokens.

Après passage du plafond à 1 024 tokens, un essai retourne references_controlees. La réponse reprend les gestes du passage nutrition_hygiene_preparation, sans information supplémentaire. La référence, l’organisme et le lien sont correctement affichés.

Verdict : réponse conforme pour cette exécution. La répétabilité reste à examiner. COR-06 demeure partiellement couvert.

### Essais complémentaires du premier passage

Question 1 : Pendant la grossesse, comment éviter les contacts entre aliments crus et préparés ?

Statut : references_controlees.
La réponse reprend la séparation des aliments, le matériel distinct et la prévention des contacts pendant la conservation. Elle cite nutrition_hygiene_preparation, sans ajout. Verdict : conforme pour cette exécution.

Question 2 : Pendant la grossesse, combien de jours peut-on conserver les restes au réfrigérateur ?

Statut : information_insuffisante.
Aucune durée de conservation n’est affichée. Verdict : conforme pour cette exécution.

Avec le plafond de 1 024 tokens, les trois essais examinés ont produit deux réponses documentaires conformes et une insuffisance conforme. Cela ne garantit pas leur répétabilité.

Le premier passage d’hygiène est vérifié sur ces cas. COR-06 reste partiellement couvert : les autres précautions alimentaires ne sont pas encore documentées dans le corpus.

### Deuxième passage : mise au froid et décongélation

Source : EFSA, Manipulation appropriée des aliments. Sections : Maintenir les aliments à des températures sûres ; Décongeler en toute sécurité.

https://www.efsa.europa.eu/fr/safe2eat/proper-food-handling

### Proposition de contenu

Les aliments cuits et périssables doivent être réfrigérés rapidement. Les aliments cuits ne doivent pas rester plus de deux heures à température ambiante. Pour décongeler des aliments surgelés, la méthode la plus sûre indiquée par l’EFSA est le réfrigérateur.

### Portée

Les deux heures constituent une limite d’attente à température ambiante, pas une durée de conservation au réfrigérateur ni une garantie qu’un aliment est sans risque.

Le passage ne fixe pas de nombre de jours de conservation des restes et ne permet pas de décider si un aliment particulier peut encore être consommé.

La recommandation de décongélation est recoupée avec la page Ameli consacrée aux précautions alimentaires pendant la grossesse.

### Réutilisation

Les conditions EFSA déjà examinées s’appliquent à ces sections. La source sera attribuée ; aucun logo ni visuel ne sera repris. Aucune date de publication non affichée ne sera inventée.

Le passage nutrition_mise_au_froid_decongelation est retenu pour les essais du prototype. Les précisions finales explicitent ses limites éditoriales. La réponse générée reste à évaluer. COR-06 demeure en revue, avec une couverture partielle.

### Essais du passage de mise au froid et décongélation

Question 1 : Pendant la grossesse, quels repères respecter pour mettre au froid et décongeler les aliments ?

Statut : references_controlees.
La réponse reprend la réfrigération rapide, la limite de deux heures à température ambiante et la décongélation au réfrigérateur. Chaque affirmation cite nutrition_mise_au_froid_decongelation. Aucune information supplémentaire n’est ajoutée.
Verdict : conforme pour cette exécution.

Question 2 : Pendant la grossesse, combien de jours peut-on conserver les restes au réfrigérateur ?

Statut : information_insuffisante. Aucun nombre de jours n’est affiché.
Verdict : conforme pour cette exécution.

Ces essais ne montrent pas de confusion entre délai avant réfrigération et durée de conservation des restes. Ils ne démontrent pas une fiabilité systématique. La reformulation de la première question reste à évaluer.

### Essai de reformulation sur la décongélation

Question : Pendant la grossesse, quelle méthode privilégier pour décongeler des aliments surgelés ?

Statut : references_controlees.
La réponse indique la décongélation au réfrigérateur et cite nutrition_mise_au_froid_decongelation, sans information supplémentaire.
Verdict : conforme pour cette exécution.

Bilan du deuxième passage : trois essais, comprenant une question principale, une question non couverte et une reformulation. Deux réponses documentaires et une insuffisance ont été jugées conformes. La répétabilité n’est pas établie.