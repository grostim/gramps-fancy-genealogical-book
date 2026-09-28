# Avancement L7 — livre HTML

Compte rendu du 28 septembre 2026. Les PR #51–#57 ont livré le rendu HTML, sa navigation par génération et branche, les notes HTML sûres, l’archive ZIP, la compatibilité des anciennes commandes JSON et les améliorations clavier/petit écran.

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

1. Installer l’archive du module dans une version Desktop de Gramps prise en charge, ouvrir le rapport **Pages Web → Gramps Fancy Genealogical Book**, choisir une famille et produire une sortie `.zip`.
2. Extraire l’archive dans un dossier local, déconnecter le réseau, ouvrir `index.html` et vérifier les liens, les notes, les citations, les images recadrées et les médias marqués `BOOK_EXCLUDE`.
3. Vérifier qu’un document partagé n’est reproduit qu’une fois et que chaque contexte renvoie vers sa cible.
4. Examiner la lecture et le reflow sur plusieurs tailles de fenêtre, parcourir tout le livre au clavier et vérifier les annonces avec un lecteur d’écran.
5. Reprendre séparément la revue visuelle des PDF L6 : typographie, pagination, images, index et renvois par rapport à la v1.1 et aux maquettes.

Cette recette couvre notamment AC-10, AC-12, AC-15, AC-20 et AC-23. La qualification complète Desktop/Web AC-22 demeure ouverte ; Gramps Web n’a pas encore été validé. Voir le [plan d’action](action-plan.fr.md#l7--livre-html-et-archive-autonome) et le [suivi des exigences](requirements.fr.md).
