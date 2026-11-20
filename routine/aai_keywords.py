#!/usr/bin/env python3
"""Keyword ledger for the aai-site-daily routine. The ledger of record is Engram aai_keywords; this file keeps
the local mirror (routine/keywords.json) and the rules, so the pick and the preserve gains check are
deterministic and testable.

    python3 aai_keywords.py locked                          the locked and owned terms (routine/locked.json; only Umar locks)
    python3 aai_keywords.py propose '<json>'                record a candidate head term for Umar to lock {term, volume, page1, note}
    python3 aai_keywords.py measure '<json list>'           one position row per term per day {term, google_position, top10, page}
    python3 aai_keywords.py preserve                        terms that dropped 2+ places from their best, or left the top 3; frozen terms
    python3 aai_keywords.py upsert '<json list>'            merge Search Console rows by (kind, term) {kind: query|page, term, page, clicks, impressions, position, window_days}
    python3 aai_keywords.py pick [day]                      the one page to fix: most impressions, position 4..15, no fix in 14 days, not frozen
    python3 aai_keywords.py fix <term> '<json>'             write last_fix {day, commit, what} on a locked, owned or page row
    python3 aai_keywords.py judge                           fixes 14+ days old with their clicks then and now
    python3 aai_keywords.py show
"""
import datetime
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
MIRROR = HERE / "keywords.json"
LOCKED = HERE / "locked.json"


def load():
    return json.loads(MIRROR.read_text()) if MIRROR.exists() else {"rows": [], "positions": []}


def save(d):
    MIRROR.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")


def locked():
    if LOCKED.exists():
        return json.loads(LOCKED.read_text())
    return {"locked": [], "candidates": [], "note": "Umar locks a term by saying so in chat; the routine writes it here only on his word."}


def save_locked(l):
    LOCKED.write_text(json.dumps(l, indent=1, ensure_ascii=False) + "\n")


def today():
    return datetime.date.today().isoformat()


def key(r):
    return (r.get("kind"), (r.get("term") or "").strip().lower()[:80])


def propose(payload):
    l = locked()
    c = json.loads(payload)
    c.setdefault("proposed_day", today())
    terms = {x["term"].lower() for x in l["candidates"]}
    if c["term"].lower() in terms:
        l["candidates"] = [{**x, **c} if x["term"].lower() == c["term"].lower() else x for x in l["candidates"]]
    else:
        l["candidates"].append(c)
    save_locked(l)
    print(json.dumps({"candidates": len(l["candidates"]), "locked": [x["term"] for x in l["locked"]]}))


def measure(payload):
    rows = json.loads(payload)
    d = load()
    day = today()
    d["positions"] = [p for p in d["positions"] if not (p.get("day") == day and p.get("term", "").lower() in {r["term"].lower() for r in rows})]
    for r in rows:
        d["positions"].append({"day": day, "term": r["term"], "google_position": r.get("google_position"),
                               "top10": r.get("top10", []), "page": r.get("page"), "gsc_impressions": r.get("gsc_impressions"),
                               "gsc_position": r.get("gsc_position")})
    save(d)
    print(json.dumps(trend(d), indent=1, ensure_ascii=False))


def trend(d=None):
    d = d or load()
    out = {}
    for p in sorted(d["positions"], key=lambda x: x["day"]):
        t = out.setdefault(p["term"], {"series": []})
        t["series"].append({"day": p["day"], "pos": p["google_position"]})
    for term, t in out.items():
        s = t["series"]
        poss = [x["pos"] for x in s if x["pos"] is not None]
        t["today"] = s[-1]["pos"] if s else None
        t["previous"] = s[-2]["pos"] if len(s) > 1 else None
        t["best"] = min(poss) if poss else None
        t["change"] = (t["previous"] - t["today"]) if (t["today"] is not None and t["previous"] is not None) else None
        t["frozen"] = t["today"] is not None and t["today"] <= 3
        t["series"] = s[-7:]
    return out


