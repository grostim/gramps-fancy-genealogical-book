# Avancement L7 — livre HTML

Compte rendu du 28 septembre 2026. Les PR #51–#55 ont livré le rendu HTML, sa navigation, les notes sécurisées, le générateur ZIP et son intégration au rapport Gramps. L’export prépare les médias dans un répertoire temporaire.

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
- La PR #55 a été fusionnée après correction d’un retour P2 sur la gestion des extensions. Les jobs Actions n’ont pas pu démarrer sur sa tête corrigée : GitHub signale un problème de facturation ou de plafond de dépenses ; la validation CI de L7.4 reste donc à reprendre après rétablissement du compte.
- Le rapport Gramps crée une archive HTML ZIP par défaut pour une destination `.zip`. Le mode automatique accepte aussi les anciennes commandes CLI qui indiquent seulement une destination `.json` ; le format JSON reste disponible explicitement pour le diagnostic.
- Depuis Gramps Desktop, ouvrir Rapports > Web > Gramps Fancy Genealogical Book, choisir la famille et la destination .zip, puis extraire l’archive et ouvrir index.html.
- Le script CI d’intégration Gramps conserve la sortie JSON de diagnostic pour ses contrôles existants. Le code L7.5 ajoute une mise en page fluide, le retour à la ligne des textes longs, un lien d’évitement clavier, un indicateur de focus visible et des textes alternatifs issus du portrait, de la légende ou de la description, avec un libellé de secours explicite. La génération HTML ZIP via une vraie session Gramps, la recette hors ligne AC-10/AC-23, l’essai sur plusieurs tailles d’écran, la navigation clavier/lecteur d’écran et la revue visuelle PDF restent à effectuer.
- La revue visuelle des PDF générés en L6 reste séparée et ouverte.

Le détail des étapes figure dans le [plan d’action](action-plan.fr.md#l7--livre-html-et-archive-autonome).
