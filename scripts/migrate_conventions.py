#!/usr/bin/env python3
"""Bring existing pages up to the conventions in AGENTS.md and wiki/SCHEMA.md.

The rules were tightened after most of the wiki had already been written, and
nothing applied them retroactively, so two incompatible styles ended up living
side by side: 26 pages citing [[1985ltr.md#p0]] and 10 citing [[Sources/1985ltr]].
This is the one-off pass that closes that gap.

What it changes:

  * drops positional anchors (#p4, #p.12). AGENTS.md forbids them because Raw/
    files have no headings or block IDs, so they resolve to nothing.
  * rewrites [[Moat.md]] as [[Concepts/Moat]] -- folder prefix, no extension
  * fills in missing frontmatter keys and canonicalises `type` per directory
  * points `source:` at the Raw/ file in wikilink form

It does not touch the prose, and it never invents a citation: a link whose
target does not exist is left alone and reported, because choosing a new target
is an editorial decision.

    python3 scripts/migrate_conventions.py --dry-run
    python3 scripts/migrate_conventions.py --exclude 'Sources/(19[89]|20)'
"""

from __future__ import annotations

import argparse
import re
from collections import Counter

from wikilib import META_PAGES, load_pages, split_frontmatter

FAKE_ANCHOR = re.compile(r"#p\.?\d+|#section\d+", re.IGNORECASE)

TYPE_BY_DIR = {
    "Sources": "source-summary",
    "Concepts": "concept",
    "Applications": "application",
    "Cases": "case",
    "People": "person",
    "Principles": "principle",
    "Synthesis": "synthesis",
}

STABILITY_DIRS = {"Concepts", "Principles", "Synthesis"}

# Letters are dated the following February, when Buffett signs them.
LETTER_DATE = "{}-02-28"


def index_by_basename(pages: dict[str, str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for name in pages:
        out.setdefault(name.split("/")[-1], []).append(name)
    return out


def fix_links(text: str, by_basename: dict[str, list[str]], stats: Counter) -> str:
    def replace(match: re.Match) -> str:
        body = match.group(1)
        target, sep, alias = body.partition("|")
        target, hash_sep, anchor = target.partition("#")
        target = target.strip()

        if anchor and FAKE_ANCHOR.match("#" + anchor):
            stats["anchors_dropped"] += 1
            anchor, hash_sep = "", ""

        if target.startswith("Raw/"):
            return "[[" + target + (hash_sep + anchor if anchor else "") + sep + alias + "]]"

        bare = target[:-3] if target.endswith(".md") else target
        if target.endswith(".md"):
            stats["extensions_dropped"] += 1

        if "/" not in bare:
            candidates = by_basename.get(bare, [])
            if len(candidates) == 1:
                bare = candidates[0]
                stats["prefixes_added"] += 1
            else:
                stats["unresolved_links"] += 1

        return "[[" + bare + (hash_sep + anchor if anchor else "") + sep + alias + "]]"

    return re.sub(r"\[\[([^\]]+)\]\]", replace, text)


def fix_frontmatter(name: str, text: str, stats: Counter) -> str:
    folder, _, stem = name.partition("/")
    if folder not in TYPE_BY_DIR:
        return text

    fm, body = split_frontmatter(text)
    lines = [ln for ln in fm.strip().splitlines() if ln.strip()] if fm else []
    keys = {}
    for line in lines:
        match = re.match(r"([A-Za-z_][\w-]*)\s*:(.*)", line)
        if match:
            keys[match.group(1)] = match.group(2).strip()

    year = stem[:4] if re.match(r"^\d{4}ltr$", stem) else None
    wanted: dict[str, str] = {}

    if "title" not in keys:
        if year:
            wanted["title"] = f'"{year} Annual Letter"'
        else:
            spaced = re.sub(r"(?<!^)(?=[A-Z])", " ", stem)
            wanted["title"] = f'"{spaced}"'
    wanted["type"] = TYPE_BY_DIR[folder]

    if folder in STABILITY_DIRS and "stability" not in keys:
        wanted["stability"] = "medium"
    if "tags" not in keys:
        wanted["tags"] = f"[{folder.lower().rstrip('s')}]"
    if "date" not in keys:
        wanted["date"] = LETTER_DATE.format(int(year) + 1) if year else "2026-07-30"

    if folder == "Sources":
        if year:
            wanted["year"] = year
            wanted["sourcetype"] = keys.get("sourcetype") or "annual-letter"
            wanted["source"] = f"[[Raw/{stem}.md]]"

    merged = dict(keys)
    for key, value in wanted.items():
        if key not in merged or (key in {"type", "source"} and merged[key] != value):
            if merged.get(key) != value:
                stats["frontmatter_fields"] += 1
            merged[key] = value

    order = ["title", "type", "stability", "tags", "date", "year", "sourcetype", "source"]
    ordered = [k for k in order if k in merged] + [k for k in merged if k not in order]
    rendered = "\n".join(f"{k}: {merged[k]}" for k in ordered)
    return f"---\n{rendered}\n---\n\n{body.lstrip(chr(10))}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--exclude",
        default="",
        help="regex of page names to leave alone, e.g. 'Sources/(19[89]|20)'",
    )
    args = parser.parse_args()
    skip = re.compile(args.exclude) if args.exclude else None

    pages = load_pages()
    by_basename = index_by_basename(pages)
    stats: Counter[str] = Counter()
    touched = 0

    for name, path in sorted(pages.items()):
        if name in META_PAGES or (skip and skip.search(name)):
            continue
        original = path.read_text(encoding="utf-8")
        updated = fix_frontmatter(name, fix_links(original, by_basename, stats), stats)
        if updated != original:
            touched += 1
            if not args.dry_run:
                path.write_text(updated, encoding="utf-8")

    print(f"pages rewritten: {touched}")
    for key in sorted(stats):
        print(f"  {key}: {stats[key]}")
    if args.dry_run:
        print("(dry run, nothing written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
