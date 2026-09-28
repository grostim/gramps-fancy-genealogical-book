# Avancement L7 — livre HTML

Compte rendu du 28 septembre 2026. Les PR #51 et #52 ont livré le rendu HTML et sa navigation, puis la PR #53 a ajouté les notes formatées et sécurisées. La tranche L7.4 prépare une archive ZIP locale avec les médias dérivés du modèle éditorial.

## Contenu rendu

- Couverture avec le titre éditorial disponible, les deux partenaires de F0 et l’identifiant de la famille.
- Sommaire lié aux parties éditoriales, puis avant-propos, ascendance, descendance, annexe documentaire et index lorsqu’ils sont présents dans le modèle.
- Occurrences généalogiques, fiches à leur occurrence principale, notices familiales, enfants et types de filiation conservés, événements familiaux, citations et appels.
- Identifiants stables issus du modèle pour les parties, occurrences, fiches, sections familiales, notices, citations et entrées d’index.
- Chaque partie ascendante/descendante propose des liens vers ses générations. Les occurrences de branche renvoient aux racines centrales P0/P1.
- Les portraits, images des fiches et notices, médias des citations et `BOOK_FEATURED` sont reliés à des dérivés PNG ; une image mise en avant conserve une seule reproduction et les autres apparitions y renvoient.
- Notes en Markdown converties en paragraphes, titres, listes, emphases, citations, blocs de code et liens contrôlés. Les styles natifs sémantiques Gramps sont rendus à la place du Markdown lorsqu’ils sont présents.
- HTML brut et notes HTML_CODE toujours visibles comme texte échappé ; liens actifs limités à `http`, `https` et `mailto`. Les images Markdown n’embarquent pas de média et affichent leur texte alternatif.
- `write_html_archive` écrit `index.html` et les PNG nécessaires sous `media/`, avec CSS embarqué et horodatages ZIP déterministes. Les chemins de Gramps et les fichiers originaux ne sont pas inclus.

## Vérifications et limites

- `tests/test_html_renderer.py` vérifie les parties, les liens internes, l’unicité des identifiants et l’échappement d’un nom hostile.
- La CI de la PR #53 passe sous Python 3.10–3.13, Ruff, build, Gramps et LuaLaTeX ; la CI de l’archive L7.4 reste à confirmer.
- L’API ZIP n’est pas encore branchée sur le sélecteur de sortie du rapport Gramps. La recette AC-10/AC-23, l’ouverture hors ligne, les contrôles clavier, les tailles d’écran et la revue visuelle PDF restent à réaliser.
- La revue visuelle des PDF générés en L6 reste séparée et ouverte.

Le détail des étapes figure dans le [plan d’action](action-plan.fr.md#l7--livre-html-et-archive-autonome).
