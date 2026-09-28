# L2 technical probes / Prototypes techniques L2

These development files are excluded from the add-on archive. They contain only synthetic data. They do not implement the full genealogy engine.

## Layout

`python prototypes/build_layout.py` writes the standalone `layout-spike.tex`. Open it in the Codex LaTeX editor. It exercises a long chronology, repeated citations, long footnotes, final-page references, compact profiles, a large image placeholder, escaped characters, contents and a reduced person index. Images remain placeholders; PDF incorporation and automated full indexing are future probes.

The built-in compiler failed before reading the source on 2026-09-27 because its Tectonic bundle was not cached or downloadable; that attempt provided no evidence about the document. The pinned LuaLaTeX CI now compiles the layout spike and both production-rendered fixtures with stable references and no overfull boxes. This establishes compilation, not page-by-page visual correctness against the original mockups.

The CI harness now compiles the layout spike and both production-rendered books in an isolated directory with shell escape disabled, up to five passes, and log checks for unresolved references and overfull boxes. Inspect the resulting PDFs page by page before declaring visual acceptance; the original mockups remain local because they contain real family examples. The rich fixture is intended to land in the 15–30 page range.

## Media

Run `python prototypes/media_spike.py` with Pillow installed. Outputs stay in `.work/media-spike/`. The demonstrated central 25–75% rectangle converts a 1200×800 image to pixel bounds `(300,200,900,600)` and a 600×400 derivative. Gramps 6.0.8 `MediaRef.get_rectangle` and `gen.utils.image.image_size` use percentage coordinates; the probe adds a proposed covering-pixel rounding policy.

The JSON also records all four PDF page-count/URL decisions (§ 7.3). No real PDF parsing/rasterization, EXIF orientation or server-media resolution has been demonstrated. Distinct reference regions have distinct derivative cache keys; placement still obeys the single documentary reproduction rule.

## Web

See [web-spike.md](web-spike.md). No development instance was supplied, and the local Docker daemon was unavailable. Static source inspection identifies integration obstacles; it does not qualify deployment.

## Français

Ces fichiers de développement, exclusivement fictifs, sont exclus de l’archive du plugin. Ils n’implémentent pas le moteur généalogique complet.

### Composition

`python prototypes/build_layout.py` génère `layout-spike.tex`, ouvert dans l’éditeur LaTeX Codex. Il couvre chronologie longue, citations réutilisées, notes longues, renvois de pages, fiches compactes, cadre pleine page, caractères échappés, sommaire et index réduit. Les images sont des cadres ; incorporation de PDF et index complet automatisé restent à éprouver.

Le compilateur intégré a échoué avant lecture du source le 27 septembre 2026, car ses ressources Tectonic n’étaient pas en cache et leur téléchargement était impossible ; cet essai ne fournissait aucune preuve sur le document. La CI LuaLaTeX épinglée compile maintenant le prototype de mise en page et les deux fixtures issues du moteur de rendu, avec renvois stabilisés et sans débordement. Cela confirme la compilation, pas encore la qualité visuelle page par page face aux maquettes originales.

La CI compile maintenant le prototype et les deux livres produits par le moteur dans un répertoire isolé, sans shell escape, avec cinq passes maximum et vérification des journaux de renvois et débordements. Examiner les PDF page par page avant de déclarer la recette visuelle terminée ; les maquettes originales restent locales puisqu’elles contiennent des exemples familiaux réels. La fixture riche vise 15–30 pages.

### Médias

Exécuter `python prototypes/media_spike.py` dans un environnement avec Pillow. Les résultats restent dans `.work/media-spike/`. La région centrale 25–75% d’une image 1200×800 devient `(300,200,900,600)`, soit 600×400 pixels. Les API Gramps 6.0.8 emploient des pourcentages ; le prototype propose un arrondi couvrant les pixels de bord.

Le JSON consigne aussi les quatre règles PDF/URL du § 7.3. Lecture/rastérisation PDF, orientation EXIF et résolution des médias serveur restent à réaliser. Les régions ont des clés de cache distinctes ; cela n’autorise pas plusieurs reproductions documentaires principales.

### Web

Voir [web-spike.md](web-spike.md). Aucune instance de développement fournie et démon Docker local indisponible. L’inspection statique révèle des obstacles ; elle ne qualifie aucun déploiement.

## Reproducible LuaLaTeX build

The pinned LuaLaTeX CI compiles the standalone layout spike and two synthetic books generated through the production `render_latex(BookModel)` renderer. The rich fixture has a long profile, 80 events, a publishable note, and a cited source; the sparse fixture has a central couple but no events, notes, or citations. Each document is compiled for up to five passes until its reference files stabilize. The build fails on unresolved references or overfull boxes and writes PDFs, TeX sources, and logs under `.work/latex-spike/`.

To reproduce the generated books locally on macOS or Linux with Python and Docker:

```sh
python -m pip install 'mistune>=3,<4'
PYTHONPATH=src python prototypes/build_rendered_book.py
docker run --rm \
  --user "$(id -u):$(id -g)" \
  --env HOME=/tmp \
  --volume "$PWD:/work" \
  --workdir /work \
  texlive/texlive:latest@sha256:1cb66a6dc31fe153369c5bb63549aea31c2ffb351613af67b182d84c8521fe89 \
  bash scripts/compile_latex_prototype.sh
```

The `latex-prototype` CI job keeps the PDFs, sources, and LuaLaTeX logs for all three documents as a 14-day artifact. Compilation success does not replace the pending visual review against the local-only reference mockups. The TeX Live image is pinned by its upstream multi-platform digest; refresh it only alongside a successful compilation.

## Compilation LuaLaTeX reproductible

La CI LuaLaTeX épinglée compile le prototype de mise en page autonome et deux livres fictifs générés par le vrai `render_latex(BookModel)`. La fixture riche contient une fiche longue, 80 événements, une note publiable et une source citée ; la fixture peu documentée contient un couple central sans événements, notes ni citations. Chaque document est compilé jusqu’à stabilisation des fichiers de références, en cinq passes maximum. La compilation échoue si des renvois restent non résolus ou si le texte déborde ; PDF, sources TeX et journaux sont écrits dans `.work/latex-spike/`.

Pour générer et compiler les livres localement sous macOS ou Linux avec Python et Docker :

```sh
python -m pip install 'mistune>=3,<4'
PYTHONPATH=src python prototypes/build_rendered_book.py
docker run --rm \
  --user "$(id -u):$(id -g)" \
  --env HOME=/tmp \
  --volume "$PWD:/work" \
  --workdir /work \
  texlive/texlive:latest@sha256:1cb66a6dc31fe153369c5bb63549aea31c2ffb351613af67b182d84c8521fe89 \
  bash scripts/compile_latex_prototype.sh
```

La tâche CI `latex-prototype` conserve les PDF, sources et journaux des trois documents dans un artefact pendant 14 jours. La réussite de compilation ne remplace pas la revue visuelle à venir face aux maquettes de référence, qui restent stockées localement. L’image TeX Live est épinglée par son digest multiarchitecture publié en amont ; toute mise à jour doit être suivie d’une compilation réussie.
