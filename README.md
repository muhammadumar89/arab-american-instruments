# Arab American Instruments site

Static site. `python3 build.py` writes `site/`. Preview: `python3 -m http.server 8041 --directory site`.

- Copy, products, industries and Design Lab notes are data in `build.py`.
- Banner videos: `assets/video/` (Pexels License, gated for brands; see `assets/video/CREDITS.md`). Re-encode with `raw/encode.sh` (raw clips are not committed).
- Product images: `assets/img/products/`, cropped from Design Lab renders and board layouts.
- House rules: no hyphens or dashes in copy (the tagline is kept verbatim), no prices, no customer names, every banner a real world video mixing Saudi and American places with devices and technology.
