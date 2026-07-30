#!/usr/bin/env python3
"""Find a citable passage in Raw/ and print it ready to paste into the wiki.

Writing a page means quoting the letters, and the letters are hard-wrapped at
about 100 columns with words hyphenated across the break. Copying a sentence out
of `grep` output therefore produces something that looks right and fails
verify_quotes, which is the friction that pushes an agent toward writing the
quote from memory instead. This closes that gap: search by phrase, get back the
unwrapped sentence and the wikilink that cites it.

    python3 scripts/quote.py "circle of competence"
    python3 scripts/quote.py --year 1996 "circle of competence"
    python3 scripts/quote.py --context 2 "margin of safety"

Matching ignores line wrapping, curly quotes and dashes, so the phrase you
remember will find the sentence as printed.
"""

from __future__ import annotations

import argparse
import re
import sys

from wikilib import RAW, normalize

# Titles and abbreviations that end in a period without ending a sentence.
# Without this, "Mr. Market" is split in two and searching for it finds nothing —
# in a corpus where he is the most quoted character in the whole collection.
ABBREVIATIONS = r"Mr|Mrs|Ms|Dr|St|Jr|Sr|Inc|Co|Corp|Ltd|No|vs|approx|Rev|Gen|Prof"

SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z“\"])")
ENDS_IN_ABBREVIATION = re.compile(rf"(?:\b(?:{ABBREVIATIONS})|\b[A-Z])\.$")


def unwrap(text: str) -> str:
    """Undo the PDF's hard wrapping so sentences read as one line.

    A hyphen at end of line is kept. In this corpus it is nearly always a real
    compound — "capital-\\nallocation", "per-\\nshare", "vice-\\nchairman" — and
    dropping it would print "muchsought-after" where the letter says
    "much-sought-after". True syllable breaks ("charac-\\nteristics") do occur
    and come out wrong, which is why verify_quotes accepts either reading.
    """
    text = re.sub(r"-\s*\n\s*", "-", text)
    text = re.sub(r"\s*\n\s*", " ", text)
    return re.sub(r" {2,}", " ", text).strip()


def sentences(text: str) -> list[str]:
    """Split into sentences, rejoining across abbreviations and initials.

    A naive split puts "Mr." and "Market" in different sentences, and the most
    quoted character in the corpus becomes unsearchable. The same goes for
    "Warren E. Buffett" and "Scott Fetzer Co."
    """
    out: list[str] = []
    for part in SENTENCE_END.split(unwrap(text)):
        part = part.strip()
        if not part:
            continue
        if out and ENDS_IN_ABBREVIATION.search(out[-1]):
            out[-1] = f"{out[-1]} {part}"
        else:
            out.append(part)
    return out


def search(phrase: str, year: str | None, context: int) -> list[tuple[str, str]]:
    needle = normalize(phrase)
    hits = []
    for path in sorted(RAW.glob("*.md")):
        if year and not path.stem.startswith(year):
            continue
        parts = sentences(path.read_text(encoding="utf-8", errors="replace"))
        for i, sentence in enumerate(parts):
            if needle in normalize(sentence):
                lo, hi = max(0, i - context), min(len(parts), i + context + 1)
                hits.append((path.stem, " ".join(parts[lo:hi])))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phrase")
    parser.add_argument("--year", help="restrict to one letter, e.g. 1996")
    parser.add_argument(
        "--context", type=int, default=0, help="sentences either side to include"
    )
    args = parser.parse_args()

    hits = search(args.phrase, args.year, args.context)
    if not hits:
        print(f'no passage in Raw/ contains "{args.phrase}"')
        print("If the wiki cites this as a quotation, that citation is unsupported.")
        return 1

    for stem, passage in hits:
        print(f"[[Sources/{stem}]]")
        print(f'  "{passage}"')
        print()
    print(f"{len(hits)} passage(s) in {len({s for s, _ in hits})} letter(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
