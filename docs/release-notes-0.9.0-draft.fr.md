# Brouillon interne — notes de version 0.9.0

**Statut : préparation uniquement.** Le module reste marqué `EXPERIMENTAL` dans Gramps. Aucune GitHub Release n’est publiée et ce document n’annonce pas une version stable.

## Contenu prévu

- Rapport Gramps 6 centré sur une famille de référence, avec livres HTML hors ligne en ZIP, PDF produit par LuaLaTeX et instantané JSON de diagnostic.
- Parcours des ascendances et descendances, fiches et notices familiales, index, renvois internes et appels de citation réutilisables.
- Notes éditoriales F0, événements, sources et dépôts, gestion des médias et recadrages, textes alternatifs, réglages de langue français/anglais et confirmation de confidentialité à chaque export.
- Archive reproductible et catalogue français compilé pendant la construction.

## Exemple fictif

Le [README français](../README.fr.md#exemple-en-ligne-de-commande) décrit l’import et l’export de l’exemple [reference-family.ged](../examples/reference-family.ged). Ses personnes, lieux et références d’archives sont fictives ; il ne contient pas de média. Dans un profil isolé Gramps 6.0.8-1, l’archive 0.9.0 produit depuis cet exemple un PDF français balisé de 9 pages A4 et un ZIP HTML valide dont les 29 liens locaux sont résolus. Les neuf pages PDF ont été examinées sans coupure ni superposition visible. Voir les [relevés d’import](validation-example-import-20261006.json) et d’[export](validation-example-report-20261006.json). Ce n’est pas un modèle de livre complet ; l’ouverture interactive du ZIP et l’installation via le gestionnaire graphique restent à qualifier. Le renderer actuel a depuis produit un PDF GUI A4 balisé de 103 pages et un ZIP HTML avec vingt portraits publics dans un autre arbre fictif isolé. La revue initiale des 103 pages a révélé une ligne de renvoi orpheline dans la citation [299] ; le renderer a été corrigé, puis les pages d’annexe du nouvel export GUI ont été relues sans défaut visible. La conformité PDF/UA, l’accessibilité, l’ouverture interactive du ZIP et l’installation via le gestionnaire graphique restent à qualifier. Les détails figurent dans la [validation du cycle du paquet](validation-addon-lifecycle.fr.md).

## Vérifications déjà disponibles

- La CI du [run 37517722010](https://github.com/grostim/gramps-fancy-genealogical-book/actions/runs/37517722010) passe sur Python 3.10–3.13, Windows, macOS, Gramps 6.0.7 et 6.0.8 en CLI, le canari 6.1 et le prototype LuaLaTeX.
- Sur Gramps 6.0.8 en profil propre, l’archive 0.9.0 génère les sorties JSON, HTML ZIP et PDF ; le PDF français balisé compte 18 pages A4. Les marges configurées sont de 15 mm. Voir la [validation du paquet](validation-addon-lifecycle.fr.md).
- L’export GUI de référence a produit un PDF A4 balisé de neuf pages, toutes examinées ; il porte sur le renderer au commit `b8141bc`. Un nouvel export GUI du renderer actuel a produit un PDF balisé de 103 pages et un ZIP HTML avec vingt portraits publics. La revue page par page initiale a trouvé une coupure dans la citation [299] ; après correction, le nouvel export a conservé 103 pages et les pages d’annexe ont été relues. Voir la [qualification GUI](validation-addon-lifecycle.fr.md). L’installation via le gestionnaire graphique et l’accessibilité restent à qualifier.

## Limites connues

- Le support vérifié de façon répétable porte sur les exports CLI de Gramps 6.0.7 et 6.0.8. Le canari 6.1 est non bloquant ; les autres versions Desktop ne sont pas qualifiées.
- Gramps Web n’est pas pris en charge : l’audit de l’API 3.23.1 relève des blocages pour la catégorie `CATEGORY_WEB`, les archives `.zip`, le chemin de sortie serveur et la progression des tâches. Voir [l’audit Gramps Web](validation-gramps-web.fr.md).
- Les grands livres restent lents et gourmands en mémoire. Un build synthétique N=1 000 a pris 500,995 s en trois passes et atteint 1 104 003 072 octets de RSS ; les deux mesures dépassent les repères actuels. L’option de compilation prolongée évite certaines expirations, sans garantir que le livre aboutisse. Voir [les mesures de performance](validation-performance.fr.md).
- Les PDF sont balisés, mais la conformité PDF/UA et les annonces au lecteur d’écran n’ont pas été validées. Le lecteur d’écran HTML et les médias photographiques réalistes restent aussi à examiner.
- La recette des 27 scénarios AC-01 à AC-27 n’est pas terminée ; plusieurs saisies et exports depuis les éditeurs GUI restent à vérifier. Le statut de chaque scénario est dans la [matrice d’exigences](requirements.fr.md).
- Les données privées lisibles et celles de personnes vivantes peuvent figurer dans le livre. La confirmation affichée par le rapport n’anonymise pas les données ; vérifier le contenu et les droits avant partage.
- La procédure de mise à niveau depuis une version antérieure réellement distribuée reste à qualifier. L’archive est générée localement et ignorée par Git ; elle n’est pas publiée.

## Conditions avant une version stable

Terminer les recettes fonctionnelles requises ou faire approuver explicitement les changements de périmètre, qualifier l’installation via le gestionnaire graphique, achever les autres exports GUI requis, décider des seuils de performance, terminer les revues d’accessibilité et résoudre le blocage Gramps Web ou faire approuver explicitement un changement de périmètre. La revue page par page initiale du PDF GUI de 103 pages produit le 9 octobre a trouvé une ligne de renvoi orpheline dans la citation [299] ; le renderer a été corrigé et les pages d’annexe du nouvel export ont été relues. Si l’artefact de release diffère de cet export, refaire sa revue visuelle. Réexaminer ensuite ces notes et construire l’artefact de release avant toute publication.
