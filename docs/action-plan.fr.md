# Plan d’action — Gramps Fancy Genealogical Book

Version de travail du 26 septembre 2026, suivi actualisé le 28 septembre 2026. Ce document organise le développement ; il ne remplace pas la spécification fonctionnelle.

## 1. Références et niveau de certitude

Le plan repose sur les discussions « Spécification plugin Gramps » et « Concevoir un livre généalogique », ainsi que sur l’inspection du dépôt au commit `ab42de1`.

Le fichier local [specification-v1.1.md](specification-v1.1.md) est une synthèse historique de démarrage. Le [texte intégral visible de la v1.1](reference/specification-v1.1.visible.txt) a depuis été récupéré via l’aperçu ChatGPT, avec sa [provenance](reference/README.md). Il comporte 18 sections et **27 scénarios AC-01 à AC-27**, malgré les 24 annoncés dans la discussion. La [matrice d’exigences](requirements.fr.md) les associe aux tâches ci-dessous. Le [Markdown original](reference/Gramps_Fancy_Genealogical_Book_Specification_v1.1.md) et les quatre maquettes ont été récupérés ensuite ; les maquettes restent locales, hors Git, car elles contiennent des données familiales réelles. Voir la [revue visuelle](reference/mockup-review.md).

Les éléments suivants sont confirmés par les échanges accessibles :

- Plugin pour Gramps 6, organisé autour d’une famille de référence.
- Architecture séparant intégration Gramps, extraction/normalisation, moteur généalogique, modèle éditorial et rendus LaTeX/PDF et HTML.
- Présentation familiale, ascendance par générations et descendance par branches comme base de conception retenue dans les échanges sur la maquette ; règles détaillées au § 4 de la v1.1.
- Repères permettant de situer la famille dans la généalogie, avec navigation utilisable sur papier et à l’écran.
- Événements de vie détaillés pour les individus concernés : professions, distinctions, service militaire et autres événements présents dans Gramps.
- Portraits et photographies des personnes et familles, avec annexes pour les illustrations complémentaires.
- Citations réutilisables par plusieurs faits ; annexes documentaires compactes associant citation, source, dépôt et médias justificatifs.
- URL affichées en clair ; reproduction limitée à la zone sélectionnée dans Gramps lorsqu’une région de média existe.
- Identifiants techniques anglais, notamment `BOOK_PUBLICATION`, `BOOK_PROFILE`, `BOOK_EXCLUDE` et `BOOK_FEATURED` ; interface traduisible et documentation française/anglaise.
- Publication des objets privés lorsque leur lecture est autorisée par Gramps, sans contournement des droits disponibles.
- Premier jalon limité à un plugin installable, une sélection de famille et un modèle intermédiaire testable, suivi d’une revue de la fondation.

Les règles précises de filiation, de profondeur, de sélection des fiches, de priorité entre métadonnées et de pagination sont relevées dans la matrice d’exigences. Les options techniques proposées ci-dessous restent révisables sur preuve issue des prototypes.

## 2. Point de départ (constat initial du 26 septembre)

| Élément | État constaté | Travail restant |
| --- | --- | --- |
| Git local | Branche `codex/initial-project`, commit initial enregistré | Organiser la branche de base et les prochaines revues |
| GitHub | URL `origin` configurée ; création et push non confirmés, authentification CLI en échec au dernier essai | Rétablir l’accès, créer le dépôt et publier les branches |
| Entrée Gramps | Enregistrement, options et rapport écrits | Vérifier chargement, installation, interface et CLI sur Gramps réel |
| Extraction | Parents et enfants d’une famille, noms et handles | Contrôler identifiants, références absentes, filiations et couverture des données |
| Modèle | `Person`, `Family`, `BookModel` et export JSON simples | Séparer données normalisées, parcours et structure éditoriale |
| Rendus | Fonctions HTML et LaTeX de démonstration | Construire les moteurs complets et leur échappement |
| Packaging | Archive `.addon.tgz` générée lors de l’initialisation | Vérifier installation, exhaustivité et reproductibilité |
| Qualité | Deux tests unitaires présents ; workflow pytest/Ruff/build écrit | Exécuter les contrôles, corriger leurs échecs et ajouter l’intégration Gramps |
| Documentation | README FR/EN, architecture et synthèse de spécification | Importer les références complètes et documenter progressivement chaque fonction |

