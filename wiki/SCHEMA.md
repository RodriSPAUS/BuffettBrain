# Warren Buffett Financial Brain — Schema

*This file defines how the wiki is **shaped**: directory layout, page structure, frontmatter, and linking conventions. It is the authority on how to write a page.*

*How the agent **behaves** — the Ingest / Query / Lint operations and the citation-integrity rules — is defined in `AGENTS.md`. The two files do not overlap; consult that one when deciding what to do, this one when writing.*

## ✅ Core Principles

- **Source fidelity first**: Every claim must be traceable to an original source (e.g., `Source: [[Sources/2024ltr]]`, `Source: [[Sources/DUKE2024]]`). Never paraphrase without attribution, and never present as a quotation any text that is not verbatim in the cited `Raw/` file — see *Citation Integrity* in `AGENTS.md`.
- **Obsidian-native**: All links use `[[wikilink]]` syntax. No external URLs in content — only `[[PageName]]` or `[[Sources/2024ltr]]`.
- **Concept-first organization**: Pages represent *ideas*, not just sources — e.g., `Concepts/Moat.md`, `Concepts/IntrinsicValue.md`, `Concepts/CapitalAllocation.md`. Source summaries (`Sources/2024ltr.md`) exist to feed and update these.
- **No human edits to wiki/**: This directory is LLM-owned. You curate `Raw/`; the LLM maintains `wiki/`.

## 📁 Directory Structure

```
wiki/
├── index.md              # Catalog of all pages (auto-updated on ingest)
├── log.md                # Append-only chronological log (e.g., "## [2026-07-27] ingest | Sources/2024ltr")
├── SCHEMA.md             # This file — wiki structure and page conventions
├── Sources/              # Source summaries (structured by year/content type)
│   ├── 1977ltr.md        # Source summary page for 1977 annual letter
│   ├── DUKE2024.md       # Source summary page for Duke University speech 2024
│   ├── CNBCInterview.md  # Source summary page for CNBC interview
│   └── ...
├── Concepts/             # Core mental models and frameworks
│   ├── Moat.md           # Concept page, seeded from all sources mentioning moats
│   ├── ManagementQuality.md
│   ├── CapitalAllocation.md
│   ├── Float.md
│   └── ...
├── Applications/         # Actionable tools and checklists
│   ├── BusinessQualityChecklist.md
│   └── RedFlags.md
├── Cases/                # Deep dives into key holdings and acquisitions
│   ├── GEICO.md
│   ├── SeeCandies.md
│   └── ...
├── People/               # Profiles of key figures
│   ├── WarrenBuffett.md
│   └── CharlieMunger.md
├── Principles/           # Enduring philosophies
│   ├── OwnershipMindset.md
│   └── Fidelity.md
└── Synthesis/            # Cross-source thematic analyses
    ├── MoatEvolution.md
    ├── FidelityTimeline.md
    └── FloatGrowth.md
```

## 📝 Page Conventions

### Source Summary Pages (e.g., `Sources/2024ltr.md`, `Sources/DUKE2024.md`)

- YAML frontmatter required:
  ```yaml
  ---
  title: "2024 Annual Letter"
  type: source-summary
  stability: high
  tags: [2024, letter, buybacks, cash-position, succession]   # see Tag Rules
  date: 2024-02-24
  year: 2024
  sourcetype: annual-letter  # annual-letter, interview, speech, article, etc.
  source: [[Raw/2024ltr.md]]
  ---
  ```
- Do not write this block by hand. `make new P=Sources/2024ltr` emits it correctly,
  with the letter's own signature date read out of `Raw/`.
- Content sections, all four required and checked by `make structure`: `## 🔑 Key Themes`,
  `## 💬 Notable Quotes`, `## 📊 Investment Decisions`, `## 🔗 Cross-References`
- **Cover what the source covers.** The page is a router into `Raw/`, so breadth beats
  depth: a topic the source spends real space on gets at least a line, and a topic
  deliberately passed over is named as passed over. `make coverage` lists subjects the
  source repeats that appear nowhere in `wiki/`.
- **At least one link into the compiled layer** (`Concepts/`, `Cases/`, `People/`,
  `Principles/`, `Applications/`, `Synthesis/`). A summary that links only to other
  summaries has been filed, not integrated, and `make structure` fails it.
- Each quote or insight cites the source page it came from (e.g., `[[Sources/2024ltr]]`), and the quoted text itself acts as the locator. Do **not** append positional anchors such as `#p5` or `#section3`: `Raw/` files carry no headings or block IDs, so those anchors resolve to nothing and imply a precision the citation does not have. Use an anchor only once the target file genuinely contains it.

### Concept Pages (e.g., `Concepts/Moat.md`)

- YAML frontmatter:
  ```yaml
  ---
  title: "Moat"
  type: concept
  stability: high  # low/medium/high — reflects how consistently Buffett uses this idea
  tags: [moat, competitive advantage, economic moat]
  date: 2026-07-27
  source: [[Sources/2024ltr]]
  ---
  ```
- Structure: open. A concept page needs a definition and grounded examples, but the
  headings are the writer's — rebuilt pages produced "The Lesson That Orders Everything
  Else" and "Why Integrity Is Weighted So Heavily", which beat the generic names they
  replaced. What *is* enforced is grounding: `make propagation` measures distinct sources
  cited per page, which is what "Examples from Letters" was a proxy for.
- Unlike `Sources/`, whose four headings are fixed: a summary is a router, and a reader
  scans the same four places on all 48 of them.
- Every example links to its source: e.g., `Coca-Cola (1988) — [[Sources/1988ltr]]`

### Synthesis Pages (e.g., `Synthesis/MoatEvolution.md`)

- YAML frontmatter:
  ```yaml
  ---
  title: "Moat Evolution"
  type: synthesis
  stability: medium
  tags: [cross-source, theme, evolution]
  date: 2026-07-27
  source: [[Sources/1988ltr]], [[Sources/2024ltr]], [[Sources/CNBCInterview]]
  ---
  ```
- Structure: Cross-source thematic analysis with explicit links to multiple sources
- Must reference at least 2 different sources to qualify as synthesis

## 🏷️ Tag Rules

Tags exist so Dataview can filter. A tag that is true of every page in the wiki
filters nothing, so `make structure` requires **at least three tags that say what
this page is about** and discounts the rest.

- Discounted: the year (it is already the `year:` key), and boilerplate —
  `annual-letter`, `letter`, `warren-buffett`, `berkshire-hathaway`, `investing`,
  `summary`, `finance` and similar. See `BOILERPLATE` in `scripts/check_structure.py`
  for the enforced list.
- Wanted: what distinguishes this page. `moat`, `float`, `buybacks`, `loss-reserving`,
  `misery-index`, `nebraska-furniture-mart`, `wppss`.
- A useful test: could this tag set belong to any other letter? If yes, it is not
  doing any work.

`tags: [annual-letter, 1995, warren-buffett, berkshire-hathaway]` is the failure this
rule exists to stop — a real page that would have carried the identical tag set had it
summarised any of the other 47 letters.

## 🔗 Linking Rules

- Always link entities: `[[Concepts/Moat]]`, `[[Concepts/ManagementQuality]]`, `[[Concepts/CapitalAllocation]]`
- Always link sources: `[[Sources/2024ltr]]`, `[[Sources/DUKE2024]]`, `[[Sources/CNBCInterview]]`
- Always link cases: `[[Cases/GEICO]]`, `[[Cases/SeeCandies]]`
- Always link people: `[[People/WarrenBuffett]]`, `[[People/CharlieMunger]]`
- Use relative paths within wiki: `[[Applications/BusinessQualityChecklist]]`, `[[Synthesis/MoatEvolution]]`
- Never leave a named person, company, or principle unlinked — if no page exists yet, create a stub with `TODO: flesh out`.
- **Never invent a link target.** `make new` prints every page that exists, grouped by
  directory, in the Cross-References section of the skeleton; copy from that list. A
  page that arrived with `[[Moat]]`, `[[Owner-Earnings]]`, `[[Ajit-Jain]]` and
  `[[Tony-Nicely]]` cost 19 broken links, and every one of them was a plausible guess
  at a name that already existed in another form.

## 🧹 Maintenance Workflow

The Ingest, Query, and Lint operations are specified in `AGENTS.md` and are not repeated here.
This file governs what a page must look like once one of those operations decides to write it.

Every rule on this page is checked by `make lint` — `make frontmatter` for the frontmatter
specifications above, `make links` for the linking rules below. Run `make quote Q="phrase"` to
get a passage in citable form before quoting it: `Raw/` files are hard-wrapped with compounds
split across lines, so text copied from `grep` will not match.

## 🌐 External Tools (Optional but Recommended)

- Use Obsidian **Dataview** plugin with frontmatter queries (e.g., `TABLE year FROM "wiki" WHERE type = "source-summary" SORT year DESC`).
  These only return complete results while `make frontmatter` passes — a page with a missing or
  non-canonical `type` silently drops out of every query.
- Use Obsidian **Graph View** to visualize conceptual centrality (e.g., which concepts are most linked?)
- Use Obsidian **Outliner** or **Templater** for consistent page scaffolding.

> 💡 This schema evolves. If you adjust a rule (e.g., add `Concepts/RiskManagement.md`), update
> this file first, then update the corresponding check in `scripts/`, then reprocess the wiki.
> A rule with no check will drift: that is how 26 pages ended up citing `[[1985ltr.md#p0]]`
> while 10 cited `[[Sources/1985ltr]]`. `scripts/migrate_conventions.py` applies a changed
> convention to existing pages in one pass.
