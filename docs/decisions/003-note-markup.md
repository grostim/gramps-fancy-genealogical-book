# Règle de rendu des notes publiables

## Portée

Les notes restent publiables uniquement quand elles portent l’étiquette Gramps `BOOK_PUBLICATION`. Cette règle concerne la sortie LaTeX actuelle ; le moteur HTML devra appliquer la même normalisation au lot L7.

## Notes saisies en Markdown

Quand le texte n’a pas de plage de style sémantique Gramps, il est analysé par Mistune en AST. Le rendu LaTeX parcourt les tokens et ne produit que des commandes LaTeX contrôlées par le plugin. Les paragraphes, titres, listes, emphases, blocs de citation, code, liens et séparateurs sont pris en charge.

Le HTML brut présent dans le Markdown est imprimé comme texte littéral échappé. Les images Markdown affichent leur texte alternatif sans télécharger le média. Les liens ne sont actifs que pour HTTP, HTTPS et `mailto:`; les autres schémas restent du texte. Les styles de couleur et de fonte choisis dans l’éditeur ne remplacent pas la typographie homogène du livre.

Les notes Gramps de type `HTML_CODE` sont toujours publiées comme texte littéral échappé, jamais comme HTML ou Markdown exécuté.

## Notes avec styles natifs Gramps

Si une note contient au moins une plage native sémantique (gras, italique, souligné, barré, exposant, indice ou lien sûr), les plages natives sont rendues et les marqueurs Markdown du même texte restent littéraux. Cette priorité évite de parser simultanément deux syntaxes de mise en forme dont les plages pourraient se chevaucher.

Les styles natifs de fonte, taille, couleur et surbrillance sont ignorés pour conserver la hiérarchie typographique et la lisibilité en niveaux de gris. Si les seules plages natives concernent ces propriétés visuelles, le texte suit la règle Markdown précédente.

Pour une note `FLOWED`, les retours simples sont des espaces et les lignes vides séparent les paragraphes. Pour une note `FORMATTED`, les retours simples restent visibles.

## Dépendance

Le parseur AST Mistune 3 est une dépendance Python requise et déclarée dans la fiche Gramps. Le paquet Python l’installe depuis `pyproject.toml`. Pour une installation d’extension Gramps Desktop ou Web depuis l’archive, Mistune doit être présent dans le même environnement Python que Gramps.

Les notes de bas de page Markdown et les tableaux ne sont pas encore convertis en notes/citations ou tableaux LaTeX ; ces syntaxes restent hors du rendu structuré actuel.
