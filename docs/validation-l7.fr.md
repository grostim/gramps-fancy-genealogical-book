# Avancement L7 — livre HTML

Compte rendu du 28 septembre 2026. La PR #51 a livré le premier rendu HTML unique, puis la PR #52 a ajouté la navigation par génération et branche. La tranche L7.3 étend le rendu aux notes publiables selon les règles de sécurité déjà appliquées au PDF.

## Contenu rendu

- Couverture avec le titre éditorial disponible, les deux partenaires de F0 et l’identifiant de la famille.
- Sommaire lié aux parties éditoriales, puis avant-propos, ascendance, descendance, annexe documentaire et index lorsqu’ils sont présents dans le modèle.
- Occurrences généalogiques, fiches à leur occurrence principale, notices familiales, enfants et types de filiation conservés, événements familiaux, citations et appels.
- Identifiants stables issus du modèle pour les parties, occurrences, fiches, sections familiales, notices, citations et entrées d’index.
- Chaque partie ascendante/descendante propose des liens vers ses générations. Les occurrences de branche renvoient aux racines centrales P0/P1.
- Notes en Markdown converties en paragraphes, titres, listes, emphases, citations, blocs de code et liens contrôlés. Les styles natifs sémantiques Gramps sont rendus à la place du Markdown lorsqu’ils sont présents.
- HTML brut et notes HTML_CODE toujours visibles comme texte échappé ; liens actifs limités à `http`, `https` et `mailto`. Les images Markdown n’embarquent pas de média et affichent leur texte alternatif.

## Vérifications et limites

- `tests/test_html_renderer.py` vérifie les parties, les liens internes, l’unicité des identifiants et l’échappement d’un nom hostile.
- La CI du dépôt doit confirmer la non-régression de cette tranche ; la recette complète des notes et des cas adversariaux AC-10/AC-23 reste à réaliser.
- Les médias et leurs chemins ne sont pas encore inclus ; l’export ZIP autonome, les contrôles clavier, les textes alternatifs et les essais sur plusieurs tailles d’écran restent à réaliser en L7.4–L7.5.
- La revue visuelle des PDF générés en L6 reste séparée et ouverte.

Le détail des étapes figure dans le [plan d’action](action-plan.fr.md#l7--livre-html-et-archive-autonome).
