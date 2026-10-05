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

Le premier script mesure la construction du modèle, la préparation des dérivés, la sérialisation JSON, les deux moteurs de rendu et l’archive ZIP. Il compile aussi un PDF sur le petit cas ramifié. Les portraits PNG pseudo-aléatoires font 96 × 72 pixels par défaut ; `--portrait-size WIDTHxHEIGHT` permet de choisir une autre taille avec `--with-media`. Le script limite une image synthétique à 24 millions de pixels et le volume estimé des sources à 256 Mio. Depuis le 4 octobre, il place explicitement le dossier `src` du checkout en tête du chemin Python avant ses imports du projet : il mesure ainsi le code courant même si l’environnement virtuel contient une ancienne installation non éditable. Le préfixe `PYTHONPATH=src` des commandes ci-dessus reste valide.

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

Un livre fictif N=10 a été compilé avec LuaHBTeX 1.24.0 en un PDF A4 balisé de 22 pages. `pypdf` y trouve 452 destinations nommées, dont 204 cibles `target-*` avec l’alphabet attendu, ainsi que 342 annotations de lien sans destination interne nommée manquante. Les pages physiques 5, 6, 14 et 22 ont été rendues à 120 ppp et examinées.

Une comparaison séparée N=100, avec 20 portraits synthétiques, a été exécutée une fois par variante sur macOS 27.0 arm64, CPython 3.14.0 et LuaHBTeX 1.24.0 :

| Mesure | Base32 | Base64 URL sûre | Écart |
| --- | ---: | ---: | ---: |
| Génération LaTeX | 0,205227 s | 0,061724 s | −69,92 % |
| Source LaTeX | 783 196 octets | 725 713 octets | −57 483 (−7,34 %) |
| Compilation PDF complète | 90,437760 s | 84,805061 s | −5,632699 s (−6,23 %) |
| PDF | 1 409 982 octets | 1 405 934 octets | −4 048 (−0,29 %) |

Le temps de compilation repose sur une exécution par variante et reste indicatif. Le PDF N=1 000 n’a pas été recompilé ; son délai précédent reste non résolu. Voir les [données brutes](validation-latex-url-safe-targets-20261001.json) et l’aperçu local `../output/pdf/gramps-fancy-book-target-encoding-preview-20261001.pdf` (SHA-256 `feda0dcb2bd5ab550dff8592ba673d4271bff952757705a126bcf426c2017078`).

### Destinations PDF compactées par condensat BLAKE2s — 1er octobre 2026

Les noms Hyperref gardent le préfixe `target-` et encodent maintenant en Base64 URL sûre sans remplissage un condensat BLAKE2s de 96 bits de l’identifiant stable. Le nom obtenu est déterministe, indépendant de la pagination et beaucoup plus court que l’encodage réversible de l’identifiant complet. Pour 17 768 cibles, la probabilité théorique d’au moins une collision est d’environ 2 × 10⁻²¹.

Sur le jeu ramifié N=1 000 avec 2 002 personnes et 200 portraits fictifs, la source baisse de 7 167 003 à 5 147 816 octets (−28,17 %). La génération LaTeX médiane passe de 0,612325 à 0,640712 s (+0,028387 s, +4,64 %), un coût négligeable face à la compilation PDF. Les mesures de chaque variante comprennent trois répétitions sur macOS 27 arm64 et CPython 3.14.0 ; le point de référence Base64 a été rejoué dans le même environnement avec l’encodeur précédent.

Sur le jeu N=100 avec 20 portraits, une compilation par variante passe de 84,805061 à 68,898323 s (−15,906738 s, −18,76 %). La source baisse de 725 713 à 521 949 octets (−28,08 %). Le PDF candidat pèse 1 455 375 octets, soit 49 441 octets (+3,52 %) de plus que la référence. La durée vient d’une exécution par variante et reste indicative.

Un aperçu synthétique N=10 compilé avec LuaHBTeX 1.24.0 fait 23 pages A4 balisées. `pypdf` trouve 455 destinations nommées, dont 206 cibles au format attendu, 342 annotations de lien et aucune destination interne manquante. Les pages physiques 1, 6, 7, 11, 20 et 23 ont été rendues à 120 ppp et examinées. Voir les [mesures détaillées](validation-latex-short-targets-20261001.json) et l’[aperçu PDF](../output/pdf/gramps-fancy-book-short-target-digest-preview-20261001.pdf), SHA-256 `3757bc729a94a5c885fb26a2581417c4fe009148156b7978ab65af71b5faf51b`.

La compilation PDF N=1 000 n’a pas été relancée ; le délai précédent reste à résoudre. Les personnes, événements, médias et citations de cet aperçu sont fictifs.

### Essai rejeté — destinations PDF indexées — 1er octobre 2026

