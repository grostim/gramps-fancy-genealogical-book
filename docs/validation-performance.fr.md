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

### Essai rejeté — premier passage LuaLaTeX en mode brouillon — 5 octobre 2026

Une variante temporaire a lancé le premier passage du PDF prolongé avec `-draftmode`, puis les passages suivants normalement. L’idée était de réduire le coût de l’écriture du PDF intermédiaire. Sur le même jeu ramifié N=1 000 avec 200 portraits synthétiques, la variante prend 741,368 s, contre 738,982 s pour la référence : elle est 2,386 s (0,32 %) plus lente sur ces mesures uniques. Les deux résultats comptent 1 214 pages A4 balisées, font 12 587 394 octets et produisent un texte extrait identique. La structure relevée est également identique : 34 562 destinations nommées, 29 413 annotations de lien dont 17 341 renvois internes et 12 072 liens URI, sans cible interne manquante.

Le profil d’une compilation N=100 avec médias prend 62,703 s au total. Son premier passage brouillon dure 20,776 s ; deux passages normaux suivent en 20,900 et 20,909 s, les deux derniers produisant la même empreinte du fichier auxiliaire. La médiane de référence récente est de 62,622 s. Le premier fichier auxiliaire a une empreinte différente ; il ne permet donc pas de supprimer les passages normaux requis pour stabiliser les renvois. Aucun gain n’est établi et le changement temporaire a été retiré. Les plafonds standard de production restent dépassés à N=1 000. Un seul grand export candidat et un seul profil N=100 ne permettent pas une comparaison statistique. Voir le [relevé brut](validation-latex-draft-first-pass-n1000-20261005.json).

### Essais de balisage automatique des paragraphes — 5 octobre 2026

Une fixture ramifiée N=100 avec 20 portraits a été compilée en une passe directe par variante sous LuaHBTeX 1.24.0 (TeX Live 2026, macOS 27.0 arm64, CPython 3.13.7). La source de référence, avec le balisage activé, prend 20,094 s et produit un PDF diagnostique de 127 pages, 1 323 952 octets et 12 196 éléments de structure. L’option `para/flattened=true` conserve les 127 pages, réduit la structure de deux éléments et le fichier de 46 octets, mais la passe prend 20,662 s (+2,83 % sur une exécution par variante). Cette différence ne démontre ni gain ni régression stable.

La désactivation de `para/tagging` dans l’annexe échoue : tagpdf signale des relations parent-enfant interdites entre la racine et les éléments de liste, puis `there is no open structure on the stack`. Aucun PDF n’est produit. Ni l’aplatissement, qui ne réduit presque pas la structure ni le temps, ni la désactivation, qui invalide la structure, n’est retenu. La génération de production conserve donc son balisage.

Ces compilations ne sont que des passes de diagnostic ; leurs renvois ne convergent pas. Elles ne qualifient ni le délai à N=1 000 ni le comportement avec un lecteur d’écran. Le [relevé brut](validation-latex-paragraph-tags-20261005.json) enregistre les temps, tailles et comptes de balises.

### Coût indicatif du balisage PDF — N=100 — 5 octobre 2026

Trois passes LuaLaTeX par variante ont été exécutées sur la même source synthétique ramifiée N=100 sans médias, dans l’ordre `tagging=on`, `off`, `off`, `on`, `on`, `off`. La médiane balisée est de 19,623 s (runs : 19,459, 19,623, 20,072 s) et son PDF médian de 986 897 octets ; le journal compte 12 022 objets de structure et 9 644 nœuds MC. Sans balisage, la médiane est de 9,603 s (9,603, 9,148, 9,625 s) et le PDF fait 444 034 octets sur chacun des trois runs. Tous comptent 105 pages. L’écart médian observé est de −51,06 % sur la durée et −55,01 % sur la taille.

Les six fichiers proviennent d’une seule passe chacun : les références de page ne convergent dans aucun. L’ordre fixe ne contrebalance que partiellement les effets de cache ; les runs ne couvrent qu’une machine, une version de TeX Live et un jeu sans médias. La variante sans balisage ne possède pas de structure d’accessibilité et n’est pas une sortie acceptable. Ce résultat indicatif désigne le coût du balisage et de sa finalisation comme piste de profilage ; il ne permet ni d’attribuer tout l’écart au seul tagpdf, ni de recommander sa désactivation. Aucun réglage de production n’a changé. Voir les [données brutes](validation-latex-tagging-cost-n100-20261005.json).

### Finalisation de tagpdf sur N=1 000 — 5 octobre 2026

Les hooks de mesure intégrés à tagpdf ont été activés uniquement dans une copie temporaire de la source actuelle à marges de 15 mm. Sur le livre ramifié N=1 000 avec 200 portraits, une passe directe de LuaLaTeX prend 243,149 s au mur et produit un diagnostic PDF balisé de 987 pages. Ce fichier d’une seule passe n’a pas de références convergées et ne constitue pas le PDF final.

