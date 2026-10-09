# Proposition : rapports à sortie personnalisée dans Gramps Web

**Statut :** proposition publiée le 9 octobre 2026 dans l’[issue officielle #1048](https://github.com/gramps-project/gramps-web-api/issues/1048) ; décision des mainteneurs et qualification runtime en attente.

## Contexte

Gramps Fancy Genealogical Book s’enregistre comme rapport `CATEGORY_WEB` et génère lui-même des fichiers PDF ou HTML ZIP. L’audit de Gramps Web API 3.23.1 confirme que cette catégorie est filtrée, que ZIP n’est pas un type de résultat accepté et que l’option personnalisée `destination` de l’extension est distincte du chemin contrôlé par le serveur sous `REPORT_DIR`. Voir l’[audit de compatibilité](validation-gramps-web.fr.md).

L’extension doit conserver son parcours Desktop. Gramps Web doit fournir un contrat serveur pris en charge et sûr pour les rapports installés qui produisent leurs propres fichiers.

## Capacités minimales à discuter

1. **Découverte explicite du rapport.** Le serveur peut exposer un rapport installé qui déclare utiliser le contrat de sortie personnalisée, sans rendre exécutables par défaut tous les rapports d’une catégorie nouvelle ou existante.
2. **Types de sortie déclarés.** Un rapport peut déclarer les extensions et types MIME qu’il produit. Les premiers résultats requis sont le PDF (`application/pdf`) et le ZIP (`application/zip`) ; le serveur renvoie le nom de fichier et le type de contenu correspondants.
3. **Chemin de sortie contrôlé par le serveur.** L’API crée une cible unique sous `REPORT_DIR` et la transmet au rapport par un champ documenté. Un rapport ne peut pas choisir un chemin arbitraire sur le serveur. Le serveur vérifie le fichier produit et supprime les sorties temporaires après téléchargement ou échec.
4. **Options et confidentialité habituelles.** Les options de famille, de profondeur et de format apparaissent dans l’interface Web, sont validées côté serveur et parviennent au rapport sans altération après validation. La case Gramps `privacy_acknowledged` reste décochée par défaut ; le parcours Web affiche l’avertissement avant la génération et exige une confirmation affirmative. Le contrat définit l’encodage de cette option et garantit qu’une valeur absente ou fausse n’est jamais interprétée comme vraie. Sans confirmation, la génération est refusée avant toute écriture.
5. **État des tâches et diagnostics.** La génération utilise le cycle normal des tâches asynchrones. L’API 3.23.1 ne transmet pas de callback de progression pour `generate_report` ; le contrat devra donc définir soit une progression prise en charge par les rapports, soit un état d’exécution indéterminé clairement affiché. Les échecs produisent des journaux exploitables sans révéler de données privées ni de chemins du serveur.

Les mainteneurs choisiraient le point d’extension exact. Il pourrait s’agir d’une capacité déclarée par le rapport ou d’un autre adaptateur documenté ; la proposition ne demande ni d’activer globalement `CATEGORY_WEB`, ni d’intégrer en dur cette extension à l’API.

## Vérifications d’acceptation d’une implémentation

Sur une version épinglée de Gramps Web API et une base fictive :

- Un rapport ayant déclaré la capacité apparaît dans la découverte ; un rapport sans cette capacité reste masqué lorsque sa catégorie n’est pas prise en charge.
- Les options de famille, de profondeur et de format sont validées côté serveur ; toute valeur invalide est refusée avant l’écriture. L’interface présente l’avertissement et une case de confidentialité décochée par défaut. Une valeur absente ou fausse est refusée avant toute écriture ; une valeur vraie est transmise au plugin avec la sémantique booléenne attendue par `BooleanOption`.
- Les sorties PDF et ZIP sont générées sous `REPORT_DIR`, téléchargées avec l’extension et le type MIME déclarés, et reconnues comme fichiers valides.
- Un rapport ne peut ni écrire hors de `REPORT_DIR`, ni écraser un fichier sans rapport, ni laisser de sortie partielle en cas d’échec.
- L’interface expose les états en attente/en cours/terminé/échoué ; elle présente une progression si le contrat en fournit une, sinon un état d’exécution indéterminé. Les échecs donnent accès à des diagnostics utiles sans données privées ni chemins internes.
- La génération existante dans l’interface Desktop et en CLI continue de fonctionner sans réglages propres au Web.

## Décision à obtenir

Ce brouillon doit être discuté avec les mainteneurs de Gramps Web avant toute implémentation. S’ils préfèrent un adaptateur maintenu ou un contrat de sortie plus restreint, la proposition devra suivre leur voie prise en charge. Ne pas revendiquer la compatibilité Gramps Web avant la réussite des vérifications runtime.

## Demande publiée aux mainteneurs (anglais)

Le guide de contribution de l’API demande de discuter les changements non triviaux dans une issue avant de les implémenter ([CONTRIBUTING.md](https://github.com/gramps-project/gramps-web-api/blob/master/CONTRIBUTING.md)). Le texte ci-dessous a été publié le 9 octobre 2026 dans l’issue #1048, après autorisation explicite de l’utilisateur.

**Title:** Supported custom-output report contract for third-party Gramps reports

> We maintain a third-party Gramps report that creates its own PDF or HTML ZIP instead of using the standard document output. We would like to make it usable from Gramps Web without adding a server-specific fork or writing outside the server-managed report directory.
>
> In the current released API (v3.23.1), `get_reports()` filters reports by `REPORT_DEFAULTS`, which does not include `CATEGORY_WEB`; `MIME_TYPES` does not include `.zip`; and `run_report()` supplies its own output path through the standard `of` option. Our report currently declares `CATEGORY_WEB`, accepts PDF/ZIP, and has a separate `destination` option, so the existing endpoint cannot discover or return these outputs.
>
> Is there a supported extension point, or would the maintainers consider one, for a report to declare its output formats and receive a server-controlled destination under `REPORT_DIR`? We need the API to discover only reports that opt into this contract, validate their normal report options (including an explicit privacy confirmation), return PDF and ZIP with the declared file name and MIME type, and preserve the usual task lifecycle. We do not want to enable every `CATEGORY_WEB` plugin by default.
>
> What contract would fit the API best, and what security, cleanup, option-validation, and task-status requirements should a plugin meet? We can adapt the report and add integration coverage once the supported interface is agreed.

Les constats de version ci-dessus ont été revérifiés le 30 septembre 2026 sur les sources épinglées de [v3.22.3 : constantes MIME et catégories](https://github.com/gramps-project/gramps-web-api/blob/v3.22.3/gramps_webapi/const.py) et [implémentation de l’API des rapports](https://github.com/gramps-project/gramps-web-api/blob/v3.22.3/gramps_webapi/api/report.py). GitHub indique toujours `v3.22.3` comme dernière release publiée à cette date.

Le 3 octobre, la dernière version publiée était v3.22.3. Le [nouvel audit épinglé sur `master`](validation-gramps-web.fr.md) au commit `375371f` ne révélait pas de contrat de sortie personnalisée.

Le 6 octobre, la [version officielle la plus récente](https://github.com/gramps-project/gramps-web-api/releases) est toujours v3.23.1. La relecture des sources épinglées confirme les mêmes limites ([audit actualisé](validation-gramps-web.fr.md)). Le texte ci-dessus est désormais aligné sur cette version ; à cette date, aucune issue n’avait été soumise aux mainteneurs.

## Publication — 9 octobre 2026

Le brouillon approuvé est maintenant publié dans l’[issue #1048](https://github.com/gramps-project/gramps-web-api/issues/1048). Son texte a été relu depuis GitHub et correspond au texte approuvé. Les recherches préalables n’ont trouvé aucune issue portant sur `custom-output` ou `CATEGORY_WEB`. La dernière release vérifiée reste v3.23.1 ; le contrôle statique du `master` `2b374c8` confirme les mêmes obstacles. Cette publication ouvre la discussion ; elle ne constitue ni une acceptation des mainteneurs ni une qualification Gramps Web. Voir le [relevé de publication et de sources](gramps-web-output-contract-issue-20261009.json).
