# Mesure de performance — L8.3

Mesures répétées le 29 septembre 2026 sur macOS 27.0 arm64 et CPython 3.14.0, avec Gramps 6.0.8 et son Python embarqué 3.13.2, LuaHBTeX 1.24.0 (TeX Live 2026), Pillow 12.3.0 et Mistune 3.3.4.

## Méthode et jeux synthétiques

Lancer depuis la racine du dépôt, dans un environnement Python où le projet et son extra médias sont installés (pip install -e ".[media]"); LuaLaTeX doit être disponible dans PATH :

    PYTHONPATH=src python scripts/benchmark_book.py --shape both --descendant-couples 10 100 1000 --with-media --compile-pdf-for 100 --repeat 3

    PYTHONPATH=src python scripts/benchmark_gramps_extraction.py --gramps /Applications/Gramps.app/Contents/MacOS/Gramps --descendant-couples 10 100 1000 --repeat 3 --output docs/validation-gramps-extraction-20260929.json

Dans le premier banc, chaque taille est exécutée trois fois ; les temps et pics de mémoire présentés sont les médianes. Les tailles JSON, HTML et LaTeX y sont stables sur les trois répétitions. Les imports Gramps sont mesurés séparément et leurs handles internes font légèrement varier la taille JSON.

Deux structures sont comparées :

- Jeu large : un couple central avec N enfants et leur partenaire. Chaque personne reçoit une fiche ; il n’y a ni événement ni média. Il conserve le point de repère initial, mais ne représente pas un arbre profond.
- Jeu ramifié : N unions descendantes réparties en branches, avec au plus deux enfants par famille. Chaque personne a un événement de naissance ; chaque famille a un événement d’union. Chaque événement a une citation, les sources sont partagées entre 25 citations, et un dépôt ainsi que des lieux sont inclus. Les notes publiables apparaissent environ une fois par douze personnes et une fois par dix familles. Un portrait PNG synthétique avec région de recadrage apparaît environ une fois par dix personnes.

Le premier script mesure la construction du modèle, la préparation des dérivés, la sérialisation JSON, les deux moteurs de rendu et l’archive ZIP. Il compile aussi un PDF sur le petit cas ramifié. Les médias sont des images pseudo-aléatoires déterministes, et non des portraits réels.

Le second script lance le rapport JSON par l’interface en ligne de commande de Gramps à partir d’arbres GEDCOM équilibrés, importés dans un profil `GRAMPSHOME` distinct pour chaque répétition. Il installe l’archive construite depuis le dépôt et copie Mistune dans ce profil temporaire, car l’application macOS ne fournit pas cette dépendance. Le fichier [validation-gramps-extraction-20260929.json](validation-gramps-extraction-20260929.json) conserve les mesures brutes. Un chronométrage ajouté uniquement à la copie temporaire du rapport sépare `GrampsDatabaseAdapter.read_snapshot_by_gramps_id` de la construction du modèle. Le temps de bout en bout et le pic RSS comprennent aussi le démarrage de Gramps, l’import GEDCOM et l’écriture JSON. Aucun arbre Gramps habituel n’est ouvert ou modifié.

## Durées et mémoire

Les temps sont en secondes. Le pic additionnel est le maximum Python suivi au-dessus de l’instantané et des images sources déjà chargés. Les valeurs Mo sont décimales.

### Jeu large

| Couples descendants N | Personnes | Familles | Modèle | JSON | HTML | LaTeX | ZIP HTML | Pic additionnel (Mo) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 22 | 11 | 0,009 | 0,018 | 0,001 | 0,001 | 0,002 | 0,58 |
| 100 | 202 | 101 | 0,078 | 0,144 | 0,009 | 0,012 | 0,010 | 3,31 |
| 1 000 | 2 002 | 1 001 | 0,751 | 1,419 | 0,086 | 0,120 | 0,093 | 31,09 |

### Jeu ramifié avec médias

| Couples descendants N | Personnes | Familles | Événements / citations | Notes | Médias / dérivés | Modèle | Dérivés | JSON | HTML | LaTeX | ZIP HTML | Pic additionnel (Mo) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 22 | 11 | 33 | 3 | 2 / 2 | 0,016 | 0,001 | 0,038 | 0,004 | 0,006 | 0,006 | 1,88 |
| 100 | 202 | 101 | 303 | 27 | 20 / 20 | 0,136 | 0,010 | 0,327 | 0,034 | 0,051 | 0,045 | 7,26 |
| 1 000 | 2 002 | 1 001 | 3 003 | 267 | 200 / 200 | 1,335 | 0,099 | 3,217 | 0,341 | 0,518 | 0,430 | 68,41 |

