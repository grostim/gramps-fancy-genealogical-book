# Avancement L4 — parcours généalogiques

Compte rendu actualisé le 4 octobre 2026. L4 reste en cours ; AC-01 et AC-03 à AC-09 sont qualifiés sur le modèle et le contrat textuel LaTeX. AC-01 et AC-03 à AC-09 disposent maintenant de fixtures Gramps CLI natives vérifiées en HTML et PDF. La saisie dans l’interface et la pagination d’un livre complet restent à valider.

## Parcours disponibles

- La famille F0 doit comporter deux partenaires connus, qui deviennent P0 et P1 en génération 0.
- L’ascendance et la descendance ont chacune une limite indépendante. `unlimited` est la valeur par défaut ; une limite entière positive ou zéro peut être saisie.
- L’extraction Gramps charge récursivement les familles et personnes reliées dans ces deux directions, puis conserve les unions et la fratrie comme contexte. Elle n’ouvre pas l’ascendance du conjoint d’un descendant.
- Le moteur indépendant de Gramps produit les générations négatives et positives, les sections familiales, les rôles d’occurrence, les racines de branche et les chemins de filiation.
- F0 est une section unique au début de l’ascendance ; la descendance conserve les occurrences centrales comme renvois. Les enfants des autres unions des ancêtres figurent comme contexte, sans développement de leur descendance.
- Les relations enfant-parent explicitement « None » ne sont pas parcourues. Les familles monoparentales restent admises dans le graphe.
- Un chemin qui revisite une personne est conservé comme occurrence visible, signalé par un diagnostic et arrêté avant de développer la boucle.
- L’éligibilité de fiche applique `BOOK_PROFILE = YES` ou un événement individuel/familial substantiel autre que naissance et décès.
- Chaque occurrence renseigne `primary_occurrence_id` pour renvoyer à la première apparition de la personne, même sans fiche complète. Pour une personne éligible, `profile_anchor` et `is_primary_profile` désignent toujours sa fiche unique et son occurrence principale.
- Dans un même groupe de génération, branche et famille, les plages de naissance comparables et disjointes sont ordonnées chronologiquement. Les plages qui se chevauchent, les égalités et les dates non comparables sont départagées par identifiant/handle Gramps ; les dates absentes ou non comparables restent à la fin du groupe. Aucun ordre de naissance précis n’est déduit d’une plage ambiguë.
- La chronologie des événements utilise les bornes comparables de Gramps plutôt que sa valeur scalaire de tri. Les événements dont les plages se chevauchent conservent leur position source, avec la clé technique comme départage stable ; les dates non comparables arrivent après les dates classables.
- Les sections familiales suivent d’abord l’ordre des générations et des occurrences de branche, puis l’ordre source des unions dans les listes Gramps du partenaire ou de l’enfant concerné. L’identifiant familial ne sert que de départage déterministe.
- Chaque section familiale a un identifiant stable, référence les occurrences de ses partenaires et enfants dans le périmètre, et expose les liens parent-enfant avec la valeur du type de filiation normalisée depuis Gramps pour chaque parent, lorsqu’elle est disponible. Chaque occurrence conserve les identifiants de ses sections ; génération, branche, chemin et ancre de fiche fournissent les données du repère.
- La recette native T-04 fait passer par l’import Gramps 6.0.8 les liens `Adopted`, `Foster`, `Stepchild`, `Sponsored` et `Unknown`, ainsi qu’une valeur personnalisée `Other` ; le lien `None` est conservé dans les données mais omis du graphe. Les sorties HTML/PDF françaises affichent notamment « Enfant du conjoint » pour `Stepchild`. Les familles monoparentales ne montrent que leur parent enregistré. La même fixture confirme qu’un événement Marriage associé à F0 conserve le rôle Gramps `Family`. La saisie graphique reste à qualifier.
- La recette native AC-01 fait apparaître les deux partenaires de F0 au début de l’ascendance, génération 0, puis renvoie leurs apparitions de descendance vers leur première occurrence ou fiche dans le modèle, le HTML et le PDF. Le contrôle PDF inspecte les annotations de liens internes et confirme que les deux partenaires centraux renvoient depuis la génération 0 de descendance vers leur page de fiche.
- La recette native AC-03 ajoute une seconde union F0003 au parent central et un enfant admissible par `BOOK_PROFILE=YES`. Après import Gramps 6.0.8, l’enfant figure une fois en génération 1 dans la section de F0003 ; le modèle et le HTML ne créent qu’une fiche. Les noms de l’enfant, du partenaire et leurs liens sont présents dans le HTML et le PDF.
- La recette native AC-05 relie un ancêtre commun aux deux branches du couple et introduit une boucle d’ascendance explicite. Après import Gramps 6.0.8, les deux occurrences de l’ancêtre sont conservées, mais le modèle, le HTML, le PDF et l’index n’en créent qu’une fiche ; un diagnostic signale la boucle et aucun chemin de cette fixture ne dépasse quatre personnes.
- La recette native AC-06 ajoute un frère à l’un des ancêtres et un enfant à ce frère. Le frère, marqué `BOOK_PROFILE=YES`, apparaît comme occurrence collatérale et reçoit une seule fiche et entrée d’index ; son enfant reste hors des occurrences, sections familiales et rendus HTML/PDF.
- La recette native AC-07 ajoute deux conjoints avec uniquement des événements naissance et décès. Tous deux restent mentionnés dans leur union ; seul celui marqué `BOOK_PROFILE=YES` reçoit une fiche dans le modèle, le HTML et le PDF.
- La recette native AC-08 ajoute un conjoint avec uniquement des événements naissance et décès et associe son mariage à la famille, avec le rôle Gramps `Family`. Le mariage le rend admissible à une fiche ; son détail n’apparaît que dans la notice familiale du modèle, du HTML et du PDF.
- La recette native AC-09 conserve la famille monoparentale F0002 avec son seul parent enregistré et sa filiation `Foster`. Le modèle et le HTML réutilisent ce parent dans ses deux sections généalogiques, sans en ajouter un autre ; le PDF le montre seul dans la section familiale.

