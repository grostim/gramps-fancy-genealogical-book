# Qualification de l’accessibilité PDF

## Audit automatique PDF/UA-2 — 9 octobre 2026

Les PDF sont produits en PDF 2.0 avec balisage. Le renderer n’émet pas
de déclaration de conformité PDF/UA : sa commande `DocumentMetadata`
définit actuellement seulement `lang` et `tagging=on`.

La qualification utilise **veraPDF Greenfield 1.30.3**, version stable
construite le 7 octobre 2026, installée uniquement dans un répertoire temporaire.
Le profil est explicitement `ua2`, sans réparation des métadonnées :

```sh
verapdf --flavour ua2 --format xml book.pdf > report.xml
```

L’option explicite évite la sélection automatique d’un profil PDF/A lorsque
le document ne déclare aucun standard. Voir la [documentation de validation](https://docs.verapdf.org/cli/validation/).

Les empreintes, résultats par fichier, versions et rapport XML intégral sont
conservés dans le [relevé](validation-pdf-accessibility-20261009.json) et
le [rapport veraPDF](validation-pdf-accessibility-20261009.xml).
Les fixtures sont fictives ; aucun arbre personnel n’est utilisé.

### Résultats observés

| Fixture | Pages | Règles réussies / échouées rapportées | Contrôles réussis / échoués rapportés |
| --- | ---: | ---: | ---: |
| CI riche, anglais | 16 | 1 727 / 1 | 58 223 / 1 |
| CI riche, français | 15 | 1 727 / 1 | 58 532 / 1 |
| CI peu documentée, anglais | 4 | 1 727 / 1 | 3 368 / 1 |
| N=1 000, tagpdf installé 0.99y | 1 108 | 1 727 / 1 | 10 996 605 / 1 |

Les quatre audits terminent normalement ; aucun échec de parsing, manque
de mémoire ni exception veraPDF n’est rapporté. Le code de sortie est 1
et les quatre fichiers sont **non conformes** au profil demandé.
Le seul échec signalé est ISO 14289-2:2024, clause 5, test 1 :
le schéma d’identification PDF/UA manque dans les métadonnées XMP.
Cette absence correspond au code de production actuel.

Les trois fichiers CI proviennent du commit `c99a378` de la PR #336,
[run 37936272667](https://github.com/grostim/gramps-fancy-genealogical-book/actions/runs/37936272667),
artifact `11618726899`. Le grand PDF provient du renderer `bf80ada`,
première paire, variante installée du
[banc N=1 000](validation-latex-tagpdf-version-paired-n1000-20261009.json).
Il n’a pas été recompilé pour cet audit. Aucune métadonnée n’a été réparée
et aucune déclaration de conformité n’a été ajoutée en production.

## Portée et suite

veraPDF couvre les exigences qu’il peut vérifier automatiquement ; sa
[documentation](https://docs.verapdf.org/validation/) distingue explicitement
les contrôles automatiques des contrôles humains pour PDF/UA. Un résultat
automatique ne qualifie pas la pertinence des textes alternatifs, le sens
des titres ou l’ordre de lecture effectif avec une aide technique.

Avant d’annoncer la conformité ou d’activer sa déclaration en production :

1. Vérifier l’ordre de lecture de la couverture, du sommaire, des profils,
   des notices, des notes et citations, de l’annexe et de l’index ; inclure
   des pages de continuation et les renvois en pied de page.
2. Vérifier avec un lecteur d’écran les annonces des titres, listes, liens,
   images et textes barrés, en français et en anglais ; consigner le lecteur,
   sa version, le lecteur PDF, les pages et les observations.
3. Confirmer la pertinence des textes alternatifs et que les éléments
   décoratifs ne perturbent pas la lecture ; les portraits synthétiques ne
   suffisent pas à qualifier les descriptions de photos représentatives.
4. Si ces contrôles passent, produire une variante avec la déclaration
   PDF/UA-2 appropriée, refaire l’audit automatique et vérifier l’absence
   de régression de contenu, liens, géométrie et pagination avant adoption.
5. Répéter la qualification sur les sorties Gramps Desktop courantes et
   les environnements cibles ; cette étape reste distincte de la recette
   synthétique et de la comparaison de versions tagpdf.

Les audits existants du balisage, des liens ParentTree/OBJR et des BBox
restent utiles. Ils ne remplacent pas ces vérifications.
