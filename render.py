#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Render + check harness for this repo's markdown CSS. Self-contained: needs only
pandoc, Google Chrome, and pdftoppm (poppler) on PATH.

  ./render.py                  render every fixtures/*.md to out/<name>.preview.png and
                               out/<name>.print-1.png (and .print.pdf) so you can eyeball both media
  ./render.py fixtures/x.md    render one file (or any .md path)
  ./render.py --readme         regenerate the committed README image (preview.png) from fixtures/showcase.md
  ./render.py --check          headless: assert structural invariants on the rendered HTML; exit 1 on failure

How to reproduce a rendering bug: drop a minimal .md in fixtures/, run ./render.py, look at
out/. If it's a structural/parsing issue, add an assertion to CHECKS and run ./render.py --check.

Pipelines mirror the real consumers (so what you see here is what they produce):
  preview = pandoc (READER) -> HTML + tokens.css + preview.css, screenshotted by Chrome  (~= VS Code preview)
  print   = pandoc (READER) -> HTML + tokens.css + print.css, Chrome --print-to-pdf       (= md-print)
READER is kept identical to md-print's PANDOC_FORMAT; bump both together.
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"
OUT = ROOT / "out"
READER = "gfm+tex_math_dollars"  # keep in sync with md-print's PANDOC_FORMAT
MATHJAX = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg-full.js"
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def sh(*args: str) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def to_html_body(md: Path) -> str:
    return sh("pandoc", str(md), "-f", READER, "-t", "html")


def page(body: str, css: list[str], body_class: str = "", mathjax: bool = False) -> str:
    links = "\n".join(f'<link rel="stylesheet" href="{(ROOT / c).as_uri()}">' for c in css)
    mj = f'<script src="{MATHJAX}"></script>' if mathjax else ""
    return (
        f'<!doctype html><html><head><meta charset="utf-8">{links}{mj}</head>'
        f'<body class="{body_class}">{body}</body></html>'
    )


def _chrome(html: str, *flags: str) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html)
        path = f.name
    try:
        sh(
            CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--default-background-color=ffffffff", *flags, f"file://{path}",
        )
    finally:
        os.unlink(path)


def render(md: Path) -> None:
    OUT.mkdir(exist_ok=True)
    body = to_html_body(md)
    has_math = 'class="math' in body
    name = md.stem

    preview_png = OUT / f"{name}.preview.png"
    _chrome(page(body, ["tokens.css", "preview.css"], "vscode-body"),
            "--window-size=860,1600", f"--screenshot={preview_png}")

    pdf = OUT / f"{name}.print.pdf"
    flags = [f"--print-to-pdf={pdf}", "--no-pdf-header-footer"]
    if has_math:  # let MathJax typeset before the snapshot (mirrors md-print)
        flags += ["--run-all-compositor-stages-before-draw", "--virtual-time-budget=10000"]
    _chrome(page(body, ["tokens.css", "print.css"], mathjax=has_math), *flags)
    sh("pdftoppm", "-png", "-r", "110", "-f", "1", "-l", "1", str(pdf), str(OUT / f"{name}.print"))
    print(f"  {name}: out/{name}.preview.png  out/{name}.print-1.png")


# (fixture stem, [substrings that MUST appear], [substrings that must NOT appear])
CHECKS = [
    ("regressions",
     ['<ul>', '<ol', '<table>', 'class="math inline"', 'class="math display"',
      'type="checkbox"', '<del>', 'href="https://example.com'],
     ['Mechanism / understand them - Deepest pain']),  # list must not collapse to a paragraph
    ("showcase", ['<table>', '<ul>', 'type="checkbox"'], []),
]


def check() -> int:
    import re
    failures = []
    for stem, must, must_not in CHECKS:
        html = re.sub(r"\s+", " ", to_html_body(FIXTURES / f"{stem}.md"))  # normalize pandoc line-wraps
        for s in must:
            if s not in html:
                failures.append(f"{stem}.md: missing {s!r}")
        for s in must_not:
            if s in html:
                failures.append(f"{stem}.md: found forbidden {s!r}")
    # the original bug, asserted precisely: the no-blank-line list is a real list
    reg = to_html_body(FIXTURES / "regressions.md")
    if reg.count("<li>") < 3:
        failures.append("regressions.md: list-without-blank-line did not produce list items")
    for f in failures:
        print("FAIL:", f, file=sys.stderr)
    print(f"{'FAILED' if failures else 'OK'}: {len(CHECKS)} fixtures checked", file=sys.stderr)
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*", help="markdown files to render (default: fixtures/*.md)")
    ap.add_argument("--check", action="store_true", help="assert HTML invariants; exit 1 on failure")
    ap.add_argument("--readme", action="store_true", help="regenerate preview.png from fixtures/showcase.md")
    args = ap.parse_args()

    if args.check:
        return check()
    if args.readme:
        render(FIXTURES / "showcase.md")
        import shutil
        shutil.copy(OUT / "showcase.preview.png", ROOT / "preview.png")
        print("updated preview.png")
        return 0

    targets = [Path(p) for p in args.paths] if args.paths else sorted(FIXTURES.glob("*.md"))
    print(f"rendering {len(targets)} fixture(s) to out/")
    for md in targets:
        render(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