## Limites avant la sortie de L4

- `tests/test_genealogy_acceptance.py` qualifie AC-01 et AC-03 à AC-09 sur des graphes fictifs et vérifie aussi leur traduction en sorties LaTeX. `scripts/verify_gramps.py` couvre maintenant AC-01 et AC-03 à AC-09 depuis la fixture native dans le modèle, le ZIP HTML et le PDF ; l’interface Gramps reste à exercer.
- `tests/test_date_ranges.py` vérifie les groupes transitifs de plages chevauchantes, le maintien de l’ordre source pour la chronologie d’événements, l’usage des bornes malgré des valeurs scalaires contradictoires et le placement final des dates textuelles/non comparables. Le 4 octobre, la suite complète passe : 54 tests.
- Les rendus LaTeX et HTML consomment le modèle `genealogy`. Leurs contrats sont couverts à des degrés différents ; la pagination, les renvois multipasses et l’apparence du PDF restent à contrôler visuellement en L6.
- Le modèle éditorial fournit déjà profils, notices familiales, index et cibles de navigation au rendu LaTeX. La validation porte ici sur leur structure textuelle, pas sur la composition paginée finale.
- Les six rôles éditoriaux de F0 et les diagnostics de sélection sont vérifiés sur une fixture Gramps CLI native. La saisie dans l’interface Gramps 6 et l’acceptation visuelle PDF restent ouvertes ; voir la [décision sur les notes F0](decisions/004-f0-editorial-notes.md).

