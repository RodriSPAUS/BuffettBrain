"""Shared helpers for the wiki lint scripts.

Stdlib only, so `make lint` works anywhere Python 3.9+ is installed.

The one piece of real logic here is `normalize()`. Raw/ letters are plain-text
extractions of Berkshire PDFs: they are hard-wrapped at ~100 columns, use curly
quotes and en/em dashes, and split words across lines with a hyphen. A quote
copied into the wiki is therefore almost never a byte-for-byte substring of the
source even when it is a perfectly faithful quotation. Normalizing both sides
the same way is what makes verbatim checking possible at all.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RAW = REPO / "Raw"
WIKI = REPO / "wiki"

# Directories inside wiki/ that hold agent-written pages.
PAGE_DIRS = [
    "Sources",
    "Concepts",
    "Applications",
    "Cases",
    "People",
    "Principles",
    "Synthesis",
]

# Pages that are navigation/meta rather than content.
META_PAGES = {"index", "log", "SCHEMA"}

_PUNCT_MAP = {
    "’": "'",
    "‘": "'",
    "“": '"',
    "”": '"',
    "–": "-",
    "—": "-",
    "…": "...",
    " ": " ",
    "­": "",
}


def normalize(text: str, *, join_hyphen: bool = True, drop_quotes: bool = True) -> str:
    """Fold away every difference that is presentation rather than wording.

    `join_hyphen` removes a hyphen that only exists because the PDF wrapped a
    word across two lines. `drop_quotes` ignores quote characters entirely, so
    `'record'` and `"record"` compare equal — the wiki routinely swaps them when
    nesting a quote inside a quote, and that is a typographic choice, not a
    misquotation.
    """
    text = unicodedata.normalize("NFKC", text)
    for src, dst in _PUNCT_MAP.items():
        text = text.replace(src, dst)
    if join_hyphen:
        text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    if drop_quotes:
        text = re.sub(r"[\"'`]", "", text)
    return text


def raw_variants(text: str) -> tuple[str, ...]:
    """Both readings of a line-wrapped hyphen: joined, and kept as a real hyphen.

    "much-\\nsought-after" is `much-sought-after` in the original; but
    "per-\\nshare" spans a word that genuinely has no hyphen in some letters.
    Checking against both readings avoids flagging correct quotes.
    """
    joined = normalize(text, join_hyphen=True)
    kept = normalize(re.sub(r"-\s*\n\s*", "-", text), join_hyphen=False)
    return (joined, kept) if joined != kept else (joined,)


def load_raw() -> dict[str, tuple[str, ...]]:
    """Map each Raw/ stem to its normalized readings."""
    out = {}
    for path in sorted(RAW.glob("*.md")):
        out[path.stem] = raw_variants(path.read_text(encoding="utf-8", errors="replace"))
    return out


def raw_contains(raw: dict[str, tuple[str, ...]], stem: str, fragment: str) -> bool:
    """Is `fragment` present in the letter `stem`, ignoring presentation?

    Both sides get both hyphen readings. Wiki pages are hard-wrapped just like
    the letters, so a compound may break across lines on one side and not the
    other: 'significantly-\\nundervalued' quoted from a source that reads
    'significantly-undervalued' on a single line is a faithful quotation, and
    normalizing only the haystack reports it as fabricated.
    """
    if stem not in raw:
        return False
    needles = raw_variants(fragment)
    return any(needle in variant for needle in needles for variant in raw[stem])


def load_pages() -> dict[str, Path]:
    """Map each wiki page name ('Concepts/Moat') to its path."""
    out = {}
    for path in sorted(WIKI.rglob("*.md")):
        out[path.relative_to(WIKI).with_suffix("").as_posix()] = path
    return out


WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")


def link_target(link: str) -> tuple[str, str]:
    """Split a wikilink body into (target, anchor), dropping any alias."""
    body = link.split("|")[0].strip()
    target, _, anchor = body.partition("#")
    return target.strip(), anchor.strip()


def split_frontmatter(text: str) -> tuple[str, str]:
    """Return (frontmatter, body). Frontmatter is '' when absent."""
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", text
    return text[3:end], text[end + 4 :]


def frontmatter_keys(fm: str) -> dict[str, str]:
    keys = {}
    for line in fm.splitlines():
        match = re.match(r"([A-Za-z_][\w-]*)\s*:(.*)", line)
        if match:
            keys[match.group(1)] = match.group(2).strip()
    return keys


class Report:
    """Collects findings so a script can print a summary and set an exit code."""

    def __init__(self, title: str):
        self.title = title
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def finish(self, *, limit: int = 40, warn_only: bool = False) -> int:
        print(f"== {self.title} ==")
        for label, items in (("ERROR", self.errors), ("warn", self.warnings)):
            for msg in items[:limit]:
                print(f"  {label}: {msg}")
            if len(items) > limit:
                print(f"  ... and {len(items) - limit} more {label}")
        if not self.errors and not self.warnings:
            print("  clean")
        print(f"  -> {len(self.errors)} errors, {len(self.warnings)} warnings\n")
        if self.errors and not warn_only:
            return 1
        return 0


def main_guard(fn):
    """Run `fn` and exit with its status."""
    if __name__ != "__main__":
        return fn
    sys.exit(fn())
