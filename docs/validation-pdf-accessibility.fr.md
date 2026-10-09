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

## Contrôle continu des exigences automatiques

`scripts/verify_pdf_ua2.py` lance veraPDF avec le profil explicite `ua2`,
conserve XML et stderr, puis refuse tout défaut supplémentaire. Son mode
par défaut exige un résultat automatique conforme. La CI utilise
`--allow-missing-identification` pour autoriser uniquement le défaut connu
ISO 14289-2:2024, clause 5, test 1, objet MainXMPPackage,
`containsPDFUAIdentification == true`. Le JSON continue d’indiquer
`is_compliant: false` et `human_accessibility_qualified: false`.

Le binaire CI est fixé à 1.30.3 par URL versionnée et SHA-256. Les rapports
FR, EN et peu documenté, ainsi que ceux des contrôles négatifs, sont
conservés dans l’artefact CI, y compris après échec. Une erreur d’exécution,
un rapport incomplet ou un défaut différent fait échouer le contrôle.

Exemple, avec un répertoire de rapport neuf :

```sh
python scripts/verify_pdf_ua2.py book.pdf --verapdf /path/to/verapdf \
  --report-directory /tmp/ua2-new-report --allow-missing-identification
```

Les contrôles locaux prouvent qu’un clone intact est accepté et que les
cas langue absente et attribut Alt supprimé sont refusés, même avec
l’exception de métadonnées. Un essai avec **Alt vide** a en revanche été
accepté par veraPDF 1.30.3 : l’audit existant du renderer exige toujours
un texte alternatif non vide, et la revue humaine doit en vérifier le sens.
Ces contrôles ne constituent pas une qualification exhaustive du validateur.
Voir le [relevé des contrôles](validation-pdf-ua2-ci-controls-20261009.json).

Le PDF GUI conservé de 103 pages avec vingt portraits publics a également
été audité : un seul échec, le même schéma PDF/UA absent, sur 1 002 036
contrôles réussis rapportés. Il utilise le renderer antérieur au déplacement
du groupe `samepage` après `\item` ; cette preuve ne remplace pas la
réexportation GUI du renderer actuel. Le rapport intégral est
[conservé](validation-pdf-accessibility-native-gui-20261009.xml).

## Qualification finale CI et export natif courant

La PR #339 est fusionnée après le succès du
[run 37946900354](https://github.com/grostim/gramps-fancy-genealogical-book/actions/runs/37946900354),
commit `1283c51`. Les six relevés attendus sont présents dans l’artefact
`11624441929` : FR, EN, peu documenté, clone intact et deux corruptions.
L’archive téléchargée correspond à son empreinte GitHub. Les trois sorties
normales et le clone intact passent la garde automatique ; les cas langue
absente et Alt supprimé sont rejetés. Les fichiers restent non conformes
au profil PDF/UA-2 en raison de l’identification absente.

Un nouveau profil Gramps 6.0.8-1 a aussi reçu l’archive courante, avec
Mistune et les dépendances média uniquement dans ce profil. Le checkout
n’est pas ajouté au `PYTHONPATH`. La fixture fictive de 202 personnes,
101 familles, 303 citations et vingt portraits publics produit un PDF
natif CLI de 103 pages, 77 489 201 octets. L’audit des 2 034 liens ne
trouve aucun écart ParentTree/OBJR ni destination non résolue ; les vingt
figures ont un Alt non vide et des BBox valides. veraPDF signale uniquement
le même défaut d’identification.

Les pixels des **103 pages** sont identiques au PDF GUI corrigé conservé
du 9 octobre, lors d’un rendu PDFium à 108 ppp sur ce Mac. Les pages
physiques 1, 22, 70 et 97 ont également été examinées directement : pas
de coupure visible, attribution du portrait lisible, citation [299] entière
sur la page 97. La comparaison exhaustive porte sur les pixels à cette
résolution ; elle ne qualifie ni la lecture d’écran ni le nouveau parcours GUI.

Le temps natif observé de 41,955 s comprend l’extraction et le rapport :
ce n’est ni une mesure du compilateur seul ni une comparaison appariée.
Le PDF reste au-dessus du repère de 16 Mio. Aucune réduction des images
ni déclaration de conformité n’est adoptée. Voir le
[relevé complet](validation-native-current-portraits-20261009.json).
