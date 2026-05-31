#!/bin/sh
# Regenerate preview.png: render sample.md through tokens.css + preview.css (the
# VS Code screen path) and screenshot it with Chrome headless.
#
# Run this AFTER changing any CSS, and commit the updated preview.png so the repo's
# README always shows the current look. Needs: pandoc + Google Chrome.
set -eu

DIR="$(cd "$(dirname "$0")" && pwd)"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

pandoc "$DIR/sample.md" -f gfm -o "$TMP/body.html"
cat > "$TMP/preview.html" <<EOF
<!doctype html>
<html><head><meta charset="utf-8">
<link rel="stylesheet" href="file://$DIR/tokens.css">
<link rel="stylesheet" href="file://$DIR/preview.css">
</head><body class="vscode-body">
$(cat "$TMP/body.html")
</body></html>
EOF

"$CHROME" --headless=new --disable-gpu --hide-scrollbars \
  --default-background-color=ffffffff --window-size=860,1500 \
  --screenshot="$DIR/preview.png" "file://$TMP/preview.html" >/dev/null 2>&1

echo "wrote $DIR/preview.png"
