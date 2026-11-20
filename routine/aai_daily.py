#!/usr/bin/env python3
"""The local half of the aai-site-daily routine (Arab American Instruments, https://arabamerican.ai).

The routine session (Claude, with the Engram connector and a signed in Chrome) does the judgement, the
browser reads and the Engram writes. This script does the bookkeeping that must never drift: the episode
number, the reward arithmetic, the brand gate over the built site, the page audit, the screenshot rotation
and the first week backlog. Engram is the source of truth; routine/ledger.json is the mirror so a run
with a broken connector still knows what it has seen.

    python3 aai_daily.py episode-template          print an aai_episodes row skeleton with the next episode number
    python3 aai_daily.py record-episode '<json>'   mirror an episode row after Engram took it
    python3 aai_daily.py feedback '<json>'         mirror this run's aai_episode_feedback row
    python3 aai_daily.py reward '<json>'           compute the reward from counts (keys below)
    python3 aai_daily.py lessons                   print the LESSONS block of the task file
    python3 aai_daily.py audit                     rebuild site/ and read every page: title, description, H1, JSON-LD,
                                                   videos and posters, images without alt, sitemap lastmod, llms.txt
    python3 aai_daily.py gate                      brand gate over the built site text; exit 1 on any hit
    python3 aai_daily.py rotate [n]                the inner pages to screenshot today (oldest seen first), marks them seen
    python3 aai_daily.py backlog                   the first week backlog with each item's state
    python3 aai_daily.py backlog mark <id> <status> [note]
"""
import json
import os
import re
import subprocess
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SITE = REPO / "site"
LEDGER = HERE / "ledger.json"
ALLOW = HERE / "gate_allow.json"
TASK = Path.home() / ".claude" / "scheduled-tasks" / "aai-site-daily" / "SKILL.md"
SITE_URL = "https://arabamerican.ai"

# Reward (one episode): outcomes, never activity. A quiet day scores 0 and is valid.
REWARD = {
    "backlog_shipped": 2,            # a first week backlog item live and verified on the domain
    "term_held_or_up": 1,            # a locked or owned term at or above its last read
    "term_dropped_after_commit": -2,  # a drop of 2+ places with a commit on the owning page since the last read
    "clicks_delta_positive": 2,      # a page fixed 14+ days ago whose Search Console clicks rose
    "design_shipped": 2,             # one look and feel change live with before and after screenshots and a named revert
    "design_broke": -2,              # a shipped change found broken later (overflow, console error, unreadable text)
    "brand_hit_live": -2,            # the gate found a banned word or number on the live site
    "connector_failure": -1,         # Engram, Search Console or Chrome could not be read
}

BACKLOG = [
    ("gsc-bing", "Search Console and Bing Webmaster Tools verified for arabamerican.ai; sitemap submitted to both"),
    ("structured-data", "JSON-LD from build.py: Organization with sameAs on home and about, Product on every hardware page, BreadcrumbList everywhere, Article on lab notes"),
    ("llms-markdown", "sitemap lastmod per page; llms.txt and llms-full.txt; a Markdown copy (index.md) of every page"),
    ("analytics", "GA4 tag in page() once Umar gives the property id"),
    ("titles", "every page title leads with what a searcher types; descriptions under 160 characters; home title not the bare company name"),
    ("request-form", "/build/ form posts to a real endpoint (Lambda and SES like codeatoms.ai) and an AAI address; until then requests are unmeasured, never zero"),
    ("home-weight", "home page video weight: lazy loading proven on a phone, poster on every video, the largest clips re-encoded with raw/encode.sh"),
]


# ------------------------------------------------------------------ ledger

def load():
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    return {"episodes": [], "feedback": [], "seen": {}, "backlog": {}}


def save(d):
    LEDGER.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def next_episode(d):
    return max([e.get("episode", 0) for e in d["episodes"]] + [0]) + 1