La compilation Python et la construction de l’archive ont été réalisées précédemment. Elles ne prouvent ni la compatibilité Gramps ni la conformité fonctionnelle du plugin.

## 3. Ordre de réalisation

| Lot | Objectif | Dépendances | Preuve de fin |
| --- | --- | --- | --- |
| L0 | Consolider les exigences et le dépôt | Accès aux documents ; accès GitHub pour la publication | Référentiel traçable et dépôt distant prêt |
| L1 | Fiabiliser le plugin minimal | Peut avancer avec les échanges déjà disponibles | Installation Gramps et export JSON réellement démontrés |
| L2 | Valider les risques techniques et les contrats | L1 ; règles utiles de L0 | Prototypes Gramps Web/LaTeX/médias et décisions documentées |
| L3 | Extraire et normaliser les données utiles | L0, L1, contrats L2 | Jeu de données complet et indépendant de Gramps |
| L4 | Construire les parcours généalogiques | L3 ; règles exactes de L0 | Familles, branches et liens conformes aux cas d’acceptation |
| L5 | Assembler le livre et ses annexes | L4 ; contrats de médias/citations L2–L3 | Modèle éditorial complet et cohérent |
| L6 | Produire le livre LaTeX/PDF | L5 et prototype LaTeX L2 | PDF lisible, paginé et conforme aux références |
| L7 | Produire le livre HTML et son ZIP | Contrats L5 stabilisés | Livre consultable localement avec navigation et médias |
| L8 | Qualifier et distribuer la version initiale | L6, L7 ; décision Gramps Web L2 | Recette complète et distribution documentée |

Chemin principal : L0/L1 → L2 → L3 → L4 → L5 → L6/L7 → L8. L0 et L1 peuvent avancer conjointement. Les deux rendus peuvent être développés indépendamment une fois le modèle éditorial stabilisé. La documentation et les contrôles accompagnent chaque lot.

**Suivi au 28 septembre 2026 :** les premiers incréments d’extraction L3 et les corrections de revue sont fusionnés. L4 se poursuit avec le parcours borné des filiations, les sections familiales contextuelles, les occurrences par génération et les liens parent-enfant qui conservent leurs types. La sortie de L4 reste conditionnée à la qualification des scénarios AC-01, AC-03 à AC-09 et à l’intégration du modèle dans les rendus.

## 4. Lots détaillés

### L0 — Référentiel de conception et gestion du projet

**Actions**

1. L0.1 — Importer `Gramps_Fancy_Genealogical_Book_Specification_v1.1.md` et les deux maquettes dans un répertoire de références, en conservant leur version et leur provenance.
2. L0.2 — Distinguer clairement la synthèse locale du document intégral ; relever les écarts entre code, synthèse et spécification.
3. L0.3 — Construire une matrice « exigence → section source → tâche → scénario → résultat ». Maintenir AC-01 à AC-27 avec leurs identifiants d’origine.
4. L0.4 — Consigner les décisions déjà prises et les seules ambiguïtés restantes. Toute nouvelle proposition indique sa justification et les fonctions affectées.
5. L0.5 — Rétablir l’authentification GitHub, créer le dépôt avec la visibilité retenue, publier une branche de base et conserver le travail de fondation sur une branche de revue.
6. L0.6 — Clarifier la licence de distribution, déjà déclarée GPL dans les métadonnées mais dépourvue de fichier de licence dans le squelette ; compléter les fichiers correspondants une fois le choix confirmé.

