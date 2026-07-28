# Warren Buffett Financial Brain — Schema

*This is the authoritative configuration file for the LLM-maintained wiki. It defines conventions, workflows, and rules for ingestion, linking, and maintenance.*

## ✅ Core Principles

- **Source fidelity first**: Every claim must be traceable to an original letter (e.g., `Source: [[2024ltr.md]]`). Never paraphrase without attribution.
- **Obsidian-native**: All links use `[[wikilink]]` syntax. No external URLs in content — only `[[PageName]]` or `[[2024ltr.md]]`.
- **Concept-first organization**: Pages represent *ideas*, not just sources — e.g., `Moat.md`, `Intrinsic-Value.md`, `Capital-Allocation.md`. Source summaries (`2024ltr.md`) exist to feed and update these.
- **No human edits to wiki/**: This directory is LLM-owned. You curate `Raw/`; the LLM maintains `wiki/`.

## 📁 Directory Structure

```
wiki/
├── index.md          # Catalog of all pages (auto-updated on ingest)
├── log.md            # Append-only chronological log (e.g., "## [2026-07-27] ingest | 2024ltr.md")
├── SCHEMA.md         # This file — the single source of truth for wiki rules
├── 2024ltr.md        # Source summary page for 2024 letter
├── 2023ltr.md        # ...and so on
├── Moat.md           # Concept page, seeded from all letters mentioning moats
├── Margin-of-Safety.md
├── Intrinsic-Value.md
├── Management-Quality.md
└── ...
```

## 📝 Page Conventions

### Source Summary Pages (e.g., `2024ltr.md`)
- YAML frontmatter required:
  ```yaml
  ---
  source: 2024ltr.md
  date: 2024-02-24
  type: source-summary
  year: 2024
  ---
  ```
- Content sections: `## Key Themes`, `## Notable Quotes`, `## Investment Decisions`, `## Cross-References`
- Each quote or insight must cite its location (e.g., "p. 5", "Section: 'Market Outlook'") if available.

### Concept Pages (e.g., `Moat.md`)
- YAML frontmatter:
  ```yaml
  ---
  type: concept
  stability: high  # low/medium/high — reflects how consistently Buffett uses this idea
  ---
  ```
- Structure: `## Definition`, `## Types`, `## Examples from Letters`, `## Evolution Over Time`
- Every example links to its source: e.g., `Coca-Cola (1988) — [[1988.md]]`

## 🔗 Linking Rules

- Always link entities: `[[Coca-Cola]]`, `[[American-Express]]`, `[[GEICO]]`
- Always link concepts: `[[Moat]]`, `[[Margin-of-Safety]]`, `[[Circle-of-Competence]]`
- Always link sources: `[[2024ltr.md]]`, `[[2023ltr.md]]`
- Never leave a named person, company, or principle unlinked — if no page exists yet, create a stub with `TODO: flesh out`.

## 🧹 Maintenance Workflow

- On ingest of new source: update `index.md`, `log.md`, relevant concept pages, and create new entity pages as needed.
- On query: synthesize answer from existing wiki pages; if answer reveals a gap (e.g., no `Circle-of-Competence.md`), create stub and log it.
- Weekly lint: check for orphaned pages, broken links, contradictions, and stale claims.

## 🌐 External Tools (Optional but Recommended)

- Use Obsidian **Dataview** plugin with frontmatter queries (e.g., `TABLE year FROM "wiki" WHERE type = "source-summary" SORT year DESC`)
- Use Obsidian **Graph View** to visualize conceptual centrality (e.g., which concepts are most linked?)
- Use Obsidian **Outliner** or **Templater** for consistent page scaffolding.

> 💡 This schema evolves. If you adjust a rule (e.g., add `risk-tolerance.md`), update this file first — then instruct the LLM to reprocess the wiki.