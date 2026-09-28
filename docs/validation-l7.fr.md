# Avancement L7 — livre HTML

Compte rendu du 29 septembre 2026. Les PR #51–#57 ont livré le rendu HTML, sa navigation par génération et branche, les notes HTML sûres, l’archive ZIP, la compatibilité des anciennes commandes JSON et les améliorations clavier/petit écran.

## Contenu livré

- Le livre HTML présente la couverture, les parties généalogiques, fiches, notices familiales, citations, médias et index reliés par des identifiants stables.
- Les notes Markdown et styles natifs Gramps sont formatés ; le HTML brut reste du texte littéral et les liens actifs sont limités à `http`, `https` et `mailto`.
- L’archive `.zip` contient `index.html`, le CSS intégré et les PNG autorisés sous `media/`. Les liens sont relatifs, les fichiers Gramps originaux sont exclus et les horodatages ZIP sont déterministes.
- L’image mise en avant est publiée une fois ; les autres contextes pointent vers cette reproduction.
- Le rendu inclut une mise en page adaptable, un lien clavier d’accès au contenu, un indicateur de focus visible et des textes alternatifs informatifs.
- Le format automatique choisit le ZIP pour une destination `.zip` et conserve l’export JSON des anciennes commandes qui fournissent une destination `.json`.

## Vérifications automatisées et état CI

- `tests/test_html_renderer.py` couvre les parties, liens internes, identifiants uniques et l’échappement d’un nom hostile.
- Les commentaires pertinents de la PR #55 sur les extensions de fichier ont été corrigés. La PR #56 préserve la compatibilité JSON ; la PR #57 apporte les améliorations clavier et petit écran.
- Les exécutions Actions récentes des PR #55–#57 ont été bloquées avant le lancement des jobs par un message GitHub relatif aux paiements ou au plafond de dépenses. Elles ne constituent donc pas une validation CI de ces têtes ; relancer après rétablissement du compte.

## Recette manuelle à terminer

1. Installer l’archive du module dans une version Desktop de Gramps prise en charge, ouvrir le rapport **Pages Web → Gramps Fancy Genealogical Book** et choisir une famille. Vérifier que la confirmation de confidentialité est décochée à chaque lancement ; sans la cocher, vérifier que le rapport refuse de générer un fichier ; la cocher pour produire le `.zip`.
2. Marquer un média fictif à la fois `BOOK_EXCLUDE` et `BOOK_FEATURED`. Après génération, vérifier que l’objet n’est référencé par aucun `<img>` de `index.html` et qu’aucun fichier correspondant n’existe dans `media/` dans le ZIP. Cette absence est le critère de réussite, même si le média est aussi mis en avant.
3. Extraire l’archive dans un dossier local, déconnecter le réseau, ouvrir `index.html` et vérifier les liens, les notes, les citations et les images recadrées.
4. Pour AC-10, attacher la même note Markdown fictive marquée `BOOK_PUBLICATION` à deux contextes éditoriaux distincts. Vérifier qu’elle apparaît dans chacun, que le format Markdown et les styles natifs sont rendus, et que chaque contexte reste navigable.
5. Pour AC-20, générer le PDF et le ZIP HTML à partir des mêmes données fictives. Comparer les personnes, événements, notes publiées, citations et médias sélectionnés ; vérifier aussi que le ZIP s’ouvre hors ligne et que le PDF conserve ses renvois.
6. Pour AC-23, publier le nom `<img src=x onerror=alert(1)>` et une note contenant `<script>alert(1)</script> <img src=x onerror=alert(1)> [lien](javascript:alert(1))`. Vérifier que ces balises apparaissent comme texte échappé, qu’aucun élément ni gestionnaire d’événement actif n’est produit, que le lien dangereux n’est pas cliquable et qu’aucune alerte ne s’exécute à l’ouverture.
7. Examiner la lecture et le reflow sur plusieurs tailles de fenêtre, parcourir tout le livre au clavier et vérifier les annonces avec un lecteur d’écran.
8. Reprendre séparément la revue visuelle des PDF L6 : typographie, pagination, images, index et renvois par rapport à la v1.1 et aux maquettes.

Les étapes 1, 2, 4, 5 et 6 définissent explicitement les critères des AC-22, AC-13, AC-10, AC-20 et AC-23. La recette reste à exécuter : ces critères ne sont pas encore qualifiés. Gramps Web n’a pas encore été validé. Voir le [plan d’action](action-plan.fr.md#l7--livre-html-et-archive-autonome) et le [suivi des exigences](requirements.fr.md).