def episode_template():
    d = load()
    print(json.dumps({
        "episode": next_episode(d), "day": date.today().isoformat(), "run_id": "", "kind": "routine",
        "backlog_done": [], "channels": {"google": {}, "gsc": {}, "links": "", "design": "", "ai_citations": None},
        "defects": [], "decisions": [], "feedback_applied": [], "lessons_added": [], "gap_records": [],
        "reward": 0, "summary": ""}, indent=2))


def record_episode(payload):
    d = load()
    row = json.loads(payload)
    d["episodes"] = [x for x in d["episodes"] if x.get("episode") != row.get("episode")] + [row]
    save(d)
    print("recorded episode", row.get("episode"))


def feedback(payload):
    d = load()
    row = json.loads(payload)
    d["feedback"] = [x for x in d["feedback"] if x.get("episode") != row.get("episode")] + [row]
    save(d)
    print("recorded feedback for episode", row.get("episode"))


def reward(payload):
    j = json.loads(payload)
    unknown = sorted(set(j) - set(REWARD))
    if unknown:
        sys.exit(f"reward: unknown keys {unknown}; expected {sorted(REWARD)}")
    print(sum(w * int(j.get(k, 0)) for k, w in REWARD.items()))


def lessons():
    t = TASK.read_text(encoding="utf-8") if TASK.exists() else ""
    block = t.rsplit("\n## LESSONS", 1)[1] if "\n## LESSONS" in t else ""
    for ln in block.splitlines():
        if ln.startswith("- "):
            print(ln)


# ------------------------------------------------------------------ site reading

