#!/usr/bin/env bash
# Re-sync the latest scripts/projects into the repo and push the update.
# Use AFTER publish.sh has created the repo. Run from this folder:  bash update.sh
set -e

SRC="$HOME/jalmiburung/social-media"

echo "==> Re-syncing $SRC -> ./src (mirror, skipping heavy/generated files)"
mkdir -p src
rsync -a --delete \
  --exclude node_modules --exclude .venv --exclude out --exclude __pycache__ \
  --exclude '*.mp4' --exclude '*.mp3' --exclude '*.png' --exclude 'konawe_cues.json' \
  --exclude 'planet_konawe' --exclude 'planet_konawe_scenes.csv' \
  "$SRC"/ src/

echo "==> Re-adding Research paddy-decline scripts"
cp "$HOME/jalmiburung/Research/"paddy_*.py src/ 2>/dev/null || true
# training_points_*.csv intentionally NOT copied (kept private)

echo "==> Commit + push"
git add -A
git commit -m "Update: Konawe video (SIRAD, Neraca infographic, auto-sync cues), CRF render" || {
  echo "Nothing to commit."; exit 0; }
git push
echo "Done."