Un prototype temporaire remplaçait les identifiants de cibles par des labels `target-0`, `target-1`, etc. Il triait les graines Base64 réversibles, puis réécrivait les références dans `\gfbpagelink`, `\hyperlink`, `\hypertarget` et `\label`. Ce système dépend de l’ensemble complet des cibles : ajouter une cible dont la graine se trie avant une cible existante décale ses labels. Le commentaire de revue de la PR #201 a relevé que cela contrevient au contrat d’ancres dérivées de l’identité dans [la décision 001](decisions/001-data-contracts.md). Le prototype a donc été retiré ; les destinations de production restent dérivées de l’identité par les condensats BLAKE2s 96 bits de la PR #200.

La mesure du prototype reste utile pour isoler le coût de ces noms courts. Sur N=1 000, la source LaTeX passe de 7 167 003 octets avec Base64 direct à 4 532 920 octets (−36,76 %) et de 5 147 816 octets avec BLAKE2s à 4 532 920 (−11,95 %). Trois mesures de génération donnent une médiane de 0,873835 s, contre 0,640712 s avec BLAKE2s. Une compilation complète du prototype a réussi en trois passes de 261,899, 259,468 et 259,112 s, pour 781,415 s au total et un PDF de 13 215 543 octets ; cet essai diagnostique relevait temporairement les plafonds à 420 s par passe et 900 s au total. Les limites de production restent 120 s par passe et 180 s au total, et le délai N=1 000 n’est donc pas résolu.

Sur N=100, une compilation par variante donne 68,629 s avec le prototype séquentiel et 68,898 s avec BLAKE2s ; l’écart de 0,39 % est indicatif. Le PDF du prototype passe de 1 455 375 à 1 371 810 octets (−5,74 %). Son aperçu N=10 est un PDF A4 balisé de 23 pages ; `pypdf` relève 455 destinations nommées, 206 cibles numériques uniques et denses, 342 annotations de lien dont 210 internes, sans destination manquante. Il s’agit d’un artefact de prototype, pas du rendu courant. Voir les [données brutes](validation-latex-indexed-targets-20261001.json) et l’[aperçu du prototype](../output/pdf/gramps-fancy-book-indexed-targets-preview-20261001.pdf), SHA-256 `60920f931695a1593259640acfd1b3c89378528d9a29f90ff64c423ba93c7aee`.

### Profil instrumenté d’une passe LuaLaTeX — N=1 000 — 1er octobre 2026

Avec les destinations stables BLAKE2s de production, une passe instrumentée du jeu ramifié N=1 000 s’est achevée en 274,902 s. Les marqueurs CPU placent environ 118,174 s dans l’annexe documentaire, 46,416 s dans les fiches, 32,010 s dans les connexions familiales et 21,692 s dans les notices. Les pages sont composées de façon différée par TeX ; ces intervalles entre marqueurs indiquent les postes dominants, mais ne séparent pas exactement tous les coûts d’expédition des pages. Le profil a été mesuré avant le retrait des ancres d’appel non référencées décrit ci-dessous. Voir les [points de mesure bruts](validation-latex-n1000-section-profile-20261001.json).

### Ancres d’appel de citation non référencées retirées — 1er octobre 2026

Chaque appel de citation dans l’annexe avait sa propre destination PDF, mais aucun lien ne visait ces destinations : le libellé visible de chaque appel renvoie déjà directement à la fiche ou à la notice. Le renderer n’émet plus ces ancres inutilisées. Les noms des destinations effectivement liées restent dérivés de l’identité par BLAKE2s.

Sur N=1 000, cette suppression de 3 270 destinations réduit la source LaTeX de 5 147 816 à 4 918 916 octets (−4,45 %) ; la médiane de génération passe de 0,640712 à 0,620243 s. Sur N=100, une compilation par variante donne 67,994 s au lieu de 68,898 s (−1,31 %, écart indicatif) et le PDF passe de 1 455 375 à 1 437 997 octets (−1,19 %). L’aperçu balisé de 169 pages garde ses 3 073 annotations de lien et ne contient aucune destination interne manquante. Les pages 12, 29, 49, 99 et 163 ont été revues à 110 ppp ; la mise en page reste lisible dans les connexions, notices, fiches, annexe et index. Le PDF N=1 000 n’a pas été recompilé après ce changement. Voir les [données brutes](validation-latex-call-anchor-pruning-20261001.json) et l’[aperçu PDF](../output/pdf/gramps-fancy-book-no-unused-call-targets-preview-20261001.pdf), SHA-256 `74eb25edc8d9c3504585beef7172e49256d9b165fc6500684e544a5104465923`.

### Métadonnées de l’annexe regroupées par citation — 1er octobre 2026

Les détails de source, dépôts, URL et légendes de médias d’une citation restent affichés sur des rangées distinctes, mais sont composés comme un seul paragraphe balisé. Les appels multiples gardent leur liste et les renvois vers les fiches ou notices ne changent pas.

