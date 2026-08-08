# Warren Buffett Second Brain — Agent Instructions

Operational configuration for any LLM agent working in this repository. Provider-agnostic:
Claude Code, Codex, Cursor or any other agent reads this first. It is named `AGENTS.md`
because that is the filename agent CLIs load on their own; `CLAUDE.md` imports it and holds
no rules of its own.

## Where each rule lives

Each rule lives in exactly one place. These files do not overlap.

| File | Governs | Read it when |
| --- | --- | --- |
| `AGENTS.md` (this file) | **What the agent does** — the three operations, citation integrity, conduct | deciding how to act |
| `wiki/SCHEMA.md` | **How a page is shaped** — directory layout, page structure, frontmatter, linking | writing or editing a page |
| `Makefile` + `scripts/` | **Whether the rules were followed** | before closing any task |
| `LESSONS_LEARNED.md` | **What has already gone wrong here** | before changing how you work; append to it after any session that hit a problem |

Together the first two are Layer 3 of `Karpathy_pattern.md`, split because conduct and form
change at different rates.

**`wiki/SCHEMA.md` is part of these instructions, not a reference you may skip.** The line
below imports it for agents that support imports; for those that do not, open it.

@wiki/SCHEMA.md

Better still, do not write a page from memory of the schema. `make new P=Sources/1978ltr`
emits the frontmatter, the required sections, and the list of pages that actually exist to
link to. Fill in the prose.

## Language

Respond in the language the user wrote in — queries, ingests, lint reports, all of it.
Everything *stored* is English regardless: page text, file names, directory names.

## Setup

    make hooks

Once per clone. It installs a pre-commit hook that refuses any commit containing a quotation
that is not in the letter it cites — the only check that runs before the damage exists rather
than after. Everything else in this file tells you what to do; this is what happens when you
do not.

## Tooling

A rule that nothing checks is a rule that drifts. Every convention in this file and in
`wiki/SCHEMA.md` has a check behind it:

| Command | What it enforces |
| ------- | ---------------- |
| `make lint` | all of the below; run before closing an ingest. Fails only on **new** errors — the pages not yet rewritten carry a recorded backlog in `scripts/baseline.json`, and the gate can only ratchet downwards |
| `make check P=Sources/1996ltr` | **zero tolerance on one page.** Run it on every page you finish: `make lint` forgives errors a file already had, which is right for the backlog and wrong for a page you just wrote |
| `make quote Q="phrase"` | finds a citable passage and prints it unwrapped, with its wikilink |
| `make quotes` | every quotation appears verbatim in the `Raw/` file it cites |
| `make figures` | every number on a page appears in the letter it cites |
| `make links` | no broken wikilinks, phantom sources, missing folder prefixes, fake anchors, orphans |
| `make frontmatter` | required keys and canonical `type` values per directory |
| `make structure` | required sections per directory, at least one link into the compiled layer, tags that say something |
| `make coverage` | subjects a source repeats that appear nowhere in `wiki/` — the check for *did the summary leave something out*. Warnings, not errors: some repeated names are genuinely disposable |
| `make propagation` | are ingested sources reaching the compiled layer? Coverage and distinct sources per page |
| `make raw` | `Raw/` text is intact enough to quote from |
| `make lint-detail` | every error, including the known backlog |
| `make baseline` | re-record the backlog after fixing pages, tightening the gate. Never run it while known fabrications are still in the wiki: it would bless them |

`make quote` is the one to reach for while writing. `Raw/` files are hard-wrapped with
compounds broken across lines, so a sentence copied out of `grep` output looks correct and
fails `make quotes`. That friction is what produces invented quotations; the tool removes it.

## System Architecture

Three layers, per `Karpathy_pattern.md`:

**Layer 1 — Raw Sources** (`Raw/`)

- Markdown of Buffett-related material, 1977–2024
- Naming: `YYYYltr.md` for annual letters, `EventNameYYYY.md` for everything else —
  `DUKE2024.md`, `CNBCInterview.md`, `ShareholderMeeting2023.md`
- **Human-curated and immutable.** The agent reads `Raw/` and never writes to it. The one
  narrow exception is a mechanical extraction repair such as `scripts/repair_raw_spacing.py`,
  which may only insert whitespace and asserts the character sequence is unchanged. Never edit
  the wording of a source.

**Layer 2 — The Wiki** (`wiki/`)

- `Sources/` summaries · `Concepts/` mental models · `Applications/` checklists ·
  `Cases/` holdings · `People/` figures · `Principles/` philosophy · `Synthesis/` cross-source analysis
- **Agent-owned.** The agent writes and maintains this layer entirely; the human reads it.

**Layer 3 — The Schema** (`AGENTS.md` + `wiki/SCHEMA.md`)

