# Warren Buffett Second Brain

This is a structured, interconnected knowledge base for Warren Buffett's investment philosophy and core principles, compiled from various sources including annual letters, interviews, speeches, and articles, organized according to the Karpathy pattern.

## Language Policy

**All content in this knowledge base is in English.** This includes:
- All wiki pages in the `wiki/` directory
- All source summaries in `wiki/Sources/` (annual letters, interviews, speeches, etc.)
- All concept pages in `wiki/Concepts/`
- All cross-source syntheses in `wiki/Synthesis/`
- All file names and directory names
- All comments and documentation

However, **responses to user prompts will be provided in the same language as the user's input**. The system will detect the language of the incoming query and respond in kind, while maintaining all English content standards for the actual knowledge base entries. This allows international users to interact with the system in their native language while preserving the English standard for all stored content and documentation.

## Layout

- `Raw/` — the source letters, human-curated and not edited by the agent
- `wiki/` — the compiled layer, written and maintained by the agent
- `AGENT.md` — what the agent does; `wiki/SCHEMA.md` — how a page is shaped
- `scripts/` — the checks that enforce both

The directory structure of `wiki/` is specified in `wiki/SCHEMA.md`. It is documented in one
place on purpose: three copies of a layout become three different layouts.

## Checks

```
make lint                      # run before closing any ingest
make quote Q="circle of competence"   # find a citable passage in Raw/
```

`make lint` verifies that every quotation in `wiki/` appears verbatim in the letter it cites,
that no wikilink is broken, that frontmatter matches the schema, and that the source text is
intact enough to quote from. It runs on every push via GitHub Actions.

The citation check is the important one. A fabricated quotation is indistinguishable from a
real one once written and propagates into every synthesis built on top of it, so the wiki is
worth exactly what that check says it is.

## Contributing

All new additions must be in English. Please follow the conventions established in `wiki/SCHEMA.md` and maintain bidirectional linking throughout the knowledge base. Sources can include:
- Annual shareholder letters (1977-present)
- Interviews (TV, radio, print)
- Speeches and presentations
- Articles and commentary
- Other Buffett-related materials

## Purpose

This knowledge base organizes Warren Buffett's investment philosophy, principles, and case studies extracted from various sources. Each concept is linked to its original source for reference and verification.