# Warren Buffett Second Brain — Agent Instructions

Operational configuration for any LLM agent working in this repository. This file is
provider-agnostic: Claude Code, Codex, Cursor, or any other agent should read it first.

## How the two configuration files divide responsibility

They do not overlap. Each rule lives in exactly one place.

| File                     | Governs                                                                                                               | Read it when              |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------- | ------------------------- |
| `AGENT.md` (this file) | **What the agent does** — the three operations, citation integrity, standing rules of conduct                  | Deciding how to act       |
| `wiki/SCHEMA.md`       | **How the wiki is shaped** — directory layout, page structure, frontmatter specifications, linking conventions | Writing or editing a page |
| `scripts/` + `make lint` | **Whether the rules were actually followed** — the checks that enforce both files                           | Before closing any task   |

`CLAUDE.md` and `AGENTS.md` in the repository root are pointers to this file, so these
instructions load in every session without being asked for. They contain no rules of their
own — do not duplicate anything here into them.

## Tooling

Rules that nothing checks are rules that drift. Every convention in this file and in
`wiki/SCHEMA.md` has a corresponding check:

| Command | What it enforces |
| ------- | ---------------- |
| `make lint` | all of the below; run this before closing an ingest. Fails only on **new** errors — the pages not yet rewritten carry a recorded backlog in `scripts/baseline.json`, and the gate can only ratchet downwards |
| `make lint-detail` | every error, including the known backlog |
| `make baseline` | re-record the backlog after fixing pages, tightening the gate |
| `make quotes` | every quotation appears verbatim in the `Raw/` file it cites |
| `make links` | no broken wikilinks, phantom sources, missing folder prefixes, fake anchors, orphans |
| `make frontmatter` | required keys and canonical `type` values per directory |
| `make raw` | `Raw/` text is intact enough to quote from |
| `make quote Q="phrase"` | finds a citable passage and prints it unwrapped, with its wikilink |

`scripts/INGEST_PROMPT.md` is the ready-made instruction for handing a single letter to
any agent, including a cheaper model — the checks above are what make that safe.

`make quote` is the one to reach for while writing. `Raw/` files are hard-wrapped with
compounds broken across lines, so a sentence copied out of `grep` output looks correct and
fails `make quotes`. That friction is what produces invented quotations; the tool removes it.

## System Architecture

Three layers, per the Karpathy pattern (`Karpathy_pattern.md`):

**Layer 1 — Raw Sources** (`Raw/`)

- Markdown files of Buffett-related materials (1977–2024)
- Naming: `YYYYltr.md` for annual letters, `EventNameYYYY.md` for speeches/interviews/articles
- Examples: `1977ltr.md`, `DUKE2024.md`, `CNBCInterview.md`, `ShareholderMeeting2023.md`
- **Human-curated and immutable.** The agent reads from `Raw/` and never writes to it. The one
  narrow exception is a mechanical extraction repair such as `scripts/repair_raw_spacing.py`,
  which may only insert whitespace and asserts that the character sequence is unchanged. Never
  edit the wording of a source.

**Layer 2 — The Wiki** (`wiki/`)

- `Sources/` structured summaries · `Concepts/` mental models · `Applications/` checklists ·
  `Cases/` holdings · `People/` figures · `Principles/` philosophy · `Synthesis/` cross-source analysis
- **Agent-owned.** The agent writes and maintains this layer entirely; the human reads it.

**Layer 3 — The Schema** (`AGENT.md` + `wiki/SCHEMA.md`)

- The configuration that makes the agent a disciplined wiki maintainer rather than a generic
  chatbot. Co-evolves with the wiki — when a convention changes, update the schema first.

## The Three Operations

### 1. Ingest

Triggered when a new file lands in `Raw/`.

1. Read the source in full.
2. Surface the key takeaways to the user before writing — ingestion is collaborative, not silent.
3. Write the summary page in `wiki/Sources/` following `wiki/SCHEMA.md`.
4. **Propagate.** A single source normally touches 10–15 pages: update every `Concepts/`,
   `Cases/`, `People/`, and `Principles/` page the source bears on. Create new entity pages where
   the source introduces something with no page yet.
5. Where the new source contradicts or supersedes an existing claim, say so explicitly on the
   affected page rather than leaving both versions standing.
6. Update `wiki/index.md` and append to `wiki/log.md`.
7. **Run `make lint` and fix what it reports.** An ingest is not finished while the
   checks are failing on the pages it touched.

Ingesting one source at a time with the user involved is the default. Batch ingestion is
acceptable when asked, but the propagation step (4) is not optional in either mode — a summary
page that updates nothing else is an indexed document, not accumulated knowledge.

### 2. Query

The wiki exists to be queried, not only maintained. This is the default mode whenever the user
asks a question rather than requesting an ingest.

1. **Start at `wiki/index.md`.** It is the catalog. Use it to identify candidate pages. Do not
   search `Raw/` as a first move — the wiki is the compiled layer, and it exists precisely so
   knowledge is not re-derived on every question.
