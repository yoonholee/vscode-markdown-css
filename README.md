# Markdown CSS (single source of truth)

One place for how vault markdown looks, on screen and in print. Tracked in the (private) vault repo.

## Files

- `tokens.css` — shared house-style design tokens: palette (~85% black, grayscale, surgical Stanford red `#8c1515`) and font families (Source Serif/Tiempos titles, Source Sans body, Source Code mono). Source: `Personal/Personal Aesthetic.md`, `Concepts/Fonts.md`.
- `preview.css` — VS Code Markdown preview (screen): force light mode, rem sizes, vertical rhythm, hide the frontmatter table.
- `print.css` — `md-print` PDF (Chrome): `@page`, pt sizes, page-break control.

`preview.css` and `print.css` both consume `tokens.css`'s `:root` variables. Change a color or font in `tokens.css` once and both media update. No `@import`: each consumer loads `tokens.css` as a separate stylesheet (CSS custom properties are global), which avoids webview/Chrome import-resolution issues.

## How each is wired

- **Preview:** vault `.vscode/settings.json` → `"markdown.styles": ["assets/css/tokens.css", "assets/css/preview.css"]`. VS Code only loads a local `markdown.styles` file that sits inside a workspace folder, so it lives here in the vault. Edit a file → reload the VS Code window (`Developer: Reload Window`) → reopen preview.
- **Print:** `md-print.py` (`dotfiles/hosts/laptop/bin/`) passes both files as `--css` (`tokens.css` then `print.css`), resolved from `~/repos/vault/assets/css/` (override with `VAULT_CSS_DIR`). Edit → `md-print <file.md>`.

## History

Replaced a public `vscode-md-preview-light` GitHub repo served via jsdelivr CDN (User-settings `markdown.styles`). jsdelivr only serves public repos, so making it private forced moving the CSS in-vault. That old repo is now private and superseded (safe to delete). print.css previously lived in dotfiles with hardcoded Helvetica — drift from the house style, now folded onto `tokens.css`.