La finalisation consomme 21,167 s CPU : 17,9 s pour écrire les éléments de structure (`StructElems`), 2,92 s pour l’`IDTree` et 0,342 s pour le `ParentTree` ; les autres phases durent chacune moins de 0,004 s. L’écriture des éléments de structure représente 84,57 % de la finalisation mesurée. L’ensemble de la finalisation pèse environ 8,7 % du temps mural de la passe ; même une suppression irréaliste de tout ce travail ne suffirait pas à expliquer l’écart avec la limite de 120 s par passe. La [source officielle de tagpdf](https://github.com/latex3/tagpdf/blob/main/tagpdf-tree.dtx) qualifie elle-même l’écriture des éléments de structure de lente.

Le balisage reste activé. Ce profil unique n’établit ni une tendance statistique ni le budget de production. Les précédents marqueurs de section attribuaient 95,377 s CPU à l’annexe sur une source antérieure ; il faut poursuivre sur les sections dominantes plutôt que traiter la seule finalisation. Les durées détaillées sont dans le [relevé brut](validation-tagpdf-finalization-n1000-20261005.json).

### Profil de l’annexe documentaire par groupes de citations — N=1 000 — 5 octobre 2026

La source actuelle à marges de 15 mm a été instrumentée dans une copie temporaire avec des marqueurs tous les 250 éléments de citation. Sur une passe directe, les 3 003 citations produisent un PDF de diagnostic balisé de 987 pages en 244,663 s au mur ; les références ne convergent pas. Les douze groupes complets de 250 citations totalisent 93,835 s CPU, soit 7,820 s en moyenne par groupe. Leur durée va de 6,752 à 8,893 s ; les trois dernières citations prennent 0,205 s.

Les intervalles incluent composition et sorties de pages : ils ne séparent pas le coût des champs de citation, des liens, des images ou des éléments de structure. Aucun bloc unique ne concentre le temps ; la charge semble répartie dans le travail répété des entrées. Le relevé n’est qu’une passe diagnostique sur une machine et ne qualifie pas le PDF final convergé. Aucune modification de production n’en découle encore. Les temps bruts figurent dans le [relevé par groupe](validation-latex-appendix-groups-n1000-20261005.json).

### Première passe intermédiaire sans balisage, PDF final balisé — 5 octobre 2026

Le renderer lance maintenant uniquement la première passe LuaLaTeX avec `tagging=off`, puis rétablit la source d’origine avant les passes suivantes. Les références restent soumises au contrôle de convergence habituel ; le PDF installé est produit par une passe balisée. Trois tailles ont été comparées sur des compilations uniques dans des répertoires neufs. Les deux variantes prennent trois passes pour chaque fixture : N=1 passe de 5,128 à 4,862 s (−5,19 %), N=10 de 10,193 à 9,047 s (−11,24 %), et N=100 avec 20 médias de 61,829 à 51,621 s (−16,51 %). Tous les PDF candidats sont balisés et gardent le même nombre de pages ; les fichiers N=10 et N=100 ont aussi la même taille que leur référence.

Sur N=100, les empreintes du texte extrait, de la structure, des destinations nommées et des liens URI sont identiques entre variantes ; aucun avertissement de mise en page n’est relevé. Une paire de mesures par taille sur une seule machine ne suffit pas à établir une comparaison statistique. Trois nouvelles compilations N=100 via le helper de production ont ensuite confirmé la durée actuelle ; voir la section ci-dessous. Le N=1 000 a lui aussi été recompilé avec cette optimisation ; la mesure est détaillée plus bas. Le [relevé comparatif initial](validation-latex-untagged-first-pass-20261005.json) conserve les mesures appariées.

### Qualification après optimisation — N=1 000 — 5 octobre 2026

Le livre ramifié N=1 000, avec 200 portraits et les marges à 15 mm, a été recompilé via le helper de production avec les limites prolongées (600 s par passe, 1 800 s au total). La durée est de 576,678 s, contre 738,982 s sur le relevé antérieur : −162,304 s (−21,96 %) sur ces deux exécutions uniques. Les deux PDF sont balisés, font 1 214 pages et 12 587 394 octets. Les empreintes du texte extrait, de l’arbre de structure, des destinations nommées et des annotations URL sont identiques.

La mesure confirme un gain sans changement des sorties contrôlées, mais la durée dépasse toujours le plafond standard de 180 s au total. Une seule compilation par variante ne constitue pas une comparaison statistique ; le budget de production N=1 000 n’est donc pas atteint. Le [relevé brut](validation-latex-untagged-first-pass-n1000-20261005.json) contient les empreintes et les limites.

### Répétitions avec le renderer courant — N=100 — 5 octobre 2026

Trois compilations du jeu ramifié N=100 avec 20 portraits de 96 × 72 pixels passent par le helper de production sur le commit `c4f7b15`. Elles prennent 51,175 s, 51,643 s et 51,729 s ; la médiane est de 51,643 s. Les trois sont sous le repère provisoire de 60 s. La source LaTeX générée est identique sur les runs (410 393 octets) et les PDF font 1 312 074 ou 1 312 083 octets. Cette série actuelle confirme le seuil N=100 sur cette machine ; elle ne constitue pas une comparaison entre variantes et ne qualifie pas le livre N=1 000 pour la production. Les [données brutes](validation-latex-untagged-first-pass-n100-20261005.json) enregistrent chaque run.

### Hyperliens différés à la première passe — N=100 — 5 octobre 2026

Une variante temporaire ajoute l’option `draft` de `hyperref` en même temps que `tagging=off` pour la première passe seulement. Le [manuel officiel de hyperref](https://tug.ctan.org/macros/latex/contrib/hyperref/doc/hyperref-doc.pdf) indique que `draft` désactive les fonctions hypertexte ; la source originale est restaurée avant les passes suivantes. Sur trois compilations par variante, la médiane passe de 51,643 s à 45,109 s (−6,534 s, −12,65 %). Les trois PDF candidats sont balisés et comptent 127 pages ; leurs empreintes de texte, d’arbre de structure, de destinations et de liens URL égalent celles de la référence. La taille binaire diffère de quelques octets entre certains runs, sans différence dans les sorties comparées.

Ce relevé N=100 est prometteur. La mesure suivante à N=1 000 est consignée dans la section ci-dessous ; il s’agit d’un run unique et le budget de production reste dépassé. Les [mesures brutes](validation-latex-hyperref-draft-first-pass-n100-20261005.json) détaillent chaque série N=100.

### Hyperliens différés à la première passe — qualification N=1 000 — 5 octobre 2026

Le même jeu ramifié N=1 000 avec marges de 15 mm et 200 portraits synthétiques a été recompilé via le helper de production après la fusion de la PR #272. Avec les plafonds diagnostiques prolongés (600 s par passe, 1 800 s au total), le build prend 514,058 s ; le précédent relevé avec `tagging=off` à la première passe prenait 576,678 s, soit −62,620 s (−10,86 %). Par rapport au PDF de référence à 15 mm (738,982 s), le gain cumulé est de 224,924 s (−30,44 %). Chaque valeur provient d’une seule compilation.

Le PDF final est balisé, compte 1 214 pages et pèse 12 587 399 octets, soit cinq octets de plus que les deux versions précédentes. Les empreintes du texte extrait, de la structure, des destinations et des liens URL sont identiques pour les trois PDF. Leurs octets ne sont pas identiques. Le run nécessite toujours les plafonds prolongés et dépasse le budget standard de 180 s au total ; une seule mesure par variante n’établit pas de tendance statistique. Les contrôles de cette exécution ne comprennent pas une revue visuelle complète. Le [relevé brut](validation-latex-hyperref-draft-first-pass-n1000-20261005.json) donne les empreintes, la configuration et les limites.

### Essai rejeté — factorisation des champs de source — N=100 — 5 octobre 2026

Une variante a remplacé les champs auteur et informations d’édition répétés de l’annexe par une macro LaTeX partagée. Sur le jeu ramifié N=100 avec médias, le source passe de 410 393 à 409 857 octets (−536). Le PDF balisé de 127 pages prend 45,042 s, soit 0,067 s (0,15 %) de moins que la médiane précédente de 45,109 s. Le run est 0,044 s plus rapide que le meilleur des trois runs de référence, mais l’écart à la médiane reste inférieur à l’étendue de 0,132 s observée dans cette série ; une seule mesure ne démontre pas de gain.

Les empreintes du texte extrait, de l’arbre de structure, des destinations nommées et des liens URL correspondent à la référence. La variante reste écartée : le run unique ne démontre pas de gain mesurable, et aucun changement de production n’est conservé. N=1 000 n’a pas été recompilé et aucune revue visuelle complète n’a été effectuée. Voir le [relevé brut](validation-latex-shared-citation-fields-n100-20261005.json).

### Essai rejeté — deuxième passe sans balisage — N=100 — 5 octobre 2026

Une seconde variante garde le balisage désactivé pendant les deux premiers passages ; `hyperref` est en mode `draft` uniquement au premier, puis redevient actif. La répétition depuis le source LaTeX de production (410 393 octets, sans macro expérimentale) converge en quatre passes et prend 54,800 s, soit 9,691 s (21,48 %) de plus que la médiane de référence de 45,109 s. Le run initial prenait 54,689 s. Les deux temps candidats dépassent les trois runs de référence (45,086–45,218 s).

Le texte, l’arbre de structure, les destinations et les liens URL ont les mêmes empreintes que la référence. L’essai est rejeté parce que la séquence requiert une quatrième passe et n’accélère pas l’export. Le code temporaire a été retiré. Aucune revue visuelle complète ni compilation N=1 000 n’a été faite pour cette variante. Voir le [relevé brut](validation-latex-defer-tagging-second-pass-n100-20261005.json).

### Répétition du build optimisé — N=1 000 — 5 octobre 2026

Une troisième compilation complète avec le renderer courant prend 534,127 s. Sur les trois runs (514,058, 509,888 et 534,127 s), la médiane mesurée est de 514,058 s et l’étendue de 24,239 s (4,72 % de la médiane). Les trois compilations utilisent les limites diagnostiques étendues et restent très au-dessus du plafond standard de 180 s au total.

Les trois PDF sont balisés PDF 2.0 et comptent 1 214 pages. Ils font respectivement 12 587 399, 12 587 395 et 12 587 393 octets. Les empreintes du texte, de l’arbre de structure, des destinations et des liens URL correspondent exactement. Aucune revue visuelle complète n’a été faite sur le troisième run. Voir les [mesures brutes](validation-latex-hyperref-draft-first-pass-n1000-repeats-20261005.json).

### Essai rejeté — macro pour l’autorité URL — N=100 — 5 octobre 2026

Une transformation temporaire du source remplace l’autorité `https://archives.example.test` de 909 commandes `bookurl` par une macro LaTeX. Le source passe de 410 393 à 394 997 octets (−3,75 %). Trois compilations prennent 45,245 s, 45,180 s et 49,784 s ; la médiane est de 45,245 s, soit 0,136 s (0,30 %) de plus que la médiane de référence de 45,109 s. Les empreintes du texte, de la structure, des destinations et des URL correspondent pour les trois PDF candidats. La variante est écartée : la réduction du source n’accélère pas la compilation de façon mesurable. Aucun changement de production n’est conservé. Voir les [mesures brutes](validation-latex-url-host-macros-n100-20261005.json).

### Diagnostic du coût de génération des liens — N=100 — 5 octobre 2026

Un run diagnostique garde le balisage actif, mais compile les trois passes avec `hyperref` en mode brouillon. Il prend 33,836 s contre une médiane de production de 45,109 s (−24,99 %). Le PDF balisé de 127 pages conserve le même texte extrait, mais ne contient aucune annotation de lien ni destination nommée. Ce résultat indique que la génération des liens constitue un coût important sur cette fixture ; il ne justifie pas de les désactiver en production. La prochaine investigation cherchera à réduire leur coût tout en conservant les annotations et éléments Link. Voir le [profil brut](validation-latex-hyperref-all-draft-n100-20261005.json).

### Essai rejeté — wrapper interne de lien — N=100 — 5 octobre 2026

Une macro `gfbpagelink` temporaire appelle directement les commandes internes de début et de fin de lien de `hyperref` pour les cibles internes sûres du renderer. Trois compilations candidates prennent 44,980 s, 45,434 s et 46,042 s ; la médiane de 45,434 s dépasse de 0,325 s (0,72 %) la référence à 45,109 s. Les trois PDF candidats conservent exactement les empreintes du texte, de la structure, des destinations et des URL, avec 2 978 annotations de lien et 3 526 destinations nommées chacun. La variante est écartée, car elle n’accélère pas la compilation. Voir les [mesures brutes](validation-latex-hyperref-link-wrapper-n100-20261005.json).

### Diagnostic sans hooks de liens de tagpdf — N=100 — 5 octobre 2026

Trois compilations via le helper de production retirent temporairement les hooks avant/après de tagpdf pour les annotations GoTo et URI, tout en gardant `hyperref`, le balisage ordinaire et la génération des liens actifs. La médiane est de 39,473 s (38,974–40,092), soit 5,636 s (12,49 %) de moins que la référence de production à 45,109 s. Chaque PDF balisé de 127 pages conserve les 2 978 annotations de lien, les 3 526 destinations nommées, les mêmes noms de destination et cibles URI ainsi que la même empreinte du texte extrait. En revanche, l’arbre de structure perd les 2 671 rôles `Link`.

Le résultat distingue deux coûts probables : la médiane sans hooks dépasse de 5,637 s l’unique run à 33,836 s sans hyperliens ; cet écart est proche des 5,636 s séparant la production de la variante sans hooks. Cela suggère que la création des annotations et leur rattachement aux éléments Link prennent chacun environ 5,6 s sur cette fixture. La mesure sans hyperliens n’a qu’un run ; cette décomposition reste indicative et non additive contrôlée. La variante sans hooks est écartée, car les liens disparaissent de la structure d’accessibilité. Aucun changement de production n’est conservé. Voir les [mesures brutes](validation-latex-hyperref-link-hooks-n100-20261005.json).

### Hooks GoTo et URI mesurés séparément — N=100 — 5 octobre 2026

Trois compilations séquentielles par variante retirent les hooks tagpdf d’un type d’action PDF, tout en gardant l’autre paire active. Sans les hooks GoTo, la médiane est de 41,427 s (40,933–41,437), soit 3,682 s (8,16 %) de moins que la production. Sans les hooks URI, elle est de 42,877 s (42,722–43,061), soit 2,232 s (4,95 %) de moins. Chaque variante conserve les 2 978 annotations, les 3 526 destinations nommées, les mêmes noms de destination et cibles URI ainsi que l’empreinte exacte du texte extrait.

La structure sans hooks GoTo garde 909 rôles `Link` pour les liens URI ; celle sans hooks URI garde 1 762 rôles `Link` pour les liens internes. Chaque variante perd donc la structure d’accessibilité du type de lien désactivé. Les hooks GoTo ont l’effet mesuré le plus marqué sur cette fixture, mais aucune variante n’est adaptée à la production. Le prochain profil ciblera la conservation des rôles des liens internes en réduisant leur coût structurel. Voir le [relevé brut](validation-latex-hyperref-link-hook-types-n100-20261005.json).

### Opérations des sockets de liens tagpdf en ligne — N=100 — 5 octobre 2026

Une source temporaire remplace les appels à `UseTaggingSocket` des hooks URI et GoTo par les opérations équivalentes des plugs noyau par défaut actuels de tagpdf. Trois compilations prennent 43,750 s, 44,710 s et 44,732 s ; la médiane est de 44,710 s, soit seulement 0,399 s (0,88 %) de moins que la référence de 45,109 s. L’étendue candidate est de 0,982 s : cet écart ne prouve pas de gain mesurable.

Les trois PDF conservent exactement les empreintes de structure et de texte, 2 671 rôles `Link`, 2 978 annotations et 3 526 destinations nommées. L’essai est rejeté : le gain n’est pas établi et cette approche dupliquerait dans la source produite l’implémentation interne du socket de tagpdf. Aucun changement de production n’est conservé. Voir le [relevé brut](validation-latex-hyperref-link-socket-inline-n100-20261005.json).

### Essai rejeté — callback `linksplit` retiré — N=100 — 5 octobre 2026

Trois compilations temporaires retirent le callback LuaTeX `linksplit` et réinstallent les hooks URI et GoTo pour préserver les opérations de balisage. Elles prennent 44,251 s, 44,145 s et 45,087 s ; la médiane est de 44,251 s, soit 0,858 s (1,90 %) sous la référence de 45,109 s. L’étendue candidate de 0,942 s est supérieure à l’écart de médiane : aucun gain de compilation n’est établi. Chaque PDF balisé conserve 127 pages, 2 978 annotations (1 762 GoTo et 1 216 URI), 3 526 destinations, les mêmes cibles URI et le même texte extrait.

L’audit direct des PDF révèle toutefois 2 978 annotations Link qui ne disposent que de 2 671 valeurs `StructParent` distinctes. Dans chaque candidat, 303 clés sont réutilisées par 307 annotations supplémentaires ; l’arbre ParentTree totalise 2 798 entrées au lieu de 3 105 dans la référence, pages comprises. Seules 2 671 références `OBJR` pointent vers leur annotation correspondante, contre 2 978 en production. La piste est rejetée : les fragments supplémentaires ne sont pas associés individuellement à l’arbre d’accessibilité. Aucun changement de production n’est conservé. N=1 000, la revue visuelle complète et le lecteur d’écran restent à qualifier. Voir les [mesures brutes et l’audit ParentTree](validation-latex-hyperref-no-split-n100-20261005.json).

### Profil du coût des liens et essai d’un dispatch de socket fixe — N=100 — 5 octobre 2026

Un profil instrumenté du renderer courant compte 2 959 appels Lua `linksplit` et environ 0,018 s de CPU Lua au total. La macro TeX qui insère l’objet `OBJR` est appelée 2 959 fois et son intervalle instrumenté représente environ 0,483 s ; ce chiffre inclut le coût du marqueur et constitue une borne haute. Le PDF de 127 pages garde ses 2 978 annotations, 2 978 entrées ParentTree/OBJR pour les liens et 3 526 destinations nommées.

Trois candidats remplacent ensuite `\UseTaggingSocket` par `\tag_socket_use:nn` dans les hooks URI/GoTo. La médiane est de 44,709 s (43,504–44,714), soit 0,400 s (0,89 %) sous la médiane de référence de 45,109 s. L’étendue candidate atteint 1,210 s et dépasse l’écart : aucun gain n’est établi. Les trois PDF conservent les 2 978 annotations, les références ParentTree/OBJR réciproques, les 2 671 rôles Link, le texte, les cibles URI et destinations. La source augmente de 611 octets. L’essai est rejeté sans changement de production. Le [guide tagpdf](https://github.com/latex3/tagpdf/blob/main/tagpdf-user.dtx) décrit cette API de socket de bas niveau comme légèrement plus efficace ; sur cette fixture, le gain n’est pas mesurable. Voir le [relevé brut](validation-latex-hyperref-link-socket-dispatch-n100-20261005.json).

### Temps de génération de la source LaTeX — livre complet N=1 000 — 5 octobre 2026

Le banc synthétique courant a généré trois fois le livre ramifié N=1 000, avec 2 002 personnes, 3 003 citations et 200 portraits. La génération complète de la source LaTeX de 4 037 562 octets prend 0,982, 0,980 et 0,980 s ; la médiane est de 0,980 s. La compilation PDF n’a pas été lancée dans cette mesure.

Cette durée représente environ 0,19 % de la médiane de compilation optimisée N=1 000 (514,058 s) dans une comparaison indicative entre exécutions. Elle couvre tout le livre, pas seulement l’annexe ; le coût Python propre à celle-ci est donc inférieur à une seconde. Une optimisation Python ne peut pas expliquer une réduction substantielle du temps PDF. Le prochain effort de performance doit rester sur la composition et la sortie de pages LuaLaTeX. Le [relevé brut](validation-latex-generation-n1000-20261005.json) décrit les runs et leurs limites.

### Profil et correction du retour à la ligne des URL — N=100 — 5 octobre 2026

Une source temporaire du livre ramifié N=100 (202 personnes, 101 familles, 303 événements et citations, 27 notes, sans médias) a été instrumentée autour des liens de page, des ancres et des URL. Sur trois passes directes, 909 sorties de la macro bookurl cumulent 1,604 à 1,626 s CPU (médiane : 1,614 s) ; les 1 743 liens de page prennent 0,038 s et les 1 455 ancres 0,015 s. Une variante remplace deux appels nolinkurl par un seul autour de l’adresse visible complète, tout en conservant la cible href.

La variante donne 1,582 s de médiane CPU pour les 909 sorties bookurl (1,582–1,597 s), soit 1,90 % sous la médiane instrumentée de la version à deux appels. Ce relevé ne démontre pas un gain de compilation complet. Pour contrôler les annotations sans les marqueurs de mesure, chaque PDF a ensuite été recompilé directement en trois passes jusqu’à la convergence : les deux PDF balisés A4 comptent 105 pages et conservent 2 978 annotations Link, 1 220 annotations URI avec le même ensemble ordonné de cibles, 2 667 rôles Link, 2 978 références OBJR et 3 083 clés ParentTree. Après retrait des en-têtes courants et des espaces d’extraction, les empreintes de texte correspondent. Le candidat pèse 975 032 octets contre 975 450 pour la référence.

La revue visuelle à 140 ppp des pages 67 et 70 montre que la variante coupe les URL après le slash au lieu de séparer « reg » et « ister », y compris lorsque la coupure tombe au changement de page. Une autre fixture confirme la cible exacte et le texte visible d’une URL avec %2F, paramètres de requête et fragment #record. Le changement est retenu pour la lisibilité des URL, sans revendiquer de gain de performance. Le [relevé brut](validation-latex-macro-profile-n100-20261005.json) distingue les compilations instrumentées des PDF non instrumentés et décrit leurs limites.

### Profil par citation de l’annexe documentaire — N=1 000 — 5 octobre 2026

Une copie temporaire de la source du livre ramifié N=1 000 a reçu un marqueur LuaTeX au début et à la fin de chaque entrée de citation. La fixture contient 2 002 personnes, 1 001 familles, 3 003 événements et citations ainsi que 200 images synthétiques. Une seule passe LuaHBTeX produit un PDF de diagnostic de 1 214 pages, balisé, de 12 712 225 octets ; les renvois restent non convergés, comme attendu pour ce diagnostic. Aucun changement du renderer n’est conservé.

Les 3 003 intervalles d’entrée totalisent 108,350 s CPU ; la médiane est de 0,020357 s, le 90e centile de 0,109848 s et le maximum de 0,225137 s. Les 200 entrées qui rendent un média ont une moyenne de 0,063495 s contre 0,034125 s pour les 2 803 autres. Les entrées appelées depuis plusieurs usages (267 citations, deux appels chacune) ont une moyenne de 0,052843 s contre 0,034445 s pour les 2 736 entrées à un seul appel. Les sous-groupes avec média et deux appels cumulent 2,56 s sur 33 entrées ; sans média et un seul appel, 84,11 s sur 2 569 entrées.

Ces intervalles incluent la composition du paragraphe et l’expédition de page entre les marqueurs. Le diagnostic place donc le média et la multiplication des renvois parmi les pistes à examiner, sans isoler leur coût causal ; les marqueurs ajoutés et les frontières de paragraphes peuvent aussi influer sur la durée. Toutes les entrées de cette fixture partagent auteur, publication, page, date, dépôt et trois URL ; ce jeu ne permet pas de comparer le coût de ces champs. La prochaine mesure doit comparer de façon contrôlée les chemins média et appels multiples en conservant le balisage, les annotations et les destinations. Voir le [relevé détaillé](validation-latex-citation-entries-n1000-20261005.json).

### Profil direct des insertions d’image et des renvois de citation — N=1 000 — 5 octobre 2026

Une seconde copie temporaire instrumente les appels `\includegraphics` et `\gfbpagelink` à l’intérieur de l’annexe, sans supprimer ni remplacer les images, liens ou balises. Une passe LuaHBTeX produit un PDF de diagnostic balisé de 1 214 pages. Le chronométrage porte sur les macros elles-mêmes ; la composition autour des appels et les expéditions de page ne sont pas attribuées à ces durées.

Sur 200 références média dans les citations, 160 sont des insertions d’image effectives ; les autres réemploient une image déjà présentée par un renvoi. Les 160 appels `\includegraphics` cumulent 0,738 s CPU, soit 4,61 ms par insertion. Les 3 310 appels observés à `\gfbpagelink` cumulent 11,677 s. Les métadonnées comptent 3 270 appels éditoriaux ; 40 liens supplémentaires se trouvent dans des notices avec média et sont conservés dans le relevé, sans les assimiler à des appels de citation.

Pour les notices sans média, les 2 569 entrées avec un seul appel cumulent 8,378 s de liens (3,26 ms par entrée). Les 234 entrées à appels multiples cumulent 2,287 s pour 468 liens (9,77 ms par entrée, 4,89 ms par lien). Ce rapport par entrée augmente avec le nombre de liens ; il ne prouve pas qu’une variante de production accélérerait le PDF. L’image coûte peu dans la macro d’insertion isolée, ce qui ne permet pas d’expliquer à elle seule les intervalles de citation plus longs du premier profil.

L’audit comparatif des deux PDF de diagnostic confirme le même texte extrait, 1 214 pages A4, 29 406 annotations Link (17 334 GoTo et 12 072 URI), 34 562 destinations, 29 406 associations OBJR vers leurs annotations, 400 figures munies de texte alternatif et les mêmes rôles de structure. Le nombre d’octets varie de six, sans différence sémantique observée. Il s’agit d’un contrôle structurel d’une passe non convergée, pas d’une mesure comparative du temps d’export complet. Aucun changement du renderer n’est retenu. Le [relevé brut](validation-latex-citation-macros-n1000-20261005.json) donne les empreintes, les groupes et les limites.

### Essai rejeté — récupération du folio avec `refcount` — N=100 — 6 octobre 2026

Une copie temporaire remplace `\pageref*` par `\getpagerefnumber` dans la macro `\gfbpagelink`, puis compile six fois le même livre ramifié N=100 avec le helper de production, dans l’ordre référence, candidat, candidat, référence, référence, candidat. Les trois durées de référence sont 44,180, 44,773 et 44,801 s (médiane 44,773 s) ; celles du candidat sont 44,416, 44,531 et 44,473 s (médiane 44,473 s). La baisse médiane de 0,300 s (0,67 %) est inférieure à l’étendue de 0,621 s observée sur la référence et ne démontre pas un gain.

Les six PDF balisés comptent 127 pages, 3 526 destinations, 1 762 annotations GoTo et 1 216 annotations URI, 2 671 rôles `Link` et 2 978 références OBJR. Leur texte extrait et leurs comptes de rôles sont identiques. La variante est rejetée sans modification du renderer. Le résultat N=100 ne mesure pas le build N=1 000, qui reste au-dessus des plafonds de production. Le [relevé brut](validation-latex-pageref-number-n100-20261006.json) conserve les temps, tailles, empreintes et limites.

### Profil natif d’une passe PDF N=1 000 — 6 octobre 2026

Une passe directe de la source actuelle, avec balisage et hyperliens actifs, prend 247,720 s et produit un PDF diagnostique de 1 214 pages (12 712 216 octets), balisé, avec 34 562 destinations et 29 406 annotations de lien. Au moment de la finalisation, le journal tagpdf annonce environ 119 869 objets de structure et 97 374 nœuds feuilles de contenu marqué. Une observation `ps` proche de cette phase indique environ 964 Mo de RSS ; ce n’est pas une mesure du pic sur tout le processus.

Sur la même fixture N=1 000, une passe intermédiaire comparable à celle du helper de production (`tagging=off`, `hyperref` en mode `draft`) prend 21,692 s, produit également 1 214 pages, mais aucune balise, destination ni annotation de lien. L’écart cumule l’effet du balisage et celui des hyperliens ; cette paire de passes uniques ne les sépare pas et ne mesure pas le PDF final convergé. Les deux essais produisent des diagnostics seulement.

L’échantillonneur macOS a collecté 20 s de piles CPU pendant chaque passe. Les symboles internes de LuaHBTeX ne sont pas présents dans le binaire installé ; le rapport n’attribue donc pas les piles à des routines ni à des macros LaTeX. Aucun changement de production ne découle de ce profil. Le [relevé brut](validation-latex-native-sample-n1000-20261006.json) consigne les commandes, les sorties, les tailles et les limites.

### Profil factoriel balisage/hyperliens — N=1 000 — 6 octobre 2026

Trois passes directes par cellule ont été mesurées, avec l’ordre des variantes décalé entre les séries. La médiane sans tags ni liens est de 21,310 s (21,302–21,692) ; avec tags seuls, 106,917 s (106,904–107,447) ; avec liens seuls, 89,619 s (89,315–89,793) ; avec les deux actifs, 247,720 s (247,525–247,757). Les empreintes du source LaTeX sont stables dans chacune des quatre cellules.

Les différences appariées estiment à 85,602 s (85,225–86,137) le coût du balisage lorsque les liens sont en brouillon et à 68,101 s (68,005–68,317) celui des hyperliens sans balisage. Le résidu factoriel — temps avec les deux actifs moins les trois autres cellules de la même série — a une médiane de 72,305 s, avec une étendue de 72,304 à 72,702 s. Les trois séries montrent donc un surcoût conjoint stable sur cette fixture ; elles n’identifient pas la commande LuaTeX, tagpdf ou hyperref qui le cause.

Les douze PDF sont A4 et comptent 1 214 pages ; `pdftotext` produit la même empreinte de texte pour les douze, et l’audit pypdf retrouve les balises, destinations et annotations attendues par cellule. Les renvois de pagination restent non convergés. Les variantes brouillon ou sans balisage omettent une partie des fonctions de livraison et ne sont pas des exports acceptables. Aucun changement de production n’est retenu. Toute optimisation restante doit réduire le travail conjoint hyperref/tagpdf sans retirer la structure accessible et être confirmée dans le build convergé et l’interface Gramps. Voir le [relevé factoriel brut](validation-latex-tagging-hyperref-factorial-n1000-20261006.json).

### Essai rejeté — dispatch direct des sockets tagpdf à N=1 000 — 6 octobre 2026

Une source temporaire remplace les appels `\UseTaggingSocket` des hooks URI et GoTo par les appels à arité fixe `\tag_socket_use:nn`, en gardant les hooks tagpdf, le callback Lua `linksplit`, les annotations et les associations OBJR actifs. La passe directe prend 247,469 s, soit 0,251 s de moins que la médiane de référence de 247,720 s et seulement 0,056 s sous la borne basse de sa plage (247,525 s). Le candidat n’a qu’un run et sa source augmente de 547 octets : aucun gain mesurable n’est établi.

L’audit trouve les mêmes 1 214 pages A4, 34 562 destinations, 29 406 annotations, 29 406 valeurs `StructParent`, 29 406 références OBJR et 26 343 rôles `Link`. Les annotations correspondent chacune à un OBJR, et `pdftotext` donne la même empreinte que la référence. L’essai N=100 précédent n’avait pas non plus établi de gain pour ce dispatch. Comme cette variante utilise une API de bas niveau de tagpdf sans bénéfice mesuré, elle est rejetée sans changement du renderer. Voir le [relevé brut](validation-latex-tag-socket-direct-n1000-20261006.json).

### Essai rejeté — balisage actif dès la première passe — N=100 — 6 octobre 2026

Une copie temporaire garde `tagging=on` dès le premier passage et ne met que `hyperref` en mode brouillon ; la source de production est restaurée pour les passes actives suivantes. Trois passes sont nécessaires pour stabiliser les empreintes `.aux`, `.toc` et `.out` ; leurs durées sont 10,876, 20,799 et 20,797 s, pour 52,475 s au total. La référence de même source SHA-256 `d3e6640c…e07308` prend 45,096 s avec le helper de production. Les trois références précédentes, avec la même empreinte de source, ont une médiane de 44,773 s et une plage de 44,180 à 44,801 s. Le seul run candidat est 7,379 s (16,36 %) plus lent que la référence appariée.

Les deux PDF sont balisés et ont 127 pages, 3 526 destinations, 2 978 annotations munies de `StructParent`, 2 671 rôles `Link` et 2 978 nœuds OBJR. `pdftotext` produit la même empreinte pour cette paire. Le réglage n’accélère pas la convergence et n’est pas conservé. Cette comparaison N=100 ne requalifie pas le build convergé N=1 000. Voir le [relevé brut](validation-latex-tagged-first-pass-n100-20261006.json).

### Profil des macros d’hyperliens — N=1 000 — 6 octobre 2026

Une copie temporaire instrumente les appels `\hyperlink` et `\href` sur la fixture ramifiée N=1 000 avec 200 portraits, en laissant le balisage et les liens actifs. Une passe directe dure 245,080 s au mur et 243,830 s CPU utilisateur. Les 17 334 appels `\hyperlink` cumulent 52,063 s CPU ; les 9 009 appels `\href`, 27,386 s. Ces intervalles additionnés représentent 79,449 s, soit 32,58 % du CPU utilisateur mesuré. Le chronométrage entoure les macros et leur traitement TeX ; le coût des marqueurs n’a pas été quantifié et la mesure ne sépare pas le travail de hyperref de celui de tagpdf.

Le PDF diagnostique balisé compte 1 214 pages A4, 34 562 destinations, 17 341 annotations GoTo, 12 072 annotations URI, 26 350 rôles Link, 29 413 associations OBJR et 400 figures. Les sept annotations, rôles Link et nœuds OBJR supplémentaires par rapport au profil factoriel proviennent des sept entrées de sommaire lues depuis le fichier `.toc` déjà rempli. Le PDF de référence était la première passe, avec un sommaire encore vide et des folios non résolus ; les empreintes textuelles diffèrent, et le journal instrumenté indique encore que les labels ont changé. Ces fichiers ne constituent donc pas une comparaison sémantique ou de convergence appariée.

Ce profil dirige le prochain diagnostic vers les chemins de liens internes et URI, sans établir un gain ni justifier une modification du renderer. Répéter la mesure avec des états `.aux`/`.toc` appariés et quantifier l’effet des marqueurs avant de retenir une optimisation. Voir le [relevé brut](validation-latex-link-macro-profile-n1000-20261006.json) et le [PDF diagnostique local](../tmp/lualatex-link-macro-profile-n1000-20261006/book.pdf).

### Contrôle apparié des macros d’hyperliens — N=100 — 6 octobre 2026

Trois paires de passes directes N=100 démarrent chacune avec le même source et sans fichiers `.aux`, `.toc` ni `.out`. L’ordre alterne référence et instrumentation. Les médianes murales sont de 20,690 s sans marqueurs et 20,620 s avec instrumentation (écart −0,070 s, soit −0,34 %). La plage de référence atteint 0,860 s ; les écarts appariés vont de −0,080 à +0,630 s. Aucun surcoût ni gain de compilation n’est mesurable dans cette série.

Les intervalles instrumentés ont des médianes de 5,564 s pour 1 751 appels `\hyperlink` et 2,690 s pour 909 appels `\href`. Dans les six PDF balisés de 105 pages, les 3 484 destinations, 1 751 liens GoTo, 1 220 liens URI, 2 660 rôles Link, 2 971 associations OBJR/`StructParent` et le texte extrait sont identiques entre référence et candidat. Les PDF diffèrent par leurs octets ; aucun bénéfice de performance n’est établi. Ces premières passes ont des renvois de page non convergés et la recette n’isole pas le coût propre des marqueurs ni celui de hyperref par rapport à tagpdf.

Cette comparaison confirme l’absence d’altération sémantique détectée par l’instrumentation dans ce cas N=100. Elle ne qualifie pas le profil N=1 000 ou l’export convergé de production. Voir le [relevé brut](validation-latex-link-macro-matched-n100-20261006.json).

### Contrôle apparié de l’instrumentation des liens — N=1 000 — 6 octobre 2026

Trois paires de passes directes repartent chacune des mêmes fichiers `.aux` et `.toc` remplis ; `.out` est absent. L’ordre est référence/instrumenté, instrumenté/référence, puis référence/instrumenté. Les médianes murales sont de 245,227 s pour la référence et de 245,818 s avec marqueurs, soit +0,591 s (0,24 %). Les écarts appariés sont +1,658, +0,701 et +0,052 s. L’étendue des références, 1,402 s, dépasse l’écart entre médianes ; ces trois paires ne démontrent pas un surcoût mesurable.

Les intervalles instrumentés médians sont de 52,142 s pour 17 334 appels `\hyperlink` et de 27,453 s pour 9 009 appels `\href`. Les six PDF balisés de 1 214 pages A4 ont 34 562 destinations, 17 341 annotations GoTo, 12 072 URI, 26 350 rôles `Link` et 29 413 associations OBJR/`StructParent`. Les empreintes du texte et des cibles URI sont identiques ; les octets PDF diffèrent. Cette sortie à une passe depuis un `.toc` rempli est un diagnostic, pas une qualification du build convergé. Le contrôle ne sépare pas le coût de hyperref de celui de tagpdf et ne justifie aucun changement du renderer. Voir le [relevé brut](validation-latex-link-macro-matched-n1000-20261006.json).

### Build multipasse convergé — N=1 000 — 6 octobre 2026

Le livre ramifié synthétique N=1 000 (2 002 personnes, 1 001 familles, 3 003 événements et citations, 200 portraits de 96 × 72 pixels) converge avec le helper de production en mode étendu : **706,759 s** au total, avec des plafonds diagnostiques de 600 s par passe et 1 800 s au total. Le relevé initial de source (4 207 469 octets, SHA-256 f72e55e1…) correspond au rendu avant préparation des dérivés médias, et non au fichier compilé. Après cette préparation, le source transmis au compilateur fait 4 311 655 octets (SHA-256 6a4ce9a3…), empreinte reproduite par le profil direct des notes. Le PDF A4 en anglais pèse 13 461 244 octets et compte 1 140 pages. Le pic de l’espace temporaire suivi par échantillons de 100 ms est de 25 581 314 octets ; le pic Python suivi est de 80 738 271 octets et le maximum RSS observé parmi les processus enfants de 1 223 671 808 octets.

L’audit du PDF retrouve 38 025 destinations nommées et 32 950 annotations de lien (20 878 GoTo et 12 072 URI). Chaque annotation possède une valeur StructParent distincte et un nœud OBJR pointant vers cette annotation ; aucune cible nommée ou page de destination explicite n’est manquante. Les 400 figures ont toutes un texte alternatif. Le document est balisé, déclaré PDF 2.0, de langue en-US et au format A4.

Le build converge, mais dépasse de 526,759 s l’enveloppe de production de 180 s et de 646,759 s le repère provisoire de 60 s. Le maximum RSS des processus enfants dépasse aussi la référence mémoire de 512 Mo ; cette valeur concerne le PDF direct synthétique et ne représente pas une mesure du parcours Gramps CLI complet. Par rapport au relevé du 5 octobre (741,591 s, 1 239 pages), le temps baisse de 4,7 %, mais la source, le renderer et le nombre de pages ont changé : ce n’est pas une comparaison attribuable ni strictement appariée. Aucune optimisation n’est revendiquée sur cette différence.

Une revue visuelle à 96 ppp des pages 1, 150, 570, 900 et 1 140 ne révèle pas de rognage ni de chevauchement. La page de titre reste volontairement aérée ; les pages de contenu utilisent la largeur utile attendue avec les marges courantes. Le [PDF courant](../output/pdf/gramps-fancy-book-converged-current-source-n1000-20261006.pdf) est conservé comme échantillon. Les [mesures et l’audit bruts](validation-latex-converged-current-source-n1000-20261006.json) contiennent les empreintes, dimensions, comptes et limites de cette exécution unique.

### Profil direct des notes de bas de page — N=1 000 — 6 octobre 2026

Une source temporaire ajoute un chronométrage Lua autour de chaque appel à la macro LaTeX de note de bas de page. Sur une passe directe avec balisage et liens actifs, 3 270 appels cumulent **45,916 s CPU**, soit 14,04 ms par appel en moyenne. Cet intervalle comprend le traitement de la note, son contenu et son renvoi vers l’annexe ; il ne sépare pas le coût de hyperref/tagpdf, les expéditions de page ni celui des marqueurs.

Le PDF diagnostique de 1 140 pages garde 38 025 destinations, 32 943 annotations (20 871 GoTo et 12 072 URI), 32 943 valeurs StructParent et 32 943 associations OBJR pointant chacune vers leur annotation. L’arbre contient 3 270 rôles Note et 400 figures avec texte alternatif. Sept annotations de sommaire de moins que le PDF convergé sont attendues, car cette passe part sans fichier .toc rempli.

Le profil direct utilise la même empreinte de source compilée que le build convergé après préparation des médias. Le SHA-256 f72e consigné dans la première mesure portait sur le source avant cette préparation ; le relevé brut de convergence distingue maintenant ces deux sources. Une paire de contrôle avec et sans marqueurs, sur cette source et des dossiers auxiliaires vierges, donne 350,509 s contre 349,049 s, soit +1,460 s (+0,42 %) pour la version instrumentée. Les textes normalisés et les comptes de structure sont identiques ; l’écart d’une seule paire ne démontre pas de surcoût mesurable. La somme de 45,916 s autour des macros est un profil du travail dans ces appels, pas un gain récupérable établi. Aucun changement de production n’est retenu. Les [mesures du profil](validation-latex-footnote-profile-n1000-20261006.json) et le [contrôle apparié](validation-latex-footnote-instrumentation-control-n1000-20261006.json) conservent les détails et limites.

### Profilage de la sérialisation de l’arbre de structure — N=1 000 — 6 octobre 2026

Une instrumentation temporaire échantillonne chaque 128e appel à deux fonctions tagpdf du writer de l’arbre. Les fonctions de préparation des clés enfants et de sérialisation des dictionnaires sont chacune appelées 128 011 fois ; 1 000 échantillons par fonction donnent des coûts CPU estimés de 7,650 s et 5,192 s respectivement, après extrapolation par intervalle. Il s’agit d’estimations issues d’une seule passe, pas de mesures complètes ou répétées. Le profil indique que le travail est réparti entre les deux fonctions ; il ne fournit pas à lui seul une optimisation sûre du renderer.

La passe directe réussit en 280,790 s et produit un PDF A4 balisé de 1 140 pages. Le contrôle non instrumenté antérieur prend 349,049 s, mais cette différence d’un run à l’autre ne constitue pas une comparaison de performance fiable. Après normalisation, les textes extraits correspondent. Les rôles, 38 025 destinations, 32 943 liens et leurs associations OBJR/`StructParent` correspondent aussi ; les ensembles de cibles URI et GoTo sont identiques et les 400 figures ont un texte alternatif. Les références de cette première passe ne sont pas convergées. Aucun changement de production n’est retenu ; voir le [relevé brut](validation-latex-tag-struct-subprofile-n1000-20261006.json).

### Vérification différée des relations de structure — N=1 000 — 6 octobre 2026

La documentation de tagpdf décrit le réglage `debug/parent-child-check=atend` : il conserve la vérification des relations parent/enfant et l’exécute en Lua après la construction de l’arbre, au lieu de vérifier chaque relation à sa création ([manuel tagpdf](https://tug.ctan.org/macros/latex/contrib/tagpdf/tagpdf-code.pdf)). Le renderer utilise ce mode documenté.

Trois paires de premières passes directes, chacune depuis des fichiers auxiliaires vierges et avec l’ordre alterné, donnent une médiane de 280,270 s avec la vérification par défaut et 261,690 s avec la vérification différée. Les écarts appariés sont −18,810, −18,110 et −18,750 s ; leur médiane est −18,750 s (−6,69 %). Les PDF audités des deux premières paires gardent la même empreinte de texte, les mêmes rôles, destinations et cibles, les 32 943 associations lien/OBJR et 400 figures munies d’un texte alternatif. Le pic RSS varie d’une paire à l’autre sans tendance claire ; ces passes dépassent toutes le seuil mémoire de 512 Mio.

Le helper de production converge ensuite une fois le livre N=1 000 en 545,189 s. Le PDF A4 balisé de 1 140 pages conserve 38 025 destinations et 32 950 annotations de lien, chacune reliée à son OBJR ; les cibles GoTo/URI, les rôles et le texte normalisé correspondent au PDF convergé témoin, sans cible GoTo absente et sans figure dépourvue de texte alternatif. Le [nouvel aperçu convergé](../output/pdf/gramps-fancy-book-converged-parent-child-check-atend-n1000-20261006.pdf) pèse 13 461 240 octets. L’export reste au-dessus du budget total de 180 s ; le run complet est unique et ne doit pas être comparé comme une médiane au build antérieur de 706,759 s. Voir les [mesures appariées et l’audit brut](validation-latex-parent-child-check-atend-n1000-20261006.json).

### Essai apparié de compression des flux PDF — N=100 — 6 octobre 2026

Trois paires de premières passes balisées repartent chacune d’un dossier auxiliaire neuf, dans un ordre alterné. Le contrôle utilise le niveau LuaTeX par défaut (9) ; le candidat fixe `\pdfvariable compresslevel=1`. La médiane passe de 21,417 s à 21,294 s (−0,57 %) ; les écarts appariés sont −0,040, −0,097 et −0,143 s. Les PDF gardent 121 pages, 3 877 destinations, 3 328 annotations de lien avec `/StructParent`, le marquage actif et la même empreinte de texte normalisé. Le fichier passe de 1 413 831 à 1 627 544 octets (+15,1 %). Le gain est trop faible pour retenir la hausse de taille ; aucun réglage de production ne change. Les niveaux par défaut sont ceux du manuel de référence LuaTeX ([manuel](https://tex.org.uk/systems/doc/luatex/luatex.pdf), section 3.2.3). Voir le [relevé brut](validation-latex-stream-compression-n100-20261006.json).

### Essai apparié sans compression des object streams — N=100 — 6 octobre 2026

Trois paires repartent du même source et de dossiers auxiliaires neufs. Le candidat fixe `\pdfvariable objcompresslevel=0`, face au niveau 1 par défaut. La médiane est de 21,268 s contre 21,431 s (−0,76 %) ; les écarts appariés sont −0,119, −0,213 et −0,002 s. Les pages, destinations, liens avec `/StructParent`, balisage et texte extrait restent identiques dans les éléments contrôlés. En revanche, le PDF médian grossit de 1 413 831 à 5 701 725 octets (4,03 fois). Ce compromis ne justifie pas la variante ; elle est rejetée sans changement de production. Voir le [relevé brut](validation-latex-object-compression-n100-20261006.json).

### Profil des folios dans les liens de page — N=1 000 — 6 octobre 2026

Une passe directe utilise le source courant (SHA-256 `f0719756…`) avec les fichiers `.aux` et `.toc` remplis par le run témoin à contrôle différé. Le wrapper instrumente `\pageref*` dans `\gfbpagelink` et compte 17 590 appels. Le timer cumule 0,510 s, soit environ 0,20 % des 259,132 s de cette passe. Une sonde locale trouve une granularité d’un tick (1/65 536 s) ; le cumul reste quantifié et comprend le coût du wrapper de mesure. Le manuel de `pdftexcmds` décrit ces valeurs en secondes mises à l’échelle et précise que la résolution dépend de l’environnement ([manuel](https://ctan.math.illinois.edu/macros/generic/pdftexcmds/pdftexcmds.pdf)). Ce profil unique ne mesure pas un gain de production, mais ne justifie pas de modifier l’affichage des folios.

Le PDF diagnostique garde 1 140 pages, 38 025 destinations, 32 950 annotations de lien portant chacune `/StructParent`, les rôles de structure identiques au build convergé et 400 figures avec texte alternatif. Son texte normalisé correspond à celui du PDF convergé. Le test ne vérifie pas le graphe complet des OBJR pour cette passe et le temps inclut l’instrumentation. La prochaine cible du profil est le coût des hooks hyperref/tagpdf qui créent les annotations et leur structure accessible. Voir le [relevé brut](validation-latex-pageref-profile-n1000-20261006.json).
### Profil séparé des annotations OBJR et du ParentTree — N=1 000 — 6 octobre 2026

Une passe directe instrumente séparément, toutes les 128 insertions, l’ajout du lien dans l’arbre de structure et l’ajout de son entrée au ParentTree. Les deux macros sont appelées 32 944 fois ; extrapolées à partir de 257 échantillons, elles représentent respectivement **1,29 s** et **56,00 s**. Le cumul estimé de 57,29 s atteint environ 21,2 % des 270,563 s de la passe. Le code l3kernel installé implémente `\tl_gput_right:Ne` en reconstruisant la liste de tokens existante à chaque ajout, ce qui correspond à un coût croissant avec la taille de la liste.

L’audit pypdf confirme 1 140 pages, 38 025 destinations, 32 950 annotations toutes munies d’un `/StructParent`, 32 950 OBJR pointant chacun vers une annotation et 32 950 correspondances exactes entre ParentTree et élément de structure propriétaire. Les rôles, les 400 figures avec texte alternatif et le texte normalisé correspondent au PDF convergé témoin. Cette passe unique ne mesure pas un gain d’optimisation ; le prochain essai regroupe les entrées par lots dans une source isolée, avec comparaison appariée avant tout changement de production. Voir le [relevé brut](validation-latex-objr-subprofile-n1000-20261006.json).
### Prototype apparié de regroupement du ParentTree — N=1 000 — 6 octobre 2026

Le prototype temporaire accumule les entrées tagpdf par lots de 128, puis les ajoute au ParentTree en une seule opération au hook `tagpdf/finish/before`. Trois premières passes appariées repartant des mêmes `.aux`/`.toc` donnent des médianes de **265,362 s** pour la référence et **210,104 s** pour le candidat ; l’écart médian apparié est de **−55,258 s (−20,82 %)**. Les ordres sont alternés.

L’audit des trois PDF candidats retrouve 1 140 pages, 38 025 destinations, les mêmes rôles, 32 950 annotations de lien et `/StructParent`, 32 950 OBJR correspondants, toutes les correspondances ParentTree, 400 figures avec texte alternatif et le même texte normalisé que le PDF convergé témoin. L’optimisation est retenue avec détection des macros internes : si les macros tagpdf ou le hook attendu manquent, le renderer laisse la voie standard intacte. Le prototype repose toutefois sur des noms internes privés ; la prochaine étape vérifie le code généré par le renderer et exécute un export multipasse convergé. Voir le [relevé brut et les audits](validation-latex-parenttree-batching-n1000-20261006.json).
### Export convergé après regroupement du ParentTree — N=1 000 — 6 octobre 2026

Le renderer applique maintenant le regroupement par lots de 128 lorsque les macros tagpdf et le hook de fin attendus existent ; sinon il garde le comportement standard. `write_latex_pdf(..., extended_compilation=True)` converge en **449,174 s** et produit un PDF A4 2.0 balisé de 1 140 pages. L’audit comparatif retrouve 38 025 destinations, 32 950 annotations/OBJR, le propriétaire correct pour chaque entrée ParentTree, les rôles identiques, les 400 figures munies d’un texte alternatif et le texte normalisé identique au témoin convergé.

Un run convergé unique précédent prenait 545,189 s ; la baisse observée est de 96,015 s (17,6 %), à considérer comme indicative, car ce n’est qu’une paire de builds complets. Les trois paires directes appariées restent la mesure solide du gain (−20,82 %). Le budget total de 180 s n’est toujours pas atteint, et le RSS de ce build n’a pas été mesuré. La [fixture de recette balisée](../output/pdf/gramps-fancy-book-parenttree-batched-recipe-check-20261006.pdf) a réussi le validateur du dépôt, y compris le texte barré et les figures. Voir le [PDF convergé N=1 000](../output/pdf/gramps-fancy-book-converged-parenttree-batched-n1000-20261006.pdf) et le [relevé complet](validation-latex-parenttree-batched-converged-n1000-20261006.json).
### Temps par passe après regroupement du ParentTree — N=1 000 — 6 octobre 2026

Une instrumentation autour des appels LuaLaTeX confirme que l’export convergé comporte trois passes. La première, sans balisage et avec `hyperref` en mode brouillon, dure **22,281 s**. Les passes balisées suivantes prennent **214,949 s** et **211,100 s** ; leurs empreintes `.aux`/`.toc` sont identiques, ce qui clôt la convergence. À elles deux, elles comptent pour **426,049 s (95,0 %)** des 448,594 s mesurées par le helper. La première passe n’est donc plus le poste à optimiser ; les mesures suivantes doivent viser le travail répété des passes balisées. Voir le [relevé par passe](validation-latex-parenttree-batched-pass-breakdown-n1000-20261006.json).


### Profil des macros hyperref après regroupement du ParentTree — N=1 000 — 6 octobre 2026

Une passe directe balisée, avec les fichiers auxiliaires remplis du build courant, prend 212,560 s. L’instrumentation chronomètre les appels complets à `\hyperlink` et `\href` : 17 601 appels cumulent 49,005 s et 9 009 appels cumulent 26,052 s. Ces intervalles incluent le travail effectué sous hyperref, notamment les opérations tagpdf ; ils se recouvrent conceptuellement et ne doivent pas être additionnés comme des coûts indépendants. L’effet des marqueurs n’est pas mesuré séparément.

L’audit retrouve les mêmes 1 140 pages, 38 025 destinations, 32 950 annotations munies de `StructParent`, 32 950 associations OBJR correctement référencées, 400 figures avec texte alternatif et la même empreinte de texte que le PDF convergé ParentTree regroupé. Cette passe diagnostique n’apporte pas de comparaison de durée appariée et ne justifie pas de changement de production. L’étape suivante profile les opérations tagpdf de structure et de contenu marqué dans ce même état auxiliaire. Voir le [relevé brut](validation-latex-link-macro-profile-parenttree-batched-n1000-20261006.json) et le [PDF diagnostique temporaire](../tmp/pdfs/link-profile-parenttree-batched-n1000-20261006/book.pdf).


### Profil des opérations tagpdf sous les liens — N=1 000 — 6 octobre 2026

Sur une passe directe balisée de 211,630 s, les wrappers Lua mesurent `tag_struct_begin:n` 128 031 fois pour 51,132 s et `tag_mc_begin:n` 124 747 fois pour 11,943 s. `tag_struct_end:` cumule 3,577 s, `tag_mc_begin_pop:n` 4,999 s, `tag_mc_end:` 1,795 s et `tag_mc_end_push:` 1,477 s. Ces mesures sont inclusives et leurs coûts peuvent se recouvrir ; le coût propre des wrappers n’a pas été étalonné. Le hook de shipout LuaTeX associe 32 944 annotations aux structures en 1,802 s ; le chemin d’insertion inline ne s’exécute pas sur ce moteur.

Le PDF de 1 140 pages correspond au témoin convergé pour les 38 025 destinations, les 32 950 annotations et leurs propriétaires OBJR/ParentTree, les rôles, les 400 textes alternatifs et l’empreinte du texte. La mesure identifie le début de structure comme prochaine piste d’analyse, sans encore établir qu’une optimisation sûre est possible. Aucun changement de production n’est retenu. Voir le [relevé brut](validation-latex-tagpdf-link-operations-profile-parenttree-batched-n1000-20261006.json) et le [PDF diagnostique temporaire](../tmp/pdfs/tagpdf-link-ops-profile-parenttree-batched-n1000-20261006/book.pdf).


### Prototype rejeté — voie rapide pour une clé de structure unique — N=1 000 — 6 octobre 2026

Un prototype temporaire remplace le parsing générique uniquement pour les appels `__tag/struct` contenant une seule clé `tag=…`, et appelle directement le même socket tagpdf. Il prend en charge 65 367 des 128 031 créations de structure ; les 62 664 listes combinées restent sur le parseur normal. Sur une passe instrumentée par variante, le temps mural passe de 212,870 à 210,590 s (−2,280 s, −1,07 %). Le profil imbriqué estime environ 2,22 s de travail net évité après le coût du socket. Ce résultat unique ne distingue pas l’effet de la variabilité des passes.

L’audit retrouve les mêmes 1 140 pages, rôles, destinations, annotations, associations OBJR/ParentTree, textes alternatifs et texte extrait que le build convergé. La sortie est donc correcte dans la fixture, mais le gain n’est ni répliqué ni assez solide pour justifier le remplacement global de `\keys_set:nn` par un contournement dans le renderer. Prototype rejeté ; aucun code de production n’est modifié. La suite profile le reste du travail dans la création des structures. Voir le [relevé brut](validation-latex-tag-structure-key-fastpath-parenttree-batched-n1000-20261006.json).


### Profil des tables TeX/Lua de tagpdf — N=1 000 — 6 octobre 2026

Une passe directe balisée mesure 1 061 820 mises à jour de propriétés tagpdf pour 12,428 s cumulées, 157 703 ajouts de séquence pour 2,378 s, et 128 031 appels à la création des nouvelles tables de propriété et de séquence (0,961 s et 0,879 s). `__tag_struct_set_tag_info:nnn` cumule 15,867 s sur 128 031 appels ; ce temps comprend des écritures de propriétés déjà comptées, et les autres intervalles peuvent également se recouvrir. Le temps mural de 221,430 s reflète cette instrumentation plus lourde et ne constitue pas une mesure de production.

L’audit du PDF confirme l’équivalence au témoin convergé : 1 140 pages, 38 025 destinations, 32 950 liens et relations OBJR/ParentTree correctes, aucun texte alternatif de figure manquant et même empreinte de texte. Deux prototypes mettent en attente les mises à jour des tables miroir Lua : le premier envoie un lot de 128 à chaque vidage, le second garde les lots jusqu’au shipout et les vide aussi avant le contrôle final de tagpdf. Ils prennent respectivement 300,26 s et 364,93 s contre 212,56 s pour la référence directe, sur une exécution par variante. Les compteurs `\hyperlink` et `\href` restent instrumentés et les graines `.aux`/`.toc` sont identiques ; ces prototypes sont rejetés comme nettement plus lents. Aucun changement de production n’est retenu. La suite profile les opérations internes de `tag_struct_begin:n`. Voir le [relevé brut](validation-latex-tagpdf-lua-mirror-batching-n1000-20261006.json), le [profil initial](validation-latex-tagpdf-structure-storage-profile-parenttree-batched-n1000-20261006.json) et le [PDF temporaire](../tmp/pdfs/tagpdf-lua-mirror-page-batched-n1000-20261006/book.pdf).

### Profilage interne de la création des structures — N=1 000 — prochaine mesure

Une passe instrumentée de 223,68 s décompose 128 031 appels à `tag_struct_begin:n`. Le parsing des clés cumule 15,882 s et l’affectation du tag et du namespace 14,486 s. La résolution des rôles prend 2,746 s, la création des tables 3,026 s au total, et l’ajout des structures enfants 3,214 s. Ces timers sont imbriqués ; ils ne s’additionnent pas avec le timer externe de 57,968 s. Le contrôle parent/enfant différé n’est pas exécuté à chaque début de structure. Un minuteur de séquence ciblait une variante incorrecte ; le temps de l’ajout réel est inclus dans celui de l’ajout d’enfant.

Le PDF balisé A4 de 1 140 pages conserve 38 025 destinations, 32 950 annotations de lien et leurs propriétaires OBJR/ParentTree, les mêmes rôles, les 400 textes alternatifs et la même empreinte du texte extrait que le témoin convergé. Cette passe fortement instrumentée n’est pas une mesure de performance de production. Aucun changement n’est retenu. La suite cible la conversion répétée des noms PDF et les écritures de propriétés au sein de l’affectation des balises. Voir le [relevé brut](validation-latex-tagpdf-struct-begin-internals-profile-parenttree-batched-n1000-20261006.json) et le [PDF temporaire](../tmp/pdfs/tagpdf-struct-begin-internals-profile-parenttree-batched-n1000-20261006/book.pdf).

### Prototypes de conversion rapide des noms PDF — N=1 000 — 6 octobre 2026

Trois variantes temporaires ciblent les noms de balises ASCII fréquents. La liste de 21 entrées `\str_case` conserve l’audit PDF complet, mais prend 255,88 s, soit 43,32 s de plus que la référence à 212,56 s. La table de commandes prend 247,58 s et échoue à l’équivalence : elle produit 1 040 clés ParentTree de moins et une empreinte de texte différente. Une courte liste avec `Link`, `text` et `text-unit` passe l’audit, mais prend 217,09 s (+4,53 s, +2,13 %) dans une exécution unique. Aucun gain n’est établi ; les trois prototypes sont rejetés sans changement du renderer. La conversion rapide des noms n’est pas retenue comme cible. Voir le [relevé brut](validation-latex-tagpdf-pdf-name-fastpath-n1000-20261006.json), le [PDF équivalent temporaire](../tmp/pdfs/tagpdf-pdf-name-fastpath-profile-parenttree-batched-n1000-20261006/book.pdf) et le [PDF rejeté](../tmp/pdfs/tagpdf-pdf-name-csname-fastpath-profile-parenttree-batched-n1000-20261006/book.pdf).

### Filtrage du miroir Lua tagpdf — N=1 000 — 6 octobre 2026

Un prototype temporaire garde les mises à jour des propriétés et séquences TeX, mais n’envoie à Lua que `tag`, `rolemap`, `parentrole` et `parentnum`, les champs observés dans les lectures directes de `tagpdf.lua`. Il supprime aussi les mises à jour du miroir de séquences. La passe prend 242,05 s contre 212,56 s pour la référence ; l’audit échoue : le PDF a 1 040 clés ParentTree de moins et une empreinte de texte différente. Cette revue statique n’a donc pas identifié tous les consommateurs du miroir. Prototype rejeté, sans changement de production ; conserver toutes les mises à jour privées dans les prochaines pistes. Voir le [relevé brut](validation-latex-tagpdf-lua-mirror-filter-n1000-20261006.json) et le [PDF temporaire rejeté](../tmp/pdfs/tagpdf-lua-mirror-selective-profile-parenttree-batched-n1000-20261006/book.pdf).

### Mesure RSS du build convergé avec ParentTree regroupé — N=1 000 — 6 octobre 2026

Une recompilation complète du source LaTeX exact (SHA-256 `b40c13e8…`) converge en trois passes : 26,509 s, 234,010 s et 240,461 s, soit 500,995 s au total. Le maximum RSS relevé par `ru_maxrss` sur macOS est de **1 104 003 072 octets (1 052,86 Mio)** pour les processus enfants, principalement LuaLaTeX ; la limite de 512 Mio n’est pas atteinte. L’espace logique du dossier temporaire atteint 22 614 240 octets (21,57 Mio). La mesure porte sur le compilateur et son dossier, pas sur l’ensemble du processus d’export Gramps.

Le PDF recompilé garde les 1 140 pages A4, 38 025 destinations, les rôles, les 400 figures avec texte alternatif, les 32 950 annotations de lien et leurs associations OBJR/ParentTree, ainsi que la même empreinte du texte extrait. Le hash binaire diffère ; `/CreationDate`, `/ModDate` et l’identifiant du trailer ont également changé. La comparaison n’a pas localisé tous les octets différents. Les deux builds ont pris 449,174 s et 500,995 s ; cette paire de runs complets ne suffit pas à attribuer l’écart. Le plafond de compilation de 180 s reste également dépassé. Voir le [relevé RSS et l’audit](validation-latex-parenttree-batched-rss-n1000-20261006.json), le [relevé convergé initial](validation-latex-parenttree-batched-converged-n1000-20261006.json) et le [PDF recompilé](../tmp/l8-3-rss-parenttree-batched-n1000-20261006/book.pdf).

### Essais de paragraphes aplatis et de taille de lot ParentTree — N=100 — 6 octobre 2026

L’option tagpdf `para/flattened=true` a été essayée sur le livre ramifié de 121 pages. Activée au début du document, elle ne retire que deux éléments `/Part` (2 289 → 2 287) ; le temps passe de 69,837 à 68,668 s sur un run par variante et le pic RSS de 338 214 912 à 348 897 280 octets. Le texte normalisé, les liens/`StructParent`/OBJR et les 40 figures avec texte alternatif restent identiques. Une réactivation après chaque titre provoque ensuite une erreur de fin de document : 1 998 débuts de paragraphe `/text-unit` contre 1 961 fins. Cette piste est donc rejetée sans modification du renderer.

La taille des lots ParentTree a ensuite été comparée en passes LuaLaTeX directes, avec les mêmes fichiers `.aux`/`.toc` convergés. Le tri initial d’un passage par valeur suggère 512 ou 1 024 ; trois paires alternées comparent alors 128 à 512 entrées par lot : les durées sont respectivement 31,955 / 32,147 / 32,032 s et 32,369 / 31,998 / 31,885 s. L’écart médian apparié est de −0,147 s (−0,46 %), inférieur aux variations observées. Les pics RSS se recouvrent largement et varient davantage que cette différence. Les six sorties gardent 121 pages, la même structure Poppler et le même texte normalisé ; elles conservent 3 335 annotations de lien avec `/StructParent`, toutes les balises `/Link` et 40 figures avec texte alternatif. Aucun changement de production n’est retenu. Ces passes directes sont diagnostiques et ne mesurent pas la convergence complète. Le [relevé brut](validation-latex-para-flattening-parenttree-batch-size-n100-20261006.json) conserve les audits et les limites de mesure.

### Essai apparié de lots ParentTree 128/512 — N=1 000 — 6 octobre 2026

Trois paires alternées utilisent la même source (SHA-256 `b40c13e8…`) et les mêmes fichiers `.aux`/`.toc` convergés. La médiane passe de **207,112 s** avec 128 entrées à **206,835 s** avec 512 ; les écarts appariés sont −1,277, −0,754 et −0,117 s, soit une médiane de **−0,754 s (−0,36 %)**. Les PDF font la même taille médiane, 13 461 244 octets. L’essai conserve donc le seuil 128 en production : il ne démontre qu’un gain inférieur à la variation pertinente et porte sur des passes directes, pas sur une compilation multipasse.

Les six sorties sont balisées et correspondent au témoin sur 1 140 pages, 38 025 destinations, 32 950 annotations de lien, leurs associations OBJR/ParentTree, les rôles, les 400 textes alternatifs et le texte extrait normalisé. L’empreinte mémoire `time -l` a une médiane de 1 174 177 232 octets pour 128 et 1 169 524 104 pour 512, mais les écarts appariés vont de −94 601 264 à +50 675 664 octets. Cette empreinte n’est pas la mesure RSS `ru_maxrss` utilisée dans le relevé précédent et ne montre pas ici de baisse stable. Aucun réglage de production n’est changé ; les budgets L8.3 restent dépassés. Tous les timings, empreintes et audits figurent dans le [relevé brut](validation-latex-parenttree-batch-size-n1000-20261006.json).

### Essai d’un seul passage balisé final — N=1 000 — 7 octobre 2026

Une séquence exploratoire compile le livre sans balisage avec `hyperref` en brouillon (20,965 s), sans balisage avec liens actifs (94,467 s), puis une seule fois avec balisage et liens actifs (208,248 s). Cette troisième passe produit un PDF de 1 140 pages dont les rôles, destinations, liens accessibles, associations OBJR/ParentTree, textes alternatifs et texte extrait correspondent aux témoins contrôlés. Cette parité ne suffit toutefois pas à valider les attributs géométriques des figures.

L’inspection des 400 attributs `/BBox` trouve une origine `(0, 0)` pour chacune des figures candidates, alors que les 400 boîtes du PDF convergé témoin ont leur position réelle ; les 400 valeurs diffèrent. Dans TeX Live 2026, le code de balisage des graphiques lit les propriétés `xpos` et `ypos` depuis les fichiers auxiliaires pour construire ces boîtes, propriétés qui ne sont enregistrées qu’en mode balisé. Le PDF de l’essai est donc invalide pour cette optimisation : une passe balisée précédente est nécessaire avant celle qui écrit les boîtes correctes. Aucun changement de production n’est retenu. La prochaine piste L8.3 doit accélérer le travail des passes balisées sans en supprimer une ni altérer les positions accessibles des figures. Le [relevé brut](validation-latex-tagged-final-pass-experiment-n1000-20261007.json) détaille les mesures et comparaisons.

### Dédoublonnage des URL partagées de l’annexe — N=100 — 7 octobre 2026

Le renderer imprime toujours les URL propres à chaque citation. Pour les champs partagés, il ne garde qu’une occurrence des URL de chaque source et dépôt dans l’annexe documentaire. Le titre, les détails de source et de dépôt, chaque citation et ses renvois restent présents. Toutes les 317 destinations URI restent accessibles, dont les 303 destinations propres aux citations.

Trois builds convergés du même livre ramifié synthétique N=100, chacun dans un répertoire neuf avec le helper de compilation de production, donnent les résultats suivants :

| Variante | Durées (s) | Médiane (s) | PDF médian (octets) | Pages | Macros bookurl | Annotations de lien | Annotations URI |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Référence | 45,346 ; 45,563 ; 45,471 | 45,471 | 1 402 062 | 121 | 909 | 3 335 | 1 216 |
| URL partagées dédoublonnées | 41,161 ; 41,116 ; 41,131 | 41,131 | 1 312 919 | 117 | 317 | 2 449 | 330 |

La médiane de compilation baisse de 4,340 s (9,54 %) et le PDF de 89 143 octets (6,36 %). Les 2 119 liens internes sont conservés et résolvent tous leur cible. Les 40 balises de figure gardent un texte alternatif non vide et une boîte /BBox de largeur et hauteur positives ; les positions de certaines figures de l’annexe changent avec le reflow. Le ParentTree associe chaque annotation restante à son propriétaire. Les pages 77, 78 et 87 ont été examinées visuellement : les URL conservées sont complètes et les images n’empiètent pas sur le texte.

Ce contrôle porte sur N=100 et un fixture synthétique ; il ne démontre pas encore l’atteinte du budget PDF N=1 000. Le validateur spécifique à la recette barrée ne s’applique pas à ce fixture, qui ne contient pas le passage requis ; le contrôle repose donc sur l’audit de structure PDF et la revue visuelle des pages citées. Le PDF témoin passe de 121 à 117 pages ; les seules destinations nommées supprimées sont page.117 à page.120, sans lien interne qui les cible. Les durées, empreintes LaTeX et détails d’audit figurent dans le [relevé brut](validation-latex-citation-url-dedup-n100-20261007.json).

### Confirmation à N=1 000 — 7 octobre 2026

Un build convergé du candidat N=1 000 est comparé au témoin de production convergé construit le 6 octobre. Cette comparaison n’a qu’un build candidat et un témoin historique ; elle indique la direction du gain mais ne remplace pas des répétitions appariées.

| Variante | Compilation (s) | PDF (octets) | Pages | Macros bookurl | Annotations de lien | Annotations URI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Témoin convergé | 449,174 | 13 461 234 | 1 140 | 9 009 | 32 950 | 12 072 |
| URL partagées dédoublonnées | 423,847 | 12 556 083 | 1 096 | 3 125 | 24 126 | 3 248 |

Le candidat gagne 25,327 s (5,64 %) et 905 151 octets (6,72 %). Les 3 125 cibles URI uniques sont inchangées, dont les 3 003 cibles de citation ; les 20 878 liens internes résolvent tous leur destination. Les 44 destinations de page finales qui disparaissent ne sont ciblées par aucun lien. Les 400 figures conservent un texte alternatif non vide et une boîte /BBox valide dans la page ; leurs positions ont été recalculées pour le reflow de l’annexe. Les 24 126 liens restants ont tous un propriétaire ParentTree correspondant. Les pages 702, 794 et 795 ont été examinées visuellement.

La compilation reste à 423,847 s, au-dessus du budget de 180 s. Une répétition et la mesure RSS sont consignées dans la section suivante ; les deux résultats doivent encore être confirmés par davantage de répétitions appariées. Le [relevé brut initial](validation-latex-citation-url-dedup-n1000-20261007.json) consigne les empreintes, le PDF témoin et l’audit comparatif.

### Répétition convergée et RSS — N=1 000 — 7 octobre 2026

Le même source candidat (SHA-256 `63d01782…`) et ses 200 médias ont été recompilés dans un dossier neuf. Le build a convergé en 407,011 s. L’exécution précédente du même source avait pris 423,847 s ; la médiane des deux mesures est de 415,429 s, avec une étendue de 16,836 s (4,05 % de la médiane). Deux mesures ne suffisent pas pour caractériser précisément la variabilité.

Sur macOS, `ru_maxrss` rapporte 1 069 842 432 octets (1 020,28 Mio) pour les processus enfants, principalement LuaLaTeX. Un échantillonnage `ps` à une seconde atteint 1 067 237 376 octets (1 017,8 Mio), et l’espace logique temporaire culmine à 21 417 167 octets (20,43 Mio), échantillonné toutes les 100 ms. Le RSS est inférieur de 34 160 640 octets au relevé historique du 6 octobre, mais ce dernier porte sur le source antérieur sans dédoublonnage ; cette comparaison ne démontre pas un gain mémoire stable. Le repère de 512 Mio reste dépassé, tout comme le budget de compilation de 180 s.

Le PDF répété reste balisé, en version 2.0 et sur 1 096 pages. Il conserve 24 126 annotations de lien, 3 248 annotations URI sur 3 125 cibles, 20 878 liens GoTo internes et les 400 figures avec texte alternatif et /BBox valide. Chaque annotation de lien retrouve son propriétaire OBJR dans le ParentTree ; le hash du texte extrait normalisé correspond exactement au premier PDF candidat. Le hash binaire diffère, les métadonnées de date et l’identifiant du trailer étant recréés à chaque compilation. Les durées par passe n’ont pas été mesurées pendant cette répétition. Voir le [relevé brut de la répétition et du RSS](validation-latex-citation-url-dedup-repeat-rss-n1000-20261007.json) et le [PDF recompilé](../tmp/l83-shared-source-url-dedup-20261007/n1000/repeat-rss/book.pdf).

La suite L8.3 doit mesurer séparément les passes balisées du build candidat et profiler leur coût restant, sans en supprimer une ni dégrader la géométrie accessible des figures.
