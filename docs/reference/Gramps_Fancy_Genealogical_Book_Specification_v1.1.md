# Gramps Fancy Genealogical Book

**Spécification fonctionnelle et technique — projet v1.1**  
**Date :** 25 septembre 2026  
**Statut :** base de travail consolidée, à valider par prototype technique avant implémentation complète  
**Langue de rédaction de cette version :** français ; documentation du projet requise en français et en anglais

> Ce document consolide les décisions prises avec le commanditaire lors des onze séries de questions relatives au livre généalogique et des échanges ultérieurs sur LaTeX, GitHub et l'architecture. Les formulations marquées **[V]** sont des exigences fonctionnelles validées ; **[P]** indique une solution technique proposée ; **[T]** un point devant être vérifié par prototype ou intégration. Les choix [P] et [T] ne doivent pas être présentés comme des capacités déjà démontrées. La spécification est autonome ; le développement n'est pas commencé et aucun dépôt nouveau n'a été créé.

## 1. Objet, principes et limites

### 1.1 Finalité

[V] Développer un **plugin de rapport Gramps 6 et versions ultérieures effectivement prises en charge**, utilisable dans Gramps Desktop (Windows, macOS, Linux) et Gramps Web, capable de générer automatiquement, à partir d'une famille/couple de référence, un livre généalogique au format **PDF A4** ou un livre **HTML statique distribué en ZIP**. L'ouvrage couvre l'ascendance des deux membres du couple, leur descendance au sens défini plus loin, les familles, les événements, les notes publiables, les médias, les citations, les sources et les annexes.

[V] L'ouvrage peut être régénéré intégralement à tout moment. La base Gramps reste l'unique source du contenu généalogique et des choix éditoriaux individuels. Aucune retouche manuelle du document généré ne doit être nécessaire. Les paramètres de génération (famille, profondeurs, langue, format, destination) sont locaux à chaque installation du plugin et mémorisés indépendamment sur Desktop et Web.

[V] Le plugin est générique : il ne contient ni noms de familles codés en dur, ni hypothèse selon laquelle les personnes de référence sont toujours les mêmes. Le livre comprend toutes les informations sélectionnées, y compris celles concernant les personnes vivantes ou marquées privées dans Gramps ; le comportement doit être annoncé explicitement au lancement d'une génération susceptible d'être diffusée.

[V] Les solutions « application web indépendante », « exporteur et générateur dans trois dépôts » et « compilation du livre uniquement par GitHub Actions » ne font **pas** partie de l'architecture retenue. Le code du plugin, lui, doit être développé et versionné dans un dépôt GitHub distinct, avec tests et distribution automatisés. Le dépôt Git privé du livre et la compilation GitHub Actions des sources LaTeX sont une **fonctionnalité optionnelle future**, non bloquante pour la première version.

### 1.2 Ce que le plugin ne fait pas

[V] Il ne corrige pas la base Gramps, ne déduit pas de filiations, ne sélectionne pas une vérité parmi des faits contradictoires, ne rédige pas de biographie fictive, n'effectue pas de traduction automatique des notes, ne crée pas d'arbre graphique supplémentaire et n'impose pas de recherche plein texte dans le livre HTML. Il ne traite pas les informations non sourcées comme des erreurs. Il ne publie pas automatiquement sur un dépôt Git le livre ou ses données.

### 1.3 Priorités de conception

[V] (1) exactitude et traçabilité des données ; (2) couverture généalogique complète dans le périmètre retenu ; (3) génération sans intervention manuelle ; (4) lisibilité à l'impression **noir et blanc** ; (5) compacité et stabilité des renvois ; (6) compatibilité Desktop/Web ; (7) maintenabilité et qualité de la distribution.

### 1.4 Maquettes de référence à transmettre aux développeurs

[V] Les deux maquettes produites pendant la conception du projet doivent être **remises explicitement à toute personne ou agent chargé de l'implémentation** et consultées avant de figer les modèles LaTeX/HTML :

1. **Maquette structurelle du livret familial** : `maquette_structure_livret_familial.pdf` et `maquette_structure_livret_familial.html` (format A4, présentation du couple central, ascendances, descendance, repères et navigation).
2. **Maquette « événements et sources »** : `maquette_livret_familial_evenements_sources.pdf` et `maquette_livret_familial_evenements_sources.html` (fiches, événements, notes, références documentaires et annexes).

[P] Les maquettes sont des **références d'inspiration visuelle et structurelle**, non une source de vérité sur les données, ni des gabarits à reproduire pixel par pixel. Les décisions fonctionnelles les plus récentes de cette spécification prévalent en cas d'écart (notamment notes de bas de page, déduplication des événements familiaux, mise en page compacte, photos importantes pleine page et choix des identifiants). Les exemples nominaux, portraits et données des maquettes ne doivent **pas** être intégrés par défaut dans un dépôt GitHub public ; utiliser des données synthétiques ou une version anonymisée autorisée pour les exemples et tests publics.

[P] Prévoir dans le dossier de transmission au développeur un sous-dossier `reference_maquette/` contenant ces quatre fichiers, ou leurs liens de consultation vérifiés. Dans un dépôt public, mentionner les maquettes dans le cahier des charges sans y inclure de données familiales réelles par défaut.

### 1.5 Bilinguisme de la documentation et conventions internationales

[V] Toute la documentation livrée avec le plugin est maintenue **en français et en anglais**, avec un contenu fonctionnel équivalent : README/présentation, installation et configuration Desktop/Web, manuel utilisateur, options du rapport, conventions de métadonnées `BOOK_*`, dépendances et dépannage, architecture et guide de contribution. Les changements fonctionnels doivent mettre à jour les deux langues dans la même modification ; l'intégration continue vérifie la présence et la cohérence structurelle des deux versions. Les messages et libellés affichés dans l'interface sont internationalisables et traduits au minimum en français et en anglais. Cette exigence documentaire ne signifie pas que le contenu généalogique saisi par l'utilisateur doit être traduit automatiquement.

[V] Les noms de variables, fonctions, classes, modules, constantes, paramètres et fichiers techniques du plugin sont **en anglais** : `snake_case` pour variables/fonctions/modules, `PascalCase` pour classes et `UPPER_SNAKE_CASE` pour constantes. Les identifiants de métadonnées présents dans Gramps sont également des chaînes techniques internationales, **indépendantes de la langue de l'interface ou du livre**, et commencent par `BOOK_`. Ne pas employer d’identifiants techniques traduits ni traduire les étiquettes enregistrées en base ; seuls leurs libellés d'aide sont localisés.

