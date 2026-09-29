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

- `tests/test_html_renderer.py` couvre les parties, liens internes, identifiants uniques, l’échappement d’un nom hostile, les identifiants bibliographiques, l’affichage des URL et le rejet d’un lien `javascript:`.
- Les commentaires pertinents de la PR #55 sur les extensions de fichier ont été corrigés. La PR #56 préserve la compatibilité JSON ; la PR #57 apporte les améliorations clavier et petit écran.
- Les PR #78–#80 ont des exécutions CI complètes et réussies : tests Python 3.10–3.13, qualification Windows, intégration Gramps 6.0.8 et compilation LuaLaTeX. La CI automatise les tests unitaires et l’intégration JSON Gramps ; l’export HTML riche décrit ci-dessous demeure un contrôle manuel du ZIP.

## Vérification statique du ZIP Gramps — 29 septembre 2026

- Un export HTML ZIP a été produit par Gramps Desktop 6.0.8 en ligne de commande à partir d’une fixture GEDCOM synthétique ; le ZIP contient `index.html` et le portrait PNG fictif.
- `unzip -t` confirme l’intégrité des deux entrées. L’analyse de `index.html` trouve 29 identifiants uniques et 32 références locales ; aucune cible de fragment ni aucun fichier local ne manque, et aucune référence HTTP(S) externe n’est présente.
- Ce contrôle structurel ne démontre pas le rendu visuel, l’interaction hors ligne, le comportement du clavier ou la compatibilité avec un lecteur d’écran. L’ouverture réelle de `index.html` reste à faire.

## Export riche depuis Gramps — 29 septembre 2026

- L’archive du module a été construite depuis la branche de correction des liens bibliographiques et installée uniquement dans un nouveau profil temporaire. L’essai utilise Gramps 6.0.8 sur macOS 27.0 arm64, la fixture GEDCOM du dépôt, une image de 10 × 10 pixels générée pour le test et un fichier natif Gramps complété avec une note, une référence de dépôt et une URL fictives.
- Le profil temporaire a reçu la copie Python pure de Mistune 3.3.4 dans son seul répertoire `plugins/lib`, car l’application macOS ne fournit pas cette dépendance. Aucun arbre ni répertoire de module complémentaire habituel n’a été utilisé.
- L’export produit deux entrées (`index.html` et un PNG recadré). Le contrôle ZIP passe ; les 32 identifiants HTML sont uniques et les 31 références locales pointent toutes vers une cible existante. Les trois entrées de citation affichent l’identifiant Gramps, le dépôt et son URL complète `https://example.invalid/shared-document` ; ce domaine est fictif et n’a pas été ouvert. La même note publiée apparaît dans la fiche individuelle et la section familiale, avec le gras et l’italique Markdown. Le dérivé média mesure 8 × 6 pixels ; le JPEG source n’est pas inclus.
- Le test unitaire du rendu vérifie également qu’une URL `javascript:` de citation n’est pas produite comme lien.
- L’analyse de l’archive ne démontre toujours pas son affichage dans un navigateur hors ligne, la navigation au clavier ni la lecture par un lecteur d’écran.

## Recette manuelle à terminer

1. Installer l’archive du module dans une version Desktop de Gramps prise en charge, ouvrir le rapport **Pages Web → Gramps Fancy Genealogical Book** et choisir une famille. Vérifier que la confirmation de confidentialité est décochée à chaque lancement ; sans la cocher, vérifier que le rapport refuse de générer un fichier ; la cocher pour produire le `.zip`.
2. Marquer un média fictif à la fois `BOOK_EXCLUDE` et `BOOK_FEATURED`. Après génération, vérifier que l’objet n’est référencé par aucun `<img>` de `index.html` et qu’aucun fichier correspondant n’existe dans `media/` dans le ZIP. Cette absence est le critère de réussite, même si le média est aussi mis en avant.
3. Ouvrir le ZIP riche déjà généré dans un navigateur hors ligne et vérifier visuellement les liens du dépôt, les notes, les citations et les images recadrées.
4. Pour AC-10, attacher la même note Markdown fictive marquée `BOOK_PUBLICATION` à deux contextes éditoriaux distincts. Vérifier qu’elle apparaît dans chacun, que le format Markdown et les styles natifs sont rendus, et que chaque contexte reste navigable.
5. Pour AC-15, associer le même média justificatif à plusieurs citations. Vérifier qu’il n’est reproduit qu’une fois après la première citation qui l’utilise et que les autres citations renvoient vers cette reproduction.
6. Pour AC-20, générer le PDF et le ZIP HTML à partir des mêmes données fictives. Comparer les personnes, événements, notes publiées, citations et médias sélectionnés ; vérifier aussi que le ZIP s’ouvre hors ligne et que le PDF conserve ses renvois.
7. Pour AC-23, publier le nom `<img src=x onerror=alert(1)>` et une note contenant `<script>alert(1)</script> <img src=x onerror=alert(1)> [lien](javascript:alert(1))`. Vérifier que ces balises apparaissent comme texte échappé, qu’aucun élément ni gestionnaire d’événement actif n’est produit, que le lien dangereux n’est pas cliquable et qu’aucune alerte ne s’exécute à l’ouverture.
8. Examiner la lecture et le reflow sur plusieurs tailles de fenêtre, parcourir tout le livre au clavier et vérifier les annonces avec un lecteur d’écran.
9. Reprendre séparément la revue visuelle des PDF L6 : typographie, pagination, images, index et renvois par rapport à la v1.1 et aux maquettes.

Les étapes 1, 2 et 4–7 définissent explicitement les critères des AC-22, AC-13, AC-10, AC-15, AC-20 et AC-23. La recette reste à exécuter : ces critères ne sont pas encore qualifiés. Gramps Web n’a pas encore été validé. Voir le [plan d’action](action-plan.fr.md#l7--livre-html-et-archive-autonome) et le [suivi des exigences](requirements.fr.md).