def preserve():
    """Preserve gains first: a term that lost 2 or more places against its best, or fell out of the top 3 after
    holding it, is the run's only target work for that term. Frozen terms (position 3 or better) keep their
    title, H1 and first screen."""
    t = trend()
    drops, frozen = [], []
    for term, x in t.items():
        if x["frozen"]:
            frozen.append(term)
        if x["today"] is None and x["best"] is not None:
            drops.append({"term": term, "best": x["best"], "today": None, "why": "absent from the top 30 after ranking"})
        elif x["today"] is not None and x["best"] is not None and x["today"] - x["best"] >= 2:
            drops.append({"term": term, "best": x["best"], "today": x["today"], "why": f"lost {x['today'] - x['best']} places from best"})
        elif x["best"] is not None and x["best"] <= 3 and x["today"] is not None and x["today"] > 3:
            drops.append({"term": term, "best": x["best"], "today": x["today"], "why": "left the top 3"})
    print(json.dumps({"drops": drops, "frozen": frozen, "rule": "a drop with no commit on the owning page since the last read is volatility: record it, leave the page alone"}, indent=1))


def upsert(rows, day=None):
    day = day or today()
    d = load()
    idx = {key(r): r for r in d["rows"]}
    added = updated = 0
    for r in rows:
        k = key(r)
        if k in idx:
            old = idx[k]
            idx[k].update({**old, **{a: b for a, b in r.items() if b is not None}, "first_seen": old.get("first_seen") or day, "last_seen": day})
            updated += 1
        else:
            d["rows"].append({"first_seen": day, "last_seen": day, "status": "open", **r})
            idx[k] = d["rows"][-1]
            added += 1
    save(d)
    return {"added": added, "updated": updated, "rows": len(d["rows"])}


def pick(day=None):
    day = datetime.date.fromisoformat(day) if day else datetime.date.today()
    frozen_pages = {x.get("page") for term, x in trend().items() if x["frozen"] for x in [x]}
    rows = load()["rows"]
    pages = [r for r in rows if r.get("kind") == "page" and r.get("impressions") and r.get("position") is not None]
    def fresh(r):
        f = (r.get("last_fix") or {}).get("day")
        return (not f) or (day - datetime.date.fromisoformat(f)).days > 14
    cands = [r for r in pages if 4 <= float(r["position"]) <= 15 and fresh(r) and r.get("page") not in frozen_pages]
    cands.sort(key=lambda r: (-int(r["impressions"]), float(r["position"])))
    return cands[0] if cands else None


def fix(term, payload):
    d = load()
    j = json.loads(payload)
    j.setdefault("day", today())
    hit = 0
    for r in d["rows"]:
        if (r.get("term") or "").lower() == term.lower() or r.get("page") == term:
            r["last_fix"] = j
            hit += 1
    if not hit:
        d["rows"].append({"kind": "target", "term": term, "first_seen": today(), "last_seen": today(), "last_fix": j, "status": "open"})
    save(d)
    print(json.dumps({"rows_marked": hit or 1, "last_fix": j}))


def judge():
    """A fix is judged at 14 days by clicks, never by impressions."""
    cutoff = datetime.date.today() - datetime.timedelta(days=14)
    out = []
    for r in load()["rows"]:
        f = r.get("last_fix")
        if f and datetime.date.fromisoformat(f["day"]) <= cutoff:
            out.append({"term": r.get("term"), "page": r.get("page"), "fix": f, "clicks_now": r.get("clicks"),
                        "clicks_at_fix": f.get("clicks_at_fix"), "delta": (r.get("clicks") or 0) - (f.get("clicks_at_fix") or 0)})
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd == "locked":
        print(json.dumps(locked(), indent=1, ensure_ascii=False))
    elif cmd == "propose":
        propose(sys.argv[2])
    elif cmd == "measure":
        measure(sys.argv[2])
    elif cmd == "preserve":
        preserve()
    elif cmd == "upsert":
        print(json.dumps(upsert(json.loads(sys.argv[2]), *(sys.argv[3:4]))))
    elif cmd == "pick":
        print(json.dumps(pick(*(sys.argv[2:3])), ensure_ascii=False))
    elif cmd == "fix":
        fix(sys.argv[2], sys.argv[3])
    elif cmd == "judge":
        judge()
    elif cmd == "trend":
        print(json.dumps(trend(), indent=1, ensure_ascii=False))
    else:
        print(json.dumps(load(), indent=1, ensure_ascii=False))
