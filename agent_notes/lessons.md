# Lessons — consumer-side knowledge (VS Code preview + md-print)

Hard-won facts about the two renderers. The CSS is simple; the delivery is where the traps are.

## VS Code Markdown preview

The preview is VS Code's **built-in** Markdown preview (opened via the `preview-to-side` extension → `markdown.showPreviewToSide`), a Chromium webview. NOT Obsidian — `.obsidian/` changes do nothing.
Styling comes from the `markdown.styles` setting. A local file there loads **only if it sits inside a workspace folder** (verified in VS Code's `localResourceRoots`: it adds the workspace folders, else the previewed doc's own dir). That is why the CSS lives in the vault, not an outside clone, and why jsdelivr (public-only) was dropped when the repo went private.
`markdown.styles` arrays do **NOT merge**: a workspace-level entry fully REPLACES the user-level one. (A workspace `display:none`-only CSS once dropped the user's light theme → whole preview went dark.) The User-settings note "absolute paths don't work" is wrong; the real rule is "must be under a workspace folder."
VS Code renders YAML frontmatter as `table.frontmatter` (class is in VS Code's shipped `markdown-language-features/media/markdown.css`); we hide it in preview.css. A markdown-it override in an extension does NOT work: VS Code registers its own `front_matter` rule `before("fence")` and re-sets the renderer after `extendMarkdownIt`, so an override loses. Print doesn't rely on this — md-print strips frontmatter in Python.
Forcing light mode is whack-a-mole: preview.css overrides `.vscode-dark <tag>`, but VS Code injects per-token inline colors for fenced code (the syntax highlighter) that win over `code{}` rules, and elements like `hr`/selection/scrollbars leak. Set a light editor theme, or neutralize syntax tokens, for full coverage.

## md-print (PDF)

Pipeline: pandoc markdown → standalone HTML (MathJax SVG for math, vendored locally) → Chrome headless `--print-to-pdf`, US letter. `tokens.css` + `print.css` passed as two `--css` flags from `$VAULT_CSS_DIR` (default `~/repos/vault/assets/css`).
Chrome `--print-to-pdf` **drops `background` by default** — need `print-color-adjust: exact` for header/code fills to appear. (Borders survive; backgrounds don't.)
A PDF embeds whatever font resolved; substitution is invisible to the reader and changes pagination, which feeds md-print's `--agent` orphan/page-fit introspection. So font determinism matters more for print than screen.
md-print guards a missing/uninitialized submodule with a clear error; VS Code preview does not (it silently renders unstyled). After a fresh clone: `git submodule update --init`.

## Fonts (this machine, fc-list verified 2026-05-30)

Installed: Tiempos Headline, Source Serif 4, Source Sans 3, MonoLisa.
**NOT installed: Source Code Pro** — the named first choice of `--font-mono`. Code silently renders in the paid MonoLisa fallback, not the intended free font. The fallback chain is "working" by accident.

## Verify the real render, not a replica

When changing how something renders in VS Code or Chrome, observe the actual output (open the preview HTML / the PDF), not a hand-built markdown-it stand-in. A replica that shares your assumption can't falsify it. (Three preview "fixes" shipped wrong this way before the cause was found by reading VS Code's actual bundled code.)
