#!/usr/bin/env python3
"""Emit a page skeleton with the frontmatter and sections already correct.

The schema is a specification, and every agent that has worked in this repository
has written frontmatter from memory instead of reading it — inventing keys
(`author`, `source_document`, `link`), missing required ones, and replacing the
four canonical sections with its own headings. That is not a comprehension
failure. Reproducing a spec from memory is a task nobody does reliably, and there
is no reason to ask: the frontmatter is eight fixed keys and the sections are four
fixed headings.

So the generator writes them and the model writes only prose. A page produced this
way cannot fail `make frontmatter`, because the model never touches the
frontmatter.

The skeleton carries explicit `> TODO:` markers rather than empty slots.
LESSONS_LEARNED records what empty slots produce: a model handed a four-row metric
table with no data in the source filled the rows in anyway. Structure may be
pre-filled; claims may not.

Usage:
    python3 scripts/new_page.py Sources/1978ltr      # date read from Raw/
    python3 scripts/new_page.py Concepts/Moat
    python3 scripts/new_page.py Cases/Wesco --force  # overwrite
"""

from __future__ import annotations

import re
import sys
from datetime import date as _date
from pathlib import Path

from wikilib import RAW, WIKI

# Mirrors CONTRACT in check_frontmatter.py. If you change one, change both --
# and `make lint` will tell you if you forgot, because a generated page is
# checked like any other.
TYPES = {
    "Sources": "source-summary",
    "Concepts": "concept",
    "Applications": "application",
    "Cases": "case",
    "People": "person",
    "Principles": "principle",
    "Synthesis": "synthesis",
}

# Keys beyond title/type/date that each directory requires.
EXTRA = {
    "Sources": ["year", "sourcetype", "source"],
    "Concepts": ["stability", "tags"],
    "Applications": ["tags"],
    "Cases": ["tags"],
    "People": ["tags"],
    "Principles": ["stability", "tags"],
    "Synthesis": ["stability", "tags", "source"],
}

SECTIONS = {
    "Sources": [
        ("## 🔑 Key Themes", "One subsection per theme the letter actually develops.\n"
                             "Roughly one third quotation, two thirds your own framing prose.\n"
                             "Quote only what `make quote Q=\"...\"` returns.\n{SECTIONS}"),
        ("## 💬 Notable Quotes", "Six to nine blockquotes. Verbatim, no ellipsis games."),
        ("## 📊 Investment Decisions", "What was bought, sold, declined or written down, with figures."),
        ("## 🔗 Cross-References", "{MENU}"),
    ],
    "_concept": [
        ("## Definition", "What the idea is, in Buffett's terms."),
        ("## Examples from Letters", "Each example links its source: Coca-Cola (1988) — `Sources/1988ltr`."),
        ("## Contrasts & Nuances", "Where the idea is misapplied, or where Buffett changed his mind."),
        ("## See also", "Wikilinks carrying the folder prefix."),
    ],
}

# The hints above name link targets in backticks, never as real `[[wikilinks]]`:
# a skeleton must not fail `make links` on the day it is created, and a template
# example is not a link.

MONTHS = ("January February March April May June July August September "
          "October November December").split()
LETTER_DATE = re.compile(r"\b(" + "|".join(MONTHS) + r")\s+(\d{1,2}),\s*((?:19|20)\d\d)\b")


def letter_date(stem: str, year: int) -> tuple[str, bool]:
    """The date the letter was signed, read out of Raw/ when it is there.

    Look at the head and the tail only, and require the following year. Buffett
    signs above the salutation or under his name at the end; dates in the body are
    fiscal year-ends and holdings dates, and scanning the whole file picks those
    up first — 1978 yields 'December 31, 1978' 150 lines before the real
    'March 26, 1979'.
    """
    raw = RAW / f"{stem}.md"
    if not raw.exists():
        return f"{year + 1}-01-01", False
    lines = raw.read_text(encoding="utf-8", errors="replace").splitlines()
    for chunk in ("\n".join(lines[-40:]), "\n".join(lines[:20])):
        for month, day, yr in LETTER_DATE.findall(chunk):
            if int(yr) == year + 1:
                return f"{yr}-{MONTHS.index(month) + 1:02d}-{int(day):02d}", True
    return f"{year + 1}-01-01", False


