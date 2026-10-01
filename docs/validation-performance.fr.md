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

### Profil des passes LuaLaTeX — 1er octobre 2026

Une exécution par variante a chronométré séparément chaque appel LuaLaTeX du helper de production `_compile_latex`, dans un répertoire temporaire neuf. Les fixtures ramifiées contiennent deux portraits synthétiques à N=10 et vingt à N=100 (96 × 72 pixels). À N=100, la copie balisée et la copie diagnostique non balisée utilisent le même modèle, les mêmes médias et la même source rendue ; seul `tagging=on` est remplacé par `tagging=off` dans la source temporaire.

| Cas | Passes | Durée par passe (s) | Total (s) | Taille PDF |
| --- | ---: | ---: | ---: | ---: |
| N=10, balisé | 3 | 6,794 ; 6,829 ; 6,828 | 20,452 | 255 856 octets |
| N=100, balisé | 3 | 53,302 ; 53,800 ; 54,063 | 161,166 | 1 935 504 octets |
| N=100, balisage désactivé pour le diagnostic | 2 | 32,694 ; 32,923 | 65,639 | 868 690 octets |

À N=100, les trois passes balisées durent chacune près de 54 s ; elles portent la génération complète à 161,166 s. La copie non balisée est 2,46 fois plus rapide, mais Poppler indique `Tagged: no` sur son PDF de 194 pages. Cette mesure suggère un surcoût substantiel du balisage, sans autoriser à le désactiver en production. Chaque variante n’a été exécutée qu’une fois ; ces chiffres servent à orienter le profilage, pas à établir une nouvelle enveloppe statistique. Le relevé contient aussi les tailles des sources LaTeX : [profil brut des passes](validation-latex-pass-profile-20261001.json).