def build():
    env = {k: v for k, v in os.environ.items() if k not in ("AAI_BASE", "AAI_SITE_URL")}
    r = subprocess.run([sys.executable, str(REPO / "build.py")], cwd=REPO, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("build.py failed:\n" + r.stderr[-2000:])


class Reader(HTMLParser):
    """Visible text plus the head facts of one page."""
    SKIP = {"script", "style", "noscript", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.desc = None
        self.h1 = []
        self.jsonld = []
        self.videos = []
        self.imgs_no_alt = 0
        self.text = []
        self._stack = []
        self._in = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.SKIP:
            self._stack.append(tag)
            if tag == "script" and a.get("type") == "application/ld+json":
                self._in = "ld"
            return
        if tag == "title":
            self._in = "title"
        elif tag == "h1":
            self._in = "h1"
            self.h1.append("")
        elif tag == "meta" and a.get("name") == "description":
            self.desc = a.get("content", "")
        elif tag == "video":
            self.videos.append({"poster": bool(a.get("poster")), "preload": a.get("preload"), "loading": a.get("loading"),
                                "autoplay": "autoplay" in a, "src": a.get("src") or a.get("data-src")})
        elif tag == "source" and self.videos and not self.videos[-1].get("src"):
            self.videos[-1]["src"] = a.get("src") or a.get("data-src")
        elif tag == "img" and not a.get("alt"):
            self.imgs_no_alt += 1

    def handle_endtag(self, tag):
        if self._stack and tag == self._stack[-1]:
            self._stack.pop()
            if tag == "script":
                self._in = None
        if tag in ("title", "h1"):
            self._in = None

    def handle_data(self, data):
        if self._in == "title":
            self.title += data
        elif self._in == "h1":
            self.h1[-1] += data
        elif self._in == "ld":
            try:
                j = json.loads(data)
                self.jsonld += [x.get("@type") for x in (j if isinstance(j, list) else [j]) if isinstance(x, dict)]
            except Exception:
                self.jsonld.append("INVALID")
        elif not self._stack:
            s = data.strip()
            if s:
                self.text.append(s)


def pages():
    out = []
    for f in sorted(SITE.rglob("index.html")):
        rel = "/" + f.relative_to(SITE).parent.as_posix().strip(".")
        rel = "/" if rel in ("/", "/.") else rel.rstrip("/") + "/"
        html = f.read_text(encoding="utf-8")
        if 'http-equiv="refresh"' in html or rel == "/credits/":
            continue  # redirects carry no copy; /credits/ quotes Pexels titles and file names verbatim
        r = Reader()
        r.feed(html)
        out.append((rel, f, r, html))
    return out


def audit():
    if not SITE.exists():
        build()
    rows = []
    for rel, f, r, html in pages():
        rows.append({
            "page": rel, "title": r.title.strip(), "title_len": len(r.title.strip()),
            "desc_len": len(r.desc or ""), "desc_over_160": len(r.desc or "") > 160, "no_desc": r.desc is None,
            "h1": [h.strip() for h in r.h1], "h1_count": len(r.h1),
            "jsonld": r.jsonld, "videos": len(r.videos), "videos_without_poster": sum(1 for v in r.videos if not v["poster"]),
            "videos_autoplay": sum(1 for v in r.videos if v["autoplay"]),
            "imgs_without_alt": r.imgs_no_alt, "bytes": f.stat().st_size,
            "has_md_copy": (f.parent / "index.md").exists(),
        })
    smap = (SITE / "sitemap.xml").read_text(encoding="utf-8") if (SITE / "sitemap.xml").exists() else ""
    vids = sorted(((p.stat().st_size, p.name) for p in (SITE / "assets" / "video").glob("*.mp4")), reverse=True)
    out = {
        "day": date.today().isoformat(), "pages": len(rows),
        "sitemap_urls": smap.count("<loc>"), "sitemap_has_lastmod": "<lastmod>" in smap,
        "llms_txt": (SITE / "llms.txt").exists(), "llms_full_txt": (SITE / "llms-full.txt").exists(),
        "video_clips": len(vids), "video_mb": round(sum(s for s, _ in vids) / 1e6, 1),
        "largest_clips_mb": [(n, round(s / 1e6, 1)) for s, n in vids[:6]],
        "home_title_is_bare_name": next((r["title"] == "Arab American Instruments" for r in rows if r["page"] == "/"), None),
        "pages_without_jsonld": [r["page"] for r in rows if not r["jsonld"]],
        "pages_desc_over_160": [r["page"] for r in rows if r["desc_over_160"]],
        "pages_h1_not_one": [r["page"] for r in rows if r["h1_count"] != 1],
        "videos_without_poster": sum(r["videos_without_poster"] for r in rows),
        "rows": rows,
    }
    print(json.dumps(out, indent=1, ensure_ascii=False))


# ------------------------------------------------------------------ brand gate

BANNED = [
    # Umar's standing rules for AAI copy, 14 and 15 Nov 2026
    r"made to order", r"\bcustom\b", r"\bbespoke\b", r"\btailored\b", r"made for its owner",
    r"design house", r"hardware design company", r"world'?s first",
    r"\bdefen[cs]e\b", r"\bmilitary\b",
    r"\bnot a \w+ company", r"\bnot just\b", r"\bwe are not\b", r"\bnot an? \w+ (house|shop|vendor)",
    # competitors are never named in copy
    r"\banduril\b", r"\bsamsara\b", r"\bpalantir\b", r"\bspec ?5\b", r"\bbosch\b", r"\baxon\b",
    # internal names, parts and people never reach the public site
    r"\bdrive ?sense\b", r"\bVIM\b", r"\brk35\d\d\b", r"\bcm5\b", r"\bradxa\b", r"\brockchip\b", r"\bkhadas\b", r"\baffan\b",
    r"\bboards? at fab\b", r"\bin design\b", r"\bdesign complete\b", r"\breference concept\b",
    # numbers that describe a design, not an offering; and prices
    r"\b\d+\s*(cameras?|lenses|GB|MB|TB|TOPS|mAh|boards?|chips?|cores?|MP)\b", r"\$\s?\d", r"\bSAR\s?\d", r"\bUSD\b",
    r"\bpricing\b", r"\bper unit\b", r"\bper device\b",  # "no list price" is allowed copy; a figure is not
]
DASHES = [r"—", r"–", r"\s-\s"]


def visible_text(r, html):
    # title and description are copy too
    return "\n".join([r.title] + ([r.desc] if r.desc else []) + r.text)


def gate():
    """Exit 1 when the built site carries a banned word, a dash, a hyphenated word outside gate_allow.json,
    or a number that describes a design. Run by nightly_push.sh before every commit; a hit blocks the push."""
    build()
    allow = set(json.loads(ALLOW.read_text())) if ALLOW.exists() else set()
    hits = []
    for rel, f, r, html in pages():
        txt = visible_text(r, html)
        for pat in BANNED:
            for m in re.finditer(pat, txt, flags=re.I):
                hits.append({"page": rel, "rule": pat, "text": txt[max(0, m.start() - 40): m.end() + 40].replace("\n", " ")})
        for pat in DASHES:
            for m in re.finditer(pat, txt):
                hits.append({"page": rel, "rule": "dash", "text": txt[max(0, m.start() - 40): m.end() + 40].replace("\n", " ")})
        for m in re.finditer(r"\b[A-Za-z]+(?:-[A-Za-z]+)+\b", txt):
            if m.group(0) not in allow and m.group(0).lower() not in {a.lower() for a in allow}:
                hits.append({"page": rel, "rule": "hyphen", "text": txt[max(0, m.start() - 40): m.end() + 40].replace("\n", " ")})
    if hits:
        print(json.dumps({"gate": "FAIL", "hits": hits}, indent=1, ensure_ascii=False))
        sys.exit(1)
    print(json.dumps({"gate": "PASS", "pages": len(pages())}))


# ------------------------------------------------------------------ rotation and backlog

def rotate(n=2):
    """The inner pages to screenshot today: never seen first, then the longest unseen. Marks them seen.
    Prints a warning when the pace will not show every page inside a fortnight."""
    if not SITE.exists():
        build()
    d = load()
    seen = d.setdefault("seen", {})
    inner = [rel for rel, *_ in pages() if rel != "/"]
    today = date.today()
    def age(p):
        s = seen.get(p)
        return 10**6 if not s else (today - date.fromisoformat(s)).days
    inner.sort(key=lambda p: -age(p))
    picks = inner[:n]
    stale = [p for p in inner if age(p) > 14]
    for p in picks:
        seen[p] = today.isoformat()
    save(d)
    print(json.dumps({"day": today.isoformat(), "screenshot": ["/"] + picks, "stale_over_14_days": len(stale),
                      "advice": ("take 3 today" if len(stale) > 2 * n else "pace is fine")}))


def backlog(args):
    d = load()
    st = d.setdefault("backlog", {})
    if args and args[0] == "mark":
        _, bid, status, *note = args
        if bid not in {b for b, _ in BACKLOG}:
            sys.exit(f"unknown backlog id {bid}; ids: {[b for b, _ in BACKLOG]}")
        st[bid] = {"status": status, "day": date.today().isoformat(), "note": " ".join(note)}
        save(d)
    rows = [{"id": b, "item": t, **st.get(b, {"status": "open"})} for b, t in BACKLOG]
    nxt = [r["id"] for r in rows if r["status"] not in ("done", "blocked")][:2]
    print(json.dumps({"next": nxt, "items": rows}, indent=1))


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0] if a else "episode-template"
    if cmd == "episode-template":
        episode_template()
    elif cmd == "record-episode":
        record_episode(a[1])
    elif cmd == "feedback":
        feedback(a[1])
    elif cmd == "reward":
        reward(a[1])
    elif cmd == "lessons":
        lessons()
    elif cmd == "audit":
        audit()
    elif cmd == "gate":
        gate()
    elif cmd == "rotate":
        rotate(int(a[1]) if len(a) > 1 else 2)
    elif cmd == "backlog":
        backlog(a[1:])
    else:
        print(__doc__)