Sur N=100, une compilation candidate prend 63,967656 s, contre 67,993585 s pour la variante précédente (−5,92 %, une exécution mesurée par variante). Le PDF balisé A4 passe de 169 à 165 pages et de 1 437 993 à 1 398 169 octets (−2,77 %). Les 3 073 annotations de lien, dont 1 861 internes, restent identiques ; aucune destination nommée interne ne manque, et l’ensemble des cibles d’identité `target-*` reste identique. Le texte extrait est identique après retrait des en-têtes courants et folios recalculés. Les pages physiques 99 (annexe) et 165 (index) ont été examinées à 110 ppp, sans chevauchement ni coupure observée. La source N=1 000 baisse de 4 918 916 à 4 900 298 octets (−0,38 %) ; aucune version finale multipasse N=1 000 n’a été produite et son délai reste à qualifier. Voir les [données brutes](validation-latex-appendix-metadata-20261001.json) et l’[aperçu PDF](../output/pdf/gramps-fancy-book-appendix-metadata-compact-preview-20261001.pdf), SHA-256 `6c51b6cb0756faacd2bff70676af756b04f63a54d09ded006d5b7aa90c66ebbc`.

### Profil actuel après réductions ciblées — une passe N=1 000

Une nouvelle passe instrumentée sur le renderer courant a terminé avec LuaHBTeX. Les intervalles CPU entre marqueurs sont de 38,963 s pour les connexions familiales, 21,979 s pour les notices, 46,727 s pour les fiches, 108,100 s pour l’annexe et 21,048 s dans l’index jusqu’au point de contrôle des 2 000 entrées. L’intervalle CPU de l’annexe était de 118,174 s au profil antérieur aux deux réductions ; cette différence de 10,074 s (−8,52 %) ne sépare pas les effets de la suppression des ancres d’appel et du regroupement des métadonnées.

La mesure murale directe de cette passe, chronométrée autour du processus LuaLaTeX, est de 272,254 s. Le diagnostic n’avait pas de délai d’expiration ; cette durée dépasse les limites de production de 120 s par passe et 180 s au total. Les intervalles entre marqueurs sont des mesures CPU et ne servent pas à comparer ces limites murales. LuaLaTeX a écrit un PDF diagnostique A4 balisé de 1 572 pages, mais une seule passe ne stabilise pas les références : ce fichier n’est pas un aperçu final. Aucun PDF multipasse N=1 000 n’a été produit après ces changements. Voir les [points de mesure complets](validation-latex-n1000-current-profile-20261001.json).

### Paragraphes de citation regroupés — 2 octobre 2026

Le titre et les rangées de métadonnées de chaque citation sont maintenant composés dans un même paragraphe avec des sauts de ligne visibles. Quand aucun média rendu ne s’intercale, le renvoi simple vers la fiche ou la notice partage aussi ce paragraphe. Les reproductions restent à leur place et les appels multiples conservent leur liste.

Sur N=100, le PDF balisé A4 candidat passe de 165 à 161 pages et de 1 398 169 à 1 362 256 octets (−2,57 %). Les 303 entrées, leurs 579 appels, les 1 861 liens internes, les 1 475 cibles d’identité et les 317 URI distinctes sont présents ; aucune destination interne ne manque et le texte des appels reste identique après normalisation des folios. Le nombre d’annotations passe de 3 073 à 3 079, avec six annotations externes supplémentaires et le même ensemble d’URI. Les pages physiques 99, 100, 153, 154, 155 et 161 ont été examinées à 110 ppp ; aucun chevauchement ni texte coupé n’a été observé. La structure PDF passe de 13 339 à 12 215 éléments. La compilation candidate a pris 65,629 s contre 63,968 s pour la référence, une exécution par variante mesurée avec des versions Python différentes ; cela ne permettait pas de conclure sur la durée. La comparaison répétée à environnement constant ci-dessous remplace cette estimation.

Sur N=1 000, la source LaTeX baisse de 11 144 octets (−0,23 %). Une passe LuaHBTeX diagnostique mesure 101,872 s CPU dans l’annexe, contre 108,100 s au profil précédent (−5,76 %), et 262,122 s murales contre 272,254 s (−3,72 %). Ce sont des mesures uniques, sur la même fixture, le même macOS et le même compilateur ; le profil antérieur utilisait CPython 3.14.0 et celui-ci CPython 3.12.14. Le PDF diagnostique balisé passe de 1 572 à 1 535 pages et de 13 582 172 à 13 242 192 octets, mais ses références ne convergent pas en une passe. Son temps mural dépasse encore les limites de production de 120 s par passe et 180 s au total ; le PDF final multipasse N=1 000 reste à produire. Voir les [données brutes](validation-latex-citation-paragraphs-20261002.json).

