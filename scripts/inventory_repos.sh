#!/usr/bin/env bash
set -euo pipefail

BASE="$HOME/Projects/veloserve-ai"
REPOS="$BASE/repos"
OUT="$BASE/knowledge/repos/repos_inventory.md"

mkdir -p "$(dirname "$OUT")"

echo "# Veloserve Repository Inventory" > "$OUT"
echo "" >> "$OUT"
echo "Generated: $(date)" >> "$OUT"
echo "" >> "$OUT"

for repo in "$REPOS"/*; do
  [ -d "$repo/.git" ] || continue

  name=$(basename "$repo")
  echo "## $name" >> "$OUT"
  echo "" >> "$OUT"

  cd "$repo"

  echo "**Remote:** $(git remote get-url origin 2>/dev/null || echo unknown)" >> "$OUT"
  echo "" >> "$OUT"

  echo "**Default branch:** $(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@refs/remotes/origin/@@' || echo unknown)" >> "$OUT"
  echo "" >> "$OUT"

  echo "**Recent commits:**" >> "$OUT"
  git log --oneline -5 >> "$OUT" || true
  echo "" >> "$OUT"

  echo "**Detected files:**" >> "$OUT"
  find . -maxdepth 2 -type f \
    \( -name "package.json" -o -name "composer.json" -o -name "requirements.txt" -o -name "pyproject.toml" -o -name "Dockerfile" -o -name "docker-compose.yml" -o -name "go.mod" -o -name "Cargo.toml" -o -name "README.md" \) \
    | sort >> "$OUT"
  echo "" >> "$OUT"

  echo "**Top-level structure:**" >> "$OUT"
  find . -maxdepth 1 -mindepth 1 | sort | sed 's#^\./##' >> "$OUT"
  echo "" >> "$OUT"
done

echo "Inventory written to $OUT"