[V] Conventions retenues : note publiable `BOOK_PUBLICATION` ; attribut individuel `BOOK_PROFILE = YES` ; média exclu `BOOK_EXCLUDE` ; média mis en valeur `BOOK_FEATURED`. Pour les six rôles éditoriaux de notes de la famille centrale, les noms techniques **proposés** sont `BOOK_TITLE`, `BOOK_SUBTITLE`, `BOOK_INTRODUCTION`, `BOOK_DEDICATION`, `BOOK_AUTHOR` et `BOOK_PUBLICATION_DATE` : leur mécanisme de rattachement précis reste à tester sur Gramps 6. [P] Définir dans un module unique les constantes `BOOK_*` et les règles de lecture des valeurs ; ne pas dupliquer ces chaînes entre extraction, moteur, rendus et tests.

## 2. Vocabulaire et conventions

- **Famille centrale F0** : objet Famille Gramps sélectionné par l'utilisateur, dont les deux partenaires connus définissent le couple de référence, notés P0 et P1. La famille F0 reste identifiable par son handle Gramps et son identifiant public s'il existe.
- **Personne de la lignée** : personne rencontrée dans un parcours ascendant ou descendant selon les liens parent–enfant explicitement enregistrés.
- **Personne annexe** : conjoint/partenaire d'une personne de la lignée, ou frère/sœur d'un ancêtre, inclus pour documenter le contexte sans ouvrir automatiquement toute sa propre ascendance/descendance.
- **Occurrence** : représentation d'un même objet à un endroit du livre (mention, fiche, renvoi) ; une personne peut avoir plusieurs occurrences mais une seule fiche complète.
- **Fiche** : notice individuelle développée, distincte d'une mention synthétique dans une fratrie, une liste ou une famille.
- **Citation** : objet Citation Gramps ; **source** : objet Source Gramps ; **dépôt** : objet Repository/Dépôt et ses références de dépôt. Ne pas confondre la citation avec le document média qu'elle peut justifier.
- **Média** : objet média Gramps et, selon le contexte, une association/référence vers cet objet. Un même fichier peut être associé à plusieurs objets.
- **Référence interne** : ancre stable, construite à partir du type d'objet et du handle interne ou d'un identifiant normalisé, indépendamment du numéro de page ou du numéro éditorial d'une citation.

[P] Ne pas supposer que les identifiants publics `I…`, `F…`, `C…` ne changent jamais : les handles servent de clés techniques au sein d'une base et les identifiants publics sont restitués lorsqu'ils sont disponibles, sans prétention à une stabilité absolue après import ou fusion de bases.

## 3. Interface, lancement et options

### 3.1 Point d'entrée

[V] Le plugin est accessible depuis les **rapports Gramps**. Dans Gramps Desktop, une fenêtre native de configuration permet de sélectionner F0, les paramètres et la destination de sortie. Depuis Gramps Web, le rapport doit être visible parmi les rapports installés sur le serveur, paramétrable et téléchargeable depuis le navigateur. [T] La représentation exacte des paramètres personnalisés, le retour de progression et le téléchargement d'une archive ZIP doivent être éprouvés sur la version Web ciblée : le seul fait qu'un rapport soit visible n'en démontre pas toutes les fonctions.

### 3.2 Paramètres requis

| Paramètre | Valeur par défaut | Règle |
|---|---|---|
| Famille de référence | Dernière famille valide utilisée localement | Sélection dans les familles Gramps ; l'objet doit exister au lancement. |
| Ascendance maximale | Toutes les générations accessibles | Entier ≥ 0 ou « illimité » ; réglage indépendant de celui de descendance. |
| Descendance maximale | Toutes les générations accessibles | Entier ≥ 0 ou « illimité » ; le couple est la génération 0. |
| Langue du livre | Langue configurée dans Gramps pour le contexte de génération | Dérogation manuelle ; repli déterministe lorsque la langue n'est pas traduite. |
| Format de sortie | Valeur mémorisée localement | Choix exclusif au lancement : PDF ou HTML (ZIP). |
| Destination | Dernière destination locale appropriée | Nom de fichier et emplacement choisis avant génération ou selon l'interface Web. |

[V] Il ne faut pas ajouter d'options personnalisant l'ordre des branches, familles ou personnes. [P] Les choix de thème, d'interprétation généalogique ou d'inclusion des informations privées ne sont pas des paramètres à ajouter en v1 : leurs règles sont figées dans la présente spécification.

### 3.3 Préparation et exécution

[V] Afficher une progression par grandes étapes et un journal technique détaillé, accessibles selon les possibilités de Desktop/Web. Distinction stricte entre annulation utilisateur, erreur bloquante et anomalie non bloquante. Les fichiers partiels ne remplacent jamais un livrable précédent valide. [P] Produire le résultat dans un répertoire temporaire propre à l'exécution, valider le résultat, puis effectuer la mise à disposition finale de façon atomique lorsque le système le permet. Le dossier de travail est supprimé après réussite sauf mode de diagnostic explicite ; les fichiers nécessaires à la compilation LaTeX peuvent être exportés séparément dans la perspective Git future.

## 4. Définition du périmètre généalogique

### 4.1 Couple de départ

[V] L'utilisateur choisit **une famille Gramps**, pas deux personnes indépendantes. Ses deux partenaires connus sont P0/P1. Leurs fiches, lorsqu'elles sont éligibles, et la section F0 apparaissent au **début de la partie ascendante** ; la partie descendante renvoie à cette présentation. [P] Si F0 n'a qu'un partenaire connu, ou aucun, ne pas prétendre produire un livre centré sur un couple complet : rejeter la sélection avec un message explicite. Les familles monoparentales rencontrées *dans le périmètre* restent parfaitement admises (§ 4.5).

### 4.2 Relations parent–enfant

[V] Parcourir les filiations enregistrées, notamment biologiques, adoptives, d'accueil, de belle-famille et les autres types explicites, sans privilégier les liens biologiques ni arbitrer les filiations incertaines. Reproduire le type de lien saisi dans Gramps lorsque cette information est disponible. [P] Ne pas convertir une simple union entre adultes en relation parent–enfant. Dans une référence enfant, un lien explicitement déclaré « aucun » pour l'un des partenaires ne crée pas une filiation avec ce partenaire ; les autres liens réellement enregistrés sont parcourus. Cette distinction est à tester avec les relations de l'API Gramps utilisée.

