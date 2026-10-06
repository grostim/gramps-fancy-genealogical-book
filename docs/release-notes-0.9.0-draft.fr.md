# Brouillon interne — notes de version 0.9.0

**Statut : préparation uniquement.** Le module reste marqué `EXPERIMENTAL` dans Gramps. Aucune GitHub Release n’est publiée et ce document n’annonce pas une version stable.

## Contenu prévu

- Rapport Gramps 6 centré sur une famille de référence, avec livres HTML hors ligne en ZIP, PDF produit par LuaLaTeX et instantané JSON de diagnostic.
- Parcours des ascendances et descendances, fiches et notices familiales, index, renvois internes et appels de citation réutilisables.
- Notes éditoriales F0, événements, sources et dépôts, gestion des médias et recadrages, textes alternatifs, réglages de langue français/anglais et confirmation de confidentialité à chaque export.
- Archive reproductible et catalogue français compilé pendant la construction.

## Exemple fictif

Le [README français](../README.fr.md#exemple-en-ligne-de-commande) décrit l’import et l’export de l’exemple [reference-family.ged](../examples/reference-family.ged). Ses personnes, lieux et références d’archives sont fictifs ; il ne contient pas de média. Son import CLI dans un profil isolé Gramps 6.0.8-1 est vérifié ; l’export du rapport à partir de cet exemple reste à faire. Voir le [relevé d’import](validation-example-import-20261006.json). Ce n’est pas un modèle de livre complet.

## Vérifications déjà disponibles

- La CI du [run 37517722010](https://github.com/grostim/gramps-fancy-genealogical-book/actions/runs/37517722010) passe sur Python 3.10–3.13, Windows, macOS, Gramps 6.0.7 et 6.0.8 en CLI, le canari 6.1 et le prototype LuaLaTeX.
- Sur Gramps 6.0.8 en profil propre, l’archive 0.9.0 génère les sorties JSON, HTML ZIP et PDF ; le PDF français balisé compte 18 pages A4. Les marges configurées sont de 15 mm. Voir la [validation du paquet](validation-addon-lifecycle.fr.md).
- La recette CLI actuelle ne prouve pas l’installation graphique du paquet courant. La fenêtre temporaire Gramps et l’export GUI correspondant restent à qualifier.

## Limites connues

- Le support vérifié de façon répétable porte sur les exports CLI de Gramps 6.0.7 et 6.0.8. Le canari 6.1 est non bloquant ; les autres versions Desktop ne sont pas qualifiées.
- Gramps Web n’est pas pris en charge : l’audit de l’API 3.23.1 relève des blocages pour la catégorie `CATEGORY_WEB`, les archives `.zip`, le chemin de sortie serveur et la progression des tâches. Voir [l’audit Gramps Web](validation-gramps-web.fr.md).
- Les grands livres restent lents et gourmands en mémoire. Un build synthétique N=1 000 a pris 500,995 s en trois passes et atteint 1 104 003 072 octets de RSS ; les deux mesures dépassent les repères actuels. L’option de compilation prolongée évite certaines expirations, sans garantir que le livre aboutisse. Voir [les mesures de performance](validation-performance.fr.md).
- Les PDF sont balisés, mais la conformité PDF/UA et les annonces au lecteur d’écran n’ont pas été validées. Le lecteur d’écran HTML et les médias photographiques réalistes restent aussi à examiner.
- La recette des 27 scénarios AC-01 à AC-27 n’est pas terminée ; plusieurs saisies et exports depuis les éditeurs GUI restent à vérifier. Le statut de chaque scénario est dans la [matrice d’exigences](requirements.fr.md).
- Les données privées lisibles et celles de personnes vivantes peuvent figurer dans le livre. La confirmation affichée par le rapport n’anonymise pas les données ; vérifier le contenu et les droits avant partage.
- La procédure de mise à niveau depuis une version antérieure réellement distribuée reste à qualifier. L’archive est générée localement et ignorée par Git ; elle n’est pas publiée.

## Conditions avant une version stable

Terminer les recettes fonctionnelles requises ou faire approuver explicitement les changements de périmètre, qualifier l’installation et les exports graphiques du paquet courant, décider des seuils de performance, achever les revues d’accessibilité et résoudre le blocage Gramps Web ou faire approuver explicitement un changement de périmètre. Réexaminer ensuite ces notes et construire l’artefact de release avant toute publication.