### Tailles de sortie

| Forme | N | JSON (octets) | HTML (octets) | LaTeX (octets) | ZIP HTML (octets) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Large | 10 | 85 862 | 23 911 | 66 732 | 2 706 |
| Large | 100 | 762 212 | 188 611 | 613 752 | 10 445 |
| Large | 1 000 | 7 525 712 | 1 835 611 | 6 083 952 | 80 717 |
| Ramifié | 10 | 186 329 | 62 297 | 128 262 | 34 409 |
| Ramifié | 100 | 1 639 117 | 543 853 | 1 188 448 | 331 657 |
| Ramifié | 1 000 | 16 265 394 | 5 363 871 | 11 797 460 | 3 306 591 |

### Compilation PDF complète

| Couples descendants N | Personnes | Événements | Médias | Compilation LuaLaTeX médiane | Plage | PDF (octets) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 202 | 303 | 20 | 4,483 s | 4,377–4,573 s | 739 729 |
| 1 000 | 2 002 | 3 003 | 200 | 34,459 s | 34,303–34,714 s | 7 074 362 |

Les compilations moyennes ont été répétées trois fois avec la commande principale. Les trois compilations de grande taille ont utilisé :

    PYTHONPATH=src python scripts/benchmark_book.py --shape branching --descendant-couples 1000 --with-media --compile-pdf-for 1000 --repeat 3

Les six PDF compilés ont terminé sans avertissement de mise en page.

### Extraction réelle depuis Gramps

Chaque taille a été importée dans une base Gramps neuve trois fois. Les temps et le pic mémoire sont les médianes ; la mémoire est le RSS maximal du processus Gramps mesuré par `/usr/bin/time -l`, en Mo décimaux.

| Couples descendants N | Personnes | Familles | Événements / citations | Notes | Lieux | Adaptateur (s) | Modèle (s) | Rapport JSON complet (s) | RSS maximal (Mo) | JSON médian (octets) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 22 | 11 | 33 | 2 | 22 | 0,0041 | 0,0027 | 0,755 | 188,78 | 326 342 |
| 100 | 202 | 101 | 303 | 26 | 25 | 0,0333 | 0,0220 | 1,035 | 206,68 | 2 870 536 |
| 1 000 | 2 002 | 1 001 | 3 003 | 266 | 25 | 0,3515 | 0,2240 | 3,815 | 305,04 | 28 585 990 |

Chaque événement est associé à une citation. Une source et un dépôt sont partagés ; les notes sont réparties entre personnes et familles. Les nombres d’objets attendus ont été contrôlés après chaque import. Les profils ne sont pas réutilisés entre répétitions : Gramps régénère ses handles internes, ce qui explique une faible variation de taille JSON (326 199–326 410, 2 869 817–2 870 998 et 28 583 790–28 588 036 octets selon la taille). Les mesures portent sur le même volume sémantique, pas sur une identité octet par octet entre bases recréées.

## Interprétation et limites

Le modèle ramifié met en évidence des charges absentes du cas large : à 2 002 personnes, il traite 3 003 événements et citations, 267 notes et 200 dérivés de médias. Sous tracemalloc, la sérialisation JSON prend 3,217 s au grand format et le pic additionnel atteint 68,41 Mo. Ces durées sont instrumentées et ne prédisent pas directement le temps ressenti en production.

Les mesures Gramps montrent que l’adaptateur lit 2 002 personnes, 1 001 familles et 3 003 événements/citations en 0,351 s ; le rapport CLI complet prend 3,815 s et son processus atteint 305,04 Mo de RSS maximal. Le RSS comprend l’application Gramps et n’est donc pas comparable au pic additionnel Python suivi par tracemalloc dans l’autre banc d’essai.

Ce relevé ne fixe pas encore de seuils d’acceptation. Le graphe importé ne couvre que les descendants ramifiés ; il reste à mesurer l’ascendance, les unions multiples, les implexes et les médias à partir de Gramps. Les images pseudo-aléatoires du banc direct ne reproduisent pas la compression de vraies photos. Tracemalloc ignore les allocations natives de Pillow et la mémoire du sous-processus LuaLaTeX. Les seuils seront déterminés après ces scénarios et les environnements de production visés.
