# Mesure de performance — L8.3

Mesures répétées le 29 septembre 2026 sur macOS 27.0 arm64 et CPython 3.14.0, avec Gramps 6.0.8 et son Python embarqué 3.13.2, LuaHBTeX 1.24.0 (TeX Live 2026), Pillow 12.3.0 et Mistune 3.3.4.

## Méthode et jeux synthétiques

Lancer depuis la racine du dépôt, dans un environnement Python où le projet et son extra médias sont installés (pip install -e ".[media]"); LuaLaTeX doit être disponible dans PATH :

    PYTHONPATH=src python scripts/benchmark_book.py --shape both --descendant-couples 10 100 1000 --with-media --compile-pdf-for 100 --repeat 3

    PYTHONPATH=src python scripts/benchmark_gramps_extraction.py --gramps /Applications/Gramps.app/Contents/MacOS/Gramps --scenario branching ancestors multiple-unions pedigree-collapse media --descendant-couples 10 100 1000 --repeat 3 --output docs/validation-gramps-scenarios-20260929.json

Dans le premier banc, chaque taille est exécutée trois fois ; les temps et pics de mémoire présentés sont les médianes. Les tailles JSON, HTML et LaTeX y sont stables sur les trois répétitions. Les imports Gramps sont mesurés séparément et leurs handles internes font légèrement varier la taille JSON.

Deux structures sont comparées :

- Jeu large : un couple central avec N enfants et leur partenaire. Chaque personne reçoit une fiche ; il n’y a ni événement ni média. Il conserve le point de repère initial, mais ne représente pas un arbre profond.
- Jeu ramifié : N unions descendantes réparties en branches, avec au plus deux enfants par famille. Chaque personne a un événement de naissance ; chaque famille a un événement d’union. Chaque événement a une citation, les sources sont partagées entre 25 citations, et un dépôt ainsi que des lieux sont inclus. Les notes publiables apparaissent environ une fois par douze personnes et une fois par dix familles. Un portrait PNG synthétique avec région de recadrage apparaît environ une fois par dix personnes.

Le premier script mesure la construction du modèle, la préparation des dérivés, la sérialisation JSON, les deux moteurs de rendu et l’archive ZIP. Il compile aussi un PDF sur le petit cas ramifié. Les portraits PNG pseudo-aléatoires font 96 × 72 pixels par défaut ; `--portrait-size WIDTHxHEIGHT` permet de choisir une autre taille avec `--with-media`. Le script limite une image synthétique à 24 millions de pixels et le volume estimé des sources à 256 Mio.

Le second script lance le rapport JSON par l’interface en ligne de commande de Gramps à partir de GEDCOM fictifs. Chaque répétition utilise un profil `GRAMPSHOME` neuf, puis le script installe l’archive construite depuis le dépôt et copie Mistune dans ce profil temporaire. Le fichier [validation-gramps-extraction-20260929.json](validation-gramps-extraction-20260929.json) conserve le premier relevé ramifié. Les cinq scénarios élargis et leurs mesures brutes figurent dans [validation-gramps-scenarios-20260929.json](validation-gramps-scenarios-20260929.json). Un chronométrage ajouté uniquement à la copie temporaire du rapport sépare `GrampsDatabaseAdapter.read_snapshot_by_gramps_id` de la construction du modèle. Le temps de bout en bout et le pic RSS comprennent aussi le démarrage de Gramps, l’import GEDCOM et l’écriture JSON. Aucun arbre Gramps habituel n’est ouvert ou modifié.

Les scénarios élargis gardent un volume proche entre formes, avec un paramètre N de 10, 100 ou 1 000 :

- **Ramifié :** arbre de descendance de référence, au plus deux enfants par famille.
- **Ascendance :** N unions d’ancêtres réparties entre les deux personnes centrales. Une seule ligne parentale continue à chaque génération afin de mesurer la profondeur sans croissance exponentielle.
- **Unions multiples :** même arbre ramifié, avec une seconde union sans enfant et un partenaire distinct pour chaque descendant.
- **Implexe / ancêtres communs :** même arbre, enrichi d’une union de cousins et d’un enfant pour cinq unions descendantes. Les cousins sont issus de branches différentes et partagent des ancêtres.
- **Médias :** même arbre ramifié, avec un PNG valide de 1 × 1 pixel lié à chaque dixième personne. Chaque lien vise un objet média distinct.

