#!/usr/bin/env python3
"""Run every wiki check and return a single exit code.

This is the Lint operation from AGENTS.md, made executable. Run it before
closing any ingest.

By default the gate is a ratchet: it compares against scripts/baseline.json and
fails only when a file gains errors it did not already have. That keeps the
check meaningful while the older summaries are still being rewritten -- a gate
that is red on every push cannot tell you that today's edit broke something.

    python3 scripts/lint.py                       fail only on regressions
    python3 scripts/lint.py --strict              fail on any error, ignoring the baseline
    python3 scripts/lint.py --record              re-record the baseline from current state
    python3 scripts/lint.py --page Sources/1996ltr   zero tolerance, one page

--page exists because the ratchet has a blind spot that matters during a rewrite.
It lets a file keep the errors it already had, which is right for a backlog and
wrong for a page you just rewrote: if 1996 is recorded with five errors and comes
back from a rewrite with five errors, nothing fires. Run --page on every page you
finish. It ignores the baseline entirely and demands zero.
"""

from __future__ import annotations

import sys

import baseline
import check_frontmatter
import check_raw_quality
import check_structure
import lint_links
import verify_quotes
from wikilib import Report

CHECKS = [
    ("raw quality", check_raw_quality),
    ("citation integrity", verify_quotes),
    ("link integrity", lint_links),
    ("frontmatter", check_frontmatter),
    ("structure", check_structure),
]


def run(module) -> Report:
    """Run one check with its printing suppressed, and hand back the findings.

    argv is blanked for the duration: some checks read sys.argv for the paths
    they should scan, and would otherwise treat this script's own flags as
    filenames -- `--page Sources/1996ltr` made verify_quotes try to open a file
    called Sources/1996ltr at the repository root.
    """
    captured: list[Report] = []
    original = Report.finish
    argv = sys.argv

    def capture(self, *args, **kwargs):
        captured.append(self)
        return 0

    Report.finish = capture
    sys.argv = argv[:1]
    try:
        module.main()
    finally:
        Report.finish = original
        sys.argv = argv
    return captured[0]


def page_argument(argv: list[str]) -> str | None:
    if "--page" not in argv:
        return None
    index = argv.index("--page")
    if index + 1 >= len(argv):
        sys.exit("--page needs a page, e.g. --page Sources/1996ltr")
    return argv[index + 1].removeprefix("wiki/").removesuffix(".md")


def check_one_page(page: str, results: dict) -> int:
    """Every finding that names this page, with no baseline forgiveness."""
    needle = f"wiki/{page}.md"
    total = 0
    for name, report in results.items():
        hits = [e for e in report.errors if needle in e]
        total += len(hits)
        print(f"{name}: {len(hits)} errors")
        for hit in hits:
            print(f"    {hit}")
    print()
    if total:
        print(f"FAIL: {needle} has {total} errors. A finished page must have none.")
        return 1
    print(f"PASS: {needle} is clean on every check.")
    return 0


def main() -> int:
    strict = "--strict" in sys.argv
    record = "--record" in sys.argv
    page = page_argument(sys.argv)

    results = {name: run(module) for name, module in CHECKS}

    if page:
        return check_one_page(page, results)

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