### Compilation répétée N=100 après regroupement — 2 octobre 2026

La variante de référence sans regroupement (commit `c6d0480`) et le renderer regroupé (commit `11bc028`) ont chacun été compilés trois fois sur la même machine, avec la même fixture ramifiée et le même outil de mesure. L’ordre des six exécutions était référence, candidate, candidate, référence, référence, candidate. Les six compilations multipasses via le helper de production ont réussi. L’environnement était macOS 27.0 arm64, CPython 3.12.10, Mistune 3.3.4, Pillow 9.5.0 et LuaHBTeX 1.24.0 (TeX Live 2026).

| Mesure | Sans regroupement — trois valeurs ; médiane | Paragraphes regroupés — trois valeurs ; médiane | Variation des médianes |
| --- | ---: | ---: | ---: |
| Compilation PDF complète (s) | 65,344950 ; 66,342804 ; 66,120247 — **66,120247** | 63,398461 ; 63,673968 ; 63,491654 — **63,491654** | −3,98 % |
| Source LaTeX (octets) | 496 971 ; 496 971 ; 496 971 — **496 971** | 495 847 ; 495 847 ; 495 847 — **495 847** | −0,23 % |
| PDF final (octets) | 1 398 173 ; 1 398 173 ; 1 398 167 — **1 398 173** | 1 362 252 ; 1 362 253 ; 1 362 256 — **1 362 253** | −2,57 % |
| Pic temporaire échantillonné (octets) | 3 274 166 ; 3 274 158 ; 3 274 166 — **3 274 166** | 3 238 060 ; 3 238 062 ; 3 238 064 — **3 238 062** | −1,10 % |

La médiane de compilation s’améliore de 2,629 s sur cette fixture. Elle reste légèrement au-dessus du budget provisoire de 60 s. Cette répétition confirme le gain à N=100, mais ne qualifie pas N=1 000 : le profil diagnostique précédent reste à 262,122 s pour une passe, et aucun PDF final multipasse n’a été produit à cette taille. Le pic temporaire est échantillonné toutes les 100 ms ; de très courts pics peuvent manquer. Les rapports complets des six exécutions figurent dans les [données brutes](validation-latex-citation-paragraph-repeats-20261002.json).

### Ancres LaTeX factorisées — 2 octobre 2026

Chaque ancre d’identité appelle maintenant une macro LaTeX avec son identifiant une seule fois. Cette macro développe exactement les deux commandes précédentes, `\hypertarget` et `\label` : la destination cliquable et le renvoi de page gardent la même clé. Sur la source ramifiée N=1 000 avec 200 portraits synthétiques, les 14 498 appels de macro ont été développés dans une copie de contrôle ; le texte obtenu est identique octet pour octet à la source de référence. La source générée baisse de 4 889 154 à 4 381 781 octets (−10,38 %).

Trois compilations complètes N=100 par variante, alternées dans le même environnement macOS 27 arm64, CPython 3.12.10 et LuaHBTeX 1.24.0, ont toutes réussi. La durée médiane passe de 63,431 à 63,317 s (−0,18 %) : cet écart est trop faible pour établir un gain de temps. La source N=100 baisse de 495 847 à 444 279 octets (−10,40 %) et le pic temporaire échantillonné de 3 238 060 à 3 186 495 octets (−1,59 %) ; la taille médiane du PDF reste pratiquement identique (1 362 251 contre 1 362 254 octets). La fixture utilisait Pillow 9.5.0, inférieur au minimum optionnel déclaré de 10 ; les deux variantes ont utilisé cette même version, et ce relevé ne qualifie pas le traitement des médias. Il ne résout pas le délai de compilation N=1 000. Voir les [six rapports et la comparaison des sources](validation-latex-anchor-macro-20261002.json).

### URL LaTeX sans répétition de l'adresse — 2 octobre 2026

Les 909 appels de rendu d'URL de la fixture N=100 transmettent maintenant à `\bookurl` le nom d'hôte et le suffixe une seule fois chacun. La macro reconstitue l'URL complète pour le lien cliquable et conserve les deux réglages de coupure visuelle. Sur la source N=100 instrumentée, cette factorisation retire 34 208 octets (444 452 → 410 244, −7,70 %) ; sur N=1 000 avec 9 009 appels, elle retire 344 541 octets (4 381 781 → 4 037 240, −7,86 %). Pour chaque appel du corpus, l'URL précédente égale exactement la concaténation des deux arguments nouveaux.

