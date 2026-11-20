#!/bin/sh
# Last action of every aai-site-daily run. Runs the brand gate on the freshly built site, commits the source
# (never site/, which GitHub Actions builds) and pushes main. Never force pushes, never rewrites history.
#   sh routine/nightly_push.sh "episode 3: structured data on every page"
cd "$(dirname "$0")/.." || exit 1
python3 routine/aai_daily.py gate >/tmp/aai_gate.json 2>&1 || { echo "GATE FAILED, NOTHING PUSHED:"; cat /tmp/aai_gate.json; exit 2; }
git add build.py assets routine README.md .gitignore .github 2>/dev/null
if git diff --cached --quiet; then echo "NOTHING TO PUSH"; exit 0; fi
git commit -q -m "${1:-aai-site-daily: routine update}" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" || { echo "COMMIT FAILED"; exit 3; }
git push -q origin main || { echo "PUSH FAILED (not forced; fix and push by hand)"; exit 4; }
echo "PUSHED $(git rev-parse --short HEAD)"
