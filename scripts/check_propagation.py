#!/usr/bin/env python3
"""Measure whether ingested sources are reaching the compiled layer.

This is the check that was missing when the wiki accumulated 48 source summaries
that between them fed only 13 letters into any concept page. Nothing reported
that, because the summaries themselves were fine — the failure was in what they
did *not* change elsewhere, and absence is exactly what a per-file checker cannot
see.

Two numbers, both about reach rather than correctness:

  coverage   how many sources are cited anywhere outside wiki/Sources/
  depth      how many distinct sources each compiled page draws on

A concept that has been properly propagated cites many years, because Buffett
returns to every idea for decades. A concept page citing two letters is a
definition someone wrote once, not an idea traced through a corpus.

Reported as warnings, not errors: this is a progress metric for work in flight,
and it should never block a commit. What it must do is make a stalled propagation
visible, which is all that was needed to catch the original failure.
"""

from __future__ import annotations

import re
import sys

from wikilib import RAW, WIKI, Report, load_pages

# Below this, a compiled page has not been traced through the corpus.
THIN = 6

# Directories that make up the compiled layer — everything except the summaries.
COMPILED = ["Concepts", "Cases", "People", "Principles", "Applications", "Synthesis"]

SOURCE_LINK = re.compile(r"\[\[Sources/([A-Za-z0-9_]+)")


def main() -> int:
    report = Report("check_propagation: are sources reaching the compiled layer?")
    pages = load_pages()
    raw_stems = {p.stem for p in RAW.glob("*.md")}

    reached: set[str] = set()
    depths: list[tuple[str, int]] = []

    for name, path in sorted(pages.items()):
        if name.split("/")[0] not in COMPILED:
            continue
        cited = {
            stem
            for stem in SOURCE_LINK.findall(path.read_text(encoding="utf-8", errors="replace"))
            if stem in raw_stems
        }
        reached |= cited
        depths.append((name, len(cited)))

    for name, depth in depths:
        if depth < THIN:
            report.warn(f"{name}: draws on {depth} sources (thin, expected {THIN}+)")

    missing = sorted(raw_stems - reached)
    if missing:
        report.warn(
            f"{len(missing)} sources reach no compiled page: "
            + ", ".join(missing[:12])
            + (" ..." if len(missing) > 12 else "")
        )

    total = len(raw_stems)
    mean = sum(d for _, d in depths) / max(len(depths), 1)
    print(f"== {report.title} ==")
    print(f"  coverage: {len(reached)}/{total} sources reach the compiled layer "
          f"({100 * len(reached) / max(total, 1):.0f}%)")
    print(f"  depth:    {mean:.1f} sources per compiled page on average, "
          f"{sum(1 for _, d in depths if d < THIN)} of {len(depths)} pages thin")
    report.title = "detail"
    return report.finish(limit=30, warn_only=True)


if __name__ == "__main__":
    sys.exit(main())
