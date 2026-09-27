# Validation de la fondation — 27 septembre 2026

## Environnement et isolation

Gramps macOS 6.0.8, Python embarqué 3.13.2. Les tests utilisent exclusivement `tests/fixtures/reference-family.ged`, avec quatre personnes fictives et deux familles. Le script d’intégration crée son profil Gramps et son cache dans un répertoire temporaire, installe l’archive et exécute Gramps hors du checkout source. Aucun arbre personnel n’est utilisé.

## Contrôles réalisés localement

- Ruff : contrôles réussis après correction du squelette et déclaration ciblée du contexte des fichiers `.gpr.py`.
- Pytest : huit tests réussis sur l’extraction, le modèle, l’export et le packaging.
- Packaging : deux constructions produisent les mêmes octets ; l’archive contient les fichiers nécessaires au runtime et exclut les caches.
- Gramps réel : le rapport est découvert depuis l’archive installée, extrait les membres attendus et conserve les accents ainsi que la distinction handle/identifiant Gramps.
- L’adaptateur représente une famille monoparentale ; le rapport rejette son utilisation comme famille centrale, conformément à AC-02 retrouvé dans la v1.1.
- Une sélection inexistante ou explicitement vide laisse le fichier précédent intact et produit une erreur de rapport.
- Un fichier existant reste inchangé par défaut ; `overwrite=True` permet son remplacement.
- Une destination absente, un répertoire absent ou une extension incompatible produisent un diagnostic ; aucun JSON partiel ni fichier temporaire résiduel.

Les erreurs de rapport peuvent laisser Gramps retourner zéro : le script contrôle donc aussi les diagnostics et les fichiers produits.

## Reproduction

```sh
.venv/bin/ruff check .
.venv/bin/pytest -q
.venv/bin/python build_addon.py
.venv/bin/python scripts/verify_gramps.py --gramps /Applications/Gramps.app/Contents/MacOS/Gramps
```

## CI distante

Le [run GitHub Actions 36288399883](https://github.com/grostim/gramps-fancy-genealogical-book/actions/runs/36288399883), au commit `c2c82c8`, a réussi : tests et contrôles sous Python 3.10, 3.11, 3.12 et 3.13, puis intégration réelle avec Gramps 6.0.8 sur Ubuntu 24.04.

## État des validations restantes

- Interface graphique : base fictive et profil préparés ; contrôle automatisé bloqué au premier essai parce que le Mac est verrouillé. Ne pas considérer le parcours graphique comme validé à ce stade.
- Spécification : 27 scénarios retrouvés et associés au plan ; seule la fondation est implémentée. La conformité du livre complet reste à réaliser.
- Gramps Web, traduction complète de l’interface, génération du livre PDF/HTML : hors du périmètre validé.

Le jalon L1 est démontré en CLI, mais sa validation finale attend le contrôle graphique et la revue prévue au plan.
