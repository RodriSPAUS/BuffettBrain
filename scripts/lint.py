#!/usr/bin/env python3
"""Run every wiki check and return a single exit code.

This is the Lint operation from AGENT.md, made executable. Run it before
closing any ingest.
"""

from __future__ import annotations

import sys

import check_frontmatter
import check_raw_quality
import lint_links
import verify_quotes

CHECKS = [
    ("raw quality", check_raw_quality.main),
    ("citation integrity", verify_quotes.main),
    ("link integrity", lint_links.main),
    ("frontmatter", check_frontmatter.main),
]


def main() -> int:
    failed = []
    for name, check in CHECKS:
        if check() != 0:
            failed.append(name)
    if failed:
        print(f"FAIL: {', '.join(failed)}")
        return 1
    print("PASS: wiki is consistent with AGENT.md and wiki/SCHEMA.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