Les nombres d’objets attendus sont vérifiés à chaque import. Chaque fait a une citation; un dépôt et une source sont partagés. Les exécutions élargies utilisent l’interpréteur hôte CPython 3.13.7, Gramps 6.0.8 et son Python embarqué 3.13.2. Les médianes présentées ci-dessous sont séparées du relevé antérieur, exécuté avec CPython 3.14.0.

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

### Compilation PDF complète — référence non balisée du 29 septembre

Ces durées décrivent le renderer avant l’activation du balisage PDF ; elles ne sont pas comparables au renderer balisé actuel.

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

### Scénarios élargis depuis Gramps

Trois bases indépendantes ont été importées par scénario et par taille. « Faits / citations » sont identiques, car chaque fait synthétique a une citation. Les tailles JSON et le RSS sont exprimés en Mo décimaux.

| Scénario | N | Personnes | Familles | Faits / citations | Médias | Adaptateur (s) | Modèle (s) | Rapport complet (s) | RSS maximal (Mo) | JSON (Mo) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ramifié | 10 | 22 | 11 | 33 | 0 | 0,005 | 0,003 | 0,801 | 188,8 | 0,326 |
| Ramifié | 100 | 202 | 101 | 303 | 0 | 0,035 | 0,023 | 1,073 | 206,6 | 2,870 |
| Ramifié | 1 000 | 2 002 | 1 001 | 3 003 | 0 | 0,360 | 0,227 | 3,896 | 305,0 | 28,587 |
| Ascendance | 10 | 22 | 11 | 33 | 0 | 0,005 | 0,003 | 0,807 | 188,8 | 0,319 |
| Ascendance | 100 | 202 | 101 | 303 | 0 | 0,036 | 0,024 | 1,083 | 206,9 | 3,005 |
| Ascendance | 1 000 | 2 002 | 1 001 | 3 003 | 0 | 0,361 | 0,701 | 4,840 | 363,3 | 52,090 |
| Unions multiples | 10 | 32 | 21 | 53 | 0 | 0,007 | 0,004 | 0,833 | 190,0 | 0,503 |
| Unions multiples | 100 | 302 | 201 | 503 | 0 | 0,056 | 0,037 | 1,261 | 215,7 | 4,623 |
| Unions multiples | 1 000 | 3 002 | 2 001 | 5 003 | 0 | 0,571 | 0,397 | 5,861 | 372,1 | 46,109 |
| Implexe | 10 | 24 | 13 | 37 | 0 | 0,005 | 0,003 | 0,810 | 188,7 | 0,369 |
| Implexe | 100 | 222 | 121 | 343 | 0 | 0,039 | 0,025 | 1,118 | 209,0 | 3,294 |
| Implexe | 1 000 | 2 202 | 1 201 | 3 403 | 0 | 0,401 | 0,256 | 4,325 | 321,0 | 32,939 |
| Médias | 10 | 22 | 11 | 33 | 2 | 0,005 | 0,003 | 0,802 | 188,8 | 0,333 |
| Médias | 100 | 202 | 101 | 303 | 20 | 0,035 | 0,023 | 1,077 | 207,0 | 2,940 |
| Médias | 1 000 | 2 002 | 1 001 | 3 003 | 200 | 0,362 | 0,230 | 3,976 | 308,0 | 29,281 |

## Interprétation et limites

Le modèle ramifié met en évidence des charges absentes du cas large : à 2 002 personnes, il traite 3 003 événements et citations, 267 notes et 200 dérivés de médias. Sous tracemalloc, la sérialisation JSON prend 3,217 s au grand format et le pic additionnel atteint 68,41 Mo. Ces durées sont instrumentées et ne prédisent pas directement le temps ressenti en production.

### Relevé complémentaire avec des portraits plus grands

Pour exercer le décodage et le recadrage sur des dimensions plus proches de photos courantes, le banc direct a été relancé trois fois avec 100 unions descendantes et des portraits PNG synthétiques de 1 600 × 1 200 pixels :

    PYTHONPATH=src python scripts/benchmark_book.py --shape branching --descendant-couples 100 --with-media --portrait-size 1600x1200 --repeat 3

| Cas | Personnes | Portraits | Source PNG totale (octets) | Fixture médiane | Dérivés médians | ZIP HTML médian | Pic fixture tracemalloc | Pic additionnel tracemalloc | Pic total tracemalloc |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ramifié, 100 unions | 202 | 20 | 115 379 213 | 2,071 s | 1,484 s | 1,149 s | 122,59 Mo | 9,88 Mo | 126,17 Mo |