- What makes the agent a disciplined wiki maintainer rather than a generic chatbot.
  Co-evolves with the wiki: when a convention changes, update the schema first, then the
  check in `scripts/`, then the pages.

### What `Sources/` is for

A source summary is not the product. It is the **router**: the page that lets you find, months
later, which of 48 letters bears on a question, and recall enough to know whether to open the
original. `Raw/` stays the source of truth, and any claim that has to be exact is taken from
there.

That decides what a good summary optimises for. A router is judged on **breadth, not depth**:
one honest line about USAir sends you to the 1996 letter; five beautiful paragraphs on three
themes and silence on five others does not. **Cover everything the source covers.** Where a
topic carries nothing worth recording, say so in a clause rather than dropping it silently —
an omission and a judgment look identical afterwards, and only one of them is a decision.

## The Three Operations

### 1. Ingest

Triggered when a new file lands in `Raw/`.

1. Read the source in full.
2. **Enumerate its parts before summarising any of them** — sections for a letter, agenda
   items or speakers for a call, chapters for a transcript — and account for each one.
   Anything left out is left out on purpose and said so. This is what stops a summary from
   being an impression of the source rather than a map of it.
3. Surface the key takeaways to the user before writing — ingestion is collaborative, not silent.
4. Write the summary page in `wiki/Sources/` following `wiki/SCHEMA.md`.
5. **Propagate.** A single source normally touches 10–15 pages: update every `Concepts/`,
   `Cases/`, `People/` and `Principles/` page the source bears on, and create entity pages
   where the source introduces something that has none.
6. Where the new source contradicts or supersedes an existing claim, say so explicitly on the
   affected page rather than leaving both versions standing.
7. Update `wiki/index.md` and append to `wiki/log.md`.
8. **Run `make check P=Sources/YYYYltr` on the page you wrote and fix everything it reports.**
   It demands zero errors. Then `make lint` for the repository. An ingest is not finished
   while either is failing.

One source at a time, with the user involved, is the default. Batch ingestion is fine when
asked — but step 5 is not optional in either mode. A summary page that updates nothing else is
an indexed document, not accumulated knowledge.

#### Propagation has two modes. Know which one you are in.

Step 5 is the step with no termination condition and no checker, and it gets skipped more than
any other. The reason is that *catching up on a backlog* and *keeping a compiled wiki current*
are different tasks wearing the same name:

| | Backlog (many sources, nothing compiled) | Steady state (one new source, pages already rich) |
| --- | --- | --- |
| Fan-out per source | 0–21 pages, unpredictable | small and obvious |
| Judgment needed | how does this idea evolve across the whole corpus? | does this source change what the page already says? |
| Terminates? | no | yes |

**In steady state, propagate normally.** Step 5 applies in full: a new source lands in pages
that already trace their idea across decades, so the work is bounded and each decision is close
to yes/no.

**On a backlog, invert and batch.** Do not attempt 48 sources × unpredictable fan-out. Write
the summaries first, then rebuild each compiled page once from the whole corpus — "rebuild
`Concepts/Moat` from all 48 letters" terminates and can be checked. Run it after the summaries
exist: the arc of an idea is not visible while you are still writing year three.

Either way, `make propagation` reports whether it happened. If depth does not rise as you
ingest, propagation is not occurring and nothing else will tell you.

### 2. Query

The wiki exists to be queried, not only maintained. This is the default mode whenever the user
asks a question rather than requesting an ingest.

1. **Start at `wiki/index.md`.** It is the catalog; use it to pick candidate pages. Do not
   search `Raw/` as a first move — the wiki is the compiled layer and exists precisely so
   knowledge is not re-derived on every question.
2. **Drill into the relevant pages**: `Concepts/` for mental models, `Synthesis/` for
   cross-source themes, `Cases/` for holdings, `Principles/` for enduring philosophy,
   `Sources/` for what a given year actually said.
3. **Read `Raw/` to verify** a quotation, or to answer something the wiki genuinely does not
   cover. If the wiki did not cover it, that is a gap — see *Filing answers back*.
4. **Answer in Buffett's analytical voice**: plain language, business-owner framing, concrete
   analogies, candour about uncertainty and mistakes. Reason *through* the documented
   frameworks — circle of competence, moat durability, price versus value, margin of safety,
   owner earnings, management fidelity, the reinvestment hierarchy — rather than quoting them.
5. **Cite every substantive claim** with wikilinks: `[[Sources/1985ltr]]`, `[[Concepts/Moat]]`,
   `[[Cases/GEICO]]`.
6. **State the boundary explicitly.** When part of an answer draws on general knowledge rather
   than on this knowledge base, label that part as such. The persona is a reasoning style, not
   a licence to invent Buffett's words.

#### Filing answers back

Good answers are knowledge and belong in the wiki, not in chat history. After a substantive query:

