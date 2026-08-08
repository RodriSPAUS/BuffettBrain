#!/usr/bin/env python3
"""What does a source talk about that the wiki never mentions?

`make quotes` proves that what a summary says is true. Nothing proved that a
summary said enough. The 1996 page passed every check while omitting USAir
entirely — 69 lines in which Buffett calls his own analysis of the airline
superficial and wrong — because no checker can know what a letter contains.

A checker cannot know, but it can compare. Take the proper nouns a source repeats
(a name mentioned four times is a subject, not an aside) and look for them
anywhere in the wiki. What is missing is what the corpus talks about and the
compiled knowledge does not.

This is deliberately medium-independent. It has no notion of letters, sections,
years or Berkshire: give it a conference-call transcript or a video transcript
and it works the same way, because "the names this source keeps repeating" is a
property of text, not of a genre. The heading extractor in `new_page.py` is the
opposite — tuned to two layouts of one document type — and that is a convenience,
not a design.

Reported as warnings. Some repeated names are genuinely disposable: a lawyer, a
street address, an auditor. A gate that forced every one of them into a summary
would produce pages that list everything and rank nothing, which is the failure
on the other side.

    python3 scripts/check_coverage.py                    # every source
    python3 scripts/check_coverage.py Sources/1996ltr    # one
"""

from __future__ import annotations

import collections
import re
import sys

from wikilib import RAW, WIKI, Report

# A name has to recur to count as a subject of the source.
MIN_MENTIONS = 4

# Words that begin a capitalised phrase without naming anything, plus the terms
# every source in this corpus repeats and no summary needs to prove it covered.
STOP = set(
    """The This That These Those There Then Their They We Our Us It Its His Her He She
    In On At For And But Or If As So To Of By With From When While After Before Since
    Now Also Not No Yes All Both Each Some Many Most Much More Less Last Next First
    January February March April May June July August September October November December
    Chairman Shareholders Shareholder Annual Report Letter Inc Corp Corporation Company
    Companies Total Net Year Years Table Source Note Page Dear Sincerely""".split()
)

# Capitalised runs: "USAir", "Nebraska Furniture Mart", "R. C. Willey".
PROPER = re.compile(r"\b([A-Z][a-zA-Z]{2,}(?:\s+[A-Z][a-zA-Z&.]{1,})*)\b")

# A capital that only ever follows a full stop is a sentence opener, not a name.
SENTENCE_START = re.compile(r"(?:^|[.!?:;]|\n)\s*$")


def subjects(text: str) -> dict[str, int]:
    """Names the source keeps returning to.

    Only mid-sentence occurrences count. The STOP list below catches the common
    sentence openers, but no list can be complete -- "Additionally" reached a
    report as a subject the wiki had failed to cover. A real name appears
    capitalised in the middle of sentences as well as at their start, whereas an
    adverb almost never does, so position separates them without maintenance.
    """
    counts = collections.Counter()
    for match in PROPER.finditer(text):
        name = match.group(1).strip()
        if len(name) < 4 or name.split()[0] in STOP:
            continue
        if SENTENCE_START.search(text[max(0, match.start() - 40): match.start()]):
            continue
        counts[name] += 1
    return {n: c for n, c in counts.items() if c >= MIN_MENTIONS}


def wiki_text(exclude: set[str]) -> str:
    """Everything the wiki says, minus its own bookkeeping."""
    parts = []
    for path in sorted(WIKI.rglob("*.md")):
        if path.stem in {"log", "SCHEMA"} or path.stem in exclude:
            continue
        parts.append(path.read_text(encoding="utf-8", errors="replace"))
    return " ".join(parts).lower()


def main() -> int:
    argv = [a for a in sys.argv[1:] if not a.startswith("-")]
    wanted = {a.split("/")[-1].removesuffix(".md") for a in argv}

    report = Report("check_coverage: what the sources say and the wiki does not")
    haystack = wiki_text(exclude=set())

    for raw in sorted(RAW.glob("*.md")):
        if wanted and raw.stem not in wanted:
            continue
        page = WIKI / "Sources" / f"{raw.stem}.md"
        if not page.exists():
            report.warn(f"{raw.stem}: no summary page")
            continue
        if "> TODO:" in page.read_text(encoding="utf-8", errors="replace"):
            continue

        found = subjects(raw.read_text(encoding="utf-8", errors="replace"))
        missing = {n: c for n, c in found.items() if n.lower() not in haystack}
        for name, count in sorted(missing.items(), key=lambda kv: -kv[1])[:6]:
            report.warn(
                f"{raw.stem}: mentions {name} {count} times; it appears nowhere in wiki/"
            )

    return report.finish(limit=60, warn_only=True)


if __name__ == "__main__":
    sys.exit(main())
