# L2 technical probes / Prototypes techniques L2

These development files are excluded from the add-on archive. They contain only synthetic data. They do not implement the full genealogy engine.

## Layout

`python prototypes/build_layout.py` writes the standalone `layout-spike.tex`. Open it in the Codex LaTeX editor. It exercises a long chronology, repeated citations, long footnotes, final-page references, compact profiles, a large image placeholder, escaped characters, contents and a reduced person index. Images remain placeholders; PDF incorporation and automated full indexing are future probes.

On 2026-09-27 the built-in compiler failed before reading the source: its Tectonic bundle was not cached and could not be downloaded. No PDF, actual page count, resolved references or visual correctness is claimed. The source is preserved in the editor. LuaLaTeX remains the proposed production engine; native-editor compilation alone would not qualify it.

When a LuaLaTeX environment is available, compile in an isolated directory with shell escape disabled, bounded runtime, and repeat until references stabilize. Inspect logs and every page before accepting the spike. Aim for 15–30 pages; adjust synthetic chronology length after actual pagination.

## Media

Run `python prototypes/media_spike.py` with Pillow installed. Outputs stay in `.work/media-spike/`. The demonstrated central 25–75% rectangle converts a 1200×800 image to pixel bounds `(300,200,900,600)` and a 600×400 derivative. Gramps 6.0.8 `MediaRef.get_rectangle` and `gen.utils.image.image_size` use percentage coordinates; the probe adds a proposed covering-pixel rounding policy.

The JSON also records all four PDF page-count/URL decisions (§ 7.3). No real PDF parsing/rasterization, EXIF orientation or server-media resolution has been demonstrated. Distinct reference regions have distinct derivative cache keys; placement still obeys the single documentary reproduction rule.

## Web

See [web-spike.md](web-spike.md). No development instance was supplied, and the local Docker daemon was unavailable. Static source inspection identifies integration obstacles; it does not qualify deployment.

## Français

Ces fichiers de développement, exclusivement fictifs, sont exclus de l’archive du plugin. Ils n’implémentent pas le moteur généalogique complet.

### Composition

`python prototypes/build_layout.py` génère `layout-spike.tex`, ouvert dans l’éditeur LaTeX Codex. Il couvre chronologie longue, citations réutilisées, notes longues, renvois de pages, fiches compactes, cadre pleine page, caractères échappés, sommaire et index réduit. Les images sont des cadres ; incorporation de PDF et index complet automatisé restent à éprouver.

Le 27 septembre 2026, le compilateur intégré a échoué avant lecture du source : ressources Tectonic absentes du cache et téléchargement impossible. Aucun PDF, nombre de pages, renvoi résolu ou qualité visuelle n’est donc validé. Le source est conservé dans l’éditeur. LuaLaTeX reste le moteur de production proposé ; la compilation dans l’éditeur ne suffirait pas à le qualifier.

Avec un environnement LuaLaTeX disponible : compiler dans un répertoire isolé, sans shell escape, avec délai maximal et passes jusqu’à stabilisation. Examiner les journaux et chaque page. Viser 15–30 pages et ajuster la chronologie fictive après pagination réelle.

### Médias

Exécuter `python prototypes/media_spike.py` dans un environnement avec Pillow. Les résultats restent dans `.work/media-spike/`. La région centrale 25–75% d’une image 1200×800 devient `(300,200,900,600)`, soit 600×400 pixels. Les API Gramps 6.0.8 emploient des pourcentages ; le prototype propose un arrondi couvrant les pixels de bord.

Le JSON consigne aussi les quatre règles PDF/URL du § 7.3. Lecture/rastérisation PDF, orientation EXIF et résolution des médias serveur restent à réaliser. Les régions ont des clés de cache distinctes ; cela n’autorise pas plusieurs reproductions documentaires principales.

### Web

Voir [web-spike.md](web-spike.md). Aucune instance de développement fournie et démon Docker local indisponible. L’inspection statique révèle des obstacles ; elle ne qualifie aucun déploiement.
