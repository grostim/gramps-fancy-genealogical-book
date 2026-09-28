# Architecture

Cette page décrit l’implémentation de la branche de développement et distingue les fonctionnalités livrées des validations qui restent à démontrer.

Le projet comporte six responsabilités :

1. **Intégration Gramps** — enregistrement du rapport, options, accès à la base et cycle d’exécution.
2. **Extraction et normalisation** — conversion des personnes, familles, événements, sources, citations, notes et médias Gramps en objets indépendants du framework.
3. **Parcours généalogique** — chemins bornés d’ascendance et de descendance, générations, branches, occurrences et déduplication.
4. **Modèle éditorial** — parties ordonnées du livre, notices familiales, fiches, notes, citations, médias et cibles de navigation.
5. **Rendu LaTeX** — source imprimable avec renvois et références de pages.
6. **Rendu HTML** — pages statiques du livre et archive ZIP consultable hors ligne.

## Instantané et parcours

L’extraction produit le schéma JSON 0.8. Des identifiants stables de sections familiales et d’occurrences relient les partenaires, enfants, liens de filiation et apparitions répétées. Les occurrences conservent la génération, la branche et les chemins de filiation, y compris les chemins alternatifs vers une même personne. Chaque personne référence une première occurrence, même si aucune fiche complète n’est créée. Les limites d’ascendance et de descendance sont indépendantes et illimitées par défaut ; les partenaires rencontrés par mariage ne déclenchent pas une nouvelle expansion de l’ascendance.

L’adaptateur accède aux données par les accesseurs de la base Gramps et ne la modifie pas. Les références manquantes ou inaccessibles donnent des diagnostics ; les indicateurs de confidentialité sont conservés pour les données que la base fournie autorise à lire. L’adaptateur ne contourne pas les droits de Gramps. Avant chaque export, l’utilisateur doit confirmer que les données privées accessibles et les informations sur des personnes vivantes peuvent être incluses ; la confirmation précédente est réinitialisée à chaque lancement Desktop. Cette confirmation ne filtre ni n’anonymise la sortie.

## Modèle éditorial et règles de publication

Le livre ordonné relie la couverture et les préliminaires, le sommaire, les parties d’ascendance et de descendance, les notices familiales, les fiches admissibles, les documents et l’index des personnes. Une note n’est référencée pour publication que si elle porte l’étiquette `BOOK_PUBLICATION`. Les six rôles de couverture et de préliminaires sont lus sur les notes admissibles liées directement à la famille de référence (F0). Les règles implémentées permettent notamment de sélectionner une fiche avec `BOOK_PROFILE=YES`.

Chaque famille dispose d’une notice unique qui renvoie vers ses différents contextes. Les cibles de citation sont uniques par handle Gramps ; chaque appel conserve son contexte et son chemin de champ. Les entrées de citation renvoient à leur Source, aux dépôts de cette source et aux médias admissibles qui lui sont associés. La numérotation compacte suit le premier emploi dans l’ordre du livre. Les emplacements médias sont uniques par handle Gramps tout en conservant leurs régions contextuelles et leurs liens de citation.

Le rapport séparé de cohérence ne regroupe des événements qu’en présence d’un même `BOOK_FACT_ID` explicite. Il signale les plages de dates disjointes comme conflits confirmés et les références de lieux différentes comme un cas à examiner. Ce rapport ne fusionne pas les événements et ne modifie pas leur liste dans le livre. Des dates, lieux, types ou descriptions semblables ne créent jamais de groupe.

## Médias et rendus

L’utilitaire média résout les chemins relatifs de la base via Gramps et refuse les médias portant `BOOK_EXCLUDE`. Les images raster sont orientées selon EXIF, recadrées selon la région demandée puis enregistrées en PNG sans perte. Pour les PDF, l’URL d’une citation est prioritaire ; un PDF multipage sans URL reste une référence, tandis qu’un PDF monopage sans URL peut être rastérisé à 300 ppp, sous un plafond de pixels. Pillow et pypdfium2 sont facultatifs. Les erreurs de conversion récupérables deviennent des diagnostics structurés.

Le rendu LaTeX compose la couverture et les préliminaires, la généalogie, les fiches, les notices familiales, les citations, les médias, l’index et les renvois. Le rapport Gramps peut compiler cette source en PDF avec LuaLaTeX ; le compilateur désactive l’exécution shell, répète les passes jusqu’à stabilisation des fichiers auxiliaires et refuse les renvois non résolus ou les dépassements de marge. LuaLaTeX est facultatif et n’est requis que pour la sortie PDF. Ce mode reste expérimental ; son installation dans Gramps et sa revue visuelle page par page restent à valider.

Le rendu HTML produit un livre statique avec navigation interne, liens de citations, notes, médias et index. Le ZIP comprend `index.html`, les styles intégrés et les dérivés PNG autorisés avec des chemins relatifs ; il peut être consulté hors ligne après extraction. Le rendu comprend une mise en page adaptative, un lien d’accès direct au contenu, un focus clavier visible et des textes alternatifs informatifs.

La sélection automatique associe `.pdf` à la sortie PDF LuaLaTeX, `.zip` au livre HTML et `.json` historique à l’instantané JSON ; les formats peuvent aussi être choisis explicitement. Cette compatibilité ne vaut pas qualification de Gramps Web.

## Validations restantes

L’implémentation est plus avancée que ses preuves de bout en bout. Il reste notamment à exécuter les scénarios d’acceptation sur les versions Desktop et Web prises en charge, vérifier médias et liens relatifs dans un ZIP extrait, revoir clavier, lecteur d’écran et tailles de fenêtre, puis comparer visuellement le PDF généré à la spécification et aux maquettes fournies. Voir le [compte rendu de validation L7](validation-l7.fr.md) pour les preuves et limites actuelles.

Les identifiants techniques et métadonnées réservées utilisent des noms anglais et le préfixe `BOOK_`, par exemple `BOOK_PUBLICATION`, `BOOK_PROFILE`, `BOOK_EXCLUDE`, `BOOK_FEATURED` et `BOOK_FACT_ID`.

Pour l’enregistrement Gramps 6 et l’empaquetage manuel, le projet a consulté [grostim/gramps-two-way-fan-chart](https://github.com/grostim/gramps-two-way-fan-chart). Ce dépôt sert de référence d’implémentation ; son moteur généalogique et ses rendus ne sont pas copiés.
