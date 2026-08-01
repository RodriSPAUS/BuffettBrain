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

# Quotes are cited either by a [[Sources/X]] link in the same block, or by the
# page's own identity when the page *is* the summary of that source.
CITATION = re.compile(r"\[\[Sources/([A-Za-z0-9]+)")

# Curly or straight double quotes. This deliberately spans newlines: wiki pages
# are wrapped at ~80 columns, so most real quotations run over two or three lines
# and an anchored-to-one-line pattern silently skipped 53% of them.
#
# The span is unbounded rather than {MIN_QUOTE,}: a length floor inside the
# pattern makes a short quotation skip its own closing mark and swallow the prose
# up to the next one, which desynchronizes every pair after it. Match all of
# them, discard the short ones afterwards.
QUOTED = re.compile(r'["“]([^"”]*?)["”]', re.S)

# A wrapped blockquote carries '> ' on every continuation line, inside the span.
# Only that: a bullet's '- ' sits before the opening quote and never lands inside
# one, whereas Buffett's dashes routinely start a wrapped line ("the managerial
# superstars\n- men who can recognize..."), so stripping list markers here would
# delete real words.
MARKUP = re.compile(r"^[ \t]*(?:>[ \t]*)+", re.M)

SOURCE_STEM = re.compile(r"^(?:19|20)\d\dltr$")

# Regions whose quote characters are not quotations: YAML frontmatter, fenced
# code, and inline code spans. A delegated model once documented its own
# verification as *Verified via `make quote Q=\"…\"`* and the escaped quotes
# inside those backticks were reported as four fabricated citations.
FENCE = re.compile(r"^```.*?^```", re.S | re.M)
INLINE_CODE = re.compile(r"`[^`\n]*`")
FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)


def blank(text: str, pattern: re.Pattern) -> str:
    """Erase matches but keep every character position, so line numbers hold."""
    return pattern.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def scannable(text: str) -> str:
    for pattern in (FRONTMATTER, FENCE, INLINE_CODE):
        text = blank(text, pattern)
    return text.replace('\\"', "  ")


def fragments(quote: str) -> list[str]:
    """Split on ellipsis: an elided quote is several verbatim runs, not one."""
    parts = re.split(r"\.\.\.|…|\s\[\.\.\.\]\s", quote)
    return [p.strip() for p in parts if len(p.strip()) >= MIN_QUOTE]


def default_source(path: Path) -> str | None:
    """A Sources/ page implicitly cites its own letter."""
    if path.parent.name == "Sources":
        return path.stem
    return None


def strip_markup(quote: str) -> str:
    """Drop the markup a wrapped quotation carries on its continuation lines.

    Line breaks are kept: normalize() rejoins a word the wiki wrapped with a
    hyphen ("significantly-\\nundervalued") and needs the newline to see it.
    Collapsing whitespace here turns a faithful quote into a false failure.
    """
    return MARKUP.sub("", quote)


def oneline(text: str) -> str:
    return " ".join(text.split())


def cited_source(text: str, start: int, end: int, implicit: str | None) -> str | None:
    """Which letter does this quote claim to come from?

    The convention is a trailing [[Sources/X]] immediately after the quote, so
    only the remainder of the quote's last line counts as an explicit citation —
    on a Sources/ page the surrounding prose is full of cross-references to other
    letters, and reading those as citations attributes the page's own quotations
    to whichever letter it happens to mention next.
    """
    line_end = text.find("\n", end)
    trailing = CITATION.search(text, end, len(text) if line_end == -1 else line_end)
    if trailing:
        return trailing.group(1)
    if implicit:
        return implicit
    # No page identity to fall back on (Concepts/, Cases/, ...): accept a lead-in
    # citation earlier in the same block.
    left = text.rfind("\n\n", 0, start)
    last = None
    for match in CITATION.finditer(text[0 if left == -1 else left + 2 : start]):
        last = match
    return last.group(1) if last else None


def collect(paths: list[Path]) -> list[dict]:
    findings = []
    raw = load_raw()
    for path in paths:
        text = scannable(path.read_text(encoding="utf-8", errors="replace"))
        implicit = default_source(path)
        for match in QUOTED.finditer(text):
            quote = match.group(1)
            # A span crossing a blank line is not a quotation; it is the fallout
            # of an unbalanced quote character somewhere above.
            if "\n\n" in quote:
                continue
            quote = strip_markup(quote)
            if len(oneline(quote)) < MIN_QUOTE:
                continue
            stem = cited_source(text, match.start(), match.end(), implicit)
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
                    "line": text.count("\n", 0, match.start()) + 1,
                    "cited": stem,
                    "quote": oneline(quote)[:120],
                    "status": "MISATTRIBUTED" if elsewhere else "UNSUPPORTED",
                    "found_in": elsewhere,
                    "missing_fragment": oneline(missing[0])[:120],
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