**Livrables :** références versionnées, matrice d’exigences, registre de décisions, backlog ordonné et dépôt GitHub.

**Critère de sortie :** chaque exigence identifiée a une source et une tâche ; chaque scénario d’origine est référencé. Les documents manquants restent explicitement signalés tant qu’ils ne sont pas importés.

### L1 — Premier jalon : plugin minimal démontré

**Actions**

1. L1.1 — Préparer un environnement Gramps 6 reproductible et une petite base fictive ; relever les versions réellement utilisées.
2. L1.2 — Installer l’archive, charger le rapport et vérifier sa découverte, ses options et ses traductions de base.
3. L1.3 — Vérifier le contrat de `FamilyOption`, la conversion entre identifiant Gramps et handle interne et la sélection de familles incomplètes.
4. L1.4 — Sécuriser le cycle du rapport : choix du fichier, export JSON, finalisation du document et messages d’erreur. Examiner notamment la sélection vide, actuellement lue avant le bloc de gestion des erreurs.
5. L1.5 — Préciser le comportement lorsqu’une référence de personne est absente : ne pas supprimer silencieusement une relation sans diagnostic.
6. L1.6 — Exécuter les tests et Ruff ; adapter les contrôles aux noms injectés par Gramps dans les fichiers `.gpr.py`, sans neutraliser globalement les vérifications.
7. L1.7 — Ajouter des tests ciblés sur l’adaptateur et sur les échecs du rapport ; vérifier l’archive installée, les imports et l’absence de dépendance au checkout de développement.
8. L1.8 — Documenter en français et en anglais une procédure d’installation et un exemple reproductible d’export.

**Critères de sortie :** à partir d’une installation propre, une famille fictive choisie produit un JSON lisible contenant les membres attendus, en interface graphique et en CLI. Une sélection invalide et une destination non accessible produisent un diagnostic compréhensible. La CI passe sur le périmètre annoncé.

**Revue du jalon :** présenter l’architecture, l’archive et un export réel avant d’engager le moteur généalogique et les rendus complets.

### L2 — Prototypes techniques et contrats

**Actions**

1. L2.1 — Formaliser les contrats entre extraction, parcours, livre et rendus : identifiants, ordre déterministe, champs optionnels, diagnostics et version du JSON.
2. L2.2 — Définir les références stables du livre. Distinguer identifiant interne, identifiant Gramps, identifiant de publication et numéro de page ; un changement de pagination ne doit pas casser un lien.
3. L2.3 — Réaliser un prototype de 15–30 pages sous LuaLaTeX, hypothèse initiale : accents, noms longs, notes de bas de page selon les règles du texte intégral, références de pages et URL longues. Choisir le moteur et les dépendances après ce prototype.
4. L2.4 — Réaliser un prototype de média : chargement de l’original, lecture du rectangle Gramps, recadrage et génération d’un dérivé. Définir le traitement des coordonnées invalides et des fichiers absents.
5. L2.5 — Vérifier sur une instance de développement Gramps Web le chargement du rapport, les options disponibles, les accès aux médias, l’exécution sans interface graphique et la récupération du résultat.
6. L2.6 — Définir la gestion de compilation : répertoire temporaire, arguments explicites, délai maximal, journal exploitable et restitution des erreurs. Les textes généalogiques doivent être traités comme des données dans les rendus.

**Livrables :** prototypes courts, contrats documentés et décisions techniques motivées.

**Critère de sortie :** les points risqués ont une preuve de faisabilité ou une limitation précise accompagnée d’une proposition d’adaptation. La compatibilité Gramps Web ne sera annoncée que pour le périmètre effectivement vérifié.

### L3 — Extraction et normalisation

**Actions**

