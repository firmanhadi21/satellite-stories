#!/usr/bin/env bash
# Assemble the repo from your working scripts and publish it to GitHub.
# Run from this folder:  bash publish.sh
set -e

REPO_NAME="satellite-stories"            # change for a different repo name
SRC="$HOME/jalmiburung/social-media"     # where the working scripts + remotion project live

echo "==> Copying scripts from $SRC into ./src (skipping heavy/generated files)"
mkdir -p src
rsync -a \
  --exclude node_modules --exclude .venv --exclude out --exclude __pycache__ \
  --exclude '*.mp4' --exclude '*.mp3' --exclude '*.png' \
  "$SRC"/ src/

echo "==> Adding Research paddy-decline scripts"
cp "$HOME/jalmiburung/Research/"paddy_*.py src/ 2>/dev/null || true
# NOTE: training_points_random_java.csv is NOT copied (data stays private by default).
# To make paddy_classification_gee.py runnable here, copy it yourself into src/.

echo "==> git init + commit"
git init -q
git branch -M main
git add .
git commit -q -m "Satellite Stories: remote-sensing analysis -> narrated video pipeline"

echo "==> Creating GitHub repo and pushing (requires: gh auth login)"
if command -v gh >/dev/null 2>&1; then
  gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
  echo "Done -> https://github.com/$(gh api user -q .login)/$REPO_NAME"
else
  echo "gh CLI not found. Create the repo manually on github.com, then:"
  echo "  git remote add origin git@github.com:<you>/$REPO_NAME.git"
  echo "  git push -u origin main"
fi
