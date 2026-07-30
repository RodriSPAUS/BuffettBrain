#!/usr/bin/env python3
"""Quality gate on Raw/: refuse source text that cannot be quoted from.

Several letters in this collection were extracted from PDF with the spaces
dropped, producing lines like

    Berkshire'sgaininnetworthduring2013was$34.2billion.

No agent can quote verbatim from that, so it reconstructs the passage from
memory instead — which is exactly how fabricated citations get into the wiki.
Bad extraction upstream is therefore a citation-integrity problem, not a
cosmetic one, and it belongs in the same lint run.

The signal is mean word length. English prose runs ~4.8 characters per word;
glued text runs 7+. Numeric tables are excluded, since a table of returns is
legitimately full of long digit runs.
"""

from __future__ import annotations

import re
import sys

from wikilib import RAW, Report

# Above this, the file has lost word boundaries.
MEAN_WORD_LIMIT = 6.0
# Runs of glued words per 1000 characters, as a second, independent signal.
GLUE_LIMIT = 1.0


def measure(text: str) -> tuple[float, float, int]:
    # Drop the performance tables: dotted leaders and digit columns skew length.
    prose = "\n".join(
        line
        for line in text.splitlines()
        if "...." not in line and len(re.findall(r"[A-Za-z]", line)) > 20
    )
    words = re.findall(r"[A-Za-z][A-Za-z'’]*", prose)
    if not words:
        return 0.0, 0.0, 0
    mean = sum(len(w) for w in words) / len(words)
    # A lowercase letter immediately followed by an uppercase one inside a token
    # is the fingerprint of two words with the space removed.
    glued = len(re.findall(r"[a-z][A-Z]", prose))
    density = 1000 * glued / max(len(prose), 1)
    return mean, density, len([w for w in words if len(w) > 15])


def main() -> int:
    report = Report("check_raw_quality: source extraction quality")
    for path in sorted(RAW.glob("*.md")):
        mean, density, long_words = measure(path.read_text(encoding="utf-8", errors="replace"))
        if mean > MEAN_WORD_LIMIT or density > GLUE_LIMIT:
            report.error(
                f"Raw/{path.name}: mean word length {mean:.2f} "
                f"(limit {MEAN_WORD_LIMIT}), glued runs {density:.2f}/kB "
                f"(limit {GLUE_LIMIT}), {long_words} words over 15 chars "
                f"-- text has lost word boundaries, re-extract it"
            )
    return report.finish()


if __name__ == "__main__":
    sys.exit(main())
