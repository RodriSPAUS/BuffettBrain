# Warren Buffett Second Brain — Schema

*How a page is **shaped**: directory layout, page structure, frontmatter, linking. This file is
the authority on how to write a page.*

*How the agent **behaves** — the Ingest / Query / Lint operations, and the citation-integrity
rules that override everything here — is in `AGENTS.md`. The two do not overlap: that one when
deciding what to do, this one when writing.*

**Do not write frontmatter by hand.** `make new P=Sources/2024ltr` emits it correctly, with the
source's own date read out of `Raw/`, plus the required sections and the list of pages that
actually exist to link to. This file explains what the generator produces and why.

## ✅ Core Principles

- **Source fidelity first.** Every claim traces to a real source — `Source: [[Sources/2024ltr]]`.
  Never paraphrase without attribution; never present as a quotation text that is not verbatim
  in the cited `Raw/` file. See *Citation Integrity* in `AGENTS.md`.
- **Obsidian-native.** All links use `[[wikilink]]` syntax. No external URLs and no filesystem
  paths in content — only `[[Sources/2024ltr]]` and friends.
- **Concept-first.** Pages represent *ideas*, not just sources: `Concepts/Moat.md`,
  `Concepts/IntrinsicValue.md`. Source summaries exist to feed and update these.
- **No human edits to `wiki/`.** The human curates `Raw/`; the agent maintains `wiki/`.

## 📁 Directory Structure

```
wiki/
├── index.md              # Catalog of all pages (updated on ingest)
├── log.md                # Append-only chronological log: "## [2026-07-27] ingest | Sources/2024ltr"
├── SCHEMA.md             # This file
├── Sources/              # One summary per source: 1977ltr.md, DUKE2024.md, CNBCInterview.md
├── Concepts/             # Mental models: Moat.md, Float.md, CapitalAllocation.md
├── Applications/         # Checklists and tools: BusinessQualityChecklist.md, RedFlags.md
├── Cases/                # Holdings and acquisitions: GEICO.md, SeeCandies.md
├── People/               # Figures: WarrenBuffett.md, CharlieMunger.md
├── Principles/           # Enduring philosophy: OwnershipMindset.md, Fidelity.md
└── Synthesis/            # Cross-source themes: MoatEvolution.md, FloatGrowth.md
```

## 📝 Frontmatter Contract

Every page carries YAML frontmatter. `type` is fixed by the directory — it is what Dataview
queries filter on, so a wrong or missing one drops the page out of every query silently.
Enforced by `make frontmatter`.

| Directory | `type` | Required keys |
| --- | --- | --- |
| `Sources/` | `source-summary` | `title` `type` `date` `source` `year` `sourcetype` |
| `Concepts/` | `concept` | `title` `type` `stability` `tags` `date` |
| `Principles/` | `principle` | `title` `type` `stability` `tags` `date` |
| `Synthesis/` | `synthesis` | `title` `type` `stability` `tags` `date` `source` |
| `Cases/` | `case` | `title` `type` `tags` `date` |
| `People/` | `person` | `title` `type` `tags` `date` |
| `Applications/` | `application` | `title` `type` `tags` `date` |

- `date` — `YYYY-MM-DD`. On a `Sources/` page it is the source's own date, not today's.
- `stability` — `low` / `medium` / `high`: how consistently Buffett holds this idea across decades.
- `sourcetype` — `annual-letter` / `interview` / `speech` / `article` / `meeting` / `book`.
- `source` — on `Sources/` pages it points at the raw file, `[[Raw/2024ltr.md]]`. Everywhere
  else it points at wiki source pages, `[[Sources/1988ltr]], [[Sources/2024ltr]]`.

```yaml
---
title: "2024 Annual Letter"
type: source-summary
stability: high
tags: [buybacks, cash-position, succession, japanese-trading-houses]
date: 2024-02-24
year: 2024
sourcetype: annual-letter
source: [[Raw/2024ltr.md]]
---
```

## 📝 Page Conventions

### Source summaries (`Sources/`)