Le détail des tâches et critères de sortie figure dans le [plan d’action](action-plan.fr.md#l4--parcours-généalogiques-et-sélection) et dans les [exigences](requirements.fr.md).

## Essai PDF en CLI — 29 septembre 2026

Gramps 6.0.8 sur macOS a produit un PDF A4 de 9 pages depuis la base native fictive avec LuaHBTeX 1.24.0. La fixture comprenait un dérivé de portrait, visible sur la couverture et dans la fiche de la personne. Cet essai confirme l’intégration Gramps–PDF sur un livre synthétique réduit ; il ne qualifie ni la pagination d’un livre long, ni tous les cas de médias/URL, ni l’accessibilité ou l’acceptation visuelle finale, qui restent à traiter en L6.

## Essai PDF AC-01 en CLI — 4 octobre 2026

Gramps 6.0.8 et LuaHBTeX 1.24.0 ont produit un PDF A4 de 14 pages. Les deux partenaires de F0 ouvrent l’ascendance en génération 0 ; leurs occurrences de descendance renvoient vers leur première apparition ou fiche, et F0 est le premier lien familial rendu. Les annotations de liens internes du PDF ont été inspectées : les deux renvois du couple central en génération 0 de descendance ciblent leur page de fiches. Les pages 4, 6 et 7 ont été relues visuellement ; la saisie GUI et la revue visuelle du livre complet restent à faire.

## Essai PDF AC-03 en CLI — 4 octobre 2026

Gramps 6.0.8 et LuaHBTeX 1.24.0 ont produit un PDF A4 de 10 pages. La personne issue de l’autre union apparaît en génération 1, dans les liens familiaux avec ses deux parents, puis dans les fiches et l’index. Le PDF a été relu visuellement : les renvois et lignes repliées restent lisibles ; la validation visuelle du livre complet reste au lot L6.

## Essai PDF AC-05 en CLI — 4 octobre 2026

Gramps 6.0.8 et LuaHBTeX 1.24.0 ont produit un PDF A4 de 13 pages. L’ancêtre commun apparaît sur les deux branches, puis une seule fois dans les fiches et l’index ; le parcours cyclique s’arrête et le PDF compilé est lisible. La validation visuelle du livre complet reste au lot L6.

## Essai PDF AC-06 en CLI — 4 octobre 2026

Gramps 6.0.8 et LuaHBTeX 1.24.0 ont produit un PDF A4 de 14 pages. Le frère d’un ancêtre apparaît dans la fratrie, reçoit une seule fiche et une entrée d’index grâce à `BOOK_PROFILE=YES` ; son enfant n’est développé ni dans le modèle ni dans les sorties HTML/PDF. Les pages concernées ont été relues ; la validation visuelle du livre complet reste au lot L6.

## Essai PDF AC-07 en CLI — 4 octobre 2026

Gramps 6.0.8 et LuaHBTeX 1.24.0 ont produit un PDF A4 de 14 pages. Deux conjoints porteurs uniquement d’événements de naissance et décès sont mentionnés dans leurs unions ; l’un ne reçoit aucune fiche, l’autre en reçoit une seule grâce à `BOOK_PROFILE=YES`. Le modèle, le HTML et les sections concernées du PDF ont été vérifiés ; la saisie GUI et la revue visuelle du livre complet restent à faire.

## Essai PDF AC-08 en CLI — 4 octobre 2026

Gramps 6.0.8 et LuaHBTeX 1.24.0 ont produit un PDF A4 de 14 pages. Un conjoint n’ayant que des événements de naissance et décès reçoit une fiche grâce à un mariage associé à sa famille ; la description du mariage n’apparaît que dans la notice familiale, jamais dans la fiche individuelle. Les pages 10 et 12 ont été relues visuellement ; la saisie GUI et la revue visuelle du livre complet restent à faire.

## Essai PDF AC-09 en CLI — 4 octobre 2026

Gramps 6.0.8 et LuaHBTeX 1.24.0 ont produit un PDF A4 de 14 pages. La famille F0002 ne montre que son parent enregistré, sans partenaire ajouté ; le lien de filiation `Foster` reste visible. La page 7 a été relue visuellement ; la saisie GUI et la revue visuelle du livre complet restent à faire.

## Essai PDF AC-04 — filiation de beau-parent en CLI — 4 octobre 2026

La fixture Gramps 6.0.8 couvre `Adopted`, `Foster`, `Stepchild`, `Sponsored`, `Unknown`, une valeur personnalisée `Other` et `None`. Le modèle conserve les types, le graphe suit uniquement les liens explicites, et les familles monoparentales n’ajoutent pas de parent. Le ZIP HTML et le PDF français préservent ces filiations et affichent « Adopté(e) », « En nourrice », « Enfant du conjoint », « Parrainé » et « Inconnu » ; la valeur personnalisée reste `Other`. Le PDF balisé A4 compte 16 pages ; les pages 7 et 8 ont été relues visuellement. La liste d’options GUI est apparue en français et `Stepchild` a été sélectionné dans une fiche synthétique ; l’enregistrement de la famille reste à confirmer. Voir l’[aperçu AC-04](../output/pdf/gramps-fancy-book-ac04-native-parentage-fr-20261004.pdf).
