#!/usr/bin/env python3
"""Link hygiene for the wiki: broken targets, phantom sources, orphans, anchors.

Enforces the linking rules in AGENTS.md ("Standing Rules") and wiki/SCHEMA.md
("Linking Rules"):

  * every [[wikilink]] resolves to a page that exists
  * every [[Sources/X]] is backed by a real Raw/X.md
  * links carry their folder prefix ([[Concepts/Moat]], not [[Moat]])
  * links do not carry a .md extension
  * no positional anchors (#p4): Raw/ files have no headings or block IDs, so
    those resolve to nothing and lend false precision
  * no page is an orphan with zero inbound links
"""

from __future__ import annotations

import re
import sys

from wikilib import (
    META_PAGES,
    RAW,
    REPO,
    WIKILINK,
    Report,
    link_target,
    load_pages,
)

# Anchors that point at nothing. Real heading anchors are allowed.
FAKE_ANCHOR = re.compile(r"^p\.?\d+$|^section\d+$", re.IGNORECASE)

# Placeholder link targets that appear inside documentation examples.
DOC_PLACEHOLDERS = {"wikilink", "PageName", "SCHEMA", "log", "index"}

# wiki/SCHEMA.md: "No external URLs in content — only [[PageName]] or
# [[Sources/2024ltr]]." Nothing enforced it, and a delegated rebuild wrote eleven
# links of the form
#   [1986 Annual Letter](file:///c%3A/Users/.../OneDrive%20-%20.../1986ltr.md)
# which resolve on exactly one machine and leak its owner's directory layout.
# LESSONS_LEARNED records the same defect from an earlier session; it recurred
# because the rule had no check.
EXTERNAL_LINK = re.compile(r"\]\((?:file|https?)://[^)]*\)|\b(?:file:///|[A-Z]:\\\\|/Users/)")


def main() -> int:
    report = Report("lint_links: wikilink integrity")
    pages = load_pages()
    raw_stems = {p.stem for p in RAW.glob("*.md")}
    by_basename: dict[str, list[str]] = {}
    for name in pages:
        by_basename.setdefault(name.split("/")[-1], []).append(name)

    inbound = {name: 0 for name in pages}

    for name, path in pages.items():
        if name == "SCHEMA":
            continue  # SCHEMA documents the syntax; its examples are not links
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(REPO).as_posix()
        for lineno, line in enumerate(text.splitlines(), 1):
            if EXTERNAL_LINK.search(line) and rel != "wiki/log.md":
                report.error(
                    f"{rel}:{lineno} external URL or machine path; "
                    "wiki content links only with [[wikilinks]]"
                )
            for raw_link in WIKILINK.findall(line):
                target, anchor = link_target(raw_link)
                if not target:
                    continue

                if anchor and FAKE_ANCHOR.match(anchor):
                    report.error(f"{rel}:{lineno} fabricated anchor #{anchor} -> {target}")

                # Raw/ links keep their extension: wiki/SCHEMA.md specifies
                # `source: [[Raw/2024ltr.md]]`, pointing at the file itself
                # rather than at a wiki page.
                if target.startswith("Raw/"):
                    stem = target[4:-3] if target.endswith(".md") else target[4:]
                    if stem not in raw_stems:
                        report.error(f"{rel}:{lineno} Raw source does not exist: [[{target}]]")
                    continue

                if target.endswith(".md"):
                    report.error(f"{rel}:{lineno} link carries .md extension: [[{target}]]")
                    target = target[:-3]

                if target in DOC_PLACEHOLDERS:
                    continue

                if target in pages:
                    resolved = target
                elif "/" not in target and len(by_basename.get(target, [])) == 1:
                    resolved = by_basename[target][0]
                    report.warn(
                        f"{rel}:{lineno} link missing folder prefix: "
                        f"[[{target}]] should be [[{resolved}]]"
                    )
                else:
                    report.error(f"{rel}:{lineno} broken link: [[{target}]]")
                    continue

                if resolved.startswith("Sources/") and resolved.split("/")[1] not in raw_stems:
                    report.error(
                        f"{rel}:{lineno} phantom source: [[{resolved}]] has no Raw/ file"
                    )

                if resolved != name:
                    inbound[resolved] += 1

    for name in sorted(pages):
        if name in META_PAGES:
            continue
        if inbound[name] == 0:
            report.error(f"orphan page with no inbound links: {name}")

    for stem in sorted(raw_stems):
        if f"Sources/{stem}" not in pages:
            report.warn(f"Raw/{stem}.md has no wiki/Sources/ page")

    return report.finish(limit=60)


if __name__ == "__main__":
    sys.exit(main())
