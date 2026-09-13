#!/usr/bin/env python3
"""Regenerate project-status.html from the status markdown docs.

Living status dashboard: run this whenever the status docs change (or wire it
into the post-commit hook). Source of truth stays CURRENT_STATUS.md and
VERIFIED_STATUS.md — this only renders them into one styled, self-contained page
with a header showing the current git commit and generation time.

    python tools/gen_status.py

ponytail: hand-rolled ~70-line markdown subset (headings, lists, tables, fenced
code, bold, inline code, links, hr, paragraphs). No nested lists / blockquotes /
images — the two source docs don't use them. If they start to, swap this for the
`markdown` package (one import, one call).
"""
import html
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ["CURRENT_STATUS.md", "VERIFIED_STATUS.md"]
OUT = ROOT / "project-status.html"


def md_to_html(md: str) -> str:
    lines = md.splitlines()
    out, i, n = [], 0, len(lines)

    def inline(t: str) -> str:
        t = html.escape(t)
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
        return t

    while i < n:
        line = lines[i]

        if line.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].startswith("```"):
                buf.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            continue

        m = re.match(r"(#{1,6})\s+(.*)", line)
        if m:
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1
            continue

        if re.match(r"\s*[-*]\s+", line):
            out.append("<ul>")
            while i < n and re.match(r"\s*[-*]\s+", lines[i]):
                out.append("<li>" + inline(re.sub(r"\s*[-*]\s+", "", lines[i], count=1)) + "</li>")
                i += 1
            out.append("</ul>")
            continue

        if line.lstrip().startswith("|") and i + 1 < n and re.match(r"\s*\|[-\s|:]+\|\s*$", lines[i + 1]):
            def cells(row):
                return [c.strip() for c in row.strip().strip("|").split("|")]
            head = cells(line)
            i += 2
            rows = []
            while i < n and lines[i].lstrip().startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            out.append("<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>")
            for r in rows:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            out.append("</tbody></table>")
            continue

        if re.match(r"\s*(-{3,}|\*{3,})\s*$", line):
            out.append("<hr>")
            i += 1
            continue

        if line.strip() == "":
            i += 1
            continue

        para = [line]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"(#{1,6}\s|```|\s*[-*]\s+|\s*\|)", lines[i]):
            para.append(lines[i])
            i += 1
        out.append("<p>" + inline(" ".join(para)) + "</p>")

    return "\n".join(out)


def git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def main() -> int:
    sections = []
    for name in SOURCES:
        p = ROOT / name
        if not p.exists():
            print(f"skip (missing): {name}", file=sys.stderr)
            continue
        sections.append(f'<section><div class="src">{name}</div>{md_to_html(p.read_text(encoding="utf-8"))}</section>')

    if not sections:
        print("No source docs found — nothing to generate.", file=sys.stderr)
        return 1

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    branch, sha, subject = git("rev-parse", "--abbrev-ref", "HEAD"), git("rev-parse", "--short", "HEAD"), git("log", "-1", "--pretty=%s")

    page = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>FinFlow — Project Status</title>
<style>
:root {{ color-scheme: light dark; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font: 15px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: #0b1120; color: #e2e8f0; }}
.wrap {{ max-width: 860px; margin: 0 auto; padding: 32px 20px 80px; }}
header {{ border-bottom: 1px solid #1e293b; padding-bottom: 20px; margin-bottom: 8px; }}
h1 {{ margin: 0 0 4px; font-size: 26px; }}
.meta {{ color: #94a3b8; font-size: 13px; }}
.meta code {{ background: #1e293b; padding: 1px 6px; border-radius: 4px; }}
section {{ border-top: 1px solid #1e293b; padding-top: 8px; margin-top: 32px; }}
.src {{ display: inline-block; font-size: 11px; letter-spacing: .08em; text-transform: uppercase;
  color: #64748b; background: #131c2e; border: 1px solid #1e293b; border-radius: 999px; padding: 3px 10px; margin-bottom: 8px; }}
h2 {{ font-size: 20px; margin: 28px 0 8px; }}
h3 {{ font-size: 16px; margin: 20px 0 6px; color: #cbd5e1; }}
ul {{ padding-left: 22px; }}
li {{ margin: 3px 0; }}
code {{ background: #1e293b; padding: 1px 5px; border-radius: 4px; font-size: 13px; }}
pre {{ background: #131c2e; border: 1px solid #1e293b; border-radius: 8px; padding: 12px 14px; overflow-x: auto; }}
pre code {{ background: none; padding: 0; }}
a {{ color: #7dd3fc; }}
table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 14px; }}
th, td {{ border: 1px solid #1e293b; padding: 6px 10px; text-align: left; }}
th {{ background: #131c2e; }}
hr {{ border: 0; border-top: 1px solid #1e293b; margin: 24px 0; }}
@media (prefers-color-scheme: light) {{
  body {{ background: #f8fafc; color: #0f172a; }}
  header, section {{ border-color: #e2e8f0; }}
  .meta {{ color: #475569; }} .meta code, code, th {{ background: #e2e8f0; }}
  pre, .src {{ background: #f1f5f9; border-color: #e2e8f0; }}
  h3 {{ color: #334155; }} a {{ color: #0369a1; }}
  th, td, hr {{ border-color: #e2e8f0; }}
}}
</style></head><body><div class="wrap">
<header>
<h1>FinFlow — Project Status</h1>
<div class="meta">Generated {generated} &middot; branch <code>{html.escape(branch)}</code> &middot;
commit <code>{html.escape(sha)}</code> &middot; {html.escape(subject)}</div>
</header>
{''.join(sections)}
</div></body></html>
"""
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(page):,} bytes) from {len(sections)} doc(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