# A section heading in these letters sits at column 0 with a blank line either
# side, while body text is indented. Rules out table headers and figures.
NOT_A_HEADING = re.compile(r"[.,;:?!]$|\d{3}|\$|%|^(Year|Included|Berkshire$|Annual Percentage|Source:)")


def letter_sections(stem: str) -> list[str]:
    """The letter's own section headings, so coverage can be checked at a glance.

    Best effort: clean for the 1977-1996 letters, noisier for the later ones whose
    extraction carries tables. Noise is the acceptable direction of error — a
    spurious heading is discarded by whoever reads the letter, whereas a missing
    one is a topic that quietly never gets summarised. The 1996 page skipped
    USAir, 69 lines in which Buffett calls his own analysis superficial and wrong.
    """
    raw = RAW / f"{stem}.md"
    if not raw.exists():
        return []
    text = raw.read_text(encoding="utf-8", errors="replace")

    # 1997 onwards mark headings in bold and stop indenting the body, so the
    # column-0 rule below finds nothing there. Take the bold lines when a file
    # has them.
    bold = [
        h.strip()
        for h in re.findall(r"^\*\*([^*\n]{4,60})\*\*$", text, re.M)
        if not NOT_A_HEADING.search(h.strip())
        and not h.strip().endswith(":")
        and "BERKSHIRE HATHAWAY" not in h.upper()
    ]
    if len(bold) >= 4:
        out: list[str] = []
        for h in bold:
            if h not in out:
                out.append(h)
        return out

    lines = text.split("\n")
    out = []
    for i, line in enumerate(lines):
        if not line or line[0].isspace() or not line[0].isupper():
            continue
        heading = line.strip()
        if not 3 < len(heading) < 61:
            continue
        if (lines[i - 1].strip() if i else "") or (lines[i + 1].strip() if i + 1 < len(lines) else ""):
            continue
        if NOT_A_HEADING.search(heading) or heading in out:
            continue
        out.append(heading)
    return out


def link_menu() -> str:
    """The pages that actually exist, listed for the writer to choose from.

    Invented link targets are the failure mode this replaces: a delegated page
    arrived carrying [[Moat]], [[Owner-Earnings]], [[Ajit-Jain]] and
    [[Tony-Nicely]] -- nineteen broken links, every one a plausible guess at a
    name. Guessing is unnecessary when the real names are on the page in front
    of you.
    """
    from wikilib import load_pages

    compiled = {"Concepts", "Cases", "People", "Principles", "Applications", "Synthesis"}
    groups: dict[str, list[str]] = {}
    for name in sorted(load_pages()):
        folder = name.split("/")[0]
        if folder in compiled:
            groups.setdefault(folder, []).append(name.split("/", 1)[1])

    lines = [
        "Link the pages this source bears on. Copy the names below verbatim into",
        "double brackets, folder prefix included and spelling as shown. Do not invent a",
        "target: if an entity has no page, create a stub for it. A source summary that",
        "links to no compiled page fails `make structure`.",
        "",
    ]
    for folder in sorted(groups):
        lines.append(f"  {folder}/ — " + ", ".join(groups[folder]))
    lines += ["", "  Also link the letters either side of this one: Sources/<year>ltr."]
    return "\n".join(lines)


