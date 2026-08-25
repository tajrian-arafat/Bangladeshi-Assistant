#!/usr/bin/env python3
"""Generate PDF from the architecture markdown document."""

from __future__ import annotations

import sys
from pathlib import Path

import markdown
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "docs" / "architecture" / "bangladesh-digital-assistant-architecture.md"
PDF_PATH = ROOT / "docs" / "architecture" / "bangladesh-digital-assistant-architecture.pdf"

CSS = """
@page {
  size: A4;
  margin: 2cm 1.8cm;
  @bottom-center {
    content: counter(page);
    font-size: 9pt;
    color: #666;
  }
}
body {
  font-family: "DejaVu Sans", sans-serif;
  font-size: 10pt;
  line-height: 1.45;
  color: #1a1a1a;
}
h1 {
  font-size: 20pt;
  border-bottom: 2px solid #0d47a1;
  padding-bottom: 0.3em;
  page-break-before: always;
}
h1:first-of-type {
  page-break-before: avoid;
}
h2 {
  font-size: 14pt;
  color: #0d47a1;
  margin-top: 1.2em;
  page-break-after: avoid;
}
h3 {
  font-size: 11pt;
  page-break-after: avoid;
}
code, pre {
  font-family: "DejaVu Sans Mono", monospace;
  font-size: 8.5pt;
}
pre {
  background: #f5f5f5;
  border: 1px solid #ddd;
  padding: 0.6em;
  overflow-wrap: break-word;
  white-space: pre-wrap;
}
code {
  background: #f0f0f0;
  padding: 0.1em 0.25em;
}
table {
  border-collapse: collapse;
  width: 100%;
  margin: 0.8em 0;
  font-size: 9pt;
}
th, td {
  border: 1px solid #ccc;
  padding: 0.35em 0.5em;
  vertical-align: top;
}
th {
  background: #e3f2fd;
}
hr {
  border: none;
  border-top: 1px solid #ccc;
  margin: 1.5em 0;
}
ul, ol {
  padding-left: 1.4em;
}
a {
  color: #1565c0;
  text-decoration: none;
}
.cover-meta {
  color: #555;
  font-size: 10pt;
  margin-bottom: 2em;
}
"""


def main() -> int:
    if not MD_PATH.exists():
        print(f"Missing markdown file: {MD_PATH}", file=sys.stderr)
        return 1

    md_text = MD_PATH.read_text(encoding="utf-8")
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "toc", "sane_lists"],
    )

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Bangladesh Digital Assistant Architecture</title>
  <style>{CSS}</style>
</head>
<body>
{html_body}
</body>
</html>"""

    PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_doc, base_url=str(MD_PATH.parent)).write_pdf(str(PDF_PATH))
    print(f"Wrote {PDF_PATH} ({PDF_PATH.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
