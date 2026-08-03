#!/usr/bin/env python3
"""Run every wiki check and return a single exit code.

This is the Lint operation from AGENTS.md, made executable. Run it before
closing any ingest.

By default the gate is a ratchet: it compares against scripts/baseline.json and
fails only when a file gains errors it did not already have. That keeps the
check meaningful while the older summaries are still being rewritten -- a gate
that is red on every push cannot tell you that today's edit broke something.

    python3 scripts/lint.py             fail only on regressions
    python3 scripts/lint.py --strict    fail on any error, ignoring the baseline
    python3 scripts/lint.py --record    re-record the baseline from current state
"""

from __future__ import annotations

import sys

import baseline
import check_frontmatter
import check_raw_quality
import lint_links
import verify_quotes
from wikilib import Report

CHECKS = [
    ("raw quality", check_raw_quality),
    ("citation integrity", verify_quotes),
    ("link integrity", lint_links),
    ("frontmatter", check_frontmatter),
]


def run(module) -> Report:
    """Run one check with its printing suppressed, and hand back the findings."""
    captured: list[Report] = []
    original = Report.finish

    def capture(self, *args, **kwargs):
        captured.append(self)
        return 0

    Report.finish = capture
    try:
        module.main()
    finally:
        Report.finish = original
    return captured[0]


def main() -> int:
    strict = "--strict" in sys.argv
    record = "--record" in sys.argv

    results = {name: run(module) for name, module in CHECKS}
    tallies = {name: baseline.tally(r.errors) for name, r in results.items()}

    if record:
        baseline.save(tallies)
        total = sum(sum(t.values()) for t in tallies.values())
        print(f"baseline recorded: {total} known errors across {len(tallies)} checks")
        print(f"written to {baseline.BASELINE_PATH}")
        return 0

    failed = False
    for name, report in results.items():
        errors = len(report.errors)
        if strict:
            print(f"{name}: {errors} errors")
            failed |= errors > 0
            continue

        regressions, improvements = baseline.compare(name, tallies[name])
        known = sum(baseline.load().get(name, {}).values())
        status = "REGRESSION" if regressions else "ok"
        print(f"{name}: {errors} errors ({known} known) -- {status}")
        for line in improvements[:10]:
            print(f"    improved: {line}")
        if len(improvements) > 10:
            print(f"    improved: ... and {len(improvements) - 10} more files")
        for line in regressions:
            print(f"    NEW: {line}")
        failed |= bool(regressions)

    print()
    if failed:
        print("FAIL: this change introduced new errors. Run `make lint-detail` to see them.")
        return 1
    if strict:
        print("PASS: no errors at all.")
    else:
        print(
            "PASS: no new errors. Remaining known errors are in pages not yet "
            "rewritten; run `make baseline` after fixing some to tighten the gate."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
