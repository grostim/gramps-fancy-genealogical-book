# Gramps Web integration spike / Prototype d’intégration Gramps Web

Status: source-level feasibility review on 2026-09-27. No server deployment has been validated.

## Evidence inspected

- Gramps Web API commit [`bef091db`](https://github.com/gramps-project/gramps-web-api/commit/bef091db714dabb98d8351bde741b7c5407805c5), especially [`gramps_webapi/api/report.py`](https://github.com/gramps-project/gramps-web-api/blob/bef091db714dabb98d8351bde741b7c5407805c5/gramps_webapi/api/report.py) and [`gramps_webapi/const.py`](https://github.com/gramps-project/gramps-web-api/blob/bef091db714dabb98d8351bde741b7c5407805c5/gramps_webapi/const.py).
- Official [Gramps Web report guide](https://www.grampsweb.org/user-guide/reports/).
- Local Gramps 6.0.8 Desktop installation and the plugin’s successful CLI/GUI validation.

## Findings

The Web API discovers only registered reports whose category is present in `REPORT_DEFAULTS`. At the inspected revision, that mapping contains text and graphical categories; `CATEGORY_WEB`, used by the current Desktop JSON milestone, is absent. The report therefore cannot currently be assumed to appear in Gramps Web.

The Web API owns the output destination: it creates a UUID filename under `REPORT_DIR` and passes it through the standard `of` option. The current plugin instead exposes its own `destination` option. A Web-compatible adapter must consume the server-assigned output path and must never accept an arbitrary server filesystem path from the browser.

The API MIME mapping contains PDF and HTML but no ZIP. The v1 requirement for a downloadable static HTML ZIP therefore needs either upstream ZIP support, a supported server extension, or a report contract that Gramps Web already knows how to package. Returning a plain HTML file would not satisfy the v1 offline-site requirement.

`FamilyOption` is supported and its values are populated from the server database. This supports the intended F0 selection. Actual visibility of private objects is governed by the database supplied to the report; the plugin must not attempt to bypass that context.

## Proposed adaptation boundary

Keep extraction, traversal, editorial assembly and rendering independent of the launch surface. Add a small output-target abstraction with two implementations:

| Surface | Destination authority | Expected artifact |
| --- | --- | --- |
| Desktop | Native destination picker and explicit replacement option | PDF or HTML ZIP chosen by the user |
| Web | Server-provided report path under `REPORT_DIR` | MIME-supported downloadable result |

Do not add a user-entered server path. Do not claim Web compatibility by merely registering a Desktop `CATEGORY_WEB` report.

## Required live proof

1. Select a pinned Gramps Web/API version and install the add-on in a disposable server using only synthetic data.
2. Confirm report discovery and serialization of all required options, including F0, depths, language and output format.
3. Generate a PDF through the server-owned path; verify status, progress, error response and browser download.
4. Resolve ZIP support, then generate and download an offline HTML site with relative links and bundled assets.
5. Verify media resolution on the server and behavior for missing media.
6. Test an authorized private object and an inaccessible object without changing access controls.
7. Record exact Gramps, Web API, frontend, Python, OS and dependency versions.

Until those checks pass, T-01, T-05, T-09 and AC-22 remain open. The local Docker daemon was unavailable during this review, and no development Web instance was provided.

## Français

Statut : étude de faisabilité sur le code source le 27 septembre 2026. Aucun déploiement serveur n’est validé.

L’API Web ne découvre que les catégories présentes dans `REPORT_DEFAULTS`. Dans la révision inspectée, cette table contient les rapports textuels et graphiques, mais pas `CATEGORY_WEB`, utilisée par le jalon JSON Desktop. Le rapport actuel ne peut donc pas être annoncé comme visible dans Gramps Web.

L’API impose elle-même un fichier UUID sous `REPORT_DIR` et le transmet via l’option standard `of`. Le plugin actuel expose sa propre option `destination`. L’adaptation Web devra utiliser exclusivement le chemin fourni par le serveur et ne jamais accepter un chemin arbitraire saisi dans le navigateur.

La table MIME accepte notamment PDF et HTML, mais pas ZIP. L’exigence v1 d’un site HTML statique téléchargeable en ZIP demande donc une prise en charge ZIP en amont, une extension serveur supportée ou un contrat déjà reconnu par Gramps Web. Un fichier HTML isolé ne satisfait pas l’usage hors connexion attendu.

`FamilyOption` est pris en charge et alimenté depuis la base serveur, ce qui convient au choix de F0. La visibilité des objets privés dépend de la base transmise au rapport ; le plugin ne doit contourner aucun contrôle d’accès.

La frontière proposée sépare le moteur commun du choix de destination : Desktop conserve le sélecteur natif et le remplacement explicite ; Web utilise le chemin de rapport attribué par le serveur. La preuve restante doit couvrir découverte, options, PDF, ZIP HTML, progression, diagnostics, médias et droits sur une instance jetable avec données fictives. Tant que ces essais ne passent pas, T-01, T-05, T-09 et AC-22 restent ouverts.
