# Ingest prompt — one annual letter into `wiki/Sources/`

Paste this to any coding agent working inside this repository, replacing `YYYY`
with the year. It is deliberately explicit about the three things that produced
fabricated citations the last time this wiki was written by a model.

---

You are maintaining a Warren Buffett knowledge base. Read `AGENT.md` and
`wiki/SCHEMA.md` first — they govern everything below.

**Task: rewrite `wiki/Sources/YYYYltr.md` from `Raw/YYYYltr.md`.**

## The one rule that matters

Every passage you put inside quotation marks must appear **word for word** in
`Raw/YYYYltr.md`. Not paraphrased, not tidied up, not reconstructed from what you
know about Buffett. A fabricated quotation is worse than a missing one, because
it is indistinguishable from a real one and everything built on top of it
inherits the error.

You do not have to retype quotes by hand. `Raw/` files are hard-wrapped at ~100
columns with words split across lines, so anything copied out of `grep` will look
right and fail verification. Use this instead:

```
make quote Q="distinctive phrase"
```

It searches every letter, prints the sentence unwrapped and ready to paste, and
gives you the wikilink. **If it prints "no passage in Raw/ contains …", that
settles it: the quote does not exist. Do not write it.** Paraphrase without
quotation marks, or leave it out.

## Procedure

1. **Read `Raw/YYYYltr.md` in full.** It is long. Read it anyway. You cannot tell
   which passage is load-bearing from a skim.
2. **Read `wiki/Sources/1994ltr.md`.** That is the target quality and structure.
   Match it. Do not invent a different format.
3. **Write the summary.** Sections, in this order:
   - YAML frontmatter: `title`, `type: source-summary`, `stability`, `tags`,
     `date` (the date Buffett signed the letter), `year`, `sourcetype:
     annual-letter`, `source: [[Raw/YYYYltr.md]]`
   - A one-paragraph italic header saying what the year was about
   - `## 🔑 Key Themes` — 5 to 7 themed subsections, each built around real
     quotations with a line of your own framing between them
   - `## 💬 Notable Quotes` — 6 to 9 blockquotes, the lines worth remembering
   - `## 📊 Investment Decisions` — what was bought, sold or reported, and why
   - `## 🔗 Cross-References` — wikilinks to the `Concepts/`, `Cases/`,
     `People/` and `Principles/` pages this letter bears on, each with a few
     words saying *why*, plus the adjacent years
4. **Verify before you finish:**
   ```
   python3 scripts/verify_quotes.py wiki/Sources/YYYYltr.md
   ```
   It must print `clean`. If it reports errors, fix them — do not explain them
   away. `MISATTRIBUTED` means the quote is real but you named the wrong letter;
   the tool tells you the right one. `UNSUPPORTED` means it is in no letter at
   all; delete it.
5. **Then run `make lint`.** It must pass.

## What went wrong last time — do not repeat it

- **Do not fill a section because the format has one.** If the letter says
  nothing about acquisitions, write nothing about acquisitions. The previous
  version of this wiki had metrics tables with invented numbers in them purely
  because the template had four empty rows.
- **Do not cite a letter you have not opened.** Only `Raw/` files that exist may
  be cited. Check with `ls Raw/` if unsure. A previous version cited a 1972
  letter that is not in this collection, from fourteen different pages.
- **Do not carry a quote forward from a neighbouring year.** If a passage is in
  the 1999 letter, it belongs to 1999, even when the 2003 letter makes the same
  argument in different words.
- **Widely-known Buffett lines are usually not in the letters.** Many circulate
  from interviews, or are third-hand paraphrase. If `make quote` cannot find it,
  it does not go in with quotation marks around it — no matter how certain you
  are that he said it.
- **Where the source does not cover something you think matters, write
  `> TODO:` and say what is missing.** That is a useful contribution. Guessing
  is not.

## What makes a summary good rather than merely correct

Passing the verifier is the floor, not the goal. The summary is worth reading
when it does these:

- **Says which passage is the important one.** Most letters have one or two
  paragraphs that matter for decades and a lot of routine reporting around them.
  Lead with the former. The 1991 letter contains a Salomon update and the
  definition of an economic franchise; only one of those is why anyone opens it.
- **Notes where the letter argues with another year.** Buffett changes his mind
  and says so. Where this letter revises, sharpens or contradicts an earlier
  one, say which and how, and link it.
- **Keeps his own framing.** Where he gives a number, an analogy or an admission
  of error, that is usually the substance. Do not smooth it into generic
  business language.
- **Reports the bad news.** These letters are unusual because they lead with
  mistakes. A summary that keeps only the wins misrepresents the source.
