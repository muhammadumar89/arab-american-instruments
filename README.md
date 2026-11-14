# Arab American Instruments site

Static site. `python3 build.py` writes `site/`. Local preview: `python3 build.py && python3 -m http.server 8041 --directory site`. Deploy: push to main; `.github/workflows/pages.yml` builds and publishes to GitHub Pages.

- Copy, products, industries and Design Lab notes are data in `build.py`.
- Banner videos: `assets/video/` (Pexels License, gated for brands; see `assets/video/CREDITS.md`). Re-encode with `raw/encode.sh` (raw clips are not committed).
- Product and use case photos: `assets/img/stock/` (Pexels, gated; credits in `assets/video/CREDITS.md`). Our own boards and renders are never published. Founder portraits in `assets/img/team/`.
- House rules: no hyphens or dashes in copy (the tagline is kept verbatim), no prices, no customer names, every banner a real world video mixing Saudi and American places with devices and technology.
