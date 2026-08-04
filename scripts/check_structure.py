#!/usr/bin/env python3
"""Enforce the page structure and tag quality that wiki/SCHEMA.md specifies.

AGENTS.md claims every convention in the schema has a corresponding check. That
was not true: `make frontmatter` verified which keys exist and `make links`
verified that links resolve, but nothing verified that a page carried the
sections the schema names, nor that its tags said anything.

Both gaps showed up in the same delegated page. It arrived with correct
frontmatter and correct citations -- because those are checked -- and with
`Summary / Key Highlights / Investment Holdings / Corporate Governance` instead
of the four canonical sections, and with

    tags: [annual-letter, 1995, warren-buffett, berkshire-hathaway]

which is the tag set every one of the 48 letters would get. Tags that do not
distinguish one page from another cannot filter anything, so a Dataview query on
them returns either everything or nothing.

Three checks:

  sections     the headings the schema names for that directory are present
  outbound     a source summary links into the compiled layer at least once
  tags         at least MIN_TOPIC_TAGS tags that are not boilerplate

Skeletons from `make new` are exempt while they still carry a `> TODO:` marker:
they are unfinished by construction, and a gate that goes red the moment you
scaffold a page is a gate people stop scaffolding with. They are counted and
reported so nothing sits half-written unnoticed.
"""

from __future__ import annotations

import re
import sys

from wikilib import (
    META_PAGES,
    REPO,
    Report,
    frontmatter_keys,
    load_pages,
    split_frontmatter,
)

# Headings each directory must carry. Matched on the words, so the emoji and
# any trailing punctuation in the real heading do not have to be reproduced.
# Sources/ keeps its four headings because a summary is a router and readers scan
# the same four places on every one of the 48 pages.
#
# Concepts/ deliberately does not. The schema used to require "Definition" and
# "Examples from Letters", and the rebuilt pages came back with headings like
# "The Lesson That Orders Everything Else" and "Why Integrity Is Weighted So
# Heavily" — better than the generic ones they would have replaced. The purpose
# behind "Examples from Letters" was to force grounding in sources, and that is
# now measured directly and far better by `make propagation`: distinct sources
# cited per page. Requiring the heading as well is ceremony, and a rule that adds
# nothing is a rule people route around.
SECTIONS = {
    "Sources": ["Key Themes", "Notable Quotes", "Investment Decisions", "Cross-References"],
    "Concepts": [],
    "Principles": [],
    "Synthesis": [],
    "Cases": [],
    "People": [],
    "Applications": [],
}

# Directories that make up the compiled layer. A source summary that links only
# to other source summaries has been filed, not integrated.
COMPILED = ("Concepts/", "Cases/", "People/", "Principles/", "Applications/", "Synthesis/")

# Tags true of every page in this wiki, and therefore useless for filtering one
# out. The year is excluded separately: it is already the `year:` key.
BOILERPLATE = {
    "annual-letter", "letter", "annual", "shareholders", "shareholder-letter",
    "warren-buffett", "buffett", "berkshire-hathaway", "berkshire", "brk",
    "summary", "source", "source-summary", "wiki", "finance", "investing",
    "investment", "report", "notes",
}

MIN_TOPIC_TAGS = 3

HEADING = re.compile(r"^#{2,3}\s+(.+?)\s*$", re.M)
WIKILINK = re.compile(r"\[\[([^\]|#]+)")
YEARLIKE = re.compile(r"^(?:19|20)\d\d$")


def topic_tags(raw: str) -> list[str]:
    """Tags that actually distinguish this page from its neighbours."""
    inner = raw.strip().strip("[]")
    out = []
    for tag in inner.split(","):
        tag = tag.strip().strip("\"'").lower()
        if not tag or tag in BOILERPLATE or YEARLIKE.match(tag):
            continue
        out.append(tag)
    return out


def main() -> int:
    report = Report("check_structure: sections, outbound links and tag quality")
    skeletons = 0

    for name, path in sorted(load_pages().items()):
        folder = name.split("/")[0]
        if name in META_PAGES or folder not in SECTIONS:
            continue

        rel = path.relative_to(REPO).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        if "> TODO:" in text:
            skeletons += 1
            report.warn(f"{rel}: skeleton, not yet written")
            continue

        frontmatter, body = split_frontmatter(text)
        headings = " | ".join(HEADING.findall(body))

        for wanted in SECTIONS[folder]:
            if wanted.lower() not in headings.lower():
                report.error(f"{rel}: missing section '{wanted}'")

        if folder == "Sources":
            targets = WIKILINK.findall(body)
            if not any(t.strip().startswith(COMPILED) for t in targets):
                report.error(
                    f"{rel}: links to no compiled page "
                    "(Concepts/, Cases/, People/, Principles/, Applications/, Synthesis/)"
                )

        tags = frontmatter_keys(frontmatter).get("tags", "")
        topics = topic_tags(tags)
        if len(topics) < MIN_TOPIC_TAGS:
            report.error(
                f"{rel}: {len(topics)} topic tags, needs {MIN_TOPIC_TAGS} "
                f"(boilerplate and the year do not count) -- tags: {tags or 'missing'}"
            )

    if skeletons:
        report.title += f" [{skeletons} skeletons skipped]"
    return report.finish()


if __name__ == "__main__":
    sys.exit(main())
