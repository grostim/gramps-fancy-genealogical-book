# Proposition : rapports à sortie personnalisée dans Gramps Web

**Statut :** brouillon de discussion local ; ni examiné ni accepté par les mainteneurs de Gramps Web.

## Contexte

Gramps Fancy Genealogical Book s’enregistre comme rapport `CATEGORY_WEB` et génère lui-même des fichiers PDF ou HTML ZIP. L’audit statique de Gramps Web API 3.22.3 a montré que cette catégorie est filtrée, que ZIP n’est pas un type de résultat accepté et que l’option personnalisée `destination` de l’extension est distincte du chemin contrôlé par le serveur sous `REPORT_DIR`. Voir l’[audit de compatibilité](validation-gramps-web.fr.md).

L’extension doit conserver son parcours Desktop. Gramps Web doit fournir un contrat serveur pris en charge et sûr pour les rapports installés qui produisent leurs propres fichiers.

## Capacités minimales à discuter

1. **Découverte explicite du rapport.** Le serveur peut exposer un rapport installé qui déclare utiliser le contrat de sortie personnalisée, sans rendre exécutables par défaut tous les rapports d’une catégorie nouvelle ou existante.
2. **Types de sortie déclarés.** Un rapport peut déclarer les extensions et types MIME qu’il produit. Les premiers résultats requis sont le PDF (`application/pdf`) et le ZIP (`application/zip`) ; le serveur renvoie le nom de fichier et le type de contenu correspondants.
3. **Chemin de sortie contrôlé par le serveur.** L’API crée une cible unique sous `REPORT_DIR` et la transmet au rapport par un champ documenté. Un rapport ne peut pas choisir un chemin arbitraire sur le serveur. Le serveur vérifie le fichier produit et supprime les sorties temporaires après téléchargement ou échec.
4. **Options et confidentialité habituelles.** Les options de famille, de profondeur, de format et de confirmation de confidentialité apparaissent dans l’interface Web, sont validées côté serveur et parviennent au rapport sans altération. Sans confirmation de confidentialité, la génération est refusée.
5. **État des tâches et diagnostics.** La génération utilise le cycle normal des tâches asynchrones. L’utilisateur voit une progression ou un état d’exécution explicite ; les échecs produisent des journaux exploitables sans révéler de données privées ni de chemins du serveur.

Les mainteneurs choisiraient le point d’extension exact. Il pourrait s’agir d’une capacité déclarée par le rapport ou d’un autre adaptateur documenté ; la proposition ne demande ni d’activer globalement `CATEGORY_WEB`, ni d’intégrer en dur cette extension à l’API.

## Vérifications d’acceptation d’une implémentation

Sur une version épinglée de Gramps Web API et une base fictive :

- Un rapport ayant déclaré la capacité apparaît dans la découverte ; un rapport sans cette capacité reste masqué lorsque sa catégorie n’est pas prise en charge.
- Les options valides, dont la confirmation de confidentialité obligatoire, parviennent au rapport ; les valeurs invalides ou les confirmations absentes sont refusées avant toute écriture.
- Les sorties PDF et ZIP sont générées sous `REPORT_DIR`, téléchargées avec l’extension et le type MIME déclarés, et reconnues comme fichiers valides.
- Un rapport ne peut ni écrire hors de `REPORT_DIR`, ni écraser un fichier sans rapport, ni laisser de sortie partielle en cas d’échec.
- Le point d’accès des tâches expose les états terminé/échoué ainsi qu’une progression et des journaux utiles.
- La génération existante dans l’interface Desktop et en CLI continue de fonctionner sans réglages propres au Web.

## Décision à obtenir

Ce brouillon doit être discuté avec les mainteneurs de Gramps Web avant toute implémentation. S’ils préfèrent un adaptateur maintenu ou un contrat de sortie plus restreint, la proposition devra suivre leur voie prise en charge. Ne pas revendiquer la compatibilité Gramps Web avant la réussite des vérifications runtime.