### 4.3 Ascendance

[V] Une partie **commune** explore les ancêtres de P0 et P1 jusqu'aux limites configurées, avec génération 0 pour P0/P1, -1 pour leurs parents, -2 pour leurs grands-parents, etc. Les deux ascendances restent identifiables sans création de chapitres intégralement séparés. Toutes les unions connues d'un ancêtre et tous les enfants de ces unions sont présentés. Les frères/sœurs des ancêtres figurent dans les fratries avec leurs noms et dates disponibles ; leurs descendants ne sont pas développés du seul fait de cette relation collatérale.

[V] Si un frère/sœur d'un ancêtre répond au critère de fiche individuelle (§ 5), il a une fiche complète, sans que cela n'étende sa descendance. Les conjoints/partenaires rencontrés ont une présentation conforme au même critère de fiche, mais leur propre ascendance n'est pas développée **à moins qu'ils soient eux-mêmes des ancêtres de P0 ou P1**.

### 4.4 Descendance

[V] Une partie commune présente les descendants de P0 et P1, **y compris les descendants issus d'autres unions**. Générations +1, +2, etc. Les membres de la même génération sont regroupés par parent puis par union/famille ; les filiations sont explicitement conservées. Les enfants communs de P0 et P1 ne doivent pas être dupliqués. Les ascendants des conjoints introduits seulement par le mariage ne sont pas ajoutés au parcours.

[P] Définir la descendance comme l'union des descendants accessibles depuis P0 ou P1 par des arêtes de filiation enregistrées, et non comme une recherche limitée aux seuls enfants de F0. Ne pas étendre le parcours depuis le conjoint d'un descendant vers les enfants de ce conjoint qui ne sont reliés à **aucune** personne de la descendance par une filiation enregistrée.

### 4.5 Familles, unions et collatéraux

[V] Une **section familiale par union/famille**, placée à proximité des fiches concernées, présente les partenaires connus, les événements familiaux et les enfants. Les événements familiaux sont développés **une seule fois dans leur section familiale**, avec renvois depuis les fiches. Une famille avec un seul parent connu et des enfants reçoit également une section ; aucun second parent n'est inventé.

[V] Toutes les unions connues des ancêtres du périmètre et leurs enfants sont présentés. Les frères/sœurs collatéraux sont mentionnés, avec éventuellement une fiche, mais sans expansion descendante du seul fait de leur présence. Les autres familles des personnes rencontrées sont prises en compte selon leur rôle : unions nécessaires à la présentation de la lignée et unions connues des ancêtres. [P] Une section familiale est identifiable par son objet Famille Gramps ; deux familles distinctes avec les mêmes partenaires ne sont pas automatiquement fusionnées.

### 4.6 Répétitions, implexes et générations multiples

[V] Chaque personne possède **au plus une fiche complète dans l'ensemble du livre**. L'emplacement principal est sa première apparition dans l'ordre de parcours déterministe de l'ouvrage. Un ancêtre commun à P0 et P1 figure intégralement lors de sa première apparition, puis par renvoi dans l'autre lignée. Les autres occurrences mentionnent les relations et renvoient à la fiche, ou à la mention principale si aucune fiche n'existe.

[P] Une personne peut appartenir à plusieurs générations selon différents chemins (implexes, filiations multiples, données atypiques). Conserver les chemins pertinents dans le graphe, mais choisir **une occurrence principale** pour la fiche, sans écraser les autres appartenances. Les repères de génération décrivent le chemin affiché dans la section courante et ne prétendent pas attribuer à la personne une génération absolue unique. Interrompre l'expansion d'un chemin qui revisite une personne déjà rencontrée sur ce même chemin, afin d'éviter toute boucle, tout en maintenant le lien visible.

### 4.7 Profondeurs et frontières

[P] La limite d'ascendance/descendance compte les arêtes parent–enfant depuis P0/P1, et non les unions. À la frontière de profondeur, présenter la personne atteinte et les informations contextuelles requises pour sa famille, sans développer la génération suivante. Les personnes annexes peuvent disposer de fiches sans devenir de nouveaux points de départ pour un parcours hors périmètre. Ce comportement doit être couvert par des tests d'arbre reconstruit complexe.

## 5. Fiches individuelles et notices

### 5.1 Critère exact de création

[V] Créer une fiche si la personne présente **au moins un événement individuel ou familial renseigné autre que naissance et décès**, ou si l'attribut de personne `BOOK_PROFILE = YES` force sa création. Un événement familial associé à une famille dont la personne est partenaire compte pour l'éligibilité de sa fiche ; son détail reste dans la section familiale. Le critère s'applique aux conjoints et aux frères/sœurs des ancêtres comme aux personnes de la lignée. Une personne avec uniquement naissance/décès, portrait, médias ou note, sans dérogation, demeure dans les listes/sections mais n'a pas de fiche propre.

[P] « Renseigné » signifie qu'un événement de type éligible est effectivement associé et possède au moins une donnée substantielle (date, lieu, description, rôle ou autre propriété informative). Ne pas compter une coquille d'événement entièrement vide créée par erreur. La liste exacte des événements familiaux éligibles sera testée sur les données Gramps réelles ; elle n'autorise pas à multiplier les fiches pour une simple référence technique.

### 5.2 Contenu d'une fiche

[V] Présenter dans cet ordre : identité (noms, variantes utiles, dates et lieux essentiels, portrait principal si disponible), chronologie exhaustive des événements individuels, notes publiables Markdown, renvois vers les médias et les sections familiales. Présenter les attributs, titres, adresses, professions, liens et autres informations biographiques structurées, **à l'exception des métadonnées purement techniques** ; ne pas masquer des données simplement parce qu'elles sont privées ou concernent une personne vivante. Les événements conservent type, date, lieu, description, rôle et autres propriétés pertinentes ; le texte enregistré n'est ni reformulé ni inventé.

[V] En cas d'informations multiples ou contradictoires, afficher toutes les versions sans arbitrage et sans ajouter d'avertissement dans le livre. Le rapport de contrôle séparé les signale seulement dans le périmètre restreint prévu au § 12.

### 5.3 Notices synthétiques

[V] Une personne non éligible reste présente partout où le parcours ou la section familiale exige sa mention. Dans la fratrie d'un ancêtre, afficher une mention synthétique (noms et dates disponibles) et un renvoi si une fiche existe. Pour une personne sans fiche mais possédant un portrait, afficher une petite vignette à proximité du nom **lorsque l'espace le permet** ; l'absence de place n'est pas un motif de créer une fiche.