- Synthesized two or more sources into a durable insight → propose a new `Synthesis/` page
- Revealed a missing concept, case or person → create a stub marked `TODO: flesh out`
- Corrected or sharpened an existing page → update that page
- Append an entry to `wiki/log.md` with the `query` action prefix
- Skip all of the above for trivial lookups — file what compounds, not everything

### 3. Lint

Run `make lint` when asked, and after any batch ingest. Report findings to the user; never
delete content silently. Automated except where noted.

- **Citation integrity** (`make quotes`) — every quoted passage appears literally in the `Raw/`
  file it cites. Highest priority: it protects the value of everything else. It separates
  MISATTRIBUTED (real passage, wrong letter — a one-word fix, and the message names the right
  letter) from UNSUPPORTED (in no source at all).
- **Figures** (`make figures`) — numbers on a page against the letter it cites.
- **Phantom sources, broken links, orphans** (`make links`) — every `[[Sources/X]]` resolves to
  a real page backed by a real `Raw/` file; every wikilink resolves; pages with no inbound
  links get linked from `wiki/index.md` and from topically related pages.
- **Frontmatter** (`make frontmatter`) — required keys, canonical `type` values, well-formed dates.
- **Structure and tags** (`make structure`) — required sections, a link into the compiled layer,
  tags that distinguish the page.
- **Source extraction quality** (`make raw`) — a `Raw/` file that has lost its word boundaries
  cannot be quoted from, so an agent asked to cite it reconstructs the wording from memory. Bad
  extraction is a citation-integrity problem, not a cosmetic one.
- **Contradictions and stale claims** *(judgment, not automated)* — where a newer source
  supersedes an older claim, update the page and note the change.
- **Coverage gaps** *(judgment, not automated)* — concepts referenced across many sources but
  lacking a page of their own.

Log every lint pass in `wiki/log.md`.

## Citation Integrity (Non-Negotiable)

The entire value of this knowledge base is that every claim is traceable to something Buffett
actually wrote or said. A fabricated quotation destroys more value than a missing page: it is
indistinguishable from a real one and propagates into every synthesis built on top of it.

**Everything in `wiki/` traces back to `Raw/`.** Every sentence you write is grounded either
in a `Raw/` file you have read in this session, or in a `wiki/` page that is itself grounded
that way. Nothing else is a permitted input — not your training data, not what is generally
known about Berkshire, not what a letter of that era would plausibly have said. When you
cannot ground a claim, the claim does not go on the page. There is no case in which inventing
is better than omitting, and no deadline that changes this.

- **A passage in quotation marks must appear verbatim in the cited `Raw/` file.** Get it with
  `make quote Q="distinctive phrase"`, which prints it unwrapped and ready to paste, and
  confirm with `make quotes` before finishing. If the tool says the phrase is not in `Raw/`,
  it is not a quotation: paraphrase and mark it as a paraphrase, or leave it out.
- **Numbers are claims too.** A figure carries the same burden as a quotation and is checked
  the same way (`make figures`). Do not round a number into a different one, and do not restate
  a percentage as an absolute unless the source gives both.
- **Never cite a source that does not exist in `Raw/`.** If a claim needs a source the
  collection does not contain, say the source is missing. Do not invent an attribution to make
  a page look complete.
- **Do not fabricate location anchors.** `Raw/` files carry no headings or block IDs, so
  anchors like `#p4` resolve to nothing and lend false precision. Cite the page
  (`[[Sources/1985ltr]]`) and let the verbatim quote be the locator.
- **General knowledge is not a source.** Widely repeated Buffett aphorisms are frequently
  apocryphal or are third-party paraphrases. If it is not in `Raw/`, it does not enter the wiki
  as a quotation.
- **When uncertain, downgrade rather than assert.** A hedged paraphrase is recoverable; a
  confident fake citation is not.
- **Report the state of the work truthfully.** "Clean" means a check was run and passed, not
  that you expect it would. If something is unverified, unfinished or failing, say which.

## Standing Rules

- `Raw/` is immutable and human-curated; `wiki/` is agent-owned
- All file and directory names in PascalCase
- Links to wiki pages carry the folder prefix — `[[Concepts/Moat]]`, not `[[Moat]]`
- Links are bidirectional: if page A cites page B, B references A where relevant
- Never leave a named person, company or principle unlinked — create a stub if no page exists
- No content duplication between categories — each idea has one home and is linked from elsewhere
- **All content in English**, including file and directory names
- Sources are not limited to annual letters — interviews, speeches and articles are all valid
- **Record what goes wrong.** Any session that hits a difficulty, finds a rule that was written
  but not followed, needs a tool that does not exist, or produces work that has to be redone,
  appends an entry to `LESSONS_LEARNED.md` before finishing. Append, never rewrite. State the
  cost in numbers — a lesson without a measured cost is an opinion.

Page structure, frontmatter fields and directory conventions are specified in `wiki/SCHEMA.md`.