Le pic total est le maximum entre celui observé pendant la création de la fixture et celui observé ensuite ; le pic additionnel est rapporté au tas encore chargé après la fixture. Les résultats des trois répétitions et les informations d’exécution sont dans [validation-book-media-20261001.json](validation-book-media-20261001.json). Les sources sont du bruit pseudo-aléatoire non compressible, pas des photographies ; leur poids et leur contenu ne reproduisent donc pas la compression, le format ni la distribution de photos d’une base Gramps réelle. Le pic `tracemalloc` exclut les allocations natives de Pillow.

Les mesures Gramps montrent que l’adaptateur lit 2 002 personnes, 1 001 familles et 3 003 événements/citations en 0,351 s ; le rapport CLI complet prend 3,815 s et son processus atteint 305,04 Mo de RSS maximal. Le RSS comprend l’application Gramps et n’est donc pas comparable au pic additionnel Python suivi par tracemalloc dans l’autre banc d’essai.

Les nouveaux cas couvrent l’ascendance profonde, les secondes unions, les liens d’implexe et les références médias à partir d’une base Gramps. À 1 000 unions, la ligne d’ascendance atteint 52,1 Mo de JSON et 0,701 s de construction du modèle; les unions multiples atteignent le RSS maximal du lot, 372,1 Mo. Ces chiffres mesurent des GEDCOM contrôlés et le rapport CLI sur macOS. Le cas d’ascendance est une ligne volontairement profonde plutôt qu’un arbre ancestral complet; les unions secondaires n’ont pas d’enfant. Les images Gramps de 1 × 1 pixel mesurent les références et métadonnées, pas le décodage ni le recadrage. Le relevé direct complémentaire exerce ces étapes avec des PNG synthétiques de 1 600 × 1 200 pixels, sans représenter la compression ou le contenu de photos réelles. Les seuils définitifs restent à confirmer après qualification des environnements cibles, en particulier Gramps Web.

## Enveloppe de référence proposée — 1er octobre 2026

Pour rendre L8.3 actionnable, ces budgets provisoires s’appuient sur la seule configuration de référence mesurée plus haut : macOS 27.0 arm64, Gramps 6.0.8 et LuaHBTeX 1.24.0. Ils ne constituent pas encore des seuils CI ni une garantie sur d’autres machines. Comparer les médianes de trois exécutions identiques.

| Parcours de référence | Budget proposé | Résultat observé |
| --- | --- | --- |
| Export CLI Gramps, N=1 000, cinq formes synthétiques | ≤ 10 s ; RSS ≤ 512 Mo ; JSON ≤ 64 Mo | Maxima distincts : 5,861 s et 372,1 Mo RSS (unions multiples) ; 52,090 Mo JSON (ascendance) |
| Compilation PDF ramifiée, 2 002 personnes, 3 003 événements et 200 médias dérivés | ≤ 60 s ; PDF ≤ 16 Mo | Renderer balisé actuel : timeout après 120,804 s, aucun PDF ; référence non balisée : 34,714 s et 7 074 362 octets |
| Création de la fixture, dérivés et archive HTML, N=100 avec 20 PNG de 1 600 × 1 200 pixels | ≤ 8 s au total ; pic `tracemalloc` ≤ 256 Mo | 2,071 s pour la fixture, 1,484 s pour les dérivés, 1,149 s pour l’archive ; 4,704 s et 126,17 Mo de pic tracé au total |

Le renderer limite maintenant la compilation LuaLaTeX à 120 s par passe et 180 s au total, contre un maximum théorique antérieur de cinq passes de 120 s. Ce garde-fou temporel est plus large que le budget de performance PDF et sert à interrompre un export bloqué. Les budgets RSS et de taille finale restent des critères de qualification, pas des limites imposées pendant l’exécution. Une première mesure de l’espace temporaire est consignée ci-dessous ; elle ne constitue pas encore un plafond d’exécution.

### Espace temporaire mesuré le 1er octobre 2026

Le banc somme la taille logique des fichiers sous son répertoire temporaire toutes les 100 ms. Il ignore les liens symboliques ; un fichier créé et supprimé entre deux échantillons peut manquer au pic mesuré. La mesure porte sur le banc synthétique local, pas sur l’espace temporaire global du système.