### 5.4 Chronologie

[V] Utiliser les dates disponibles et les relations temporelles explicitement connues pour classer les événements. Les événements totalement indatables arrivent en fin de fiche. [P] Une date approximative est représentée par une plage/borne de comparaison sans inventer de date plus précise pour l'affichage. En cas d'ordre intrinsèquement ambigu, préserver un ordre stable (position d'origine puis clé technique), et ne pas présenter cet ordre comme une chronologie certaine. Ne pas modifier les dates Gramps.

## 6. Notes et métadonnées éditoriales

### 6.1 Notes publiables

[V] Une note est publiable **uniquement** si elle porte l'étiquette native Gramps `BOOK_PUBLICATION`. Les notes de travail sans cette étiquette ne sont pas publiées. Une même note associée à plusieurs contextes est publiée dans **chaque contexte**, même si cela répète son texte ; ne pas la confondre avec un média, dont la reproduction est dédupliquée.

[V] Le contenu des notes publiées est généralement saisi en **Markdown** et doit être rendu avec une typographie harmonisée avec le livre : paragraphes, titres, listes, emphase, liens et autres constructions compatibles. [P] Parser le Markdown avec une bibliothèque éprouvée vers une représentation intermédiaire sûre, puis rendre vers LaTeX et HTML. Le Markdown n'autorise ni HTML arbitraire exécuté dans le site statique ni injection de commandes LaTeX. Si une note contient également du formatage riche natif Gramps, définir et tester une règle documentée de conversion/normalisation, sans interpréter deux syntaxes simultanément au hasard.

### 6.2 Notes éditoriales propres à un couple

[V] Le titre, sous-titre, introduction, dédicace, nom de l'auteur et date de publication sont conservés dans des notes associées **à la famille centrale F0**, afin que différents couples puissent posséder des textes différents dans la même base. [P] Utiliser une convention de type de note ou d'intitulé pour distinguer exactement ces six rôles, tout en conservant `BOOK_PUBLICATION` comme condition de publication. Ne pas rechercher des notes globales homonymes dans toute la base.

[P] Convention à figer dans le code et le guide utilisateur après essai sur Gramps 6 : `BOOK_TITLE`, `BOOK_SUBTITLE`, `BOOK_INTRODUCTION`, `BOOK_DEDICATION`, `BOOK_AUTHOR`, `BOOK_PUBLICATION_DATE`. Ces chaînes sont des **noms proposés**, pas des fonctionnalités natives garanties. Une absence de note donne un titre/fallback automatique ou omet l'élément facultatif ; aucune date de publication n'est inventée comme un fait généalogique. En cas de notes concurrentes pour le même rôle, règle de départage stable et journal technique.

### 6.3 Personnes et médias

[V] Attribut de personne `BOOK_PROFILE = YES` : force la fiche sans étendre le périmètre généalogique. Étiquettes de média `BOOK_EXCLUDE` et `BOOK_FEATURED` : la première exclut le média du livre ; la seconde déclenche une mise en valeur, notamment la pleine page pour une photographie. [P] L'exclusion prime sur l'importance. Les métadonnées facultatives absentes ou invalides entraînent un repli sur les règles automatiques avec mention dans le journal technique, sans interruption de génération.

[V] L'ordre de présentation des personnes, branches et familles **n'est pas personnalisable** via des attributs additionnels. Les titres, légendes et descriptions des médias utilisent en premier lieu les champs natifs Gramps.

## 7. Médias et reproductions

### 7.1 Sélection et emplacements

[V] Le portrait principal Gramps est affiché en taille standard à proximité de l'identité dans une fiche, et les deux portraits du couple apparaissent en **médaillon** sur la couverture. Les autres médias sont normalement reproduits en annexes. Les photographies portant `BOOK_FEATURED` sont reproduites en **pleine page dans la partie principale**, à proximité de l'événement ou de la section familiale pertinente, sans reproduction supplémentaire dans les annexes.

[V] Si une photographie importante est liée à plusieurs événements, la placer à proximité du **premier événement concerné dans l'ordre de parcours** du livre. En présence d'une association familiale pertinente, privilégier la section familiale/événement plutôt qu'une fiche individuelle isolée. Les autres occurrences pointent vers sa page de reproduction. Si aucun événement ou famille utilisable n'existe, [P] choisir la première personne concernée selon l'ordre de parcours, puis consigner ce choix comme repli automatique.

### 7.2 Déduplication

[V] Un même objet média représenté plusieurs fois dans Gramps a **une seule reproduction documentaire principale** dans le livre ; les autres contextes comportent des renvois. Les petits portraits/vignettes nécessaires à la navigation sont des usages de présentation et non de nouvelles reproductions documentaires pleine page. [P] Dédupliquer d'abord sur l'identité de l'objet média, et ne fusionner par empreinte de fichier deux objets différents qu'après justification fonctionnelle : deux objets Gramps peuvent porter des légendes ou références distinctes.

### 7.3 Médias justificatifs et PDF

[V] Un document justificatif partagé entre plusieurs citations est reproduit une seule fois, immédiatement après la **première citation** l'utilisant ; les suivantes renvoient à cette reproduction. Plusieurs reproductions peuvent partager une page, selon lisibilité et espace disponible.

[V] **PDF multipages** : jamais reproduit dans les annexes ; si une URL externe est renseignée, seule cette URL sert d'accès au document ; sans URL, conserver la référence documentaire, sans chemin local ni reproduction. **PDF d'une page** : reproduire seulement si aucune URL n'est disponible ; sinon proposer le lien externe. [P] Les images raster usuelles peuvent être reproduites après conversion sûre vers un format accepté par LaTeX/HTML, sans dégrader silencieusement la lisibilité ; les médias non affichables donnent lieu à une notice/lien disponible, sans incorporation hasardeuse. Les URLs doivent être conservées comme données éditoriales, avec protocoles autorisés documentés.

### 7.4 Qualité et droits

[P] Respecter le ratio des images, préserver la qualité des actes (pas de réduction rendant l'écriture illisible), produire des légendes à partir des données Gramps et conserver les références de source/citation lorsque disponibles. Aucune image réelle ne doit figurer dans les fixtures ou captures d'écran d'un dépôt public. Les questions de droits de reproduction et de partage sont du ressort de l'auteur de l'ouvrage.

## 8. Citations, sources et annexes

### 8.1 Système de renvois

[V] Attribuer à chaque citation **utilisée** un numéro éditorial compact `[1]`, `[2]`, etc., dans l'ordre de sa **première apparition** au sein du livre. Une régénération peut modifier ces numéros. Le numéro n'est pas l'identifiant Gramps : ce dernier figure dans la référence bibliographique détaillée en annexe.

[V] Les citations sont appelées au voisinage du fait qu'elles justifient ; toutes les citations attachées à un fait sont restituées, sans n'en retenir une arbitrairement. Les appels mènent à des **notes de bas de page** contenant une référence bibliographique abrégée, le numéro de citation et le **numéro de page** de l'entrée correspondante en annexe. Les liens PDF internes sont cliquables ; la note reste entièrement utilisable sur papier. Les informations sans citation sont publiées normalement sans symbole ni avertissement.

[P] Une occurrence de fait peut créer une nouvelle note de bas de page pour une citation déjà connue, mais cette citation conserve **le même numéro éditorial** et **une seule entrée détaillée en annexe**. L'ordre de première apparition suit l'ordre final du modèle éditorial, et non le hasard des requêtes ou l'ordre d'itération d'un dictionnaire Python.

### 8.2 Contenu des entrées

[V] Une **annexe documentaire unique** présente chaque référence complète, suivie de ses reproductions éventuelles, selon la règle de déduplication précédente. Reproduire les informations bibliographiques disponibles : identifiant public Gramps de la citation, source, titre, auteur, date, dépôt, cote, localisation/page dans la source, URL, autres champs pertinents, et association aux documents. Une référence absente ou incomplète ne bloque pas la génération ; les éléments disponibles sont simplement publiés sans avertissement documentaire dans le livre.

[P] Une citation sans dépôt demeure une citation valide. Les objets source/citation/dépôt doivent garder leurs identités propres ; ne pas inventer de cote ou de dépôt. Les références citées dans le corps du livre renvoient vers **la citation**, puis de celle-ci vers le média justificatif s'il existe.

### 8.3 Pagination et liens

[V] Les numéros de page contenus dans les notes et les renvois correspondent à la pagination **définitive** du PDF, pas à une estimation préalable. [P] Utiliser des ancres LaTeX stables et des compilations successives jusqu'à résolution des renvois, de la table des matières et de l'index. En cas de non-convergence ou de références non résolues, ne pas publier un PDF trompeur : produire une erreur bloquante explicite. Le HTML utilise les mêmes identifiants de citation et des ancres, **sans numéro de page papier**.

## 9. Organisation et mise en page du livre

### 9.1 Séquence éditoriale

[V] Couverture automatique : titre/sous-titre/noms du couple/informations éditoriales disponibles, **portraits des deux membres en médaillon** s'ils existent. Puis éléments préliminaires disponibles (dédicace, introduction), table des matières, **partie ascendante débutant par le couple de référence**, partie descendante avec renvois au couple, annexe documentaire unique et index alphabétique des personnes. [P] Les mentions de personnes sans fiche doivent aussi être accessibles par l'index, avec renvoi vers leur occurrence principale.

### 9.2 Générations et ordres

[V] Génération centrale 0, ascendantes négatives, descendantes positives. Au sein d'une génération : regroupement **par branche familiale**, puis ordre chronologique de naissance. Au sein de la descendance : regroupement d'abord par parent et union selon la hiérarchie des branches. [P] Dates inconnues à la fin du groupe considéré ; égalité ou dates insuffisamment comparables départagées par une clé stable fondée sur les identifiants/handles Gramps. Ne pas déduire un ordre de naissance certain à partir d'une date approximative ambiguë.

### 9.3 Règles graphiques

[V] Format **A4**, style **contemporain et minimaliste**, typographie sans empattements, priorité à une **mise en page compacte** et parfaitement lisible en niveaux de gris. Aucune information ne doit dépendre exclusivement d'une couleur. Les grandes parties commencent sur une nouvelle page ; ni chaque génération ni chaque branche ne nécessitent systématiquement un saut de page. Plusieurs fiches peuvent partager une page ; une fiche longue peut se poursuivre sur plusieurs pages. Éviter les titres isolés et les blocs courts coupés.

[V] En-tête courant compact : section, génération, branche et numéro de page. Les illustrations ordinaires des annexes peuvent être disposées à plusieurs par page. Les photographies `BOOK_FEATURED` sont intégrées en pleine page dans le corps du livre. **Aucun arbre graphique supplémentaire** n'est requis : tableaux, listes, sections familiales et repères suffisent.

[P] La taille exacte des caractères, les marges, l'espacement, les gabarits de tableaux et les seuils d'images seront fixés par une maquette-test LaTeX sur documents fictifs représentant les cas limites. Éviter de promettre « aucune coupure » pour des blocs qui dépassent physiquement une page ; autoriser leur continuation avec titres/repères réitérés.

### 9.4 Index

[V] Construire un index **alphabétique des personnes**, avec les pages où elles sont présentées ; pas d'index des lieux/sources requis en v1. [P] Indexer les noms principaux et, si possible, variantes utiles sans générer de doublons confus ; les renvois vers une personne sans fiche doivent conduire à sa mention principale. Le classement alphabétique respecte autant que possible la locale du livre.

## 10. Sorties PDF et HTML

### 10.1 PDF

[V] Livre A4 imprimable et consultable numériquement, avec table des matières, index, notes de bas de page, annexes et liens internes. [P] Utiliser **LuaLaTeX** comme première hypothèse de moteur, avec modèles LaTeX maintenus dans le dépôt, `hyperref` et outil de compilation piloté automatiquement (par ex. `latexmk`). [T] Vérifier en prototype les notes longues, les références de pages avant annexes, les fichiers PDF d'une page, les photos pleine page, les sauts de page et l'index. Aucun utilisateur ne doit devoir lancer LaTeX manuellement.

### 10.2 HTML

[V] Produire une **archive ZIP contenant un site statique complet**, utilisable après extraction en local ou publication sur un serveur statique sans accès à Gramps ni génération côté serveur. Reprendre l'ordre du livre PDF sous forme de pages HTML successives, sans pagination papier. Ajouter sommaire, liens internes entre personnes/familles, citations et annexes. Pas de moteur de recherche spécifique requis. [P] Styles CSS en niveaux de gris ; pages et ressources dotées de chemins relatifs ; éviter toute dépendance à un CDN, un serveur distant ou une connexion Internet pour la consultation de base (les URL externes de documents restent facultatives).

### 10.3 Équivalence des données

[V] PDF et HTML reposent sur le **même modèle éditorial résolu** : même périmètre, même texte, mêmes citations, mêmes choix d'illustrations et de déduplication. La présentation peut différer selon le support ; la pagination papier et les notes de bas de page ne sont pas imposées au HTML. Une génération ne produit que le format sélectionné, mais les deux parcours doivent être testés sur une même fixture.

## 11. Architecture logicielle proposée

### 11.1 Modules et responsabilités

[P] Architecture modulaire **dans un seul dépôt public de plugin**, sans création de services/dépôts obligatoires :

```text
GrampsFancyBook/
  FancyBook.gpr.py               # enregistrement léger du rapport
  report_adapter.py             # interface/options Desktop & Web
  gramps_reader.py              # extraction Gramps et conversion en DTO
  domain/                       # personnes, familles, événements, citations, médias
  traversal/                    # graphe, ascendances, descendances, générations
  editorial/                    # fiches, sections, renvois, annexe, index
  rendering/
    markdown.py                 # Markdown -> modèle intermédiaire sûr
    latex.py                    # modèles et génération .tex
    html.py                     # pages et archive ZIP
  compilation.py                # LuaLaTeX, ressources, contrôles du PDF
  metadata.py                   # étiquettes/attributs BOOK_*
  diagnostics.py                # progression et journaux
  templates/                   # LaTeX, CSS, HTML, traductions
  MANIFEST
build_addon.py
tests/                           # fixtures uniquement fictives
.github/workflows/
docs/
```

[P] Il s'agit d'une **structure indicative** : respecter la convention réelle de chargement des add-ons Gramps dans le répertoire de distribution ; ne pas recopier la structure de l'ancien plugin si elle n'est pas adaptée. Le `.gpr.py` ne doit pas importer la pile LaTeX/Markdown au chargement de Gramps. La lecture Gramps est concentrée dans une couche d'adaptation ; les autres modules sont testables sur objets de domaine synthétiques sans installation de Gramps.

### 11.2 Modèle de domaine

[P] Convertir les objets Gramps en objets de domaine immuables ou assimilés, avec clés typées : `PersonKey`, `FamilyKey`, `EventKey`, `CitationKey`, `SourceKey`, `MediaKey`. Conserver les associations munies de leurs **rôles**, de leur type de relation, de leurs citations et de leurs notes ; ne pas aplatir toute l'information d'un événement familial dans chacun de ses partenaires. Construire ensuite le graphe des relations et le modèle éditorial `Book` : `Part`, `Generation`, `Branch`, `PersonOccurrence`, `PersonProfile`, `FamilySection`, `Fact`, `CitationEntry`, `MediaPlacement`, `IndexEntry`.

[P] Garder les données de source normalisées distinctes des représentations typographiques ; les moteurs de rendu ne doivent ni re-parcourir la base Gramps ni réinventer le périmètre généalogique. Les positions éditoriales et les identifiants des ancres sont calculés **avant** la génération LaTeX/HTML.

### 11.3 Algorithme de construction (contrat)

```text
1. Vérifier F0, ses deux partenaires et les paramètres.
2. Charger les objets et relations nécessaires sans modifier la base.
3. Construire le graphe parent-enfant typé ; conserver les unions séparément.
4. Parcourir les ascendances de P0 et P1 jusqu'à la limite choisie.
5. Parcourir l'union des descendances de P0 et P1 jusqu'à la limite choisie.
6. Ajouter le contexte requis : unions, conjoints, enfants et collatéraux.
7. Déterminer les appartenances branche/génération de chaque occurrence.
8. Trier les occurrences et familles de façon déterministe.
9. Fixer la première occurrence et l'unique fiche éventuelle de chaque personne.
10. Composer les sections familiales ; relier les événements familiaux une seule fois.
11. Appliquer notes publiables, attributs de fiche, choix et placements des médias.
12. Constituer les faits et leurs citations ; attribuer les numéros éditoriaux.
13. Créer les annexes (références complètes, reproductions uniques, renvois).
14. Construire la table des matières, les ancres, l'index et les diagnostics.
15. Rendre PDF ou HTML depuis le même modèle éditorial validé.
```

[P] Les parcours doivent enregistrer une **pile de chemin** pour éviter les cycles et un **registre global des occurrences/fiches** pour éviter les duplications, sans supprimer les relations alternatives visibles. Les sources manquantes et médias sans fichier sont traités conformément aux décisions documentaires, sans provoquer une exception non maîtrisée.

### 11.4 Intégration technique à valider

[T] Sur les versions ciblées de Gramps, confirmer : choix correct du type de plugin de rapport et de son fichier de sortie personnalisé ; persistance locale des options ; lecture des étiquettes Notes/Médias et attributs personnes ; présence du nom/type de relation parent–enfant ; identification du portrait principal ; traduction des noms de types d'événement ; téléchargement des médias sur Gramps Web ; rendu et téléchargement du ZIP HTML ; progression/journal dans Gramps Web ; comportement des accès aux objets privés lorsqu'un filtre de confidentialité du contexte de rapport est appliqué **avant** l'appel au plugin.

[P] Si Gramps Web ne permet pas de transmettre les objets privés au rapport avec les autorisations de l'utilisateur, ne pas prétendre les exporter en contournant le système de permissions ; signaler explicitement cette limite. Le choix éditorial « inclure les données privées » n'autorise jamais le contournement des contrôles d'accès.

## 12. Diagnostics, incohérences et erreurs

### 12.1 Rapport de contrôle généalogique

[V] Le rapport de contrôle **séparé du livre** se limite à des contradictions **entre dates et lieux associés à un même fait** ; aucune évaluation généalogique générale, aucun audit systématique des médias, des relations familiales ou du sourçage. Ne pas ajouter de warning dans le livre. [P] Limiter les alertes à des cas objectivement incompatibles ; des dates approximatives compatibles, plusieurs résidences ou professions successives ne sont pas des contradictions. Lorsque deux événements différents ne sont pas explicitement déclarés comme décrivant le même fait, ne pas les fusionner artificiellement.

### 12.2 Journal technique

[V] Les métadonnées incorrectes sont signalées dans un **journal technique** avec application des règles par défaut. Les informations bibliographiques incomplètes ou non sourcées sont publiées sans avertissement documentaire. [P] Le journal technique peut contenir les erreurs de lecture/compilation et fichiers médias introuvables lorsqu'une opération technique échoue ; cela ne doit pas être présenté comme un nouveau contrôle systématique de qualité généalogique.

### 12.3 Politique d'échec

[V] Continuer en cas d'anomalie non bloquante ; interrompre si la base/famille de référence est inexploitable, si le document ne peut être compilé, si des liens/numéros de page indispensables restent non résolus ou si le livrable final est corrompu. Les messages distinguent la cause technique, l'objet Gramps concerné lorsqu'il est identifiable, et l'étape. Aucun fichier partiellement produit ne remplace silencieusement un ouvrage antérieur.

## 13. Sécurité, confidentialité et reproductibilité

[V] Le livre contient, conformément au choix éditorial, les données de personnes vivantes et les objets marqués privés **dans la mesure où la session Gramps autorise réellement leur lecture**. Avertir l'utilisateur avant un export potentiellement destiné à être partagé ; aucun filtrage de confidentialité automatique n'est ajouté au contenu. Dépôt GitHub du code exclusivement alimenté par des fixtures fictives, sans photos, notes, logs, chemins ou exports de la généalogie réelle.

[P] Échapper strictement les champs texte injectés dans LaTeX ; désactiver le shell escape ; ne pas interpréter les notes comme du LaTeX exécutable ; traiter le Markdown comme des données ; nettoyer les noms de fichiers et chemins ; éviter la traversée de répertoires lors de la préparation des ressources et du ZIP ; interdire les références vers des chemins hors dossier de travail ; ne pas télécharger arbitrairement des URL distantes pendant la compilation ; limiter durée, mémoire et disque du processus de compilation. Fournir un résultat temporaire déterministe, indépendant des heures de génération dans les fichiers de contenu ; laisser la date de publication uniquement lorsqu'elle est explicitement renseignée ou issue d'un comportement de repli documenté.

[P] Les sources LaTeX générées et les ressources peuvent être exportables ultérieurement comme dossier autonome ; Git du **livre** n'est pas requis en v1. La reproductibilité **sémantique** (mêmes données/options/versions ⇒ même contenu et mêmes identifiants internes) est obligatoire ; l'identité bit à bit d'un PDF entre systèmes nécessite en plus versions figées des outils, polices et métadonnées normalisées et ne doit pas être promise sans test.

## 14. GitHub, packaging, installation et maintenance

[V] Le **code du plugin** est versionné dès le départ sur GitHub dans un dépôt dédié. Le plugin existant `grostim/gramps-two-way-fan-chart` est une source d'expérience pour l'installation et l'automatisation, **pas** un squelette à copier sans revue critique. Prévoir obligatoirement README, guides utilisateur et développeur, guide des conventions `BOOK_*`, journal des versions et instructions Desktop/Web **dans les deux langues FR/EN**, avec exemples fictifs et vérification de leur synchronisation dans la CI.

[P] Pipeline de qualité à chaque PR/push : lint et vérifications statiques adaptées, tests unitaires, tests d'intégration sur Gramps 6.x ciblé, vérification du paquet installable, génération PDF/HTML sur fixtures synthétiques, contrôle des liens/index/notes et analyse des fichiers de sortie. Les releases du plugin associent tag Git, archive d'installation et checksum ; les versions Gramps 6.0, 6.1 et suivantes ne sont annoncées compatibles qu'après tests effectifs. Préparer un déploiement optionnel sur Gramps Web ; ne pas imposer la modification du dépôt `portainer-util` ni réutiliser aveuglément ses secrets ou ses permissions.

[T] Installer et tester les dépendances Python, images, LaTeX et polices sur Windows, macOS, Linux et l'environnement serveur Gramps Web retenu. La compilation peut être effectuée dans le processus serveur ou dans un sous-processus isolé ; la solution exacte dépend du rapport de prototype et des contraintes d'hébergement.

## 15. Tests d'acceptation : scénarios minimaux

| ID | Jeu de données / situation | Résultat vérifiable |
|---|---|---|
| AC-01 | Famille centrale à deux partenaires | P0/P1 en génération 0 au début de l'ascendance ; renvois depuis la descendance. |
| AC-02 | Famille centrale à un seul partenaire | Refus explicite de sélectionner ce couple incomplet ; pas de livrable partiel. |
| AC-03 | Enfant d'une autre union de P0 | Présent en descendance +1 et dans sa section familiale ; aucune duplication s'il apparaît aussi ailleurs. |
| AC-04 | Filiation adoptive/d'accueil/enfant du conjoint explicitement enregistrée | Parcours respecte exactement les liens saisis et les restitue sans les renommer « biologiques ». |
| AC-05 | Personne commune à deux lignées | Une seule fiche, plusieurs mentions/renvois ; aucune boucle de parcours. |
| AC-06 | Frère d'un ancêtre très documenté | Mention en fratrie, fiche si éligible, mais pas d'expansion automatique de sa descendance. |
| AC-07 | Conjoint avec uniquement naissance et décès | Pas de fiche, mais mention familiale ; attribut `BOOK_PROFILE=YES` force sa fiche. |
| AC-08 | Personne avec événement familial et aucun événement individuel éligible | Fiche créée ; détail de l'événement uniquement en section familiale. |
| AC-09 | Famille monoparentale rencontrée dans le parcours | Section familiale valide, sans second parent inventé. |
| AC-10 | Note Markdown étiquetée, associée à deux objets | Rendue deux fois, en conservant sa mise en forme et sans code Markdown brut. |
| AC-11 | Note non étiquetée | Exclue du livre ; aucun texte de recherche publié accidentellement. |
| AC-12 | Portraits du couple et photo `BOOK_FEATURED` | Deux médaillons en couverture si médias présents ; photo importante pleine page une fois ; renvois depuis autres occurrences. |
| AC-13 | Média `BOOK_EXCLUDE` et `BOOK_FEATURED` simultanément | Le média n'est pas publié, selon la priorité d'exclusion. |
| AC-14 | Deux faits partageant une citation ; fait avec deux citations | Numéros éditoriaux unifiés par objet Citation, notes complètes et entrée unique par citation ; toutes les citations du fait apparaissent. |
| AC-15 | Document partagé par plusieurs citations | Une reproduction derrière la première citation utilisatrice ; renvois valides depuis les autres. |
| AC-16 | PDF multipages avec/sans URL ; PDF une page avec/sans URL | Respect strict des quatre règles de reproduction/lien définies au § 7.3. |
| AC-17 | Nouvelle note au début modifiant la pagination | Tous les renvois vers les pages d'annexes et index correspondent au PDF final. |
| AC-18 | Fait sans citation, source sans dépôt | Fait publié ; citation existante détaillée avec champs disponibles ; aucune fausse donnée inventée. |
| AC-19 | Deux dates incompatibles pour un même fait | Les deux dates restent dans le livre ; rapport séparé signale le conflit, sans warning ajouté au livre. |
| AC-20 | Export des mêmes données en PDF puis en HTML | Même périmètre, textes et citations ; HTML local navigable hors connexion, sans pagination papier. |
| AC-21 | Livre long et notes/images difficiles | Aucune note/citation orpheline, pas de titre isolé ni de page importante tronquée ; échec explicite si limite impossible à résoudre. |
| AC-22 | Installation Desktop + Gramps Web | Lancement du rapport, options, génération, téléchargement, progression et logs vérifiés sur environnements ciblés. |
| AC-23 | Noms contenant `&`, `%`, `_`, accents et texte Markdown inattendu | PDF compile sans injection LaTeX ; HTML n'exécute pas de script issu des notes. |
| AC-24 | Deux exécutions sur données/options inchangées | Ordre des personnes, numéros de citations et ancres stables ; aucune dérive arbitraire. |
| AC-25 | Notes, personnes et médias avec les conventions `BOOK_*` | Sélection conforme dans Gramps quelle que soit la langue de l’interface ; `BOOK_PROFILE=YES` force une fiche ; `BOOK_EXCLUDE` prime sur `BOOK_FEATURED`. |
| AC-26 | Documentation française et anglaise | README, installation, utilisation, conventions de métadonnées, dépannage et contribution disponibles et cohérents dans les deux langues ; vérification CI. |
| AC-27 | Transmission des maquettes de référence | Les deux maquettes PDF/HTML accompagnent le dossier de conception privé ; tout écart avec la spécification est arbitré en faveur des exigences validées. |

## 16. Jalons et prototypes avant réalisation complète

1. **Spike d'intégration Gramps** [T] : add-on de rapport minimal compatible Desktop et Web, sélection F0, choix PDF/ZIP, options, persistance, accès aux objets privés autorisés et progression/journal.
2. **Spike de données** [T] : famille fictive contenant filiations multiples, événements familiaux, notes étiquetées, sources/citations/dépôts, portrait, médias et PDF ; vérifier tous les champs réellement accessibles via l'API Gramps 6 retenue.
3. **Spike LaTeX** [T] : 15–30 pages fictives avec fiche longue, Markdown, notes de bas de page, annexes, document partagé, photographie pleine page, index et références de pages stabilisées.
4. **Moteur généalogique pur Python** [P] : graphes fictifs et tests de parcours/déduplication/profondeur avant développement des modèles graphiques définitifs.
5. **Moteur éditorial et rendus** : génération du modèle commun, puis PDF et HTML avec tests d'équivalence.
6. **Intégration, distribution, validation** : tests de bout en bout Desktop/Web, documentation utilisateur et GitHub Actions du code du plugin.

La réussite de ces prototypes conditionne les affirmations de compatibilité ; un échec peut conduire à changer **une solution technique proposée**, non à modifier silencieusement une exigence fonctionnelle validée.

## 17. Registre des précisions à trancher par implémentation / tests

Ce registre n'appelle pas une nouvelle série de questions fonctionnelles : il liste les décisions **techniques** à consigner après essai. Chacun de ces points doit avoir un test de non-régression.

- **T-01** : type de rapport Gramps et adaptation Web pour les fichiers de sortie personnalisés (PDF et ZIP), les paramètres et la progression.
- **T-02** : conventions exactes des six notes éditoriales sur F0 et gestion d'une note manquante/dupliquée, avec guide d'utilisation.
- **T-03** : sérialisation des dates approximatives et tri déterministe des événements/personnes en cas d'intervalles qui se chevauchent.
- **T-04** : associations familiales, rôle de l'événement, types de filiation et sens précis d'une relation déclarée « aucun ».
- **T-05** : modalités d'extraction des images originales et comportement des médias manquants selon l'hébergement ; conversion autorisée des PDF d'une page sans URL.
- **T-06** : bibliothèque Markdown, traitement du balisage natif des notes Gramps et filtre de sécurité de l'HTML/LaTeX.
- **T-07** : gabarits typographiques et seuils de lisibilité sur impressions A4 noir et blanc.
- **T-08** : stratégie de convergence des références de pages, traitement des notes longues et construction de l'index.
- **T-09** : matrices exactes des versions de Gramps, OS, LuaLaTeX et dépendances effectivement testées.
- **T-10** : export facultatif futur d'un dossier LaTeX autonome ; son éventuelle publication Git privée/GitHub Actions reste hors périmètre v1.

## 18. Sources techniques consultables et références du projet

- Références visuelles et structurelles à communiquer au développement : `reference_maquette/maquette_structure_livret_familial.pdf`, `reference_maquette/maquette_structure_livret_familial.html`, `reference_maquette/maquette_livret_familial_evenements_sources.pdf` et `reference_maquette/maquette_livret_familial_evenements_sources.html` (joints au dossier de transmission privé, cf. § 1.4).

- Documentation Gramps, *Report-writing tutorial* : https://gramps-project.org/wiki/index.php/Report-writing_tutorial
- Gramps, *Using database API* : https://gramps-project.org/wiki/index.php/Using_database_API
- Gramps Web, *Rapports* : https://www.grampsweb.org/fr/user-guide/reports/
- Gramps, manuel 6, éditeur de notes et étiquettes : https://www.gramps-project.org/wiki/index.php/Gramps_6.0_Wiki_Manual_-_Entering_and_editing_data%3A_detailed_-_part_2
- Gramps, manuel 6, liens parent–enfant : https://www.gramps-project.org/wiki/index.php/Gramps_6.0_Wiki_Manual_-_Entering_and_editing_data%3A_detailed_-_part_1
- Dépôt d'expérience existant du commanditaire (à analyser de manière critique, sans le modifier ni l'utiliser comme squelette obligatoire) : https://github.com/grostim/gramps-two-way-fan-chart

---

**Règle de gouvernance de la spécification.** Tout changement d'une exigence [V] suppose une décision explicite du commanditaire ; les choix [P] peuvent être améliorés après comparaison documentée ; les points [T] doivent être résolus par un test ou un prototype avant d'annoncer la fonctionnalité comme opérationnelle. Aucun contenu généalogique personnel n'est nécessaire pour publier ou tester le code source du plugin.
