# Validation L6 — rendus PDF et HTML

Compte rendu du 29 septembre 2026. Les essais utilisent exclusivement les fixtures généalogiques synthétiques du dépôt et un portrait fictif créé dans un répertoire temporaire.

## Environnement

- macOS, Gramps Desktop 6.0.8-1, Python embarqué 3.13.2.
- LuaHBTeX 1.24.0 (TeX Live 2026), disponible dans `/Library/TeX/texbin`.
- Archive du module construite depuis le commit de fusion de la PR #75 (`827d783`).
- Profil Gramps placé sous `/tmp/gramps-fancy-book-desktop-rich-qa-20260929`; aucun arbre personnel ni dossier d’extension utilisateur n’a été utilisé.

## Résultats

| Parcours | Résultat |
| --- | --- |
| Moteur LaTeX de production, fixture riche | PDF A4 de 18 pages : événements longs, note à plusieurs pages, portrait, photo pleine page, citations, annexe et index. Références stabilisées en deux passes, sans débordement signalé. |
| Moteur LaTeX de production, fixture peu documentée | PDF A4 de 4 pages, sans événement, note ni citation. Aucun saut de page vide. |
| Gramps macOS, GEDCOM fictif avec portrait JPEG synthétique | Import sans erreur ; export PDF A4 de 9 pages ; LuaLaTeX a terminé et le PDF contient le portrait à la couverture et dans le profil. La légende du portrait est centrée sous l’image. |
| Gramps macOS, même fixture, sortie HTML | Archive ZIP de 2 fichiers (page d’entrée et image) ; `unzip -t` confirme son intégrité. |

La revue des deux fixtures de rendu a détecté un titre de sommaire en double et une légende de portrait qui se plaçait à côté de l’image. Ces défauts ont été corrigés dans la PR #75. Les journaux de compilation et les pages témoins sont produits dans des dossiers temporaires et ne sont pas inclus dans le dépôt.

## Dépendance Gramps macOS

L’application macOS fournie n’inclut pas `mistune` dans son Python embarqué. Gramps ne charge donc pas le rapport tant que cette dépendance requise n’est pas importable. Pour poursuivre l’essai isolé, la copie pure Python déjà installée dans l’environnement de rendu a été ajoutée au seul dossier `plugins/lib` du profil temporaire. Le chargement du module, l’import du GEDCOM et les deux formats d’export ont alors fonctionné. Aucun paquet n’a été ajouté au profil Gramps habituel.

## À terminer

- Vérifier dans l’interface Gramps la présence du rapport, ses options en français, la confirmation de confidentialité et les sorties PDF/ZIP. Le profil de test est ouvert dans une seconde instance ; le contrôle d’interface ne distingue pas cette fenêtre de l’instance Gramps déjà active.
- Ouvrir le ZIP HTML hors ligne et parcourir ses liens et médias.
- Comparer le rendu aux principes de la spécification et terminer la revue des maquettes privées, sans intégrer leurs données réelles aux fixtures ou à la documentation.
- Qualifier les quatre cas PDF/URL et les autres types de médias dans Gramps.

Ces essais confirment les parcours synthétiques décrits ici ; ils ne constituent pas la recette finale des critères L6.
