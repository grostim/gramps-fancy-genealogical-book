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
- `tests/test_html_notes.py` vérifie que les notes Markdown et `HtmlCode` affichent le HTML malveillant comme texte, sans balise active ni attribut événement, et que seul un lien HTTPS autorisé devient un lien.
- Le test `test_renders_shared_citation_media_once_in_the_html_archive` vérifie qu’un ZIP contenant deux citations qui partagent un document a une seule entrée PNG, affiche la reproduction dans la première citation et lie la seconde vers son ancre.
- Les commentaires pertinents de la PR #55 sur les extensions de fichier ont été corrigés. La PR #56 préserve la compatibilité JSON ; la PR #57 apporte les améliorations clavier et petit écran.
- Les PR #78–#82 ont des exécutions CI complètes et réussies : tests Python 3.10–3.13, qualification Windows, intégration Gramps 6.0.8 et compilation LuaLaTeX. La CI automatise les tests unitaires et l’intégration JSON Gramps ; l’export HTML riche décrit ci-dessous demeure un contrôle manuel dans l’interface Gramps.
- Sur macOS 27.0 arm64 avec CPython 3.14.0, la suite complète passe (38 tests), Ruff 0.16.9 est propre et `build_addon.py` construit l’archive. L’environnement local inclut aussi les dépendances optionnelles Pillow 12.3.0 et pypdfium2 5.13.0.

## Vérification statique du ZIP Gramps — 29 septembre 2026

- Un export HTML ZIP a été produit par Gramps Desktop 6.0.8 en ligne de commande à partir d’une fixture GEDCOM synthétique ; le ZIP contient `index.html` et le portrait PNG fictif.
- `unzip -t` confirme l’intégrité des deux entrées. L’analyse de `index.html` trouve 29 identifiants uniques et 32 références locales ; aucune cible de fragment ni aucun fichier local ne manque, et aucune référence HTTP(S) externe n’est présente.
- Ce contrôle structurel ne démontre pas le rendu visuel, l’interaction hors ligne, le comportement du clavier ou la compatibilité avec un lecteur d’écran. L’ouverture réelle de `index.html` reste à faire.

## Média partagé par deux citations — contrôle Gramps, 29 septembre 2026

- Un nouveau ZIP a été produit par Gramps 6.0.8 depuis une base GEDCOM fictive dans un profil temporaire. Le même objet PNG est associé à deux citations distinctes.
- L’archive contient `index.html` et une seule entrée PNG. Les deux notices de citation renvoient vers la même reproduction. Les 209 liens HTML sont des ancres locales résolues ; les 170 identifiants sont uniques et il n’y a pas de lien externe.
- La vérification reste statique : l’ouverture visuelle hors ligne, la navigation au clavier et le lecteur d’écran ne sont pas validés. Le navigateur intégré a refusé l’URL `file://`; aucun autre chemin d’ouverture n’a été utilisé.

## Export riche depuis Gramps — 29 septembre 2026

- L’archive du module a été construite depuis la branche de correction des liens bibliographiques et installée uniquement dans un nouveau profil temporaire. L’essai utilise Gramps 6.0.8 sur macOS 27.0 arm64, la fixture GEDCOM du dépôt, une image de 10 × 10 pixels générée pour le test et un fichier natif Gramps complété avec une note, une référence de dépôt et une URL fictives.
- Le profil temporaire a reçu la copie Python pure de Mistune 3.3.4 dans son seul répertoire `plugins/lib`, car l’application macOS ne fournit pas cette dépendance. Aucun arbre ni répertoire de module complémentaire habituel n’a été utilisé.
- L’export produit deux entrées (`index.html` et un PNG recadré). Le contrôle ZIP passe ; les 32 identifiants HTML sont uniques et les 31 références locales pointent toutes vers une cible existante. Les trois entrées de citation affichent l’identifiant Gramps, le dépôt et son URL complète `https://example.invalid/shared-document` ; ce domaine est fictif et n’a pas été ouvert. La même note publiée apparaît dans la fiche individuelle et la section familiale, avec le gras et l’italique Markdown. Le dérivé média mesure 8 × 6 pixels ; le JPEG source n’est pas inclus.
- Le test unitaire du rendu vérifie également qu’une URL `javascript:` de citation n’est pas produite comme lien.
- L’analyse de l’archive ne démontre toujours pas son affichage dans un navigateur hors ligne, la navigation au clavier ni la lecture par un lecteur d’écran.