1. L3.1 — Modéliser personnes, familles, unions, filiations et références croisées en conservant les informations nécessaires aux décisions éditoriales.
2. L3.2 — Extraire événements, rôles, dates, lieux et descriptions. Préserver l’incertitude des dates et les différences entre événements individuels et familiaux.
3. L3.3 — Extraire notes, attributs et étiquettes ; établir les valeurs, portées et priorités exactes de `BOOK_*` d’après la spécification complète.
4. L3.4 — Extraire citations, sources et dépôts avec leurs identifiants distincts. Deux citations différentes d’une même source ne deviennent pas automatiquement un seul justificatif.
5. L3.5 — Extraire médias et références de médias : chemin, légende, ordre et région de recadrage. Prévoir plusieurs régions d’un même fichier selon la citation.
6. L3.6 — Préserver les droits réellement exposés par la base transmise au rapport ; définir explicitement les objets lisibles mais privés et les objets inaccessibles conformément à la spécification.
7. L3.7 — Mettre en place des diagnostics structurés et un accès évitant les lectures répétées des mêmes objets.

**Critères de sortie :** un jeu fictif riche est extrait sans modification de la base ; les relations et leurs justificatifs restent traçables. Les cas incomplets donnent un modèle exploitable et des diagnostics. Le moteur métier n’a pas besoin d’importer Gramps.

### L4 — Parcours généalogiques et sélection

**Actions**

1. L4.1 — Traduire les règles de périmètre : personnes centrales, ascendances retenues, descendances, unions et niveaux de profondeur.
2. L4.2 — Construire l’ascendance par générations avec les deux côtés du couple et les chemins de retour vers la famille centrale.
3. L4.3 — Construire la descendance par branches, avec les unions et enfants concernés selon les règles validées.
4. L4.4 — Traiter les unions multiples, parents inconnus, types de filiation, ancêtres communs, croisements de branches et cycles accidentels sans imposer une règle absente de la spécification.
5. L4.5 — Distinguer l’identité d’une personne de ses apparitions dans plusieurs contextes ; appliquer les règles de fiches détaillées, mentions et renvois.
6. L4.6 — Définir l’ordre stable des familles et des enfants conformément aux données et au cahier des charges.
7. L4.7 — Produire les liens vers parents, unions et enfants ainsi que les informations nécessaires au repère généalogique de chaque fiche.

**Critères de sortie :** les jeux de référence produisent les familles et chemins attendus, sans boucle infinie ni omission involontaire. Les répétitions de contexte sont distinguées des doublons de données. Les tags influencent la sélection selon une règle documentée.

### L5 — Modèle éditorial, citations et médias

**Actions**

1. L5.1 — Assembler les parties du livre : couverture, préliminaires, sommaire, ascendance commençant par F0, descendance, annexe documentaire unique et index des personnes.
2. L5.2 — Définir les fiches familiales et notices, les événements de vie, les portraits, les légendes et les renvois. Prévoir qu’une fiche occupe plusieurs pages.
3. L5.3 — Attribuer une cible unique à chaque citation publiée et permettre plusieurs appels depuis les faits et personnes qui l’utilisent.
4. L5.4 — Composer une notice documentaire compacte : dépôt réellement lié à la source, source, détail de citation, URL complète et médias utiles. Ne pas y répéter la liste des faits justifiés.
5. L5.5 — Préparer les images dérivées à partir des originaux, appliquer les régions de référence et conserver l’association entre extrait et citation. Le cache doit tenir compte du fichier et du rectangle. Pour les justificatifs PDF, proposer le lien de citation lorsqu’il existe, garder les documents multipages comme références et ne reproduire un document monopage sans URL qu’après rastérisation sûre.
6. L5.6 — Modéliser les cibles de navigation et les index avant pagination ; vérifier que toute référence pointe vers une section existante ou porte une indication explicite de hors périmètre.

7. L5.7 — Produire séparément le rapport de contradictions de dates/lieux pour un même fait, sans avertissement dans le livre ni audit généalogique général (AC-19).

**Critères de sortie :** le même modèle alimente les deux rendus ; aucune décision de sélection généalogique n’est recalculée dans un moteur de rendu. Une citation commune à plusieurs faits n’apparaît qu’une fois dans l’annexe, avec tous ses appels résolus. Les originaux restent intacts.

