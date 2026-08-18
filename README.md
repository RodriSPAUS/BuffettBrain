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

## Use it with an AI agent

The repo is written for an LLM agent (Claude Code, Codex, Cursor, or similar) to maintain and
query directly — `AGENTS.md` is the entry point any agent reads first. Point one at this repo and
you can ask investment questions in Buffett's analytical voice with every claim cited, or hand it
a new letter/interview/transcript to ingest and watch it propagate through the wiki.

## Language

All stored content is English: wiki pages, file names, directory names, comments. Responses to
prompts come back in whatever language the prompt was written in.

## Contributing sources

Drop a new file in `Raw/` and ask the agent to ingest it. Naming is `YYYYltr.md` for annual
letters and `EventNameYYYY.md` for everything else. Anything Buffett-related counts: annual
letters (1957–present), interviews, speeches, articles, meeting transcripts.