| Cas | Résultat PDF | Pic observé des fichiers temporaires |
| --- | --- | ---: |
| 100 unions, 20 PNG synthétiques de 1 600 × 1 200, dérivés et ZIP HTML | Pas de compilation PDF | 157 472 942 octets |
| 100 unions, portraits standards de 96 × 72, PDF | Compilé en 163,058 s ; 1 935 494 octets | 4 837 119 octets |
| 1 000 unions, 200 portraits standards de 96 × 72, PDF | Échec `timeout` après 120,804 s ; aucun PDF livré | 24 584 541 octets avant l’arrêt |

Le cas moyen compilé dépasse le budget provisoire de 60 s. Le cas N=1 000 a atteint deux fois la limite de passe de 120 s avec échantillonnage à 10 ms, puis une troisième fois à 100 ms ; le changement de cadence n’explique donc pas le timeout. Les médianes antérieures de 4,483 s pour N=100 et 34,459 s pour N=1 000 datent du 29 septembre, avant l’activation du balisage PDF par la [PR #132](https://github.com/grostim/gramps-fancy-genealogical-book/pull/132), fusionnée le 30 septembre, et avant la correction des listes familiales de la [PR #180](https://github.com/grostim/gramps-fancy-genealogical-book/pull/180), fusionnée le 1er octobre. Elles ne sont donc pas directement comparables aux mesures du renderer balisé actuel. Une comparaison diagnostique du même petit livre avec LuaLaTeX a pris 19,104 s avec `tagging=on` et 9,039 s avec le balisage désactivé uniquement dans la copie temporaire ; ce cas suggère un coût significatif du balisage, sans expliquer à lui seul les durées des livres moyens et grands. Les nouvelles mesures restent à répéter après qualification ou optimisation du renderer balisé ; l’enveloppe PDF proposée n’est pas confirmée. Les détails sont dans [le relevé temporaire brut](validation-temp-disk-20261001.json).

### Essai des destinations de structure PDF — 1er octobre 2026

Une fixture ramifiée sans média (N=10, 22 personnes, 11 familles, 33 événements) a été compilée trois fois par variante dans des répertoires temporaires neufs, via le helper `_compile_latex` du renderer de production et LuaHBTeX 1.24.0. La variante `activate/struct-dest=false` désactive les destinations d’éléments structurels tout en conservant le balisage, conformément à la [documentation de tagpdf](https://tug.ctan.org/macros/latex/contrib/tagpdf/tagpdf-code.pdf).

| Réglage | Compilation (s, médiane [plage]) | PDF (octets, médiane [plage]) |
| --- | ---: | ---: |
| Balisage actuel | 19,633 [19,179–19,883] | 221 701 [221 701–221 702] |
| Destinations de structure désactivées | 19,543 [19,121–19,991] | 211 287 [211 283–211 291] |

Les deux fichiers sont reconnus comme balisés et contiennent 25 pages A4. L’arbre de structure lu avec `pdfinfo -struct` reste identique et dans le même ordre (2 520 éléments, dont 525 liens, 441 paragraphes et 217 éléments de liste) ; les 561 destinations nommées, les 132 annotations de liens externes et le texte extrait sont identiques. `pdfinfo -struct` émet aussi 114 avertissements identiques par fichier sur l’attribut `ListNumbering` ; ce relevé ne constitue pas un contrôle de conformité.

La désactivation des destinations réduit la taille médiane du PDF de 10 414 octets (4,7 %), mais la compilation ne gagne que 0,090 s sur une médiane de 19,633 s (0,46 %), différence trop faible pour justifier une optimisation. Aucun réglage de production n’est changé ; cette fixture ne confirme pas le budget PDF et ne prédit pas le comportement des livres moyens et grands. L’inspection de l’arbre ne remplace pas un essai au lecteur d’écran. Les résultats bruts figurent dans [le relevé tagpdf](validation-tagpdf-structure-20261001.json).

Un second essai désactive directement `para/tagging` dans la copie temporaire, juste avant `\begin{document}`. Sur trois compilations de la même fixture, la médiane est de 19,937 s [19,759–20,111], contre 19,633 s avec le balisage normal ; les PDF font 221 551 octets chacun contre une médiane de 221 701 octets. Poppler indique `Tagged: no` sur les trois fichiers. Ils gardent 25 pages, 561 destinations nommées, 132 liens externes et 27 853 caractères extraits, identiques entre les répétitions. L’écart de temps (+0,304 s, +1,55 %) n’est pas un gain et le balisage est perdu : ce réglage est écarté. Il s’agit d’un diagnostic sur un petit jeu, pas d’une proposition de configuration.
