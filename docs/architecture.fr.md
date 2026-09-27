# Architecture

Le projet sépare six responsabilités :

1. **Intégration Gramps** — enregistrement du rapport, options, accès à la base et cycle d’exécution.
2. **Extraction et normalisation** — conversion en objets du domaine indépendants de Gramps.
3. **Moteur généalogique** — ascendances, descendances, générations, branches et déduplication.
4. **Modèle éditorial** — structure commune consommée par les rendus.
5. **Rendu LaTeX** — composition imprimable et compilation PDF.
6. **Rendu HTML** — site statique et distribution ZIP.

## Instantané d’extraction

Les couches d’extraction et de parcours produisent un modèle JSON v0.7 indépendant de Gramps. Les sections familiales ont des identifiants stables et pointent vers les occurrences de partenaires et d’enfants présentes dans le périmètre ; les liens parent-enfant conservent les identifiants des occurrences concernées et le type de filiation enregistré pour chaque parent. Chaque occurrence référence aussi sa première apparition avec `primary_occurrence_id`, même si aucune fiche complète n’est créée ; elle renvoie à ses sections familiales et conserve génération, branche et chemin pour le repère généalogique. Une structure éditoriale ordonnée relie les parties couverture, préliminaires, sommaire, ascendance, descendance, annexe documentaire et index aux sections familiales et occurrences du modèle. Les fiches des personnes éligibles référencent leurs événements, médias et sections familiales ; la composition narrative, les légendes et les notices de source restent à réaliser. Des limites d’ascendance et de descendance indépendantes restreignent l’extraction ; leur valeur par défaut est illimitée. Les caches indexés par handle évitent de relire un objet dans la même extraction ; les références facultatives manquantes donnent des diagnostics structurés.

Le modèle de parcours attribue à chaque occurrence sa partie, sa génération, sa famille et ses branches de départ ; les chemins alternatifs restent distincts. Les unions et partenaires donnent le contexte sans devenir de nouvelles racines. Les rendus HTML et LaTeX ne consomment pas encore ce modèle de parcours et restent des démonstrations.

Le texte des notes n’est exposé que si elles portent l’étiquette Gramps `BOOK_PUBLICATION`. Les drapeaux privés sont préservés sans exclure les données accessibles à la base fournie. Le JSON indique si l’instantané contient des objets ou associations privés ; l’avertissement requis avant la publication d’un livre complet reste à mettre en place.

## Accès aux données

L’adaptateur n’utilise que les accesseurs publics de la base Gramps. Il ne modifie pas la base et ne contourne pas ses contrôles d’accès. Une donnée inaccessible est représentée par un diagnostic, tandis qu’un membre manquant de la famille choisie bloque l’extraction.

Les noms techniques et métadonnées restent en anglais. Les noms réservés incluent `BOOK_PUBLICATION`, `BOOK_PROFILE`, `BOOK_EXCLUDE` et `BOOK_FEATURED`.

Pour l’enregistrement et l’empaquetage de Gramps 6, le projet a consulté [`grostim/gramps-two-way-fan-chart`](https://github.com/grostim/gramps-two-way-fan-chart). Il sert de référence, son moteur généalogique et ses rendus ne sont pas copiés.
