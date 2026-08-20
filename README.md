# Warren Buffett Second Brain

[![wiki lint](https://github.com/RodriSPAUS/BuffettBrain/actions/workflows/lint.yml/badge.svg)](https://github.com/RodriSPAUS/BuffettBrain/actions/workflows/lint.yml)

A structured, interconnected knowledge base of Warren Buffett's investment philosophy — built so
that every claim it makes traces back to something he actually wrote or said.

Ask any LLM about Buffett and it will answer fluently, in his voice, with confident quotes — some
real, some invented, and no way to tell which from the outside. This repository is the opposite
bet: **breadth and analytical voice, with zero tolerance for a quotation that isn't verbatim in
the source.** A pre-commit hook and a CI check enforce that on every single change, not just at
review time.

## What's inside

- **69 raw sources** (1957–2024): every Buffett Partnership and Berkshire annual letter, five
  annual-meeting conference-call transcripts, and the Owner's Manual — compiled into **68 source
  summaries**, each a router with key themes, verbatim quotes, investment decisions and
  cross-references.
- **20 case studies** — GEICO, Coca-Cola, See's Candies, BNSF, Alleghany, the Japanese trading
  houses, and more — tracing each holding from first purchase to its role in the philosophy today.
- **10 concept pages** distilling the recurring mental models: moat, float, intrinsic value,
  margin of safety, owner earnings, circle of competence, capital allocation.
- **14 people profiles**, **5 cross-source synthesis pieces** tracking how ideas evolved across
  decades (e.g. what changed technically from 1977 to 2024 versus what never moved), and a growing
  set of principles and applied checklists.
- All of it cross-linked in Obsidian-native `[[wikilinks]]` — open it as a vault and the graph view
  shows which ideas are actually load-bearing.

## Why it's trustworthy, not just plausible

- **Citation integrity is mechanical, not aspirational.** `make quotes` checks every quoted
  passage in `wiki/` against the exact `Raw/` file it cites — byte for byte. `make figures` does
  the same for every number. Fail either, and the commit doesn't happen.
- **The source layer is immutable.** `Raw/` is human-curated and never rewritten by the agent —
  it's the one thing in the repo nothing gets to reinterpret.
- **The check runs before the damage exists, not after.** `make hooks` installs a pre-commit hook
  that refuses a fabricated quotation at the moment it's typed, and the same checks run again in
  CI on every push.
- **No silent gaps.** Every source summary has to account for every part of what it summarizes —
  a topic the letter covered and the summary skipped has to say so, so a missing section reads as
  a decision instead of an accident.

## Getting started

```
make hooks                             # once per clone — see below
make lint                              # run before closing any ingest
make quote Q="circle of competence"    # find a citable passage in Raw/
make new P=Sources/1978ltr             # start a page with the schema already correct
make check P=Sources/1978ltr           # zero-tolerance check on one finished page
make help                              # everything else
```

`make hooks` installs a pre-commit hook that refuses any commit containing a quotation that is
not in the letter it cites. It is the only check that runs before the damage exists rather than
after, so install it first.

## Layout

- `Raw/` — the sources, human-curated and never edited by the agent
- `wiki/` — the compiled layer, written and maintained by the agent
- `AGENTS.md` — what the agent does · `wiki/SCHEMA.md` — how a page is shaped
- `scripts/` — the checks that enforce both
- `LESSONS_LEARNED.md` — what has already gone wrong here, and what it cost

The `wiki/` directory structure is specified in `wiki/SCHEMA.md`, in one place on purpose: three
copies of a layout become three different layouts.

## Checks

`make lint` verifies that every quotation in `wiki/` appears verbatim in the letter it cites,
that every number matches the letter it cites, that no wikilink is broken, that frontmatter
matches the schema, that pages carry their required sections and meaningful tags, and that the
source text is intact enough to quote from. It runs on every push via GitHub Actions.

The citation check is the important one. A fabricated quotation is indistinguishable from a real
one once written, and propagates into every synthesis built on top of it — so the wiki is worth
exactly what that check says it is.

## How to use it (even if you have zero experience)

This repository is **LLM-agnostic**: it does not depend on any specific model or tool. It works
with Claude, GPT, Gemini, Llama, or whatever LLM you prefer, as long as the tool can read local
files and follow the instructions in `AGENTS.md`.

The core idea is simple: open the folder and point an AI coding agent at it. The agent reads
`AGENTS.md` first and then knows how to answer questions or maintain the wiki while keeping every
quote 100% accurate.

### 1. Clone the repository

```bash
git clone https://github.com/RodriSPAUS/BuffettBrain.git
cd BuffettBrain
make hooks          # recommended — installs the safety check for quotes
```

### 2. Open it in your editor / tool of choice

#### Option A — Claude Code (recommended for most people)

1. Install [Claude Code](https://claude.ai/code) if you haven't already.
2. Open a terminal inside the `BuffettBrain` folder.
3. Run:
   ```bash
   claude
   ```
4. Claude Code will automatically detect `AGENTS.md` / `CLAUDE.md` and load the instructions.
5. Start asking questions, for example:
   - "What does Buffett say about moats? Cite the sources."
   - "Summarize the Coca-Cola case and how it fits the philosophy."
   - "Ingest this new interview I just dropped into Raw/."

#### Option B — VS Code + AI extension

You can use any of these combinations:

| Tool | How to connect |
|------|----------------|
| **Cursor** | Open the folder with Cursor → it reads `AGENTS.md` automatically |
| **Continue.dev** (VS Code extension) | Open the folder → point Continue at the workspace |
| **GitHub Copilot Chat / Copilot Workspace** | Open the folder and start a chat in the workspace context |
| **Aider, Codex CLI, or similar** | Run the tool from inside the repo directory |

In all cases the agent should start by reading `AGENTS.md`. If it doesn't, just tell it:

> Read AGENTS.md and follow those instructions for this repository.

#### Option C — Obsidian (for browsing without AI)

The `wiki/` folder is fully compatible with [Obsidian](https://obsidian.md). Just open the
`BuffettBrain` folder as a vault. You get graph view, backlinks and the full knowledge network
without needing any LLM.

### 3. What you can do once connected

- **Query** — Ask any investment question. The agent answers in Buffett's analytical voice and
  cites real pages (`[[Sources/1996ltr]]`, `[[Concepts/Moat]]`, etc.).
- **Ingest** — Drop a new letter, interview or transcript into the `Raw/` folder and tell the
  agent to ingest it. It will create the summary, update related concept/case pages and keep
  everything linked.
- **Lint / maintain** — Ask the agent to run the checks (`make lint`) and fix any issues.

You never need to understand the internal structure. Just talk to the agent in natural language.

## Language

All stored content is English: wiki pages, file names, directory names, comments. Responses to
prompts come back in whatever language the prompt was written in.

## Contributing sources

Drop a new file in `Raw/` and ask the agent to ingest it. Naming is `YYYYltr.md` for annual
letters and `EventNameYYYY.md` for everything else. Anything Buffett-related counts: annual
letters (1957–present), interviews, speeches, articles, meeting transcripts.