Le profil de convergence N=10 explique le troisième passage balisé : l’ajout des entrées du sommaire change le seul enregistrement auxiliaire `@tag@LastPage`, dont les compteurs passent de 1 921 à 1 949 contenus marqués et de 2 520 à 2 541 éléments de structure. Le sommaire et le nombre de pages sont déjà stables, mais le texte extrait change entre les passes 1 et 2. Les compteurs restent ensuite stables, et le texte, l’arbre, les destinations et les liens ne changent plus entre les passes 2 et 3. Le [code tagpdf qui calcule le remplissage des identifiants de structure à partir de `tagstruct`](https://github.com/latex3/tagpdf/blob/main/tagpdf-tree.dtx#L1895-L1903) et [assemble le ParentTree jusqu’au compteur `tagmcabs`](https://github.com/latex3/tagpdf/blob/main/tagpdf-tree.dtx#L2203-L2214) s’appuie sur ces valeurs ; les exclure du contrôle de convergence risquerait un PDF incomplet. L’optimisation doit donc réduire le coût des passes sans les supprimer.

Une passe unique instrumentée de la fixture ramifiée N=100, balisage activé et 20 portraits de 96 × 72 pixels, a duré 52,284 s et produit un PDF balisé de 194 pages. Les chronomètres englobent chaque section jusqu’au marqueur suivant, y compris les coupures et sorties de pages.

| Section | Durée (s) |
| --- | ---: |
| Ascendance | 0,033 |
| Descendance | 1,26 |
| Liens familiaux | 13,5 |
| Notices familiales | 5,1 |
| Fiches individuelles | 10,5 |
| Annexe documentaire | 14,1 |
| Index des personnes | 3,03 |
| Total des sections chronométrées | 47,523 |
| Passe complète | 52,284 |

Les liens familiaux, l’annexe documentaire et les fiches individuelles dominent cette passe. Les hooks internes tagpdf mesurent 3,284 s pour la finalisation de l’arbre, dont 2,77 s pour l’écriture des éléments de structure. Une seule exécution instrumentée sert à orienter la suite du profilage ; elle ne confirme pas de budget statistique et ne décompose pas les opérations LaTeX internes à chaque section. Le PDF obtenu reste balisé (Tagged: yes). Les données brutes figurent dans le [profil des passes](validation-latex-pass-profile-20261001.json).

### Encodage compact des destinations PDF — 1er octobre 2026

Sur la même fixture N=100 et dans deux répertoires temporaires neufs par comparaison, la variante base32 modifie uniquement les noms internes des cibles PDF. Chaque exécution complète utilise les trois passes du helper de production ; l’ordre des variantes est inversé lors de la seconde paire.

| Encodage des cibles | Durées (s) | Médiane (s) | Source compilée | PDF final médian |
| --- | ---: | ---: | ---: | ---: |
| Hexadécimal UTF-8 | 159,271 ; 157,841 | 158,556 | 1 265 310 octets | 1 935 501 octets |
| Base32 minuscule sans remplissage | 143,177 ; 146,125 | 144,651 | 1 123 555 octets | 1 946 333 octets |

Le temps complet médian baisse de 8,77 % et la source de 141 755 octets (11,2 %). Les PDF gardent 194 pages A4 et le balisage. Les 4 905 destinations nommées, dont 1 805 cibles du livre, sont présentes dans les deux variantes et chaque cible est remappée exactement une fois. La sortie de l’arbre tagpdf et le texte extrait sont identiques octet pour octet dans chaque paire. En contrepartie, le PDF final augmente de 10 833 octets environ (0,56 %). Deux paires suffisent à retenir cette piste pour le renderer ; elles ne constituent pas un budget statistique. La précédente mesure de source N=100 à 1 249 510 octets correspond à un rendu avant préparation des dérivés média ; la comparaison ci-dessus inclut les dérivés réellement compilés. Les détails sont dans le [profil brut des passes](validation-latex-pass-profile-20261001.json).

### Factorisation des renvois de page — 1er octobre 2026

La nouvelle commande LaTeX se développe en les deux mêmes liens cliquables et le même numéro de page que l’ancien texte produit directement. Sur la fixture N=100, deux compilations de trois passes donnent une source médiane de 821 686 octets, soit 301 869 octets de moins (26,86 %) que la référence base32. Le pic temporaire échantillonné passe de 4 837 119 à environ 4 345 714 octets (−10,16 %). La durée médiane est de 145,045 s contre 144,651 s pour la référence base32 : aucun gain de temps mesurable. Le PDF final conserve une taille équivalente (1 946 325 contre 1 946 333 octets). Le nouveau PDF balisé de 194 pages conserve les 4 905 destinations ; la sortie structurelle Poppler et le texte extrait sont identiques octet pour octet à la référence. Cette factorisation réduit la source et l’espace temporaire mesuré, sans accélérer la compilation. La variante a été mesurée avec CPython 3.13.7 et la référence avec 3.14.0 ; les deux utilisent LuaHBTeX 1.24.0. Voir le [profil brut des passes](validation-latex-pass-profile-20261001.json).

### Un seul lien PDF pour le nom et le folio — 1er octobre 2026

La commande de renvoi rend maintenant le nom de la personne et son numéro de page cliquables dans un seul lien. Sur la même fixture et le même runtime que la macro précédente à deux liens, deux compilations de trois passes prennent 116,948 s et 116,991 s (médiane 116,969 s), soit 19,36 % de moins que la médiane précédente de 145,045 s. Le PDF balisé de 194 pages baisse de 226 728 octets (11,65 %), de 1 946 325 à 1 719 597 octets. Le pic du dossier temporaire mesuré baisse de 4,93 %. L’arbre contient 2 869 éléments Link au lieu de 4 814 ; les 4 905 destinations nommées restent présentes. Le texte extrait est identique octet pour octet au PDF antérieur. Le hash structurel change comme attendu, car l’arbre de liens est regroupé ; les pages 12–13 des connexions familiales ont été relues pour la mise en page. Les détails figurent dans le [profil brut des passes](validation-latex-pass-profile-20261001.json).

Le profil par blocs précise l’origine des longues connexions familiales : les 50 sections qui ont des enfants contiennent 200 liens parent-enfant et prennent 10,90 s sur les deux premiers blocs de 25 ; les 51 sections sans enfant prennent environ 2,50 s. Ces mesures incluent les coupures de page. Les blocs de 25 fiches et références de l’annexe sont beaucoup plus réguliers, autour de 1,1 à 1,4 s. L’association avec les listes relationnelles est nette, mais le chronométrage ne sépare pas leur composition du travail de mise en page et de sortie des pages.

### Enfants et filiations regroupés — 1er octobre 2026

La section PDF des liens familiaux affiche maintenant chaque enfant une seule fois, puis regroupe ses parents enregistrés et les types de relation. Cette présentation suit le regroupement enfant-d’abord déjà utilisé par le renderer HTML, tout en conservant les liens de filiation enregistrés. La référence est le renderer à lien unique de la PR #190 ; les deux variantes utilisent la même fixture ramifiée et vingt portraits synthétiques de 96 × 72 pixels sur macOS 27.0 arm64, CPython 3.13.7 et LuaHBTeX 1.24.0.

| Cas | Référence | Regroupement | Écart |
| --- | ---: | ---: | ---: |
| Source LaTeX N=100 | 821 686 octets | 801 556 octets | −20 130 octets (−2,45 %) |
| Compilation PDF N=100, deux exécutions | 116,948 s ; 116,991 s | 111,406 s ; 110,942 s | Médiane 116,969 → 111,174 s (−4,95 %) |
| PDF final N=100 | 1 719 597 octets | médiane 1 628 692 octets | −90 905 octets (−5,29 %) |
| Source LaTeX N=1 000 | 8 119 289 octets | 7 917 825 octets | −201 464 octets (−2,48 %) |
| Compilation PDF N=1 000 | `timeout` après 122,715 s | `timeout` après 122,718 s | Pas d’amélioration mesurable ; aucun PDF produit |

Le PDF regroupé N=100 est balisé, fait 195 pages et pèse 1 628 695 octets. Poppler compte 2 669 éléments Link dans l’arbre, contre 2 869 auparavant ; les 1 805 cibles nommées propres au livre sont toutes présentes. Les pages 12–13 montrent les filiations regroupées ; le type de relation peut passer seul sur la ligne suivante, où il reste lisible. La source N=1 000 et sa compilation montrent que cette réduction ne résout pas le dépassement de délai des livres longs. L’aperçu local se trouve dans `output/pdf/gramps-fancy-book-parentage-grouping-preview-20261001.pdf` ; les notices et portraits sont fictifs. Il s’agit de mesures ciblées, et non d’une qualification de performance sur trois exécutions.

### Renvoi direct pour les citations à un seul appel — 1er octobre 2026

Dans l’annexe documentaire, une citation ayant un seul appel utilise maintenant un paragraphe « Voir »/« See » localisé et conserve le lien cliquable vers sa fiche ou sa notice familiale. Les citations ayant plusieurs appels gardent une liste. Chaque ancre d’appel est conservée ; le changement supprime la liste imbriquée à un seul élément, fréquente dans le jeu ramifié.

| Cas | Aperçu avec filiations regroupées | Renvoi direct | Écart |
| --- | ---: | ---: | ---: |
| Source LaTeX N=100 | 801 556 octets | 794 104 octets | −7 452 octets (−0,93 %) |
| Compilation PDF complète N=100 | médiane 111,174 s sur deux exécutions | 101,429 s, une exécution | −8,8 % par rapport à la médiane précédente ; mesure ciblée |
| PDF final N=100 | 1 628 695 octets | 1 583 991 octets | −44 704 octets (−2,74 %) |
| Pages PDF | 195 | 193 | −2 |
| Éléments structurels `L` / `LI` / `Link` | 972 / 1 854 / 2 669 | 696 / 1 578 / 2 669 | −276 listes et éléments de liste ; liens inchangés |

Le dernier PDF balisé conserve les 1 805 cibles nommées du livre. La page physique 123 a été rendue à 130 ppp et examinée : les appels uniques sont présentés en paragraphes « Voir », tandis que les appels multiples restent en puces ; aucune coupure ni superposition n’a été observée sur cette page ciblée. La comparaison de durée porte sur une exécution contre la médiane des deux précédentes et ne constitue pas une estimation stable. La source et la compilation PDF complète N=1 000 n’ont pas encore été remesurées après ce changement. L’aperçu PDF local (`../output/pdf/gramps-fancy-book-single-call-citation-preview-20261001.pdf`) contient des notices et portraits fictifs ; SHA-256 `3cf5f9b8025258db353f71d2292875c5bc0e5d244d5bbbda47f9cd143dfc2578`.

### Sections unitaires des fiches individuelles — 1er octobre 2026

Pour une fiche avec un seul événement ou une seule citation distincte, le PDF affiche maintenant l’événement ou le renvoi cliquable vers la source dans un paragraphe sous son titre. Les groupes de plusieurs événements ou sources restent des listes. Dans la fixture ramifiée N=100, les 202 fiches ont un événement et une référence distincte à une source. Seize fiches ont deux appels de citation qui désignent la même entrée ; le renderer continue à dédupliquer les entrées répétées.

| Cas | Aperçu avec renvoi simple | Paragraphes de fiche | Écart |
| --- | ---: | ---: | ---: |
| Source LaTeX N=100 | 794 104 octets | 786 832 octets | −7 272 octets (−0,92 %) |
| Compilation complète N=100 | 101,429 s, une exécution | 93,419 s, une exécution | −8,010 s (−7,90 %) ; indicatif seulement |
| PDF balisé N=100 | 1 583 991 octets ; 193 pages | 1 470 734 octets ; 177 pages | −113 257 octets (−7,15 %) ; −16 pages |
| Structure `L` / `LI` / `Link` | 696 / 1 578 / 2 669 | 292 / 1 174 / 2 669 | −404 listes et éléments de liste ; liens inchangés |

Le PDF candidat conserve exactement les mêmes 1 805 cibles nommées du livre et les 3 073 annotations de lien que l’aperçu précédent. Les pages physiques 57–58 ont été rendues à 130 ppp et examinées ; les lignes compactes des événements et sources restent lisibles, sans coupure ni superposition visible. Les deux durées sont des mesures isolées et ne constituent pas une estimation stable ; le cas N=1 000 et les fiches comportant plusieurs événements ou citations distinctes restent à mesurer. Voir la [mesure brute](validation-latex-profile-singletons-20261001.json) et l’aperçu local (`../output/pdf/gramps-fancy-book-single-event-profile-preview-20261001.pdf`, SHA-256 `6ae26746fcc1588982c7be0786226f6ad8de146636280bc5e9846cafc698c3ac`).

### Notices familiales à entrée unique — 1er octobre 2026

Dans les notices familiales PDF, un événement unique et une source distincte unique sont maintenant présentés en paragraphes sous leurs titres ; plusieurs entrées restent en listes. La fixture ramifiée N=100 comprend 101 notices, chacune avec un événement et une citation distincte. Cette variante est comparée au PDF après les sections unitaires des fiches individuelles.

| Cas | Référence après fiches unitaires | Notices familiales compactées | Écart |
| --- | ---: | ---: | ---: |
| Source LaTeX N=100 | 786 832 octets | 783 196 octets | −3 636 octets (−0,46 %) |
| Compilation complète N=100 | 93,419 s, une exécution | 90,315 s, une exécution | −3,104 s (−3,32 %), indicatif |
| PDF balisé N=100 | 1 470 734 octets ; 177 pages | 1 409 982 octets ; 169 pages | −60 752 octets (−4,13 %) ; −8 pages |
| Structure `L` / `LI` / `Link` | 292 / 1 174 / 2 669 | 90 / 972 / 2 669 | −202 listes et éléments de liste ; liens inchangés |

Les 1 805 destinations nommées du livre et les 3 073 annotations de lien restent identiques. Les pages physiques 29 et 31 ont été rendues à 130 ppp et examinées ; aucun texte coupé ni chevauchement visible. La durée repose sur une seule exécution de chaque variante. À N=1 000, la source passe de 7 771 881 à 7 735 845 octets (−0,46 %), mais la compilation expire après environ 122,65 s dans les deux cas et ne produit aucun PDF. Le pic temporaire échantillonné est de 22 266 020 octets pour la référence et 23 310 001 pour la variante ; ce relevé ponctuel n’établit pas une baisse d’espace disque. Le délai des grands livres reste à résoudre. Voir les [données brutes](validation-latex-family-notices-20261001.json) et l’aperçu local (`../output/pdf/gramps-fancy-book-single-event-notice-preview-20261001.pdf`, SHA-256 `0b3b395928504f2ad8a1b6412d878443a64200be5fe533892f080a2804db00b0`).

### Profil partiel de la première passe LuaLaTeX — N=1 000 — 1er octobre 2026

La source courante après la compaction des notices fait 7 735 845 octets pour 2 002 personnes, 1 001 familles, 3 003 événements, 3 003 citations, 1 001 notices, 2 002 fiches et 200 portraits synthétiques. Une copie temporaire a reçu des marqueurs Lua `os.clock()` avant les principales sections et tous les cent éléments dans les sections volumineuses. Une seule passe a été lancée avec les options de production, dans un répertoire neuf ; la limite diagnostique était de 121 s. Les temps ci-dessous sont les intervalles CPU rapportés par Lua, arrondis au millième ; l’instrumentation ajoute des marqueurs au document et ses coûts n’ont pas été soustraits.

| Section ou bloc achevé | CPU (s) |
| --- | ---: |
| Couverture, préliminaires et sommaire | 0,022 |
| Ascendance | 0,030 |
| Descendance | 10,686 |
| Connexions familiales, 500 sections avec enfants | 39,627 |
| Connexions familiales, 500 sections sans enfants | 13,910 |
| Fin de la section des connexions | 0,056 |
| Notices familiales, 1 000 premières | 29,593 |
| Fin des notices familiales | 0,047 |
| Fiches individuelles, 800 premières sur 2 002 | 24,365 |

LuaHBTeX a atteint le délai après 121,023 s. Le journal indique qu’il se trouvait encore dans la section des fiches ; l’annexe documentaire et l’index n’ont pas été atteints. Le fichier PDF interrompu (3 727 852 octets) n’a pas de dictionnaire de fin ni de table xref : ce n’est pas un PDF livrable. Ce profil partiel montre que les connexions familiales avec liens de filiation, les notices et les fiches consomment déjà presque tout le budget d’une passe ; il ne mesure pas le temps de l’annexe. Les résultats orientent la prochaine analyse vers les liens de filiation et la production répétée des liens de page. Ils ne constituent pas une mesure de performance non instrumentée. Les détails sont dans les [données brutes](validation-latex-first-pass-n1000-20261001.json).

### Essai rejeté — marques d’en-tête répétées — N=100 — 1er octobre 2026

Une variante temporaire n’émettait `\markright` dans les connexions familiales, les notices et les fiches que lorsque le texte du contexte changeait.

| Mesure | Référence | Variante |
| --- | ---: | ---: |
| Compilation complète N=100 | 90,315 s | 90,613 s |
| PDF | 1 409 982 octets ; 169 pages | 1 410 100 octets ; 169 pages |
| Destinations nommées comptées par pypdf | 3 898 | 3 898 |
| Annotations de lien | 3 073 | 3 073 |
| PDF balisé | oui | oui |
| Texte extrait par page identique | oui | non |

Les deux extractions comptent 215 988 caractères, mais les en-têtes de contexte et la pagination de plusieurs entrées diffèrent, notamment aux pages physiques 13–16 et 30–31. L’aperçu temporaire a donc été supprimé et le changement de source annulé.

Ces durées reposent sur une exécution chacune et ne sont pas directement comparables : elles ont été mesurées avec CPython 3.14.0 et 3.13.7 respectivement. Le résultat ne démontre aucun gain de performance et ne conserve pas le rendu existant. Voir les [données brutes](validation-latex-running-header-marks-20261001.json) ; le dernier aperçu accepté reste celui des [notices compactées](../output/pdf/gramps-fancy-book-single-event-notice-preview-20261001.pdf).

### Échappement LaTeX par table de traduction — N=1 000 — 1er octobre 2026

`escape_latex_text` utilise maintenant `str.translate` avec une table de traduction pré-calculée, au lieu d’un générateur Python caractère par caractère. Sur la fixture ramifiée avec 1 000 unions descendantes, 2 002 personnes et 200 portraits synthétiques, les trois mesures de génération de source passent d’une médiane de 2,202271 s à 2,034793 s (−7,61 %, soit −0,167478 s). Elles utilisent le même CPython 3.14.0, le même Mac et trois répétitions de chaque variante.

La source LaTeX reste exactement identique : 7 735 845 octets et SHA-256 `26cc3b3a77946413b08f19ee058de3ba451d7e359e40c32eb6167c94c05950e9` avant et après. La compilation PDF n’a pas été répétée : ce changement accélère seulement la génération Python de la source et n’allège pas le travail dominant de LuaLaTeX. Le délai N=1 000 reste à résoudre. Voir les [mesures brutes](validation-latex-text-translation-20261001.json).

### Cibles PDF en Base64 URL sûre — N=1 000 — 1er octobre 2026

Les identifiants de cibles hyperref passent du Base32 minuscule sans remplissage au Base64 URL sûr sans remplissage (`A–Z`, `a–z`, chiffres, `-` et `_`). Sur la même fixture ramifiée N=1 000, avec 200 portraits synthétiques, trois mesures de génération LaTeX passent d’une médiane de 2,034938 s à 0,613341 s (−69,86 %). La source générée passe de 7 735 845 à 7 167 003 octets (−568 842 octets, −7,35 %). Les deux séries utilisent CPython 3.14.0 sur le même Mac.

Un livre fictif N=10 a été compilé avec LuaHBTeX 1.24.0 en un PDF A4 balisé de 22 pages. `pypdf` y trouve 452 destinations nommées, dont 204 cibles `target-*` avec l’alphabet attendu, ainsi que 342 annotations de lien sans destination interne nommée manquante. Les pages physiques 5, 6, 14 et 22 ont été rendues à 120 ppp et examinées. Cette recette confirme la compilation et les renvois sur ce petit livre ; la compilation N=100/N=1 000 n’a pas été répétée et le délai des grands livres n’est pas considéré comme résolu. Voir les [données brutes](validation-latex-url-safe-targets-20261001.json) et l’aperçu local `../output/pdf/gramps-fancy-book-target-encoding-preview-20261001.pdf` (SHA-256 `feda0dcb2bd5ab550dff8592ba673d4271bff952757705a126bcf426c2017078`).
