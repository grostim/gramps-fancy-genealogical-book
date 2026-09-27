# Architecture

Le projet sépare six responsabilités :

1. **Intégration Gramps** — enregistrement du rapport, options, accès à la base et cycle d’exécution.
2. **Extraction et normalisation** — conversion en objets du domaine indépendants de Gramps.
3. **Moteur généalogique** — ascendances, descendances, générations, branches et déduplication.
4. **Modèle éditorial** — structure commune consommée par les rendus.
5. **Rendu LaTeX** — composition imprimable et compilation PDF.
6. **Rendu HTML** — site statique et distribution ZIP.

## Instantané d’extraction

Les couches d’extraction et de parcours produisent un modèle JSON v0.7 indépendant de Gramps. Les sections familiales ont des identifiants stables et pointent vers les occurrences de partenaires et d’enfants présentes dans le périmètre ; les liens parent-enfant conservent les identifiants des occurrences concernées et le type de filiation enregistré pour chaque parent. Chaque occurrence référence aussi sa première apparition avec `primary_occurrence_id`, même si aucune fiche complète n’est créée ; elle renvoie à ses sections familiales et conserve génération, branche et chemin pour le repère généalogique. Une structure éditoriale ordonnée relie les parties couverture, préliminaires, sommaire, ascendance, descendance, annexe documentaire et index aux sections familiales et occurrences du modèle. Les fiches des personnes éligibles référencent leurs notes publiables, leur portrait, leurs événements, médias et sections familiales. Une notice éditoriale unique est créée pour chaque famille du périmètre ; elle désigne une section principale et référence toutes ses apparitions contextuelles. Ses notes publiables, événements et médias ne sont donc référencés qu’une fois même si la famille apparaît à plusieurs endroits. La couverture référence les portraits disponibles des partenaires de la famille centrale. Seules les notes portant `BOOK_PUBLICATION` sont incluses dans les références éditoriales. Le portrait retenu est actuellement la première image référencée, non exclue, dans l’ordre Gramps, avec la description du média comme légende ; ce choix reste à valider sur la version prise en charge. La composition narrative et les notices de source restent à réaliser. Des limites d’ascendance et de descendance indépendantes restreignent l’extraction ; leur valeur par défaut est illimitée. Les caches indexés par handle évitent de relire un objet dans la même extraction ; les références facultatives manquantes donnent des diagnostics structurés.

Les références d’événements des fiches et notices familiales sont classées selon la valeur de tri Gramps ; les événements sans date viennent à la fin, et l’ordre d’association d’origine départage les valeurs identiques. Les plages approximatives ou chevauchantes restent à qualifier dans T‑03 avant de considérer la chronologie comme validée.

Le modèle éditorial regroupe maintenant les appels sous une cible unique par handle de citation. Chaque appel conserve son contexte, l’objet qui le porte et son chemin de champ ; plusieurs personnes, notices familiales, événements, lieux, médias ou notes publiables peuvent ainsi renvoyer à la même cible sans perdre leur identité propre. Chaque entrée renvoie aussi vers l’objet Citation, la Source nommée par cette citation, les dépôts associés à cette Source et les médias résolus, non exclus et rattachés à la citation. Cette structure commence L5.3 et L5.4 ; les numéros compacts devront être attribués depuis l’ordre définitif du livre. La notice bibliographique composée, les notes de bas de page, les pages définitives et les appels provenant de contextes éditoriaux encore absents restent à construire.

Les emplacements éditoriaux sont dédupliqués par handle de média Gramps. Chaque emplacement conserve toutes ses références admissibles, dont chaque rectangle et citation associée, ainsi que la description et le drapeau `BOOK_FEATURED`. Une reproduction documentaire unique est ainsi distincte des dérivés recadrés qui peuvent être nécessaires selon les références. La lecture des originaux, l’application des recadrages et les clés de cache fondées sur le contenu du fichier, le rectangle et la politique de conversion restent à implémenter.

Le modèle de parcours attribue à chaque occurrence sa partie, sa génération, sa famille et ses branches de départ ; les chemins alternatifs restent distincts. Les unions et partenaires donnent le contexte sans devenir de nouvelles racines. Les rendus HTML et LaTeX ne consomment pas encore ce modèle de parcours et restent des démonstrations.

Le texte des notes n’est exposé que si elles portent l’étiquette Gramps `BOOK_PUBLICATION`. Les drapeaux privés sont préservés sans exclure les données accessibles à la base fournie. Le JSON indique si l’instantané contient des objets ou associations privés ; l’avertissement requis avant la publication d’un livre complet reste à mettre en place.

## Accès aux données

L’adaptateur n’utilise que les accesseurs publics de la base Gramps. Il ne modifie pas la base et ne contourne pas ses contrôles d’accès. Une donnée inaccessible est représentée par un diagnostic, tandis qu’un membre manquant de la famille choisie bloque l’extraction.

Les noms techniques et métadonnées restent en anglais. Les noms réservés incluent `BOOK_PUBLICATION`, `BOOK_PROFILE`, `BOOK_EXCLUDE` et `BOOK_FEATURED`.

Pour l’enregistrement et l’empaquetage de Gramps 6, le projet a consulté [`grostim/gramps-two-way-fan-chart`](https://github.com/grostim/gramps-two-way-fan-chart). Il sert de référence, son moteur généalogique et ses rendus ne sont pas copiés.