Une compilation multipasse N=100 produit un PDF A4 balisé de 161 pages. Par rapport à l'aperçu précédent, le texte extrait et les 3 079 cibles de liens sont identiques, dont 1 218 annotations d'URI et 1 861 renvois internes ; les 3 560 destinations nommées sont conservées. Le PDF passe de 1 362 256 à 1 362 254 octets. Le premier passage instrumenté prend 20,507 s pour la référence et 20,751 s pour la variante ; ces mesures isolées ne démontrent aucun gain de compilation. Le cas N=1 000 reste hors du délai de production et n'a pas été recompilé. L'[aperçu PDF](../output/pdf/gramps-fancy-book-url-source-preview-20261002.pdf) utilise uniquement des données fictives ; voir les [données brutes](validation-latex-url-source-20261002.json).

Le profil isolé de l'annexe a aussi comparé une URL visible en un seul `\nolinkurl` et, à titre diagnostique seulement, l'absence de `\href`. Le premier essai n'améliore pas la passe unique (20,982 s contre 20,507 s) ; l'absence de lien la réduit à 18,045 s, mais retire les liens cliquables requis. Aucun de ces deux prototypes n'est livré.

### Compilation complète du grand livre N=1 000 — 2 octobre 2026

Le jeu ramifié fictif N=1 000 (2 002 personnes, 1 001 familles, 3 003 événements, 3 003 citations et 200 portraits synthétiques de 96 × 72 pixels) a été rendu avec la source actuelle. Le helper LuaLaTeX de production a été invoqué directement avec des plafonds diagnostiques de 600 s par passe et 1 800 s au total. Les trois passes ont réussi en 253,537, 261,122 et 276,413 s, soit 791,078 s (13 min 11 s) au total. Le PDF final A4 balisé compte 1 535 pages et 13 103 813 octets. Son journal final ne contient ni renvoi indéfini ni débordement de marge reconnu par le helper. Ses 31 271 annotations de lien comprennent 19 210 renvois internes, tous résolus parmi 34 883 destinations nommées, et 12 061 liens d'URI.

La couverture et les pages physiques 500, 1 000 et 1 535 ont été rendues à 900 pixels pour une inspection ciblée, sans texte coupé ni chevauchement observé. Cet essai ne revoit pas les 1 535 pages une par une et ne passe pas par l'interface Gramps. Le résultat démontre que le renderer converge sur ce volume lorsque la limite le permet ; il ne respecte toujours pas le budget provisoire de 60 s. L'option **Autoriser une compilation PDF prolongée (jusqu’à 30 minutes)** conserve le plafond standard par défaut et applique les plafonds du diagnostic seulement aux exports PDF qui la sélectionnent. Voir les [mesures brutes](validation-latex-n1000-extended-20261002.json) et l'[aperçu local](../output/pdf/gramps-fancy-book-n1000-extended-preview-20261002.pdf).

### Essais de lecture des folios de l’annexe — 4 octobre 2026

Deux variantes temporaires ont remplacé `\pageref*` dans `\gfbpagelink` : une macro qui mémorise le numéro déjà lu pour chaque cible, puis une lecture directe avec `refcount` qui garde `\pageref*` comme repli pour une cible absente. Aucun changement du renderer n’a été retenu.

Sur le jeu ramifié N=100 sans médias (202 personnes, 101 familles et 303 citations), la compilation complète de référence prend 62,130 s ; la variante avec cache prend 62,178 s. Le texte extrait est identique. Les deux PDF balisés ont 112 pages, 2 980 annotations dont 1 758 liens internes, et 3 491 destinations nommées ; leur taille diffère de quatre octets. Avec un seul run par variante, l’écart de durée ne montre pas de gain. La variante directe `refcount` prend 61,450 s lors d’un seul run ; son PDF conserve ces mêmes nombres de pages, annotations, liens internes et destinations. Sur N=10, une comparaison directe référence / `refcount` confirme aussi l’identité du texte extrait, des 17 pages, des 334 annotations, des 411 destinations et du balisage. Le helper de production converge dans chaque essai.

Une source N=1 000 sans médias contient 17 283 appels à `\gfbpagelink` pour 9 009 cibles ; 13 279 appels visent les 5 005 cibles répétées. Ce nombre rend la piste du cache plausible à grande taille, mais la mesure N=100 ne démontre aucun gain et le délai de compilation demeure dominé par la composition des sections. Les deux variantes sont donc rejetées faute de bénéfice mesuré ; le renderer garde `\pageref*` et ses diagnostics natifs. Le [relevé brut des essais](validation-latex-page-reference-20261004.json) consigne les limites de ces mesures uniques.

### Banc actuel avec code source explicite — 4 octobre 2026

Après correction du chemin d’import, le banc a été lancé directement depuis `.venv` sans `PYTHONPATH`, sur le jeu ramifié avec 2, 20 et 200 portraits synthétiques de 96 × 72 pixels. Chaque taille n’a été exécutée qu’une fois ; aucun PDF n’a été compilé dans ce relevé.

