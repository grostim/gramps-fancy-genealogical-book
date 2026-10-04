# Avancement L4 — parcours généalogiques

Compte rendu actualisé le 4 octobre 2026. L4 reste en cours ; AC-01 et AC-03 à AC-09 sont qualifiés sur le modèle et le contrat textuel LaTeX. AC-03 dispose maintenant d’une fixture Gramps CLI native vérifiée en HTML et PDF. La saisie dans l’interface et la pagination d’un livre complet restent à valider.

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
- La recette native T-04 fait passer par l’import Gramps 6.0.8 les liens `Adopted`, `Foster` et `None`. Le modèle conserve les valeurs, le graphe suit les deux liens explicitement enregistrés et présente la famille monoparentale avec son seul partenaire connu. La même fixture confirme qu’un événement Marriage associé à F0 conserve le rôle Gramps `Family`. La saisie graphique et les autres types de relation restent à qualifier.
- La recette native AC-03 ajoute une seconde union F0003 au parent central et un enfant admissible par `BOOK_PROFILE=YES`. Après import Gramps 6.0.8, l’enfant figure une fois en génération 1 dans la section de F0003 ; le modèle et le HTML ne créent qu’une fiche. Les noms de l’enfant, du partenaire et leurs liens sont présents dans le HTML et le PDF.

## Limites avant la sortie de L4

- `tests/test_genealogy_acceptance.py` qualifie AC-01 et AC-03 à AC-09 sur des graphes fictifs et vérifie aussi leur traduction en sorties LaTeX. `scripts/verify_gramps.py` couvre maintenant AC-03 depuis la fixture native dans le modèle, le ZIP HTML et le PDF ; l’interface Gramps reste à exercer.
- `tests/test_date_ranges.py` vérifie les groupes transitifs de plages chevauchantes, le maintien de l’ordre source pour la chronologie d’événements, l’usage des bornes malgré des valeurs scalaires contradictoires et le placement final des dates textuelles/non comparables. Le 4 octobre, la suite complète passe : 54 tests.
- Les rendus LaTeX et HTML consomment le modèle `genealogy`. Leurs contrats sont couverts à des degrés différents ; la pagination, les renvois multipasses et l’apparence du PDF restent à contrôler visuellement en L6.
- Le modèle éditorial fournit déjà profils, notices familiales, index et cibles de navigation au rendu LaTeX. La validation porte ici sur leur structure textuelle, pas sur la composition paginée finale.
- Les six rôles éditoriaux de F0 et les diagnostics de sélection sont vérifiés sur une fixture Gramps CLI native. La saisie dans l’interface Gramps 6 et l’acceptation visuelle PDF restent ouvertes ; voir la [décision sur les notes F0](decisions/004-f0-editorial-notes.md).

Le détail des tâches et critères de sortie figure dans le [plan d’action](action-plan.fr.md#l4--parcours-généalogiques-et-sélection) et dans les [exigences](requirements.fr.md).

## Essai PDF en CLI — 29 septembre 2026

Gramps 6.0.8 sur macOS a produit un PDF A4 de 9 pages depuis la base native fictive avec LuaHBTeX 1.24.0. La fixture comprenait un dérivé de portrait, visible sur la couverture et dans la fiche de la personne. Cet essai confirme l’intégration Gramps–PDF sur un livre synthétique réduit ; il ne qualifie ni la pagination d’un livre long, ni tous les cas de médias/URL, ni l’accessibilité ou l’acceptation visuelle finale, qui restent à traiter en L6.

## Essai PDF AC-03 en CLI — 4 octobre 2026

Gramps 6.0.8 et LuaHBTeX 1.24.0 ont produit un PDF A4 de 10 pages. La personne issue de l’autre union apparaît en génération 1, dans les liens familiaux avec ses deux parents, puis dans les fiches et l’index. Le PDF a été relu visuellement : les renvois et lignes repliées restent lisibles ; la validation visuelle du livre complet reste au lot L6.
