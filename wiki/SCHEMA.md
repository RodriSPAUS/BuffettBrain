# Warren Buffett Financial Brain — Schema

*This file defines how the wiki is **shaped**: directory layout, page structure, frontmatter, and linking conventions. It is the authority on how to write a page.*

*How the agent **behaves** — the Ingest / Query / Lint operations and the citation-integrity rules — is defined in `AGENT.md`. The two files do not overlap; consult that one when deciding what to do, this one when writing.*

## ✅ Core Principles

- **Source fidelity first**: Every claim must be traceable to an original source (e.g., `Source: [[Sources/2024ltr]]`, `Source: [[Sources/DUKE2024]]`). Never paraphrase without attribution, and never present as a quotation any text that is not verbatim in the cited `Raw/` file — see *Citation Integrity* in `AGENT.md`.
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
  source: [[Raw/2024ltr.md]]
  date: 2024-02-24
  type: source-summary
  year: 2024
  sourcetype: annual-letter  # annual-letter, interview, speech, article, etc.
  ---
  ```
- Content sections: `## Key Themes`, `## Notable Quotes`, `## Investment Decisions`, `## Cross-References`
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
- Structure: `## Definition`, `## Examples from Letters`, `## Contrasts & Nuances`
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

## 🔗 Linking Rules

- Always link entities: `[[Concepts/Moat]]`, `[[Concepts/ManagementQuality]]`, `[[Concepts/CapitalAllocation]]`
- Always link sources: `[[Sources/2024ltr]]`, `[[Sources/DUKE2024]]`, `[[Sources/CNBCInterview]]`
- Always link cases: `[[Cases/GEICO]]`, `[[Cases/SeeCandies]]`
- Always link people: `[[People/WarrenBuffett]]`, `[[People/CharlieMunger]]`
- Use relative paths within wiki: `[[Applications/BusinessQualityChecklist]]`, `[[Synthesis/MoatEvolution]]`
- Never leave a named person, company, or principle unlinked — if no page exists yet, create a stub with `TODO: flesh out`.

## 🧹 Maintenance Workflow

The Ingest, Query, and Lint operations are specified in `AGENT.md` and are not repeated here.
This file governs what a page must look like once one of those operations decides to write it.

## 🌐 External Tools (Optional but Recommended)

- Use Obsidian **Dataview** plugin with frontmatter queries (e.g., `TABLE year FROM "wiki" WHERE type = "source-summary" SORT year DESC`)
- Use Obsidian **Graph View** to visualize conceptual centrality (e.g., which concepts are most linked?)
- Use Obsidian **Outliner** or **Templater** for consistent page scaffolding.

> 💡 This schema evolves. If you adjust a rule (e.g., add `Concepts/RiskManagement.md`), update this file first — then instruct the LLM to reprocess the wiki.