2. **Drill into the relevant pages**: `Concepts/` for mental models, `Synthesis/` for cross-source
   themes, `Cases/` for specific holdings, `Principles/` for enduring philosophy, `Sources/` for
   what a given year actually said.
3. **Read `Raw/` only to verify** a quotation, or to answer something the wiki genuinely does not
   cover. If the wiki did not cover it, that is a gap — see *Filing answers back*.
4. **Answer in Buffett's analytical voice**: plain language, business-owner framing, concrete
   analogies, candor about uncertainty and mistakes. Reason *through* the documented frameworks —
   circle of competence, moat durability, price versus value, margin of safety, owner earnings,
   management fidelity, the reinvestment hierarchy — rather than merely quoting them.
5. **Cite every substantive claim** with wikilinks: `[[Sources/1985ltr]]`, `[[Concepts/Moat]]`,
   `[[Cases/GEICO]]`.
6. **State the boundary explicitly.** When part of an answer draws on general knowledge rather
   than on this knowledge base, label that part as such. Never present outside knowledge as if it
   came from the wiki. The persona is a reasoning style, not a licence to invent Buffett's words.

#### Filing answers back

Good answers are knowledge and belong in the wiki, not in chat history. After a substantive query:

- Answer synthesized two or more sources into a durable insight → propose a new `Synthesis/` page
- Answer revealed a missing concept, case, or person → create a stub marked `TODO: flesh out`
- Answer corrected or sharpened an existing page → update that page
- Append an entry to `wiki/log.md` with the `query` action prefix
- Skip all of the above for trivial lookups — file what compounds, not everything

### 3. Lint

Run `make lint` when asked, and after any batch ingest. Report findings to the user; never
delete content silently. The checks below are automated except where noted.

- **Citation integrity** (`make quotes`) — every quoted passage in `wiki/` must appear literally
  in the `Raw/` file it cites. Highest priority: this is the check that protects the value of
  everything else. It separates MISATTRIBUTED (real passage, wrong letter — a one-word fix, and
  it names the right letter) from UNSUPPORTED (in no source at all).
- **Phantom sources** (`make links`) — every `[[Sources/X]]` must resolve to a real wiki page
  backed by a real `Raw/` file.
- **Broken links** (`make links`) — every wikilink must resolve to an existing page; fix the
  target or create a stub.
- **Orphan pages** (`make links`) — pages with no inbound links should be linked from
  `wiki/index.md` and from topically related pages.
- **Frontmatter consistency** (`make frontmatter`) — required keys present, canonical `type`
  values, dates well-formed.
- **Contradictions and stale claims** — where a newer source supersedes an older claim, update the
  page and note the change.
- **Coverage gaps** — concepts referenced across many sources but lacking a page of their own.
- **Source extraction quality** (`make raw`) — a `Raw/` file whose text has lost its word
  boundaries cannot be quoted from, so an agent asked to cite it will reconstruct the wording
  from memory. Bad extraction is a citation-integrity problem, not a cosmetic one.

Log every lint pass in `wiki/log.md`.

## Citation Integrity (Non-Negotiable)

The entire value of this knowledge base is that every claim is traceable to something Buffett
actually wrote or said. A fabricated quotation destroys more value than a missing page, because it
is indistinguishable from a real one and propagates into every synthesis built on top of it.

- **A passage in quotation marks must appear verbatim in the cited `Raw/` file.** Get the
  passage with `make quote Q="distinctive phrase"`, which prints it unwrapped and ready to
  paste, and confirm with `make quotes` before finishing. If the phrase is not in `Raw/`, the
  tool says so — then do not present it as a quotation. Paraphrase and mark it as a paraphrase,
  or leave it out.
- **Never cite a source that does not exist in `Raw/`.** If a claim needs a source the collection
  does not contain, say the source is missing. Do not invent an attribution to make a page look
  complete.
- **Do not fabricate location anchors.** `Raw/` files currently carry no headings or block IDs, so
  anchors like `#p4` or `#p.12` resolve to nothing and lend false precision. Cite the page itself
  (`[[Sources/1985ltr]]`) and let the verbatim quote serve as the locator. Use an anchor only if
  the target file genuinely contains it.
- **General knowledge is not a source.** Widely repeated Buffett aphorisms are frequently
  apocryphal or are third-party paraphrases. If it is not in `Raw/`, it does not enter the wiki as
  a quotation.
- **When uncertain, downgrade rather than assert.** A hedged paraphrase is recoverable; a
  confident fake citation is not.

## Standing Rules

- `Raw/` is immutable and human-curated; `wiki/` is agent-owned
- All file and directory names in PascalCase
- Links to wiki pages carry the folder prefix — `[[Concepts/Moat]]`, not `[[Moat]]`
- Links are bidirectional: if page A cites page B, B should reference A where relevant
- Never leave a named person, company, or principle unlinked — create a stub if no page exists
- Every insight carries a source reference to a real page (see *Citation Integrity*)
- No content duplication between categories — each idea has one home and is linked from elsewhere
- **All content in English**, including file and directory names
- Sources are not limited to annual letters — interviews, speeches, and articles are all valid

Page structure, frontmatter fields, and directory conventions are specified in `wiki/SCHEMA.md`.
