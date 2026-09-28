# Dépannage

Voir le [README en français](../README.fr.md) pour l’installation et le [guide anglais](troubleshooting.md) pour la version originale.

## Le rapport n’apparaît pas dans Gramps

Vérifier que le module a été extrait en conservant le dossier `GrampsFancyBook/` dans le répertoire des extensions utilisateur de Gramps 6, puis redémarrer Gramps. Chercher sous **Rapports → Pages Web** (le libellé dépend de la traduction de Gramps). Si un module requis manque, installer `mistune>=3,<4` dans le même environnement Python que celui qui lance Gramps Desktop, puis redémarrer Gramps.

## Le rapport refuse la famille sélectionnée

La famille de référence (F0) doit avoir deux partenaires connus. Choisir un couple complet dans les options du rapport. Le module ne déduit pas un partenaire inconnu à partir d’autres relations.

## Le chemin de sortie est refusé ou aucun fichier n’apparaît

Le répertoire de destination doit déjà exister. La sélection automatique utilise une destination en `.zip` pour le livre HTML et conserve `.json` pour l’instantané de diagnostic. Si nécessaire, choisir explicitement le format correspondant à l’extension. **Replace an existing file** n’autorise le remplacement que lorsqu’il est activé ; sinon les fichiers existants sont conservés.

Pour un instantané JSON, le rapport écrit également un fichier distinct `<nom>_consistency.json` et peut créer un dossier voisin `<nom>_media/` si des images sont convertibles.

## Des images ou pages PDF sont absentes

La conversion d’images et de PDF est facultative. Installer `Pillow>=10` et `pypdfium2>=4` dans l’environnement Python utilisé par Gramps, puis redémarrer Gramps. En l’absence d’un convertisseur, un diagnostic est produit et les dérivés concernés sont omis. Un PDF avec une URL de citation reste un lien ; un PDF multipage sans lien est conservé comme référence plutôt que rasterisé.

## L’archive HTML ne s’ouvre pas comme livre local

Extraire d’abord le ZIP et ouvrir son fichier `index.html`. L’archive utilise des liens relatifs et doit fonctionner hors ligne après extraction. Conserver l’arborescence de l’archive lors de la copie.

## Une commande se termine sans erreur, mais semble avoir échoué

Gramps peut renvoyer le code de sortie zéro même si un rapport échoue. Vérifier que la sortie demandée a été créée et consulter les diagnostics du rapport. Pour préparer un cas reproductible, utiliser le GEDCOM fictif et le script d’intégration fournis ; ne pas joindre un export familial réel ni des journaux non expurgés à un signalement.

## Gramps Web

L’exécution dans Gramps Web n’a pas été qualifiée. Le module et ses dépendances Python devraient être installés dans l’environnement serveur ; aucune instance de test validée n’est documentée à ce jour.
