#!/usr/bin/env python3
"""Check that every quotation in wiki/ appears verbatim in the Raw/ file it cites.

This is the check AGENT.md calls non-negotiable, turned into something that can
fail a build. A fabricated quotation is indistinguishable from a real one once
written, and propagates into every synthesis built on top of it — so the wiki is
only worth what this script says it is.

Three outcomes per quote:

  ok             the text is in the cited source
  MISATTRIBUTED  the text is real Buffett, but it is in a different letter
  UNSUPPORTED    the text is in no Raw/ file at all

MISATTRIBUTED is reported with the letter that actually contains the passage, so
fixing it is a one-word edit rather than an investigation.

Usage:
    python3 scripts/verify_quotes.py              # all pages
    python3 scripts/verify_quotes.py wiki/Concepts  # only these paths
    python3 scripts/verify_quotes.py --json       # machine-readable
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from wikilib import REPO, WIKI, Report, load_raw, normalize, raw_contains

# A quoted passage short enough to be a common phrase is not worth checking:
# "we believe" will match anything and proves nothing.
MIN_QUOTE = 30

# Quotes are cited either by a trailing [[Sources/X]] on the same line, or by the
# page's own identity when the page *is* the summary of that source.
CITATION = re.compile(r"\[\[Sources/([A-Za-z0-9]+)")

# Curly or straight double quotes, not spanning a line.
QUOTED = re.compile(r'["“]([^"”\n]{%d,})["”]' % MIN_QUOTE)

SOURCE_STEM = re.compile(r"^(?:19|20)\d\dltr$")


def fragments(quote: str) -> list[str]:
    """Split on ellipsis: an elided quote is several verbatim runs, not one."""
    parts = re.split(r"\.\.\.|…|\s\[\.\.\.\]\s", quote)
    return [p.strip() for p in parts if len(p.strip()) >= MIN_QUOTE]


def default_source(path: Path) -> str | None:
    """A Sources/ page implicitly cites its own letter."""
    if path.parent.name == "Sources":
        return path.stem
    return None


def collect(paths: list[Path]) -> list[dict]:
    findings = []
    raw = load_raw()
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        implicit = default_source(path)
        for lineno, line in enumerate(text.splitlines(), 1):
            for quote in QUOTED.findall(line):
                cited = CITATION.search(line)
                stem = cited.group(1) if cited else implicit
                if stem is None:
                    continue
                frags = fragments(quote)
                if not frags:
                    continue
                missing = [f for f in frags if not raw_contains(raw, stem, f)]
                if not missing:
                    continue
                elsewhere = sorted(
                    other
                    for other in raw
                    if other != stem
                    and all(raw_contains(raw, other, f) for f in frags)
                )
                findings.append(
                    {
                        "page": path.relative_to(REPO).as_posix(),
                        "line": lineno,
                        "cited": stem,
                        "quote": quote[:120],
                        "status": "MISATTRIBUTED" if elsewhere else "UNSUPPORTED",
                        "found_in": elsewhere,
                        "missing_fragment": missing[0][:120],
                    }
                )
    return findings


def target_pages(argv: list[str]) -> list[Path]:
    roots = [Path(a) for a in argv if not a.startswith("-")]
    if not roots:
        roots = [WIKI]
    pages: list[Path] = []
    for root in roots:
        root = root if root.is_absolute() else REPO / root
        pages.extend(sorted(root.rglob("*.md")) if root.is_dir() else [root])
    return [p for p in pages if p.stem not in {"log", "SCHEMA"}]


def main() -> int:
    argv = sys.argv[1:]
    findings = collect(target_pages(argv))

    if "--json" in argv:
        print(json.dumps(findings, indent=2, ensure_ascii=False))
        return 1 if findings else 0

    report = Report("verify_quotes: quotations vs Raw/")
    for f in sorted(findings, key=lambda f: (f["status"], f["page"], f["line"])):
        where = f" (verbatim in {', '.join(f['found_in'])})" if f["found_in"] else ""
        report.error(
            f"{f['page']}:{f['line']} cites {f['cited']}{where}\n"
            f"         {f['quote']}"
        )
    return report.finish(limit=60)


if __name__ == "__main__":
    sys.exit(main())
