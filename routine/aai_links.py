#!/usr/bin/env python3
"""Earned authority for arabamerican.ai: sites we do not own that link to it. Read every run beside the positions.
Mirror routine/links.json; Engram aai_links holds the same row, one per day. No outreach, no email, no DMs:
authority comes only from what people use and cite.

    python3 aai_links.py record '<json>'   store one reading and print the delta against the last one
    python3 aai_links.py github            GitHub code mentioning arabamerican.ai outside our own repos (gh CLI)
    python3 aai_links.py last

A reading is {"day", "gsc": {"external_links", "sites": [{"domain", "links", "pages"}]}, "bing": {...} or null,
"github_mentions": n, "github_repos": [...], "note"}. A missing source is null, never zero.
"""
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
STORE = HERE / "links.json"
# Domains we control or publish on ourselves. A link from one of these is distribution, never authority.
OWNED = ["arabamerican.ai", "codeatoms.ai", "codeninjaconsulting.com", "muhammadumar89.github.io", "github.com/muhammadumar89",
         "huggingface.co/codeninjatools", "dev.to/umar_bilal", "x.com/umargik", "twitter.com/umargik", "app.codeatoms.ai"]
SELF_HOSTED = ["github.com", "x.com", "twitter.com", "dev.to", "huggingface.co", "linkedin.com", "youtube.com"]
ECHO = []  # feeds that only mirror our own posts; add a domain only after opening one of its pages


def owned(domain):
    d = (domain or "").lower().removeprefix("www.")
    return (any(d == o or d.endswith("." + o) or d.startswith(o) for o in OWNED)
            or any(d == h or d.endswith("." + h) for h in SELF_HOSTED) or d in ECHO)


def load():
    return json.loads(STORE.read_text()) if STORE.exists() else {"readings": []}


def summarize(r):
    out = {}
    for src in ("gsc", "bing"):
        s = r.get(src)
        if not s:
            out[src] = None
            continue
        sites = s.get("sites") or []
        earned = sorted({x["domain"].lower().removeprefix("www.") for x in sites if not owned(x["domain"])})
        out[src] = {"sites": len(sites), "earned_domains": len(earned), "earned": earned,
                    "external_links": s.get("external_links"), "referring_domains": s.get("referring_domains")}
    out["github_mentions"] = r.get("github_mentions")
    out["earned_confirmed"] = r.get("earned_confirmed") or []
    return out


def record(payload):
    r = json.loads(payload)
    r.setdefault("day", date.today().isoformat())
    d = load()
    prev = next((x for x in reversed(d["readings"]) if x.get("day") != r["day"]), None)
    d["readings"] = [x for x in d["readings"] if x.get("day") != r["day"]] + [r]
    STORE.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    now, before = summarize(r), (summarize(prev) if prev else None)
    delta = {}
    if before:
        for src in ("gsc", "bing"):
            if now[src] and before[src]:
                delta[src] = {"earned_domains": now[src]["earned_domains"] - before[src]["earned_domains"],
                              "new": sorted(set(now[src]["earned"]) - set(before[src]["earned"])),
                              "lost": sorted(set(before[src]["earned"]) - set(now[src]["earned"]))}
        if now["github_mentions"] is not None and before["github_mentions"] is not None:
            delta["github_mentions"] = now["github_mentions"] - before["github_mentions"]
    print(json.dumps({"day": r["day"], "now": now, "since": prev and prev["day"], "delta": delta}, indent=1))


def github():
    try:
        res = subprocess.run(["gh", "api", "-X", "GET", "search/code", "-f", "q=arabamerican.ai -user:muhammadumar89", "-f", "per_page=100"],
                             capture_output=True, text=True, timeout=60)
        j = json.loads(res.stdout)
        repos = sorted({i["repository"]["full_name"] for i in j.get("items", [])})
        print(json.dumps({"github_mentions": len(repos), "repos": repos}))
    except Exception as ex:
        print(json.dumps({"github_mentions": None, "error": str(ex)[:200]}))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "last"
    if cmd == "record":
        record(sys.argv[2])
    elif cmd == "github":
        github()
    else:
        d = load()
        print(json.dumps(d["readings"][-1] if d["readings"] else None, indent=1))
