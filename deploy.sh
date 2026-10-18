#!/usr/bin/env bash
# Commit and push the rebuilt page; GitHub Pages updates in about a minute.
set -euo pipefail
cd "$(dirname "$0")"
# build_site.py skriver index.html forfra, så PER, AST/TO og TS% (kpi.js) sættes ind igen, hvis linket mangler.
grep -q 'src="kpi.js"' index.html || perl -0pi -e 's#</body>#<script src="kpi.js"></script>\n</body>#' index.html
git add -A
if git diff --cached --quiet; then echo "Ingen ændringer at udgive."; exit 0; fi
git commit -m "Opdatér stats ($(date +%Y-%m-%d))" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git push
echo "Udgivet: https://jacquesbie.github.io/d9-streetball/"
