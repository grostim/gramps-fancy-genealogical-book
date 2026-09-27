# Foundation review / Revue de fondation

2026-09-27 — baseline `7845a3d`; review performed before extending the genealogy engine.

## English

The Desktop foundation is suitable for isolated L2 probes: native family selection, real Gramps CLI/GUI export, independent adapter/domain boundary and allowlisted packaging have demonstrated evidence. This is not approval of the future PDF/HTML or Web implementations.

Corrections from code review:

- The adapter silently omitted child references with an empty handle. It now raises a diagnostic instead of dropping the relationship. Unknown parents remain representable.
- File collisions exposed a temporary filesystem path. The report now tells the user to choose another destination or explicitly enable replacement. Atomic protection remains in the writer.
- The existing CLI integration diagnostic expectation was updated for the collision message, and one focused adapter test covers an empty child handle.

Remaining items: translations and user-facing diagnostics, typed relationship/event models, schema evolution, authorized-private-data notification at publication, Windows filesystem qualification, and full Desktop/Web acceptance. The current registration category is a Desktop design choice, not proof of Web compatibility.

No merge or release is implied by this review. The changes remain in PR #1 with the technical probes, for a single reviewable foundation.

## Français

La fondation Desktop permet les prototypes L2 isolés : sélection native, export CLI/GUI réel, séparation adaptateur/domaine et packaging par liste explicite ont des preuves. Cela ne valide pas les futurs moteurs PDF/HTML ou l’intégration Web.

Corrections de revue :

- Une référence enfant au handle vide était omise silencieusement. Elle déclenche désormais un diagnostic ; un parent inconnu reste représentable.
- Une collision de fichier exposait un chemin temporaire. Le message invite désormais à choisir une autre destination ou à activer explicitement le remplacement. La protection atomique reste dans le module d’écriture.
- L’attente du diagnostic dans l’intégration CLI existante a été adaptée et un test ciblé couvre le handle enfant vide.

Restent : traductions et diagnostics, modèles typés de relations/événements, évolution du schéma, information sur les données privées autorisées avant publication, qualification Windows et recette Desktop/Web complète. La catégorie du rapport est un choix Desktop, pas une preuve Web.

Cette revue n’effectue ni fusion ni release. Les corrections et prototypes restent dans la PR nº 1 pour une revue commune de la fondation.