### L6 — Livre LaTeX et PDF

**Actions**

1. L6.1 — Établir les gabarits à partir des deux maquettes importées : format A4, typographie, marges, fiches, portraits, tableaux et annexes ; distinguer inspirations visuelles et règles obligatoires.
2. L6.2 — Échapper les caractères LaTeX des noms, notes, légendes, chemins et URL ; définir les éléments de mise en forme des notes effectivement pris en charge.
3. L6.3 — Gérer les coupures : familles nombreuses, événements longs, fiches sur plusieurs pages, continuité des repères et lisibilité des actes recadrés.
4. L6.4 — Générer les renvois cliquables et les références de pages pour l’impression, puis résoudre les références par les passes de compilation nécessaires.
5. L6.5 — Intégrer sommaire, index et annexes selon la spécification. Afficher les URL intégrales avec des coupures de ligne utilisables.
6. L6.6 — Comparer visuellement les sorties sur une famille peu documentée et une famille riche en événements, portraits et justificatifs.

**Critères de sortie :** PDF compilé sans référence non résolue, sans contenu tronqué et sans débordement affectant la lecture sur les jeux de recette. Les repères restent compréhensibles sur les pages de continuation. Les documents justificatifs et URL sont utilisables à l’impression.

### L7 — Livre HTML et archive autonome

**Actions**

1. L7.1 — Rendre les mêmes parties et notices depuis le modèle commun, avec des ancres stables pour personnes, familles et citations.
2. L7.2 — Adapter le repère généalogique au navigateur et proposer une navigation cohérente entre générations, branches, fiches et annexes.
3. L7.3 — Échapper le contenu inséré dans HTML et traiter les liens et notes selon un contrat de mise en forme explicite.
4. L7.4 — Inclure les médias et styles dans un ZIP à chemins relatifs, consultable localement ; vérifier les noms de fichiers accentués et les liens entre pages.
5. L7.5 — Vérifier lisibilité sur plusieurs tailles d’écran, navigation clavier et textes alternatifs des images.

**Critères de sortie :** après extraction du ZIP, les pages, styles et images fonctionnent localement ; tous les liens internes attendus sont valides. Les données et citations publiées correspondent au PDF, avec les adaptations de navigation propres au support.

### L8 — Recette, documentation et distribution

**Actions**

1. L8.1 — Exécuter les 27 scénarios originaux, complétés par les cas techniques nécessaires ; lier chaque résultat à une version du plugin et de l’environnement.
2. L8.2 — Qualifier les versions Gramps, Python et moteurs documentaires retenues sur la base des essais, puis aligner la CI et la documentation sur cette matrice.
3. L8.3 — Mesurer temps de génération, mémoire et taille des sorties sur de petits, moyens et grands jeux fictifs. Fixer les seuils acceptables après une première mesure représentative.
4. L8.4 — Compléter les guides FR/EN : installation, dépendances LaTeX, configuration, `BOOK_*`, formats de sortie, dépannage, architecture et contribution. Compléter les traductions de l’interface.
5. L8.5 — Fiabiliser la fabrication des archives, versionner de façon cohérente package/enregistrement/listings et vérifier installation, mise à jour et retrait du module complémentaire.
6. L8.6 — Préparer une version candidate avec exemples fictifs, notes de version et limitations connues ; réaliser la revue avant publication de la version stable.

**Critères de sortie :** tous les critères obligatoires de la spécification sont satisfaits ou font l’objet d’un changement de périmètre explicitement accepté. La distribution est installable depuis ses propres artefacts et les guides permettent de reproduire une génération complète.

## 5. Couverture fonctionnelle et contrôles proposés

Cette vue thématique est complétée par la correspondance AC-01 à AC-27 dans [requirements.fr.md](requirements.fr.md).

