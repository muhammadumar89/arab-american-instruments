#!/usr/bin/env python3
"""Look and feel ledger for the aai-site-daily routine. One change per run, logged with before and after
screenshots and a named revert. Mirror routine/design_changes.json; Engram aai_design_changes holds the same rows.

    python3 aai_design.py record '<json>'   {day, page, width, what, why, before, after, commit, revert, episode}
    python3 aai_design.py open              changes shipped in the last 7 days (check each on today's screenshots)
    python3 aai_design.py defects           the known defect list with state (routine/defects.json)
    python3 aai_design.py defect <id> <state> [note]
    python3 aai_design.py last
"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
STORE = HERE / "design_changes.json"
DEFECTS = HERE / "defects.json"

# Known starting list (Umar's brief, 20 Nov 2026). Highest value first. A run fixes ONE.
SEED = [
    {"id": "hero-scrim", "page": "/", "defect": "hero headline hard to read over bright sky in some banner frames", "fix": "add a scrim or pick a darker frame", "state": "open"},
    {"id": "hero-coords", "page": "/", "defect": "the coordinates line under the hero buttons is illegible", "fix": "larger, higher contrast, or remove", "state": "open"},
    {"id": "body-15px", "page": "*", "defect": "body text is 15px", "fix": "16px at phone width at least; check line length", "state": "open"},
    {"id": "header-phone", "page": "*", "defect": "floating header at phone width unverified", "fix": "screenshot at 375px; pill must not cover the H1", "state": "open"},
    {"id": "pillars-phone", "page": "/", "defect": "pillar grid at phone width unverified", "fix": "single column, no clipped text", "state": "open"},
    {"id": "video-mobile", "page": "/", "defect": "22 videos on the home page; weight on mobile data", "fix": "lazy load below the fold, posters, re-encode the largest", "state": "open"},
]


def load():
    return json.loads(STORE.read_text()) if STORE.exists() else {"changes": []}


def defects():
    if DEFECTS.exists():
        return json.loads(DEFECTS.read_text())
    DEFECTS.write_text(json.dumps(SEED, indent=1) + "\n")
    return SEED


def record(payload):
    r = json.loads(payload)
    r.setdefault("day", date.today().isoformat())
    for k in ("page", "what", "why", "revert"):
        if not r.get(k):
            sys.exit(f"record: {k} is required (a change without a named revert is not shipped)")
    d = load()
    d["changes"].append(r)
    STORE.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({"changes": len(d["changes"]), "last": r}, indent=1, ensure_ascii=False))


def open_changes():
    cutoff = (date.today() - timedelta(days=7)).isoformat()
    print(json.dumps([c for c in load()["changes"] if c.get("day", "") >= cutoff], indent=1, ensure_ascii=False))


def set_defect(did, state, note):
    ds = defects()
    if did not in {x["id"] for x in ds}:
        ds.append({"id": did, "page": "", "defect": note, "fix": "", "state": state})
    for x in ds:
        if x["id"] == did:
            x.update({"state": state, "day": date.today().isoformat(), **({"note": note} if note else {})})
    DEFECTS.write_text(json.dumps(ds, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(ds, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "last"
    if cmd == "record":
        record(sys.argv[2])
    elif cmd == "open":
        open_changes()
    elif cmd == "defects":
        print(json.dumps(defects(), indent=1, ensure_ascii=False))
    elif cmd == "defect":
        set_defect(sys.argv[2], sys.argv[3], " ".join(sys.argv[4:]))
    else:
        d = load()
        print(json.dumps(d["changes"][-1] if d["changes"] else None, indent=1, ensure_ascii=False))
