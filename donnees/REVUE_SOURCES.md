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