| N | Modèle (s) | Préparation médias (s) | JSON (s / octets) | HTML (s / octets) | LaTeX (s / octets) | ZIP HTML (s / octets) | Pic Python total (Mo) | Espace temporaire échantillonné (Mo) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 0,017 | 0,005 | 0,039 / 186 329 | 0,013 / 67 437 | 0,011 / 47 830 | 0,007 / 34 662 | 4,68 | 0,063 |
| 100 | 0,144 | 0,011 | 0,337 / 1 639 117 | 0,040 / 591 563 | 0,099 / 410 168 | 0,050 / 334 234 | 9,48 | 0,628 |
| 1 000 | 1,419 | 0,099 | 3,313 / 16 265 394 | 0,396 / 5 842 609 | 0,985 / 4 037 337 | 0,510 / 3 328 646 | 78,86 | 6,297 |

Ces valeurs constituent un point de contrôle reproductible du renderer Python courant, pas des médianes ni une nouvelle qualification PDF. Le pic Python exclut les allocations natives ; l’espace temporaire est échantillonné toutes les 100 ms. Les détails et les autres durées de fixture figurent dans les [données brutes](validation-benchmark-current-source-20261004.json).

### Trois répétitions du banc actuel — 4 octobre 2026

Le même banc a été relancé trois fois, directement depuis `.venv` sans `PYTHONPATH`, sur les trois tailles ramifiées et avec les portraits de 96 × 72 pixels. Les tailles de toutes les sorties sont stables entre répétitions. Le temps de création de la fixture N=10 montre un coût de démarrage dans le premier run (66 ms contre une médiane de 3,949 ms) ; les autres mesures du tableau sont les médianes des trois runs.

| N | Modèle (s) | Préparation médias (s) | JSON (s) | HTML (s) | LaTeX (s) | ZIP HTML (s) | JSON (octets) | HTML (octets) | LaTeX (octets) | ZIP (octets) | Pic Python total (Mo) | Espace temporaire (Mo) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 0,016774 | 0,001272 | 0,038904 | 0,004765 | 0,011069 | 0,006350 | 186 329 | 67 437 | 47 830 | 34 662 | 2,012 | 0,063 |
| 100 | 0,145455 | 0,010768 | 0,334421 | 0,040023 | 0,097771 | 0,050559 | 1 639 117 | 591 563 | 410 168 | 334 234 | 9,477 | 0,628 |
| 1 000 | 1,432872 | 0,102902 | 3,373380 | 0,401161 | 1,009488 | 0,505722 | 16 265 394 | 5 842 609 | 4 037 337 | 3 328 646 | 78,853 | 6,297 |

À N=1 000, les exporteurs Python restent sous 3,4 s pour le JSON et 1,1 s pour HTML, LaTeX et ZIP ; le modèle prend 1,433 s. Le pic Python total inclut les fixtures déjà chargées, mais exclut les allocations natives. L’espace temporaire reste un échantillon toutes les 100 ms. Ce relevé ne compile toujours pas le PDF balisé, dont le budget constitue le poste L8.3 non résolu. Voir les [neuf résultats bruts](validation-benchmark-current-source-repeats-20261004.json).

### Compilations PDF actuelles N=100 — 4 octobre 2026

La fixture ramifiée courante contient 202 personnes, 101 familles, 303 événements et citations ainsi que 20 portraits synthétiques de 96 × 72 pixels. Le banc, lancé sans `PYTHONPATH`, a compilé chaque PDF via le helper de production et ses passes de convergence. Les trois runs réussissent en 62,269 s, 62,773 s et 62,772 s ; la médiane est de 62,772 s. Les fichiers font 1 318 780, 1 318 771 et 1 318 772 octets (médiane : 1 318 772). La médiane dépasse de 2,772 s, soit 4,62 %, le repère provisoire de 60 s ; les trois exports restent sous la limite totale de production de 180 s.

Une quatrième sortie conservée, le [PDF synthétique courant](../output/pdf/gramps-fancy-book-current-source-n100-20261004.pdf), compte 133 pages A4 et porte le balisage PDF 2.0 avec langue `en-US`. L’inspection de sa structure trouve 3 532 destinations, 1 762 liens internes, 1 219 liens URI, aucune cible nommée interne manquante et 40 figures avec texte alternatif. Les pages physiques 1, 84 et 127 (couverture, fiche, annexe) ont été inspectées ; aucun chevauchement ni texte coupé n’est visible dans cet échantillon. La couverture garde volontairement sa composition aérée ; les pages courantes utilisent les marges de 20 mm. La revue ne couvre pas les 133 pages. Voir le [relevé complet](validation-pdf-current-source-n100-20261004.json).

### Essai rejeté — étiquettes de page des destinations non référencées — 4 octobre 2026