| Besoin | Lots | Contrôle principal |
| --- | --- | --- |
| Famille centrale et export intermédiaire | L1–L3 | Installation réelle, GUI/CLI, identifiants et JSON |
| Ascendants et descendants | L4 | Jeux avec générations, branches, unions multiples et ancêtres communs |
| Sélection des fiches et `BOOK_*` | L3–L5 | Règles et priorités extraites de la spécification |
| Événements de vie | L3, L5–L7 | Données rares/riches, dates partielles, événements partagés |
| Repères et navigation | L4–L7 | Parcours papier, cibles HTML/PDF, fiches sur plusieurs pages |
| Citations réutilisées | L3, L5–L7 | Plusieurs faits → une citation ; une source → plusieurs citations distinctes |
| Annexes compactes et URL intégrales | L5–L7 | Présence des références, absence de répétition des faits, URL longues |
| Portraits et extraits d’actes | L2–L3, L5–L7 | Plusieurs rectangles d’une image, média absent, dimensions extrêmes |
| Droits et objets privés | L2–L3, L8 | Base autorisée, objet inaccessible, objets privés lisibles |
| Documentation bilingue | Tous | Parité des fonctions documentées et procédures reproductibles |
| Gramps Web | L2, L8 | Exécution réelle sans GUI et téléchargement du résultat |

Les données de test seront fictives et versionnées. Les comparaisons de JSON porteront sur l’identité, les relations et l’ordre attendu ; les comparaisons PDF porteront aussi sur le rendu visuel et les liens. Les tests unitaires ne remplaceront pas l’installation réelle du paquet.

## 6. Décisions et prototypes restant à mener

Les règles fonctionnelles sont établies par la v1.1 et résumées dans la matrice. Les points T-01 à T-10 du § 17 restent à résoudre par essais : sorties personnalisées Desktop/Web ; six notes éditoriales F0 ; dates et tri stable ; rôles et filiations « aucun » ; médias et PDF ; Markdown et notes riches ; lisibilité A4 ; convergence pagination/index ; matrice des environnements ; export LaTeX futur facultatif.

Gramps Web est requis pour la version cible, avec preuve d’intégration avant annonce. LuaLaTeX est l’hypothèse technique de départ. La licence et le passage éventuel du dépôt privé au public doivent être fixés avant distribution. Le traitement des régions de médias mentionné dans la discussion reste à rapprocher de la déduplication prescrite par la v1.1.

## 7. Découpage de travail et suivi

Chaque tâche `Lx.y` peut devenir une issue GitHub contenant son besoin, ses dépendances, ses livrables et ses critères de validation. Les changements passent par des branches `codex/...` et des commits conventionnels. Une revue porte sur un résultat démontrable et indique les exigences couvertes, les contrôles exécutés et les limites restantes.

Les statuts de suivi seront : à préparer, prêt, en cours, à revoir, validé ou bloqué avec cause. Le statut « validé » nécessite la preuve prévue dans le lot. Une archive construite ou une CI écrite ne suffisent pas à déclarer une intégration validée.

Les estimations calendaires seront établies après L0 et L1 : le détail des 27 scénarios et les contraintes constatées dans Gramps peuvent modifier sensiblement la charge. Le périmètre des futurs rendus ne doit pas être chiffré à partir des seuls exemples actuels.

## 8. Suivi d’exécution — 27 septembre 2026

