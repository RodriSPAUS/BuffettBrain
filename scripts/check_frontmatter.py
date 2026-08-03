#!/usr/bin/env python3
"""Enforce the frontmatter contract in wiki/SCHEMA.md.

wiki/SCHEMA.md recommends Dataview queries such as

    TABLE year FROM "wiki" WHERE type = "source-summary" SORT year DESC

which only work if `type` is present and canonical on every page. This script is
what keeps that promise true.
"""

from __future__ import annotations

import re
import sys

from wikilib import (
    META_PAGES,
    PAGE_DIRS,
    REPO,
    Report,
    frontmatter_keys,
    load_pages,
    split_frontmatter,
)

# Canonical `type` per directory, and the keys every page in it must carry.
CONTRACT = {
    "Sources": ("source-summary", ["title", "type", "date", "source", "year", "sourcetype"]),
    "Concepts": ("concept", ["title", "type", "stability", "tags", "date"]),
    "Applications": ("application", ["title", "type", "tags", "date"]),
    "Cases": ("case", ["title", "type", "tags", "date"]),
    "People": ("person", ["title", "type", "tags", "date"]),
    "Principles": ("principle", ["title", "type", "stability", "tags", "date"]),
    "Synthesis": ("synthesis", ["title", "type", "stability", "tags", "date", "source"]),
}

SOURCETYPES = {"annual-letter", "interview", "speech", "article", "meeting", "book"}
STABILITY = {"low", "medium", "high"}
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def main() -> int:
    report = Report("check_frontmatter: page metadata vs wiki/SCHEMA.md")
    pages = load_pages()

    for name, path in sorted(pages.items()):
        if name in META_PAGES:
            continue
        folder = name.split("/")[0]
        if folder not in CONTRACT:
            report.warn(f"{name}: page sits outside the directories wiki/SCHEMA.md defines")
            continue

        expected_type, required = CONTRACT[folder]
        rel = path.relative_to(REPO).as_posix()
        fm, _ = split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        if not fm:
            report.error(f"{rel}: no YAML frontmatter")
            continue

        keys = frontmatter_keys(fm)
        for key in required:
            if key not in keys:
                report.error(f"{rel}: missing required key '{key}'")

        if "type" in keys and keys["type"].strip("\"'") != expected_type:
            report.error(
                f"{rel}: type is '{keys['type']}', must be '{expected_type}' in {folder}/"
            )

        if "sourcetype" in keys and keys["sourcetype"].strip("\"'") not in SOURCETYPES:
            report.error(f"{rel}: sourcetype '{keys['sourcetype']}' is not canonical")

        if "stability" in keys and keys["stability"].strip("\"'") not in STABILITY:
            report.error(f"{rel}: stability '{keys['stability']}' must be low/medium/high")

        if "date" in keys and not ISO_DATE.match(keys["date"].strip("\"'")):
            report.error(f"{rel}: date '{keys['date']}' is not YYYY-MM-DD")

        if folder == "Sources":
            src = keys.get("source", "")
            if not src.startswith("[[Raw/"):
                report.error(f"{rel}: source must be [[Raw/<file>.md]], found '{src}'")
            if "year" in keys and not re.match(r"^\d{4}$", keys["year"].strip("\"'")):
                report.error(f"{rel}: year '{keys['year']}' is not a 4-digit year")

    for folder in PAGE_DIRS:
        if not (REPO / "wiki" / folder).exists():
            report.warn(f"wiki/{folder}/ named in wiki/SCHEMA.md does not exist")

    return report.finish(limit=60)


if __name__ == "__main__":
    sys.exit(main())
