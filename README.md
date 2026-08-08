# Warren Buffett Second Brain

A structured, interconnected knowledge base of Warren Buffett's investment philosophy, compiled
from annual letters, interviews, speeches and articles, and organised according to the Karpathy
pattern (`Karpathy_pattern.md`).

## Layout

- `Raw/` — the sources, human-curated and never edited by the agent
- `wiki/` — the compiled layer, written and maintained by the agent
- `AGENTS.md` — what the agent does · `wiki/SCHEMA.md` — how a page is shaped
- `scripts/` — the checks that enforce both
- `LESSONS_LEARNED.md` — what has already gone wrong here, and what it cost

The `wiki/` directory structure is specified in `wiki/SCHEMA.md`, in one place on purpose: three
copies of a layout become three different layouts.

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

## Checks

`make lint` verifies that every quotation in `wiki/` appears verbatim in the letter it cites,
that no wikilink is broken, that frontmatter matches the schema, that pages carry their required
sections and meaningful tags, and that the source text is intact enough to quote from. It runs on
every push via GitHub Actions.

The citation check is the important one. A fabricated quotation is indistinguishable from a real
one once written, and propagates into every synthesis built on top of it — so the wiki is worth
exactly what that check says it is.

## Language

All stored content is English: wiki pages, file names, directory names, comments. Responses to
prompts come back in whatever language the prompt was written in.

## Contributing sources

Drop a new file in `Raw/` and ask the agent to ingest it. Naming is `YYYYltr.md` for annual
letters and `EventNameYYYY.md` for everything else. Anything Buffett-related counts: annual
letters (1977–present), interviews, speeches, articles, meeting transcripts.