- Dépôt privé créé : [grostim/gramps-fancy-genealogical-book](https://github.com/grostim/gramps-fancy-genealogical-book). Branches `main` et `codex/initial-project` publiées. L’accès GitHub fonctionne via le trousseau macOS ; le précédent échec était lié au sandbox.
- L0 en cours : [matrice des 27 scénarios](requirements.fr.md) établie et texte intégral récupéré ; originaux récupérés et maquettes consultées ; licence de distribution restant à confirmer.
- L1 fusionné et validé : archive installée dans un profil isolé, famille fictive exportée et cas d’erreur contrôlés dans Gramps 6.0.8 réel ; CI réussie. Voir le [compte rendu de validation](validation-l1.fr.md).
- L2 fusionné pour les contrats et les prototypes médias/Web. La compilation LuaLaTeX et une recette sur Gramps Web restent à prouver ; voir [contrats de données](decisions/001-data-contracts.md), [revue de fondation](decisions/002-foundation-review.md) et [obstacles Gramps Web](../prototypes/web-spike.md).
- L3 : premier incrément du schéma v0.2 fusionné ; les commentaires de revue sur dates, attributs et références de dépôts ont été traités dans une PR de suivi fusionnée. Les tags éditoriaux et rectangles de recadrage restent à éprouver avec de vrais objets Gramps.
- L4 en cours : modèle JSON v0.7, extraction bornée de l’ascendance et de la descendance, occurrences par génération, ordre déterministe des sections familiales, identifiants de section, liens typés entre occurrences partenaires/enfants et cible de première apparition pour chaque personne, avec ou sans fiche. La qualification des cas d’acceptation et la consommation du modèle par les rendus restent à réaliser.
- L5 commencé : structure éditoriale ordonnée des grandes parties, reliée aux sections familiales et aux premières occurrences ; les fiches éligibles référencent leurs notes publiables, portrait légendé, événements et médias. Le modèle ajoute une notice unique par famille, reliée à sa section principale, à ses autres contextes et à ses références de notes, événements et médias. Les deux portraits de couverture sont reliés s’ils existent. La sélection utilise pour l’instant la première image Gramps non exclue, avec la description du média comme légende ; sa confirmation sur la version prise en charge reste à faire. Les événements de fiche et de famille sont classés selon la valeur de tri Gramps, les événements sans date venant à la fin ; les plages approximatives ou chevauchantes restent à qualifier (T‑03). Le modèle L5.3 regroupe les appels sous une entrée unique par citation et conserve leurs contextes et champs d’origine. L5.4 relie chaque entrée à la citation, à la source de cette citation, aux dépôts liés à cette source et aux médias résolus non exclus rattachés à la citation ; la composition de la notice reste à faire. L5.5 déduplique les emplacements par identité média tout en gardant les références, rectangles et citations associés. Les utilitaires image lisent les chemins locaux Gramps, appliquent l’orientation EXIF, recadrent en PNG sans perte et calculent une clé versionnée. Pour les PDF, ils privilégient l’URL de citation, laissent les documents multipages en référence et rastérisent les documents monopages sans URL à 300 ppp, dans la limite d’un plafond de pixels. Le rapport prépare les dérivés distincts, écrit les PNG dans un dossier compagnon du JSON et expose leur manifeste ; les erreurs de conversion figurent dans les diagnostics structurés. L’installation des dépendances facultatives et la consommation des médias par les rendus finaux restent à faire. La numérotation selon le premier emploi dans le livre composé et les notes de bas de page restent à réaliser.
- PR #12 fusionnée : aucun commentaire de revue en attente et les matrices de tests Python passent. Les deux jobs d’intégration Gramps restent rouges à cause du vérificateur qui attend le schéma `0.3`, alors que `main` annonce `0.7` ; cette assertion n’a pas été changée dans ce lot.
- PR #13 fusionnée : une entrée par citation et ses appels éditoriaux sont maintenant modélisés ; aucun commentaire de revue n’était en attente. Les matrices Python passent ; l’intégration Gramps échoue toujours sur la même assertion de version `0.3` périmée.
- PR #14 fusionnée : les entrées de citation renvoient à leur Source, aux dépôts effectivement liés à cette source et aux médias non exclus qui sont associés à la citation. Aucun commentaire de revue en attente ; les matrices Python passent et l’intégration échoue toujours sur l’assertion `0.3` périmée.
- PR #15 fusionnée : le modèle déduplique les placements selon l’identité Gramps en conservant les références et régions. Aucun commentaire de revue en attente ; les matrices Python passent, tandis que l’intégration échoue sur la même assertion `0.3` périmée.
- PR #16 fusionnée : bornes pixel couvrantes et identité de cache calculée depuis le contenu, la région et la politique de conversion. Aucun commentaire de revue ; pytest et Ruff passent sous Python 3.10 à 3.13, l’intégration Gramps reste arrêtée sur l’assertion `0.3` périmée.
- PR #17 fusionnée : lecture des médias locaux selon le répertoire Gramps, orientation EXIF, recadrage raster PNG et identité de cache versionnée. Aucun commentaire de revue ; la matrice Python passe sous 3.10 à 3.13 ; l’intégration Gramps échoue encore sur l’assertion de schéma `0.3` périmée.
- L5.5 livré dans la PR #20 fusionnée : le rapport Gramps appelle les utilitaires média, écrit les PNG dérivés dans `<nom>_media/` et consigne action, chemin, dimensions, région, citation et contexte dans `media_artifacts`. Les échecs sont des diagnostics récupérables ; le modèle JSON reste exportable. Une URL externe HTTP(S) évite la lecture d’un PDF ; sans URL, un PDF multipage reste une référence et un monopage est rasterisé à 300 ppp. Aucun commentaire n’était en attente ; les matrices pytest/Ruff et la construction passent, l’intégration Gramps restant bloquée par l’assertion périmée du vérificateur (`0.3` au lieu du schéma `0.7`). Pillow/PDFium restent facultatifs et leur installation dans les environnements Gramps n’est pas automatisée.
- L5.6 livré dans la PR #21 fusionnée : cibles d’ancrage stables avant pagination et index alphabétique des personnes, leurs occurrences et leurs variantes de nom ; chaque renvoi éditorial est associé à une cible disponible ou marquée hors périmètre. Aucun commentaire en attente ; pytest/Ruff et la construction passent sous Python 3.10 à 3.13 ; le vérificateur Gramps échoue sur son assertion de schéma `0.3` périmée.
- L5.7 à cadrer : les objets `Event` extraits ont une seule date et un seul lieu, et le modèle ne contient aucun lien explicite permettant de grouper deux événements distincts comme versions du même fait. Conformément au § 12.1, le rapport ne doit pas fusionner ces événements par heuristique ; la règle de groupement est à décider avant l’implémentation.
- L6.2 en cours : le rendu LaTeX affiche l’ascendance et la descendance par génération, les fiches éligibles avec événements et notes publiables en texte échappé, ainsi que l’index alphabétique relié aux cibles disponibles. La mise en forme riche des notes, portraits/légendes, familles, annexes de citations et compilation restent à faire ; le compilateur intégré ne peut pas récupérer son bundle Tectonic hors ligne dans cet environnement.
- Contrôle graphique macOS effectué : sélection F0001, export JSON, options conservées et refus de remplacement validés. AC-22 complet reste à réaliser sur les environnements cibles.

### Prochaines actions

1. Définir le lien explicite qui permet de reconnaître plusieurs versions d’un même fait pour L5.7 ; garder toute fusion heuristique d’événements distincts désactivée.
2. Compléter la fixture native Gramps pour éprouver `BOOK_PUBLICATION`, `BOOK_PROFILE` et les rectangles médias avec de vrais objets Gramps ; confirmer ces changements par la CI après publication de la branche.
3. Poursuivre L4 en qualifiant AC-03 à AC-09 : autres unions, filiations multiples, implexes, collatéraux, familles monoparentales et frontières de profondeur selon la v1.1.
4. En parallèle, fournir un environnement LuaLaTeX reproductible, appliquer les helpers d’échappement au modèle et compiler le prototype jusqu’à stabilisation des renvois.
5. Automatiser l’installation de Pillow/PDFium dans les environnements Gramps Desktop/Web effectivement pris en charge ; qualifier le remplacement des artefacts et l’accès aux médias sur ces environnements.