def build(target: str) -> tuple[Path, str, list[str]]:
    folder, _, stem = target.replace(".md", "").partition("/")
    if folder not in TYPES:
        raise SystemExit(f"unknown directory '{folder}'. one of: {', '.join(sorted(TYPES))}")
    if not stem:
        raise SystemExit("give a page name, e.g. Sources/1978ltr or Concepts/Moat")

    notes: list[str] = []
    fm = [f'title: "{stem}"', f"type: {TYPES[folder]}"]

    if folder == "Sources":
        match = re.match(r"^((?:19|20)\d\d)ltr$", stem)
        year = int(match.group(1)) if match else 0
        if not year:
            raise SystemExit(f"'{stem}' is not a letter stem; add non-letter sources by hand")
        signed, found = letter_date(stem, year)
        if not found:
            notes.append(f"no date found in Raw/{stem}.md — set `date:` to the letter's own date")
        fm = [
            f'title: "{year} Annual Letter"',
            "type: source-summary",
            "stability: high",
            f"tags: [{year}, letter]",
            f"date: {signed}",
            f"year: {year}",
            "sourcetype: annual-letter",
            f"source: [[Raw/{stem}.md]]",
        ]
        if not (RAW / f"{stem}.md").exists():
            notes.append(f"Raw/{stem}.md does not exist — a summary with no source is a phantom")
        notes.append(
            "replace the placeholder tags: `make structure` wants at least 3 that name "
            "what this letter is about (moat, float, buybacks...). The year and words "
            "true of every letter do not count."
        )
        found_sections = letter_sections(stem)
        section_list = ""
        if len(found_sections) < 4:
            notes.append(
                "could not read this letter's section headings out of Raw/ (its "
                "extraction lost them) — read the letter end to end and list its topics "
                "yourself before summarising"
            )
        if found_sections:
            section_list = (
                "\n\nThe letter itself is organised under these headings (best effort, read past\n"
                "any noise). Do not leave one out without deciding it carries nothing:\n\n"
                + "\n".join(f"  - {s}" for s in found_sections)
            )
        sections = SECTIONS["Sources"]
        # The tag reminder lives in the file, not only in this script's terminal
        # output. The 1996 page came back with `tags: [1996, letter]` untouched --
        # the generator had said to replace them, but it said so on stdout, and
        # whoever ran the generator was not the one who filled the page in.
        lead = (
            f"*One sentence on what {year} was about: the headline figure, and the two or\n"
            f"three arguments the letter is actually built around.*\n\n"
            f"> TODO: replace the placeholder `tags:` above. `make structure` wants at least\n"
            f"> three that name what THIS letter is about — moat, float, buybacks,\n"
            f"> loss-reserving, wppss. The year and words true of every letter do not count.\n"
            f"> Then delete this line."
        )
        title = f"# {year} Annual Letter Summary"
    else:
        for key in EXTRA[folder]:
            fm.append({"stability": "stability: medium",
                       "tags": "tags: []",
                       "source": "source: "}[key])
        fm.insert(2, f"date: {_date.today().isoformat()}")
        if "source: " in fm:
            notes.append("fill `source:` with the [[Sources/X]] pages this page draws on")
        sections = SECTIONS["_concept"]
        section_list = ""
        lead = "*One sentence on what this page is for.*"
        title = f"# {stem}"

    body = [f"---\n" + "\n".join(fm) + "\n---", "", title, "", lead, ""]
    for heading, hint in sections:
        hint = hint.replace("{MENU}", link_menu()).replace("{SECTIONS}", section_list)
        body += [heading, "", "> TODO: " + hint.replace("\n", "\n> "), ""]

    return WIKI / folder / f"{stem}.md", "\n".join(body), notes


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        print(__doc__)
        return 2
    path, text, notes = build(args[0])
    if path.exists():
        rel = path.relative_to(path.parents[2])
        existing = path.read_text(encoding="utf-8", errors="replace")
        # --force regenerates a skeleton nobody has filled in yet. It must not be
        # able to destroy a finished page: writing this script, --force on a test
        # run silently replaced four completed summaries, and only `git` got them
        # back. Deleting a real page has to be a separate, deliberate act.
        if "> TODO:" not in existing:
            print(f"{rel} already exists and has been written ({len(existing) // 1024} KB).")
            print("refusing to overwrite; delete the file first if you really mean to")
            return 1
        if "--force" not in sys.argv:
            print(f"{rel} already exists as an unfilled skeleton; pass --force to regenerate")
            return 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(path.parents[2])}")
    for note in notes:
        print(f"  note: {note}")
    print("  fill in the prose; do not edit the frontmatter")
    return 0


if __name__ == "__main__":
    sys.exit(main())