## Recette Gramps Desktop interactive — 29 septembre 2026

- Gramps Desktop 6.0.8 a été lancé avec la fixture GEDCOM du dépôt dans un profil temporaire isolé, sans ouvrir l’arbre Gramps personnel. Le rapport apparaît sous **Rapports → Pages web** et les libellés, options et onglet **Vie privée** sont en français. La famille fictive F0001 est sélectionnée.
- À chaque ouverture du rapport, la case de confidentialité est décochée. Valider sans la cocher affiche « L’avertissement de confidentialité n’a pas été confirmé » et le fichier `denied-export.zip` reste absent.
- Après avoir coché la case, le rapport aboutit et produit `approved-export.zip` dans le dossier temporaire. `unzip -t` passe ; l’archive contient `index.html` et un PNG sous `media/`.
- Le parcours confirme le refus et l’export interactif, mais pas encore la consultation visuelle hors ligne dans un navigateur, l’accessibilité clavier ou la lecture par un lecteur d’écran.

## Recette manuelle à terminer

1. La recette interactive macOS décrite ci-dessus vérifie le rapport traduit, le refus sans consentement, l’absence de fichier et l’export `.zip` avec consentement. La répétition sur une installation propre et sur les autres versions Desktop ciblées reste à faire.
2. Pour AC-13, un test de régression vérifie déjà qu’un média fictif `BOOK_EXCLUDE` + `BOOK_FEATURED` et les citations propres à ses références n’apparaissent pas dans le livre, ne créent aucun placement ou dérivé et ne laissent ni description ni `<img>` dans les sorties HTML/LaTeX. Confirmer ce comportement avec un export de l’interface Gramps et une base native fictive.
3. Ouvrir le ZIP riche déjà généré dans un navigateur hors ligne et vérifier visuellement les liens du dépôt, les notes, les citations et les images recadrées.
4. Pour AC-10, attacher la même note Markdown fictive marquée `BOOK_PUBLICATION` à deux contextes éditoriaux distincts. Vérifier qu’elle apparaît dans chacun, que le format Markdown et les styles natifs sont rendus, et que chaque contexte reste navigable.
5. Pour AC-15, associer le même média justificatif à plusieurs citations dans Gramps, produire le ZIP et vérifier visuellement que l’archive conserve une seule reproduction après la première citation qui l’utilise et que les autres citations y renvoient. Un test automatisé contrôle déjà le moteur HTML et l’unique entrée image du ZIP.
6. Pour AC-20, générer le PDF et le ZIP HTML à partir des mêmes données fictives. Comparer les personnes, événements, notes publiées, citations et médias sélectionnés ; vérifier aussi que le ZIP s’ouvre hors ligne et que le PDF conserve ses renvois.
7. Pour AC-23, publier le nom `<img src=x onerror=alert(1)>` et une note contenant `<script>alert(1)</script> <img src=x onerror=alert(1)> [lien](javascript:alert(1))`. Vérifier que ces balises apparaissent comme texte échappé, qu’aucun élément ni gestionnaire d’événement actif n’est produit, que le lien dangereux n’est pas cliquable et qu’aucune alerte ne s’exécute à l’ouverture.
8. Examiner la lecture et le reflow sur plusieurs tailles de fenêtre, parcourir tout le livre au clavier et vérifier les annonces avec un lecteur d’écran.
9. Reprendre séparément la revue visuelle des PDF L6 : typographie, pagination, images, index et renvois par rapport à la v1.1 et aux maquettes.

Les étapes 1–7 définissent explicitement les critères des AC-22, AC-13, AC-10, AC-15, AC-20 et AC-23. AC-15 est couvert par un test du moteur HTML et de l’archive ZIP ; sa vérification visuelle reste à faire. AC-23 dispose de contrôles unitaires contre l’injection ; le scénario complet dans Gramps et le navigateur reste à exécuter. Le parcours interactif macOS confirme le rapport, le refus de confidentialité sans fichier et un export ZIP accepté. Les autres scénarios cités ne sont pas encore qualifiés. Gramps Web n’a pas encore été validé. Voir le [plan d’action](action-plan.fr.md#l7--livre-html-et-archive-autonome) et le [suivi des exigences](requirements.fr.md).
