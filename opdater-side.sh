#!/usr/bin/env bash
# Lægger Claudes ændringer (fantasy-siden, PER/AST-TO/TS% og highlights) på hjemmesiden og gør din d9-streetball-mappe
# klar, så build_site.py og ./deploy.sh virker som før bagefter. Kør det med én linje i Terminal:
#   curl -fsSL https://raw.githubusercontent.com/jacquesbie/d9-streetball/claude/friendly-euler-c7rzeb/opdater-side.sh | bash
# Alt ligger i main(), så bash har læst hele scriptet, før noget køres.

main() {
  local slug="jacquesbie/d9-streetball" branch="claude/friendly-euler-c7rzeb"
  local site="https://jacquesbie.github.io/d9-streetball"
  ok() { printf '   \033[32m✓\033[0m %s\n' "$*"; }
  step() { printf '\n\033[1m%s\033[0m\n' "$*"; }
  stop() { printf '\n\033[31mStop:\033[0m %s\n\nKopiér alt herover og send det til Claude.\n' "$*"; exit 1; }

  # Henter en gren ind i main. Står index.html i konflikt, er det din egen nyeste build, der beholdes.
  merge_in() {
    git merge -q --no-edit "$1" >/dev/null 2>&1 && return 0
    local files
    files=$(git diff --name-only --diff-filter=U)
    if [ "$files" = "index.html" ]; then
      git checkout -q --ours index.html && git add index.html && git commit -q --no-edit && return 0
    fi
    git merge --abort >/dev/null 2>&1
    stop "Ændringerne kunne ikke flettes automatisk (${files:-ukendt fejl})."
  }

  command -v git >/dev/null || stop "git findes ikke på din Mac."

  step "1/4  Finder din d9-streetball-mappe (det kan tage lidt tid)"
  local dir="" d url
  while IFS= read -r d; do
    d=${d%/.git}
    case "$d" in */d9-highlights) continue ;; esac
    url=$(git -C "$d" remote get-url origin 2>/dev/null) || continue
    case "$url" in *"$slug"*) ;; *) continue ;; esac
    [ -f "$d/deploy.sh" ] || continue
    dir=$d
    [ "$(git -C "$d" rev-parse --abbrev-ref HEAD 2>/dev/null)" = main ] && break
  done < <(find "$HOME" -maxdepth 5 \( -name Library -o -name .Trash -o -name node_modules \) -prune \
             -o -type d -name .git -print -prune 2>/dev/null)
  if [ -z "$dir" ]; then
    dir="$HOME/d9-streetball"
    [ -e "$dir" ] && stop "Fandt ingen d9-streetball-mappe med git, men $dir findes allerede."
    git clone -q "https://github.com/$slug.git" "$dir" || stop "Kunne ikke hente d9-streetball fra GitHub."
    ok "Fandt ingen, så jeg har hentet en ny kopi til $dir"
  else
    ok "$dir"
  fi
  cd "$dir" || stop "Kan ikke åbne $dir."

  step "2/4  Gemmer det, du ikke har udgivet endnu"
  if [ "$(git rev-parse --abbrev-ref HEAD)" != "main" ]; then
    [ -z "$(git status --porcelain)" ] || stop "Mappen er ikke på main og har ændringer, der ikke er gemt."
    git checkout -q main || stop "Kunne ikke skifte til main."
  fi
  if [ -n "$(git status --porcelain)" ]; then
    git add -A && git commit -q -m "Opdatér stats ($(date +%Y-%m-%d))" || stop "Kunne ikke gemme dine ændringer."
    ok "Din seneste build er gemt"
  else
    ok "Intet at gemme"
  fi

  step "3/4  Henter Claudes ændringer"
  git fetch -q origin main "$branch" || stop "Kunne ikke hente fra GitHub. Tjek internettet og prøv igen."
  merge_in origin/main
  merge_in "origin/$branch"
  if ! grep -q 'src="kpi.js"' index.html; then
    perl -0pi -e 's#</body>#<script src="kpi.js"></script>\n</body>#' index.html
    git commit -q -am "Sæt PER, AST/TO og TS% (kpi.js) ind på forsiden" || stop "Kunne ikke gemme linket til kpi.js."
  fi
  ok "Fantasy-siden, PER, AST/TO, TS% og highlights er hentet"

  step "4/4  Lægger det på hjemmesiden"
  git push -q origin main || stop "GitHub ville ikke tage imod ændringerne."
  ok "Sendt til GitHub"

  printf '\n\033[32mFærdig!\033[0m Om et par minutter kan du se det her:\n'
  printf '   Forsiden (PER, AST/TO og TS%% sidst i box score):  %s/\n' "$site"
  printf '   Fantasy:                                           %s/fantasy/\n' "$site"
  printf '\nFremover bygger og udgiver du som før med build_site.py og ./deploy.sh.\n'
}

main "$@"