Une variante temporaire conservait toutes les destinations `\hypertarget`, mais n’émettait `\label` que pour les cibles utilisées par `\gfbpagelink` et donc par `\pageref*`. Sur la fixture N=1 000, 9 049 des 14 498 destinations reçoivent un folio ; 5 449 autres ancres ne portent pas d’étiquette de page et aucune cible du corpus n’est sans ancre. Ce comptage source n’inclut pas de compilation PDF N=1 000.

Sur N=100, les trois compilations de la variante convergent en 62,630, 64,429 et 64,388 s (médiane : 64,388 s), contre 62,269, 62,773 et 62,772 s (médiane : 62,772 s) pour la référence récente. La médiane candidate est supérieure de 1,616 s (2,57 %). La source passe de 410 168 à 416 613 octets (+1,57 %) et le PDF médian de 1 318 772 à 1 319 101 octets (+329). Les séries ne sont pas entrelacées ; ces mesures ne prouvent pas à elles seules une régression, mais elles n’établissent aucun gain. La variante est rejetée et le renderer reste inchangé. Les compilations candidates ont réussi les contrôles de convergence et de journal du helper de production ; aucune inspection séparée de la structure PDF n’a été faite. Voir le [relevé brut](validation-latex-unused-page-labels-20261004.json).

### Espacement resserré de l’annexe documentaire — 5 octobre 2026

La liste de l’annexe est maintenant composée dans un groupe local qui ajuste `\@listi` avant `\begin{itemize}`. Les valeurs `\itemsep=2pt`, `\parsep=0pt`, `\topsep=2pt` et `\partopsep=0pt` sont ainsi prises en compte dès l’initialisation de la liste, sans déborder sur les autres listes du livre.

Sur la fixture ramifiée N=100 avec médias, les trois compilations balisées de la variante convergent en 62,057, 62,779 et 62,580 s (médiane : 62,580 s), contre 62,269, 62,773 et 62,772 s (médiane : 62,772 s) pour la référence. L’écart médian est de −0,192 s (−0,31 %), trop faible pour établir un gain de temps. La source LaTeX augmente de 225 octets ; le PDF médian diminue de 2 534 octets (0,19 %). Le PDF passe de 133 à 130 pages et les pages examinées montrent davantage de notices dans le même espace.

Le PDF candidat reste A4, balisé PDF 2.0 et de langue `en-US`. Il contient les 303 entrées de citation et les 909 URL visibles ; leurs 317 destinations URI distinctes sont identiques à la référence. Les 1 762 liens internes restent résolus. Les deux versions ont 1 212 rectangles d’annotation URI couvrant du texte, avec une répartition identique par destination ; le candidat a huit rectangles vides de 2 × 2 points supplémentaires après recomposition. Le PDF contient 3 529 destinations nommées (les trois destinations `page.130` à `page.132` de la référence correspondent aux pages supprimées), 40 figures avec texte alternatif et aucun renvoi interne manquant. Les pages physiques 85, 105 et 124 de l’annexe ont été inspectées sans chevauchement ni coupure constatés ; la revue couvre trois pages, pas le document entier. Voir le [relevé des mesures et contrôles](validation-latex-compact-appendix-20261005.json) et le [PDF candidat](../output/pdf/gramps-fancy-book-compact-annex-n100-20261005.pdf), SHA-256 `d342bafdea506aa6d51f3d14c0e4c435c29374cba547e483d4364a4c16b45710`.

### Compilation diagnostique N=1 000 après compactage de l’annexe — 5 octobre 2026

La fixture ramifiée synthétique N=1 000, avec 2 002 personnes, 1 001 familles, 3 003 événements, 3 003 citations et 200 portraits de 96 × 72 pixels, a été recompilée depuis la source actuelle après la fusion de la PR #258. Le helper PDF de production a convergé avec les plafonds diagnostiques étendus de 600 s par passe et 1 800 s au total ; cette compilation directe du modèle synthétique ne passe pas par Gramps Desktop. La durée murale totale est de 741,591 s pour cette exécution unique. Le nombre et les durées individuelles des passes n’ont pas été consignés par le relevé.

Le PDF A4 balisé PDF 2.0 de langue `en-US` compte 1 239 pages et 12 620 918 octets. Il contient 34 587 destinations nommées et 29 427 annotations de lien : 17 341 renvois internes tous résolus, et 12 086 liens URI vers 3 125 destinations distinctes. Les 3 003 entrées de citation [1] à [3003] sont présentes. Les 400 figures ont un texte alternatif. L’annexe occupe les pages physiques 784 à 1181 ; l’index occupe les pages 1182 à 1239. Le [relevé brut](validation-latex-current-source-n1000-20261005.json) contient le SHA-256 du PDF.

