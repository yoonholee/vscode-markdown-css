# Markdown CSS (single source of truth)

One public, standalone repo for how markdown looks on screen (VS Code preview) and in print (md-print).

## Look

![rendered sample](preview.png)

`fixtures/showcase.md` rendered through `tokens.css` + `preview.css`. Regenerate after any CSS change: `./render.py --readme`, then commit `preview.png`.

## Files

- `tokens.css` — shared house-style design tokens: palette (~85% black, grayscale, surgical Stanford red `#8c1515`) and font families (Source Serif/Tiempos titles, Source Sans body, Source Code mono). Source: vault `Personal/Personal Aesthetic.md`, `Concepts/Fonts.md`.
- `preview.css` — VS Code Markdown preview (screen): force light mode, rem sizes, vertical rhythm, hide the frontmatter table.
- `print.css` — `md-print` PDF (Chrome): `@page`, pt sizes, page-break control.
- `render.py` — render/check harness (see below). `fixtures/` — markdown corpus it renders.
- `agent_notes/` — `plan.md` (improvement backlog) and `lessons.md` (renderer gotchas).

`preview.css` and `print.css` both consume `tokens.css`'s `:root` variables. Change a color or font in `tokens.css` once and both media update. No `@import`: each consumer loads `tokens.css` as a separate stylesheet (CSS custom properties are global), which avoids webview/Chrome import-resolution issues.

## Verifying changes (`render.py`)

Self-contained reproduction + regression harness. Needs `pandoc`, Google Chrome, and `pdftoppm` (poppler) on PATH.

```
./render.py                # render every fixtures/*.md → out/<name>.preview.png + out/<name>.print-1.png
./render.py fixtures/x.md  # render one file
./render.py --check        # headless: assert HTML invariants; exit 1 on failure (CI-able)
./render.py --readme       # regenerate preview.png from fixtures/showcase.md
```

The two pipelines mirror the real consumers, so what you see in `out/` is what they produce: preview = pandoc (`gfm`) → `tokens.css`+`preview.css`, Chrome screenshot; print = pandoc (`gfm`) → `tokens.css`+`print.css`, Chrome `--print-to-pdf`. The pandoc reader is kept identical to md-print's `PANDOC_FORMAT`.

**To reproduce a rendering bug:** drop a minimal `.md` in `fixtures/`, run `./render.py`, look at `out/`. If it's structural/parsing, add an assertion to `CHECKS` in `render.py` and gate it with `--check`. `fixtures/regressions.md` already pins the cases that have bitten before (lists that interrupt a paragraph with no blank line, nesting, math, tables, task lists, autolinks).

## How each is wired

Standalone public repo, not tied to any vault.

- **Preview (global):** VS Code User-settings `markdown.styles` lists two jsdelivr URLs — `tokens.css` then `preview.css` — so the preview is styled in any folder. Edit here → push → purge jsdelivr (`curl https://purge.jsdelivr.net/gh/yoonholee/vscode-markdown-css@main/preview.css`) → bump the `?v=` in User settings so VS Code refetches → reopen preview.
- **Print (local):** `md-print.py` (`dotfiles/hosts/laptop/bin/`) passes `tokens.css` then `print.css` as two `--css` flags, read from a local clone at `~/repos/vscode-markdown-css` (override with `MD_CSS_DIR`). Edit → `md-print <file.md>` (offline; no CDN). Push to keep jsdelivr in sync for the preview.

After any change: `./render.py --check`, eyeball `out/` if needed, run `./render.py --readme`, commit.

## Wide tables (convention, not CSS)

A table wider than the text column overflows in print / scrolls in preview. That's allowed, but it usually means the data is the wrong shape. **Each table should use its width to make one point** — reshape it rather than shrinking the font or relying on scroll:

- **Transpose** (rows ↔ columns) when there are few entities and many attributes — the usual comparison/benchmark case. The "many" axis becomes the short one, so it fits, and you keep aligned column comparison.
- **Stack as labeled records** (one block per row: `Attr value · Attr value …`) when there are many entities — never overflows, reads as prose, but you lose column scanning.
- **Reduce scope / split** into multiple focused tables — a table rarely needs every column; show the few that support the claim and split the rest.

## History

Briefly went private (then a vault submodule), because making it private broke jsdelivr delivery — a local `markdown.styles` file only loads inside a workspace folder, so the CSS had to live in the vault. But it's just CSS for VS Code, nothing secret, so it went back to public repo + jsdelivr (global, least machinery) and decoupled from the vault. Earlier still, `print.css` lived in dotfiles with hardcoded Helvetica — drift from the house style, now folded onto `tokens.css`.
