# Avancement L7 — livre HTML

Compte rendu du 28 septembre 2026. La première tranche L7.1 rend le modèle éditorial existant dans un document HTML unique. Elle ne produit pas encore l’archive autonome prévue par la spécification.

## Contenu rendu

- Couverture avec le titre éditorial disponible, les deux partenaires de F0 et l’identifiant de la famille.
- Sommaire lié aux parties éditoriales, puis avant-propos, ascendance, descendance, annexe documentaire et index lorsqu’ils sont présents dans le modèle.
- Occurrences généalogiques, fiches à leur occurrence principale, notices familiales, enfants et types de filiation conservés, événements familiaux, citations et appels.
- Identifiants stables issus du modèle pour les parties, occurrences, fiches, sections familiales, notices, citations et entrées d’index.
- Texte échappé dans les nœuds et attributs HTML. Les notes apparaissent en texte brut avec leurs sauts de ligne.

## Vérifications et limites

- `tests/test_html_renderer.py` vérifie les parties, les liens internes, l’unicité des identifiants et l’échappement d’un nom hostile.
- Les tests ciblés et la suite locale disponible passent ; Ruff ne signale pas d’erreur.
- Les médias et leurs chemins ne sont pas encore inclus ; l’export ZIP autonome, la mise en forme Markdown des notes, les contrôles clavier et les essais sur plusieurs tailles d’écran restent en L7.2–L7.5.
- La revue visuelle des PDF générés en L6 reste séparée et ouverte.

Le détail des étapes figure dans le [plan d’action](action-plan.fr.md#l7--livre-html-et-archive-autonome).