- **Four sections, all required**, checked by `make structure`: `## 🔑 Key Themes`,
  `## 💬 Notable Quotes`, `## 📊 Investment Decisions`, `## 🔗 Cross-References`. They are fixed
  because a summary is a router and a reader scans the same four places on all 48 of them.
- **Cover what the source covers.** Breadth beats depth: a topic the source spends real space on
  gets at least a line, and a topic deliberately passed over is named as passed over.
  `make coverage` lists subjects the source repeats that appear nowhere in `wiki/`.
- **At least one link into the compiled layer** (`Concepts/`, `Cases/`, `People/`, `Principles/`,
  `Applications/`, `Synthesis/`). A summary that links only to other summaries has been filed,
  not integrated; `make structure` fails it.
- The quoted text is the locator. Do **not** append positional anchors like `#p5` or `#section3`:
  `Raw/` files carry no headings or block IDs, so they resolve to nothing and imply a precision
  the citation does not have.

### Concept, Principle, Case, People and Application pages

- **Headings are the writer's.** Rebuilt pages produced "The Lesson That Orders Everything Else"
  and "Why Integrity Is Weighted So Heavily", which beat any generic heading a schema could have
  mandated. What is enforced instead is grounding: `make propagation` measures distinct sources
  cited per page, which is what a required "Examples from Letters" heading was only a proxy for.
- A page still needs a definition and grounded examples, and **every example links to its
  source**: `Coca-Cola (1988) — [[Sources/1988ltr]]`.

### Synthesis pages

- Cross-source thematic analysis, with explicit links to the sources it draws on.
- **At least 2 different sources**, or it is not a synthesis.

## 🏷️ Tag Rules

Tags exist so Dataview can filter. A tag true of every page in the wiki filters nothing, so
`make structure` requires **at least three tags that say what this page is about** and discounts
the rest.

- Discounted: the year (already the `year:` key) and boilerplate — `annual-letter`, `letter`,
  `warren-buffett`, `berkshire-hathaway`, `investing`, `summary`, `finance` and similar. The
  enforced list is `BOILERPLATE` in `scripts/check_structure.py`.
- Wanted: what distinguishes this page — `moat`, `float`, `buybacks`, `loss-reserving`,
  `misery-index`, `nebraska-furniture-mart`, `wppss`.
- The test: could this tag set belong to any other page? If yes, it is not doing any work.
  `tags: [annual-letter, 1995, warren-buffett, berkshire-hathaway]` is the failure this rule
  exists to stop — it would have fitted any of the other 47 letters equally well.

## 🔗 Linking Rules

- Link every entity, with its folder prefix: `[[Concepts/Moat]]`, `[[Sources/2024ltr]]`,
  `[[Cases/GEICO]]`, `[[People/CharlieMunger]]`, `[[Applications/RedFlags]]`,
  `[[Synthesis/MoatEvolution]]`. Never `[[Moat]]`.
- Never leave a named person, company or principle unlinked — create a stub with
  `TODO: flesh out` if no page exists.
- Links are bidirectional: if A cites B, B references A where relevant.
- **Never invent a link target.** `make new` prints every existing page, grouped by directory,
  in the skeleton's Cross-References section — copy from that list. A page that guessed
  `[[Moat]]`, `[[Owner-Earnings]]` and `[[Ajit-Jain]]` cost 19 broken links, and every guess was
  a plausible variant of a name that already existed in another form.
- No external URLs and no filesystem paths (`http://`, `file://`, `C:\...`) anywhere in `wiki/`.

## 🌐 Obsidian

- **Dataview** for frontmatter queries: `TABLE year FROM "wiki" WHERE type = "source-summary"
  SORT year DESC`. Complete only while `make frontmatter` passes.
- **Graph View** to see which concepts are actually central.

> 💡 This schema evolves. When a rule changes: update this file first, then the check in
> `scripts/`, then the pages. A rule with no check drifts — that is how 26 pages ended up citing
> `[[1985ltr.md#p0]]` while 10 cited `[[Sources/1985ltr]]`. `scripts/migrate_conventions.py`
> applies a changed convention across existing pages in one pass.