La couverture, une page de profil, le début, le milieu et la fin de l’annexe, ainsi que le début et la fin de l’index (pages physiques 1, 500, 784, 966, 1181, 1182 et 1239) ont été inspectés : aucune coupure ni superposition n’a été observée dans cet échantillon. La revue n’est pas exhaustive. Par rapport au diagnostic du 2 octobre (791,078 s, 1 535 pages, 13 103 813 octets), ce PDF est plus court et plus petit ; les changements de renderer cumulés entre les deux exécutions empêchent d’attribuer ces différences au seul compactage de l’annexe. Le temps standard de production (120 s par passe, 180 s au total) et le repère provisoire de 60 s restent dépassés. L’option de compilation prolongée est nécessaire pour produire ce grand PDF ; l’enveloppe de production N=1 000 n’est donc pas encore qualifiée. Le parcours GUI Gramps reste aussi à valider.

### Profil d’une passe LuaLaTeX sur la source actuelle — 5 octobre 2026

Une passe directe de LuaLaTeX a été chronométrée sur la fixture ramifiée N=1 000, avec 200 portraits synthétiques. Des marqueurs `os.clock()` ont été ajoutés uniquement à une copie temporaire de la source, avant les sept sections principales. La passe balisée A4 de 1 239 pages a duré 245,200 s au mur. Les intervalles CPU mesurés sont de 30,646 s pour les connexions familiales, 21,237 s pour les notices, 45,900 s pour les fiches, 95,377 s pour l’annexe et 20,005 s pour l’index. L’annexe reste le poste le plus long. Ces intervalles incluent la mise en page et l’expédition des pages entre les marqueurs ; la finalisation tagpdf après le dernier marqueur n’est pas attribuée à une section.

Le profil antérieur du 1er octobre mesurait 108,100 s CPU pour l’annexe. L’écart ne peut pas être attribué à une modification isolée : la source et les réglages ont évolué depuis, et le PDF diagnostique d’une seule passe n’a pas de références convergées. Il sert à orienter une nouvelle réduction des marges de page, pas à déclarer le seuil de production atteint. Les plafonds standard de 120 s par passe et 180 s au total restent dépassés. Le [relevé brut](validation-latex-current-profile-n1000-20261005.json) consigne les marqueurs et leurs limites.

### Marges de page ramenées à 15 mm — 5 octobre 2026

À la suite du retour sur les marges de 20 mm jugées trop grandes, la source LaTeX passe à 15 mm sur chaque côté. La largeur de composition du texte passe ainsi d’environ 170 à 180 mm. Le même livre ramifié N=1 000, avec 200 portraits synthétiques, a été recompilé par le helper de production avec plafonds diagnostiques étendus : 738,982 s et un PDF A4 balisé PDF 2.0 de 1 214 pages, 12 587 394 octets et langue `en-US`.

Par rapport au PDF courant à 20 mm, le livre compte 25 pages de moins et le fichier 33 524 octets de moins. Une exécution de chaque variante ne permet pas d’établir un gain de temps : les durées sont 741,591 et 738,982 s. Les 3 003 citations sont présentes, les 17 341 liens internes restent tous résolus, les 12 072 annotations URI couvrent le même ensemble de 3 125 destinations, et les 400 figures ont un texte alternatif. L’annexe occupe les pages physiques 776 à 1159 et l’index les pages 1160 à 1214.

La couverture, une fiche, le début, le milieu et la fin de l’annexe, puis le début et la fin de l’index (pages 1, 500, 776, 967, 1159, 1160 et 1214) ont été inspectés sans coupure ni chevauchement constatés. La revue ne couvre pas chaque page. La compilation prolongée reste nécessaire : la durée dépasse toujours les limites standard de 120 s par passe et 180 s au total, ainsi que le repère provisoire de 60 s. Voir le [relevé brut et les comparaisons](validation-latex-margins15-n1000-20261005.json).

### Essais de compression PDF sur N=100 — 5 octobre 2026

Sur le jeu ramifié N=100 avec 20 portraits synthétiques et les marges actuelles de 15 mm, trois compilations de référence donnent une médiane de 62,622 s et de 1 312 082 octets. Trois compilations avec `\pdfvariable compresslevel=1` donnent 62,853 s et 1 498 415 octets : la durée est 0,37 % plus élevée et le PDF 14,2 % plus volumineux. Un seul essai au niveau 0 prend 62,519 s mais produit 6 463 651 octets, soit 4,93 fois la taille de référence ; ce run unique ne permet pas de conclure sur le temps. Trois compilations avec `\pdfvariable objcompresslevel=1` donnent 63,203 s et 1 312 077 octets, sans gain de temps mesurable.

Les PDF produits restent balisés et comptent 127 pages. Aucun réglage de compression différent n’est retenu ; le coût de génération reste à chercher dans la composition LaTeX. Ces essais portent sur N=100 et une machine. Le [relevé brut](validation-luatex-compression-n100-20261005.json) détaille les durées, tailles et limites des mesures.
