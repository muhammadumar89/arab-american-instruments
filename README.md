# Arab American Instruments site

Static site. `python3 build.py` writes `site/`. Local preview: `python3 build.py && python3 -m http.server 8041 --directory site`. Deploy: push to main; `.github/workflows/pages.yml` builds and publishes to GitHub Pages.

- Copy, products, industries and Design Lab notes are data in `build.py`.
- Banner videos: `assets/video/` (Pexels License, gated for brands; see `assets/video/CREDITS.md`). Re-encode with `raw/encode.sh` (raw clips are not committed).
- Product and use case photos: `assets/img/stock/` (Pexels, gated; credits in `assets/video/CREDITS.md`). Our own boards and renders are never published. Founder portraits in `assets/img/team/`.
- House rules: no hyphens or dashes in copy (the tagline is kept verbatim), no prices, no customer names, every banner a real world video mixing Saudi and American places with devices and technology.

## Daily routine

`aai-site-daily` (scheduled task, 09:30 local) runs two tracks every day: search position in Google and AI answers, and look and feel. Its tools live in `routine/`: `aai_daily.py` (episode, reward, brand gate, page audit, screenshot rotation, first week backlog), `aai_keywords.py` (locked terms, positions, preserve gains, Search Console ledger), `aai_links.py` (earned referring domains), `aai_design.py` (one logged design change per run), `nightly_push.sh` (gate, commit, push; never force). Memory is Engram (agent `aai-site`, collections `aai_*`); the JSON files in `routine/` are mirrors. Umar locks head terms in `routine/locked.json` by saying so; the routine never locks a term itself. The gate in `aai_daily.py gate` blocks a push whose copy breaks a house rule.
