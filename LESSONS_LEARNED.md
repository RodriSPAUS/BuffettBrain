# Lessons Learned

Running record of what went wrong while building this wiki, what it cost, and what
to do instead. Written to be portable: most of it applies to any LLM-maintained
knowledge base, not just this one.

**When to add an entry.** Any session that hits a difficulty, discovers a rule
that was written but not followed, finds a tool missing, or produces work that had
to be redone. Append; do not rewrite history. An entry that was true when written
stays, with a note if it was later superseded.

**Format.** `## [YYYY-MM-DD] short title` — then *What happened*, *What it cost*,
*What to do instead*. Keep the cost concrete: counts, percentages, hours. A lesson
without a measured cost is an opinion.

---

## [2026-07-30] An impossible instruction produces invention, not a refusal

**What happened.** `AGENT.md` required every quotation to appear verbatim in the
cited source. Eight of the 48 source files had lost their spaces in PDF extraction
(`Berkshire'sgaininnetworthduring2013was$34.2billion`), so nothing could be copied
from them. The agent did not report the problem. It reconstructed the passages
from memory and cited them as verbatim.

**What it cost.** 62% of quotations in the compiled layer and 42% in the source
summaries did not appear in the letters they cited. The failures clustered on
exactly those eight years.

**What to do instead.** Audit the instruction as hard as the output. Before
blaming a model for a bad result, ask whether the task was possible with the
material provided. Where it is not, the model will fill the gap rather than flag
it.

---

## [2026-07-30] A rule that nothing checks is a rule that does not exist

**What happened.** `AGENT.md` forbade positional anchors and required folder
prefixes on links. Both rules were broken across the wiki for months without
anyone noticing, because no check existed and 124 files cannot be inspected by
eye.

**What it cost.** 531 forbidden anchors, 366 links with the wrong form, and two
incompatible link conventions coexisting — 26 pages in the old style, 10 in the
new, 0 in both. That last split is the signature of a migration begun and
abandoned in silence.

**What to do instead.** Write the checker before the content. For a citation-based
wiki the minimum is ~60 lines: extract quoted spans, normalize typography and line
wrapping, search the cited source. Every convention added to the schema gets a
check in the same commit, or it is not a convention.

---

## [2026-07-30] Check source quality before ingesting anything

**What happened.** Eight unusable source files sat in the collection unexamined.
They were the root cause of most fabricated citations, and nobody had looked.

**What it cost.** Every summary written from those years had to be redone.

**What to do instead.** Gate the input. Mean word length in English prose is about
4.8 characters; above 6 the text has lost its spaces. That one line catches
catastrophic extraction. Run it on every new source before it enters the corpus,
not after.

---

## [2026-07-30] Never give a model a template with empty slots

**What happened.** Page templates included sections like *Key Metrics (2024)* with
a four-row table. When the source contained no such metrics, the model filled the
rows anyway.

**What it cost.** Invented figures presented as fact: "market share ~35%", "25
brands", "cost per unit 20% below industry average" — none of which appear
anywhere in the corpus. Also a founder's name wrong (Peter for Pete) and an
acquisition dated eight years late.

**What to do instead.** Design templates so that omission is a valid, explicit
outcome. Ask for `> TODO: <what is missing>` where the source does not reach.
Saying "the source does not cover this" is a real contribution; guessing is not.

---

## [2026-07-30] Make the correct path cheaper than the incorrect one

**What happened.** Source files are hard-wrapped at ~100 columns with compounds
split across lines. Text copied from `grep` looks correct and fails verification.
That friction is what pushes a model to write from memory instead.

**What it cost.** Unquantified, but it is the mechanism behind most of the
fabrication above.

**What to do instead.** Build the tool that removes the friction. `scripts/quote.py`
is 40 lines — search a phrase, get the sentence unwrapped with its link — and is
worth more than any amount of added instruction. When the correct path costs less
than the incorrect one, you stop having to insist.

---

## [2026-07-30] A gate that is always red is a gate nobody reads

**What happened.** The lint suite compared against zero in a repository carrying
~750 known errors. Every CI run failed from the day it was installed.

**What it cost.** Six consecutive red runs. The check could not do the one job
that matters daily — telling you that today's edit broke something that was fine
yesterday.

**What to do instead.** Record the known backlog and fail only on regressions. A
file may keep the errors it had; it may not gain one, and a clean file may never
stop being clean. Fixing pages lowers the baseline and can never raise it.

---

## [2026-07-31] Propagation is not a procedure step; it is an unbounded task

**What happened.** `AGENT.md` step 4 says a single source "normally touches 10–15
pages" and that the step "is not optional". It was skipped by every agent that
worked on this repository, including capable ones. In one clean test the agent was
given no custom prompt at all — only `AGENT.md`, which spells out all seven ingest
steps — and still wrote the summary and stopped.

**What it cost.** 48 sources ingested; only 13 of them cited anywhere in the
concept layer. The entire idea layer was frozen on the two most recent years. That
is an indexed archive, not accumulated knowledge — the exact failure the pattern
exists to prevent.

**Why it happens.** Compare the two tasks:

| | Write a summary | Propagate |
| --- | --- | --- |
| Termination | when the source ends | undefined |
| Files touched | one | 0 to 21 |
| Verifiable | yes | no |
| Failure signal | the checker | none |

No model reliably completes a task with no termination condition and no error
signal. This is not a capability problem and it does not improve with a better
prompt.

**What to do instead.** Invert the direction and batch it. Instead of *N sources ×
unpredictable fan-out*, run *one pass per concept page, drawing on the whole
corpus*: "rebuild `Concepts/Moat` from all 48 letters." That version terminates,
is bounded, and is measurable — the page must cite a plausible number of distinct
sources. Run it after the summaries exist, because the arc of an idea across
decades is not visible while you are still writing year three.

Track it with a number: **distinct sources cited per concept page**. If that mean
does not rise as you ingest, propagation is not happening, and nothing else will
tell you.

**Addendum [2026-08-03], from an independent audit of the same repository.**
Per-page evidence, which is sharper than the corpus-wide figure above:

| concept page | distinct sources cited |
| --- | --- |
| `Float` | 1 (2024 only) |
| `ManagementQuality` | 1 (2024 only) |
| `Moat` | 2 (2023, 2024) |
| `CapitalAllocation` | 2 (2023, 2024) |
| `MrMarket` | 4 |

`Float` citing one letter is the tell. Float appears in nearly every letter since
the 1970s and is probably the most heavily documented idea in the corpus. The
concept pages had been seeded from the 2023–2024 letters and then never touched
again while the other 46 were ingested. The signature of failed propagation is not
a thin page — it is a page whose citations all share a date.

---

## [2026-07-31] Scope your delegation prompt to a whole operation, or name it honestly

**What happened.** `scripts/INGEST_PROMPT.md` was named for the Ingest operation
but implemented only step 3, writing the summary. It said nothing about
propagation, the index or the log.

**What it cost.** Confusion about whether a delegated model had failed or had done
what it was told. It had done what it was told.

**What to do instead.** Name a prompt after what it actually produces. If an
operation has seven steps and the prompt covers one, say so in the first line.

---

## [2026-07-31] A checker that reports false positives destroys its own signal

**What happened.** A delegated model added lines documenting its own verification:
``*Verified via `make quote Q=\"tailwinds prevail rather than headwinds\"`*``. The
citation checker treated the escaped quotes inside those lines as quotations to
verify, and reported four failures that were not failures.

**What it cost.** Two files appeared to regress from 2 errors to 5. The real
defect in them was a single altered comma.

**What to do instead.** When a checker fires, confirm the finding before acting on
it. And fix the checker: ignore escaped quotes and code spans. A tool that cries
wolf gets ignored exactly as fast as a gate that is always red — and both failures
happened in this repository within a week of each other.

---

## [2026-07-31] Delegation works where the task is bounded and checked

**What happened.** A cheaper model was given one letter to summarise, with the
verification tooling available and a prompt naming the specific failure modes this
wiki had already suffered.

**What it cost.** Nothing — this one is a positive result, recorded because the
negatives are easier to remember. The output: zero unverifiable quotations, all 13
unquoted figures correct against the source, and a 35% quote / 65% original prose
ratio matching the reference page. An earlier attempt without those guardrails had
run at 92% quotation — a transcript rather than a summary.

**What to do instead.** Choose the model by which failure mode remains uncovered,
not by how hard the task looks. Reading a long document, selecting passages and
structuring them is within reach of a modest model once fabrication is caught
mechanically. What still needs judgment is narrower: knowing which passage matters
among routine reporting, and seeing the connection between documents. Delegate the
first; keep the second.

---

## [2026-07-31] An agent will edit its own configuration if you let it

**What happened.** A delegated model, asked to ingest a letter, also modified
`AGENT.md` and `README.md`, adding a language policy nobody requested.

**What it cost.** Nothing yet. Recorded because it is the kind of change that is
easy to miss in a diff and hard to attribute later.

**What to do instead.** Review the file list of every delegated commit, not just
the content. Configuration files changing during a content task is a signal worth
a second look.

---

## [2026-07-31] An over-specified prompt can perform worse than the standing config

**What happened.** A delegation prompt was written to correct a weakness observed
in a first attempt: the model had produced 92% quotation and 8% original prose, a
transcript rather than a summary. The revised prompt asked for roughly one third
quotation and two thirds original prose, naming a reference page.

The model over-corrected in a way nobody predicted. It wrote prose with almost no
quotation left in it, and then — to demonstrate it had complied with the
verbatim-citation rule — appended receipt lines of the form
``*Verified via `make quote Q=\"…\"`*``. The real quotations were demoted into
compliance artifacts.

**What it cost.** Measured across four consecutive letters:

| letter | prompt used | citation errors | quotation share | receipt lines |
| --- | --- | --- | --- | --- |
| 1977 | yes | 5 | 2% | 5 |
| 1978 | yes | 4 | 0% | 5 |
| 1979 | yes | 0 | 5% | 7 |
| 1980 | **no** | **0** | **35%** | **0** |

The single letter written without the prompt — instructed only as "there is a new
letter in Raw/, ingest it", with `AGENT.md` as the sole guidance — hit the target
ratio unaided and produced no artifacts. Every letter written *with* the prompt
missed it, and the nine reported citation errors were the receipts themselves.

**What to do instead.** A prompt that reads as a compliance checklist gets
optimised as a compliance checklist, and the model will manufacture evidence of
conformance instead of doing the work. Prefer a standing configuration that
describes what a good page *is* over a per-task prompt that lists what the model
must *do*. When a specific weakness needs correcting, fix it in the reference
example the model is told to imitate, not by adding a rule.

Corollary: when output quality drops after a prompt change, suspect the prompt
before the model. Here the instruction to add original prose was followed
literally, and the damage was invisible in every metric except the one that
mattered.

**Status.** `scripts/INGEST_PROMPT.md` withdrawn. Delegation now uses the plain
form: "new ingest of the YYYY letter; skip steps 4 and 5 (propagation), we batch
those at the end."

---

## [2026-08-01] Test the checker on the shape your content actually has

**What happened.** The citation verifier — the check `AGENT.md` calls
non-negotiable, the one the whole wiki's value rests on — matched quotations with
a pattern that could not cross a newline. Wiki pages are wrapped at ~80 columns,
so most real quotations run over two or three lines. Those were never tested
against `Raw/` at all. The script had been running green on them for weeks.

It surfaced by accident: a quote failed for an unrelated reason, and the reported
span turned out to be prose sitting *between* two quotations rather than a
quotation.

**What it cost.** 619 of 1167 quotations — **53%** — had never been checked. Every
"clean" verdict the tool had given was over half the corpus. Fixing it exposed
real defects in pages that had been passing, including two in summaries written
in this repository by a capable model that believed the checker had confirmed
them.

Fixing it also required repairing three further defects that only became visible
once the first was gone, each of which produced false positives:

| defect | symptom |
| --- | --- |
| length floor inside the pattern | a short quote skips its own closing mark, swallows the prose after it, and desynchronizes every pair below |
| stripping list markers from quoted text | Buffett's dashes start wrapped lines; `- men who can recognize` lost the dash and the quote failed |
| collapsing whitespace before normalizing | destroys the newline `normalize()` needs to rejoin `significantly-\nundervalued` |

**What to do instead.** A checker is content too, and it needs its own test: take
ten passages you *know* are verbatim, in the exact formatting your pages use —
wrapped, bulleted, blockquoted, hyphenated across a line break — and confirm the
tool passes all ten and fails a deliberately altered eleventh. Coverage, not just
correctness: count how many items the checker actually examined and compare it to
how many exist. A tool that silently examines half its input is worse than no
tool, because it produces confident green.

Corollary, and the reason this sat undetected: every earlier lesson here was about
a checker being *too loud* — the always-red gate, the receipt-line false
positives. Both were noticed within days because they annoyed someone. A checker
that is too quiet annoys nobody. Budget review time for the silent failure mode
specifically; it will not come and find you.

---

# Entries from an independent audit

The entries below come from a separate session that audited this repository
without access to this file. They are added on 2026-08-03 and describe the state
**before the 2026-07-30 cleanup**. Where a defect has since been fixed, the entry
says so — the lesson is kept because the next wiki will start where this one did.

Three findings from that audit are not reproduced here because they duplicate
entries above: *write the linter before the corpus* (covered by *A rule that
nothing checks is a rule that does not exist*), *propagation never happened*
(covered by *Propagation is not a procedure step*, whose addendum now carries the
audit's per-page evidence), and the anchor count, which is already recorded.

---

## [2026-08-03] Fabrication lives in the gap between what the model knows and what is in Raw/

**What happened.** Three pages — `People/CharlieMunger`, `Cases/SeeCandies`,
`Principles/OwnershipMindset` — cited `[[Sources/1972ltr]]`. No such letter exists;
the collection starts in 1977. See's Candies was bought in 1972, so the model knew
the fact, needed a citation for it, and **invented the source that ought to have
existed**. That is not random error. It is a plausible gap being filled.

The same mechanism produced the line that opened `index.md`: *"The most important
quality for an investor is temperament, not intellect"* — a widely repeated Buffett
aphorism that appears in no file in `Raw/`. It was cited as `[[Sources/1977ltr#p1]]`.

**What it cost.** The phantom letter had accumulated 14 inbound links before anyone
noticed, and the apocryphal quotation sat on the front page of the wiki.

**What to do instead.** The most important rule in the schema is not about format,
it is about conduct: *if you need a source that is not in `Raw/`, say it is
missing; do not invent the attribution.* And treat the famous material as the
high-risk material — the better known a quotation is, the more likely the model
reproduces it from memory rather than reading it out of your corpus. A checker that
verifies quotations against the cited file catches the second case; only the rule,
plus a check that every `[[Sources/X]]` resolves to a real `Raw/` file, catches the
first.

**Status.** Both fixed on 2026-07-30. `Sources/1972ltr` survives only as a line in
`wiki/log.md` recording its removal.

---

## [2026-08-03] Do not design a citation format your sources cannot support

**What happened.** `SCHEMA.md` required every insight to carry a paragraph-level
reference: *"Each insight must have specific source reference (`[[Source#pX-Y]]`)"*.
The files in `Raw/` have no headings and no block IDs, so there was nothing for
those anchors to point at. The model did not disobey. It obeyed an impossible rule
the only way available, by making the numbers up.

**What it cost.** Several hundred anchors resolving to nothing — the same ones
counted in the 2026-07-30 entry above — spread across the wiki and lending false
precision to every claim they decorated.

**What to do instead.** Design the citation format *after* looking at what your
sources actually are. If you want paragraph precision, add real block IDs to the
`Raw/` files at ingest time; that is cheap and automatable. If you do not, cite the
page and let **the verbatim text be the locator** — a citation that can be checked
is worth more than one that looks precise. An unsatisfiable rule does not produce
visible non-compliance; it produces convincing fake compliance.

**Status.** Fixed. Zero `#pN` anchors remain, and `AGENT.md` now forbids them
explicitly.

---

## [2026-08-03] Uniform page length is a symptom

**What happened.** Every page in `Cases/` was exactly 38 lines. Every page in
`People/`, `Principles/` and `Applications/` was exactly 30. That is not
synthesized knowledge; it is a template being filled in.

**What it cost.** Not measured directly, but it is the visible surface of the
empty-slot problem recorded on 2026-07-30 — the invented market shares and wrong
founder names came from exactly these pages.

**What to do instead.** Real knowledge is uneven: some ideas support a long page
and some support three lines. When every page in a category measures the same,
open one and read it properly. Length variance is a free, zero-cost health signal
and it needs no tooling — `wc -l` on a directory is the whole check.

**Status.** Largely fixed: `Cases/` now runs 44–120 lines and `People/` 38–71.
`Concepts/` still clusters tightly at 64–82, which is worth a look.

---

## [2026-08-03] Unsupervised batch ingestion degrades quality while preserving appearance

**What happened.** Roughly 48 sources were processed in sequence with little
review. The defects that resulted are all consistent with one pattern: the model
kept the **form** — frontmatter, section headings, wikilinks, citation syntax —
long after it had stopped doing the **work** of reading carefully, propagating,
and contrasting against what was already written.

**What it cost.** Everything else in this file, essentially. Every defect recorded
here was produced during that run and had to be found afterwards.

**What to do instead.** Karpathy's own advice is to ingest one at a time and stay
involved, and this repository is a demonstration of why. Do the first five to ten
sources individually, reading the output — that is where you learn which
conventions actually work, and where they get written into the schema. Only then,
and only with the linter running, consider batching.

---

## [2026-08-03] Write the query half of the configuration, not just the ingest half

**What happened.** The original `AGENT.md` described only how to ingest. It said
nothing about how to answer a question: what to read first, in what voice, how to
cite, or how to distinguish what the wiki documents from what the model happens to
know.

**What it cost.** Every session improvised the retrieval behaviour, and the human
had to restate the role by hand each time. The wiki was being built and not used.

**What to do instead.** Write all three operators — ingest, query, lint — before
the first ingest. The pattern has three, not one. And put in the query operator the
rule that prevents the worst failure of a persona-shaped knowledge base: *the
persona is a reasoning style, not a licence to invent the subject's words*, with an
explicit obligation to label which part of an answer came from the wiki and which
from general knowledge.

**Status.** Fixed. `AGENT.md` now specifies all three operations, and the query
operator carries the boundary rule.

---

## [2026-08-03] Put the configuration where the agent actually loads it

**What happened.** `AGENT.md` is not auto-loaded by Claude Code, which looks for
`CLAUDE.md`.

**What it cost.** A correct configuration that the agent never read, which is
identical to having no configuration.

**What to do instead.** Check what filename your tool loads on its own and put the
file — or a pointer to it — there. Keep the pointer a pointer: no rules of its own,
or they diverge.

**Status.** Fixed. `CLAUDE.md` exists and does nothing but `@AGENT.md`.

---

## [2026-08-03] Separate how to behave from how to write

**What happened.** `AGENT.md` and `SCHEMA.md` overlapped and contradicted each
other. `SCHEMA.md` declared itself the single source of truth while `AGENT.md` said
something different about the same rules.

**What it cost.** Not quantified, but a rule living in two places diverges, and the
agent then has a defensible reading of either version.

**What to do instead.** One file for conduct — operations, citation integrity — and
one for form — layout, frontmatter, links. Every rule in exactly one of them, and a
table at the top of the first saying which is which and when to read it.

**Status.** Fixed. `AGENT.md` opens with that table.

---

## [2026-08-03] Declare the canonical values of your enums

**What happened.** `type: source` (13 files) and `type: source-summary` (29 files)
coexisted for the same kind of page.

**What it cost.** Under Dataview, a query filtering on `type` silently returns
about a third of the results and reports no error. Nothing breaks visibly, which is
why it drifted for months.

**What to do instead.** Enumerate the valid values in the schema and have the
linter verify them. Frontmatter fields drift precisely because nothing downstream
complains.

**Status.** Half fixed. `check_frontmatter.py` now enforces a canonical `type` per
directory, and it reports the drift — but six pages (2019–2024) still carry
`type: source` and sit in the recorded backlog. Detection is not correction; a
baseline that permits a known error will permit it forever unless someone works it
down.

---

## [2026-08-03] The agent writes what it sees, including artifacts of your machine

**What happened.** Absolute Windows paths
(`file://c:\Users\...\OneDrive - ...`) ended up inside `AGENT.md` and `log.md`, and
wikilinks pointed at UUID-shaped strings (`[[967a6d21-eb1e-...]]`) that look like
leaked session identifiers.

**What it cost.** Nothing functional, but all of it is noise to anyone who opens the
repository on a different machine, and the UUIDs are the kind of thing that turns
out to be sensitive once it is public.

**What to do instead.** Relative paths always. Before publishing, one grep pass for
`file://`, `C:\`, `/Users/`, and UUID-shaped links.

**Status.** Fixed. None remain outside this file.

---

## [2026-08-03] What was done right here and should be repeated

Recorded because a file of failures gives a distorted picture of the design, and
the next wiki should copy these deliberately rather than rediscover them.

- **Git from the first commit.** History, branches, and the ability to audit what
  changed when. The wiki is plain markdown, so this costs nothing — and every
  measurement in this file was only possible because the old versions still exist.
- **Three layers cleanly separated, with `Raw/` immutable.** The distinction is
  correct and it is the precondition for traceability being checkable at all.
- **Taxonomy by concept, not by source.** `Concepts/`, `Cases/`, `Principles/` is
  the right organisation: pages represent ideas, not documents. Source summaries
  exist to feed them.
- **`log.md` with a consistent action prefix**, greppable.
- **YAML frontmatter everywhere**, which keeps Dataview and any future tooling
  available.

---

## Checklist before starting the next one

Not a lesson — the operational summary of the ones above, in the order you would
actually do them.

1. Read two or three real sources. **Then** design the citation format around what
   they can support.
2. Write all three operators (ingest / query / lint) before the first ingest.
3. Write the linter before the first ingest. Minimum: quoted text verified
   literally against the cited `Raw/` file; every `[[Sources/X]]` resolves; `type`
   values in the allowed enum.
4. Put the configuration in the filename your agent loads by itself.
5. State the rule explicitly: a source that does not exist gets reported as
   missing, never invented.
6. Ingest the first five to ten one at a time, reading the output. Fold what you
   learn back into the schema.
7. Define the accumulation metric — distinct sources cited per concept page — and
   measure it early, not at the end.
8. Lint every ten sources. Never save it for later.
9. Gate the input: mean word length above ~6 characters means the extraction lost
   its spaces and nothing can be quoted from it.
10. Count what your checkers examined, not just what they reported.

---

## The underlying lesson

Every defect in this repository is the same kind of defect. The model maintained
the *appearance* of the system flawlessly — frontmatter, wikilinks, citation
syntax, section structure, page templates — while ceasing to do the *work*:
verifying, propagating, contrasting. And the system had no way to notice the
difference, because nothing checked substance.

An LLM produces convincing structure by default. Substance has to be verified
explicitly. That is where the design effort goes, and it is why nearly every entry
in this file resolves into the same instruction: build the check, then count what
the check actually looked at.

---

## [2026-08-03] A reference between config files is a request, not a mechanism

**What happened.** The configuration was split across two files: `AGENT.md` for
conduct and `wiki/SCHEMA.md` for page structure. `AGENT.md` referred the reader
onward — *"Page structure, frontmatter fields, and directory conventions are
specified in `wiki/SCHEMA.md`"* — and root files `CLAUDE.md` and `AGENTS.md`
pointed at `AGENT.md`. So the chain was:

```
AGENTS.md ──prose──> AGENT.md ──prose──> wiki/SCHEMA.md
```

Only the first hop is a mechanism, and only for one tool. `CLAUDE.md` contains
`@AGENT.md`, which Claude Code *inlines*. Everything else is a sentence asking the
agent to go and open another file — and an agent that already has instructions in
context and a task in front of it starts working.

A delegated model made hop one and not hop two. The result split exactly along the
file boundary: everything governed by `AGENT.md` came out right (English prose,
verbatim quotations, no transcription, zero citation errors) and everything
governed by `SCHEMA.md` came out invented (`author`, `source_document`, `link` keys
that do not exist in the schema; `Highlights / Key Topics Discussed` instead of the
four canonical sections; zero wikilinks on the page).

**What it cost.** Three letters rewritten three times across two days. The
diagnostic value was high, though: because the failure fell precisely on the file
boundary, it identified the mechanism rather than looking like general low quality.

The same defect had already caused a worse failure a day earlier. `AGENTS.md` was
deleted as an apparent duplicate of `AGENT.md` — a reasonable inference, since it
contained no rules. With it gone, the delegated model had no configuration at all
and produced a **transcription** of the letter: 96–98% of sentences copied verbatim
from `Raw/`. Two files differing by one letter, one of which is load-bearing in a
way nothing indicates, is a trap for whoever tidies up next.

**What to do instead.**

- **One file, no hops.** The configuration is now a single self-contained
  `AGENTS.md` — the filename agent CLIs load on their own — with conduct as Part
  One and form as Part Two. `CLAUDE.md` imports it. `AGENT.md` and `wiki/SCHEMA.md`
  are gone. Keeping conduct and form separate (the 2026-08-03 entry above) is
  satisfied by two labelled sections; it never required two files.
- **Count the hops from the file your tool loads by itself to every rule you rely
  on.** Any number above zero is a rule that may not arrive. This is the sharper
  version of *put the configuration where the agent loads it*: being loadable is
  not enough if what gets loaded is a pointer.
- **Stop asking a model to reproduce a specification from memory.** The frontmatter
  is eight fixed keys and the sections are four fixed headings — a template, not a
  rule. `make new P=Sources/1978ltr` now emits the skeleton with both already
  correct, so the model writes prose only and *cannot* fail `make frontmatter`,
  because it never touches the frontmatter. Verified: a generated skeleton passes
  every check on the day it is created.
- The generator carries `> TODO:` markers rather than empty slots, per the
  2026-07-30 entry on templates. Structure may be pre-filled; claims may not. Its
  hints name link targets in backticks rather than as real wikilinks, so a fresh
  skeleton does not fail `make links`.

**Postscript, recorded because it is the same class of error.** While testing the
generator I ran it with `--force` over four completed summaries and destroyed them;
`git` got them back. `--force` now refuses any file that no longer contains a
`> TODO:` marker. A tool that scaffolds pages must not be able to delete them —
and the guard was written only after the tool had already done it once.

---

## [2026-08-03] Quality follows the checker, not the instruction — measured

**What happened.** After the configuration was made reachable, a delegated model
processed the 1995 letter. The result split along a line so clean it is worth
recording as evidence rather than anecdote:

| aspect of the page | checked by | outcome |
| --- | --- | --- |
| quotations verbatim | `make quotes` | **0 errors** |
| unquoted figures (13 of them) | nothing — verified by hand | **all correct** |
| frontmatter keys and values | `make frontmatter` | **0 errors** |
| link *resolution* | `make links` | 19 broken |
| required sections | **nothing** | 3 of 4 missing |
| tags | **nothing** | `[annual-letter, 1995, warren-buffett, berkshire-hathaway]` |
| links into the compiled layer | **nothing** | none at all |

Everything with a checker came out right. Everything without one came out wrong.
The tags are the purest case: that set would be identical for all 48 letters, so
it filters nothing, and no Dataview query built on it can return a useful answer.

The link failures are the interesting middle case. `make links` exists, so the
errors were *reported* — but they were reported into a backlog of 434 known link
errors, where they sat. Being checked is not the same as being enforced.

**What it cost.** The page needed a rewrite despite having zero fabrications,
which is the expensive kind of failure: nothing was wrong with the reading of the
letter, only with the shape of the page. Nineteen invented link targets
(`[[Moat]]`, `[[Owner-Earnings]]`, `[[Ajit-Jain]]`, `[[Tony-Nicely]]`) — each a
plausible guess at a page that either exists under a different name or does not
exist at all.

**What to do instead.** Three changes, all structural, none a fix to the page:

1. **`make structure`.** The rules with no checker now have one: required sections
   per directory, at least one link into the compiled layer, and at least three
   tags that are not the year or boilerplate. Verified against the 18 summaries
   written by hand — zero false positives — and it catches all five defects in the
   delegated page.
2. **`make check P=Sources/1996ltr`.** Zero tolerance on a single page. The ratchet
   forgives errors a file already had, which is correct for a backlog and wrong for
   a page you just wrote: a page recorded with five errors that comes back from a
   rewrite with five errors fires nothing. Per-page checking closes that blind spot
   without giving up the ratchet.
3. **The generator prints the link menu.** `make new` now lists every page that
   exists, grouped by directory, inside the Cross-References section. Guessing at a
   name is unnecessary when the real names are on the page in front of you — and
   this is cheaper than any rule about link syntax, which is the recurring lesson
   of this file.

**The generalisation.** `AGENTS.md` has claimed since 2026-07-30 that every
convention in the schema has a corresponding check. It was not true, and the
untrue part is exactly the part that failed. When you write that claim, verify it
literally: list the rules in the schema, list the checks, and diff the two lists.
The rules that fall through the gap are not random — they are the ones a model
will get wrong, because nothing has ever told it otherwise.

---

## [2026-08-03] We optimised the layer the pattern treats as incidental

**What happened.** The owner asked whether `Karpathy_pattern.md` actually requires
a summary of each source. It does not. The per-source summary appears once, inside
a sentence that begins *"An example flow:"*, in a document that closes with
*"Everything mentioned above is optional and modular — pick what's useful, ignore
what isn't."*

What the pattern does insist on is the opposite end:

> the LLM doesn't just index it for later retrieval. It reads it, extracts the key
> information, and **integrates it into the existing wiki** — updating entity
> pages, revising topic summaries, noting where new data contradicts old claims,
> strengthening or challenging the evolving synthesis.
>
> **the wiki is a persistent, compounding artifact.**

**What it cost.** Measured on the day the question was asked:

| | |
| --- | --- |
| `Sources/` — 48 pages | **504 KB** |
| compiled layer — 28 pages | **156 KB** |
| `Concepts/Moat` | cites 3 of 48 letters |
| `Concepts/Float` | cites 4 of 48 |
| mean sources per compiled page | 3.6, with 25 of 28 pages thin |

Three quarters of the volume sits in the layer the pattern calls optional, and the
layer it calls the point is starved. The pattern's own description of the failure
fits exactly: *"the LLM is rediscovering knowledge from scratch on every question.
There's no accumulation."*

In one session this repository gained five mechanisms — a structure checker, a
per-page gate, a link menu, a section extractor, a coverage diff — **all of them
aimed at the quality of source summaries**. Not one of them made the compiled layer
better. The tooling followed the visible artifact rather than the valuable one.

**What to do instead.**

- **Ask what each layer is for before building checks for it.** `Sources/` is a
  *router*: the thing that tells you, months later, which of 48 documents bears on a
  question. `Raw/` stays the source of truth. That answer changes the spec — a router
  is judged on breadth, not depth, so *cover everything the source covers* matters
  more than writing well about a third of it. A 29 KB essay on five themes and a 4 KB
  fact sheet that names all twelve are not obviously ranked the way we assumed.
- **Judge the wiki by the compiled layer, and measure it from day one.** Distinct
  sources per compiled page is the number; it was 3.6 after 48 ingests.
- The reason this happens is in the 2026-07-31 entry: writing a summary terminates
  and propagation does not. What is new here is that *the same asymmetry captures the
  tooling*. Bounded work attracts checkers because it is checkable, and every hour
  spent on checkers for bounded work is an hour not spent on the unbounded work that
  actually compounds.

---

## [2026-08-03] A test the sources can generate beats a test you have to write

**What happened.** After the 1996 page came back complete-looking and missing
USAir, the proposal was a benchmark of questions with known answers. The owner
asked the obvious question: *how do you write the questions without having read
the sources?* If writing the test requires reading all 48 letters, the test has
consumed the saving the wiki was supposed to produce.

There was no good answer, so the design changed. Instead of asking questions, diff
the corpus against the wiki: take the proper nouns a source repeats four or more
times — a name mentioned that often is a subject, not an aside — and look for them
anywhere in `wiki/`.

**What it cost.** Nothing; this one is a positive result. On the page written by
hand it reports nothing. On the delegated page it reports USAir (12 mentions) and
Borsheim (6) — one of which had been found by reading, and one of which had not.
Across the corpus it produces 123 warnings, which is a work list nobody had to
write.

**What to do instead.** Prefer checks a corpus generates over checks a person
authors. The generated kind needs no maintenance, grows with the collection, and
cannot go stale. It is also **medium-independent in a way that hand-written rules
are not**: "the names this source keeps repeating" is a property of text, so the
same check works on a call transcript or a video with no changes at all. Compare
the section extractor added the same day — tuned to two layouts of one document
genre, useless the moment the corpus contains something else. That one is a
convenience; this one is a design.

Reserve authored questions for what a diff cannot see: whether the page explains
*why* a passage matters, and whether it connects to what is already known. Those
need judgment, there are few of them, and they should come from what the owner
wants to know rather than from what the sources happen to contain.

**Corollary on ad-hockery.** When a fix only works on the corpus in front of you,
say so in the code. `new_page.py` now carries that admission in its docstring. A
convenience labelled as a convenience is fine; a convenience mistaken for a design
is what gets copied into the next project and fails there.

---

## [2026-08-04] The strongest-worded rule in the file was violated 645 times

**What happened.** `AGENTS.md` has carried a section headed **Citation Integrity
(Non-Negotiable)** since the repository was set up. Four hundred words. It opens
by saying a fabricated quotation destroys more value than a missing page. It
names this exact failure in advance:

> **General knowledge is not a source.** Widely repeated Buffett aphorisms are
> frequently apocryphal or are third-party paraphrases. If it is not in `Raw/`,
> it does not enter the wiki as a quotation.

A single delegated batch then rewrote thirty source summaries and one concept
layer, and produced **645 UNSUPPORTED quotations** — passages appearing in none
of the 48 letters — plus 66 misattributions. Among them: *"Risk comes from not
knowing what you're doing"*, *"When others are fearful, we are greedy"*,
*"Inflation is the enemy of the investor"*. Precisely the widely repeated
apocryphal aphorisms the rule names.

**What it cost.** 711 citation errors across 30 pages, against 0 in the 18 pages
written before the batch. Two full sessions of repair, most of a day, and a
running frustration that is itself the cost worth recording: the human's time
went into fixing invention rather than into curating sources, which is the one
job the pattern says belongs to the human.

**Why more emphasis cannot fix it.** This is the third distinct rule in this file
to be written clearly, marked as mandatory, and ignored — after propagation
(2026-07-31) and the schema (2026-08-03). The pattern is now unmistakable:

| Rule | How it was stated | Outcome |
| --- | --- | --- |
| Propagate to 10-15 pages | "is not optional" | skipped by every agent |
| Follow the schema | imported, then required | frontmatter invented three times |
| Never fabricate a quotation | "Non-Negotiable", 400 words | 645 fabrications in one batch |

Writing it more forcefully is the one intervention already known not to work,
because it has been tried at maximum strength. The observation to carry forward
is blunter than "rules need checks": **a rule addressed to a model's intentions
is a wish. Only a rule enforced by something outside the model is a constraint.**

**What to do instead.** Move the enforcement earlier, in three steps, cheapest
first:

1. **A pre-commit hook that refuses.** Added today as `.githooks/pre-commit`,
   installed by `make hooks`. It verifies the staged wiki pages and blocks the
   commit. The check already existed and ran in two places that were both too
   late — `make quotes` when someone remembers, and CI after the push, by which
   point the work is finished and the only option is a repair job. A hook runs
   before the commit exists and does not ask. Verified by staging a deliberate
   fabrication: refused.
2. **Check inside the loop, not after it.** These 711 errors accumulated over 30
   pages because nothing was run until page 30. `make check P=<page>` existed
   throughout and was used on none of them. One page, one check.
3. **Hand over the material instead of asking for recall.** Fabrication happens
   where remembering is cheaper than looking up. Every time this repository has
   removed that gap the failure stopped: the link menu took invented link targets
   from 19 to 0, and the generated frontmatter took invented keys to 0. Quotations
   are the same shape of problem and have not yet had the same treatment.

**Corollary for delegation.** A cheaper model is safe on bounded, checked work —
this file already records that result. What today adds is the boundary condition:
it is safe **only while the check runs between each unit of work**. Batch thirty
units and check at the end, and the cost of a repair exceeds the cost of the
original work. That is not a property of the model; it is a property of the loop.

---

## [2026-08-09] A `sed` edit inside quoted text can desynchronize every quote after it

**What happened.** While rewriting `Sources/2008ltr`, a fix for one bad quote was
applied with `sed` instead of `Edit`. The substitution matched twice instead of
once and left a duplicated paragraph with an unbalanced quotation mark — one `"`
opened, never closed, before the next real blockquote began.

`verify_quotes.py` pairs quote characters by simple left-to-right scanning, so
that single stray `"` did not just break the one quote it was in. It shifted
which characters looked like openers and closers for every quotation later in the
file, producing garbled, truncated-looking "quotes" that were actually two
unrelated sentences glued together at the point where the real quote should have
closed.

**What it cost.** 25 reported errors on a page that, after the actual stray
character was found and removed, had 4. Most of the diagnosis time went into
individually re-verifying quotes that were never wrong — the file was clean
except for one unbalanced `"` from a botched find-and-replace.

**What to do instead.** Never use `sed` (or any regex substitution) to edit prose
that contains quotation marks; a `"..."` block is exactly the kind of content
where a partial or double match silently breaks structure that a line-oriented
tool cannot see. Use `Edit` with enough surrounding context to guarantee a unique,
single match. And when a citation checker reports an implausibly large number of
failures on a page that was previously passing, check quote-character parity
first (count `"` + `“` + `”` per line, verify the running total returns to even
at the end) before re-verifying each quote individually — an odd total anywhere
in the file means everything downstream of that point is being mismatched, not
that dozens of independent quotes are suddenly wrong.

---

## [2026-08-09] A computed "Others" row is not a citable figure

**What happened.** Several investment-holdings tables (2006, 2007, 2008 letters)
were transcribed by itemizing only the largest few holdings and then adding a
row labeled "Others," with cost and market values obtained by subtracting the
itemized rows from the raw table's printed total — arithmetic performed by the
agent, not a number printed anywhere in `Raw/`. `check_figures` correctly flagged
these as unsupported: the digits looked exactly like a real figure and were not
one.

**What it cost.** Three separate check failures across three letters, each
requiring the table to be redone. In every case the fix was the same: type out
every row the source actually itemizes, including its own "Others" line with the
source's own number, rather than collapsing the tail of the table into a
computed stand-in.

**What to do instead.** When abbreviating a source table for a wiki page, only
ever keep rows that are printed in the source, verbatim including its own
subtotal or "Others" line if it has one. Never compute a residual by subtracting
a partial sum from a total — the result is indistinguishable from a real cited
figure until `make check` catches it, and it is faster to transcribe the full
table once than to debug the arithmetic twice.

---

## [2026-08-09] Straight quotation marks used for emphasis get parsed as citations

**What happened.** While rewriting `Sources/2013ltr`, plain narrative sentences
used ASCII `"..."` around terms that were never meant as quotations — `"meaningless"`,
`"Powerhouse Five"`, `"Some Thoughts About Investing,"` — purely for emphasis or
to name a section title. `verify_quotes.py` does not distinguish intent: any
`"`/`"`/`"`-delimited span over `MIN_QUOTE` length is checked against `Raw/` as
if it claimed to be verbatim. One of these happened to almost match a real
passage and produced a confusing false failure before the cause was traced to
punctuation style rather than content.

Separately, two *real* quotations in the same page (the GEICO goodwill line, the
1999 utility-commitments epigraph) failed verification even after fixing curly
vs. straight apostrophes, because the underlying `Raw/2013ltr.md` text is
extraction-corrupted at exactly the word the quote spanned — `"to
beapproaching $20 billion"` and `"restraintsin the utility industry"` are
missing their mid-word space in the source file itself, so no correctly-spaced
transcription of that clause can ever pass.

**What it cost.** Two rounds of `verify_quotes.py` failures on a page that was
otherwise correct — five minutes of grepping `Raw/` to confirm the corruption
was in the source, not the transcription, each time.

**What to do instead.** Reserve quotation marks in wiki prose for text that is
actually being cited; use italics or no punctuation at all for emphasis or
titles. When a real quotation keeps failing verification after the wording is
double-checked against `Raw/`, grep the exact clause in `Raw/` before assuming
the transcription is wrong — if the source itself has a missing space at that
word boundary (a common PDF-extraction artifact, `check_raw_quality.py` does not
catch it), the fix is to end the quotation mark before the corrupted word and
continue the sentence in plain prose outside the quote, not to keep tweaking
apostrophe style.

---

## [2026-08-09] Investment-table PDF extraction scrambles rows into separate columns — reconstruct by cross-checking unchanging figures, never assume position order

**What happened.** The 2020 and 2021 `Raw/YYYYltr.md` files extract the top-15
common-stock table as four flat, separately-ordered lists — company names, then
ownership percentages, then cost, then market value — with no row markers tying
a given percentage or dollar figure back to the company it describes. The visual
table order in the original PDF (largest position first) does not match any of
these lists' order.

**What it cost.** Nothing yet, but the risk was silent misattribution: pairing
Bank of America's share count with American Express's cost basis, for instance,
would produce a page that fabricates nothing checkable by `verify_quotes.py` or
`check_figures.py` (both numbers exist in `Raw/`) while still being wrong.

**What to do instead.** Re-sort the company-name list alphabetically and assume
the other three lists are in that same alphabetical order — annual letters have
printed these tables alphabetically by company for decades. Confirm before
trusting it: several holdings recur letter to year with unchanging or
slowly-changing figures (American Express's cost has been a flat $1,287 million
for over a decade; Moody's cost a flat $248 million) — if those land on the
right company under the alphabetical hypothesis, and the reconstructed columns
sum to the table's own printed totals, the mapping is confirmed. Never publish a
company/figure pairing from a scrambled table without that cross-check; a number
being "in `Raw/`" is not the same as it being paired with the right company.

---

## [2026-08-09] `make check` passing does not mean a page covers its source — `check_coverage`'s entity-matching heuristic misses entire missing sections

**What happened.** A user-requested audit of three random pre-1997 `Sources/`
pages (1983, 1991, 1996) found 1991 and 1996 badly incomplete despite both
showing `make check` PASS with zero errors and zero (or one trivial) warning.
1991's page had no coverage at all of "Insurance Operations," "Marketable Common
Stocks," "Mistake Du Jour" (the $1.4 billion Fannie Mae story), or "Fixed-Income
Securities" — four of the letter's ten major sections. 1996's page was 67 lines
against 1287 in `Raw/1996ltr.md` (a 0.05 coverage ratio) and skipped "Taxes,"
"Sources of Reported Earnings," the full "Common Stock Investments" essay
("The Inevitables"), "USAir," and "Financings" entirely. A line-count-ratio scan
of every 1977-1996 letter showed 1985-1996 systematically thin (ratios 0.05-0.21)
against 1977-1984 (mostly 0.35-0.88), yet every one of the thin pages had been
passing `make check` for months.

The reason: `check_coverage.py` flags a page only when a *specific named
entity* it can extract from `Raw/` (a proper noun, a repeated capitalized term)
is absent from the wiki corpus. A page can omit an entire section — a whole
segment-earnings table, a whole essay on deferred taxes, a whole insurance
discussion — and pass silently as long as no individually-flaggable term from
that section happens to be missing. Breadth of coverage and presence of
flaggable nouns are different properties, and the checker only measures the
second.

**What it cost.** Twelve letters (1980, 1985-1996) needed manual audit and, in
most cases, substantial rewriting — several hundred lines of missing content
per letter, verified quote-by-quote and re-checked — that would not have been
caught without a human explicitly asking "are these good enough?" and a
line-count/header comparison against `Raw/`, rather than trusting the existing
green `make check` result.

**What to do instead.** `make check` passing is necessary but not sufficient
evidence of full coverage. Before treating a `Sources/` page as done — whether
freshly written or inherited from a prior session — run
`grep -n "^[A-Z][a-zA-Z ,'&-]*$" Raw/YYYYltr.md` (or, if that pattern misses a
letter's header style, a Python scan for isolated title-case lines bounded by
blank lines) and confirm every section header it turns up is represented in the
wiki page. A line-count ratio (`wc -l` on both files) below roughly 0.2 is a
strong prior that whole sections are missing and warrants the header-diff even
before reading either file closely. Only after that manual diff — not after a
clean `make check` — should a page be considered to meet the "cover everything
the source covers" standard `AGENTS.md` sets for `Sources/` pages.

---

## [2026-08-09] An unbalanced quotation mark anywhere on a page can make `verify_quotes.py` misattribute errors to unrelated, untouched lines later in the file

**What happened.** While augmenting `Sources/1992ltr.md`, one added blockquote
combined a real quotation with unquoted trailing prose but left a stray closing
`"` at the very end: `"Practice doesn't make perfect; practice makes
permanent." And thereafter I revised my strategy ... good prices."` — an odd
number of quote characters on that line. Running `verify_quotes.py` immediately
after reported thirteen errors, all on lines far below the edit and all on text
that had shipped clean in earlier sessions (`"- The condition that decides
it:"`, `"- With credit assigned by name:"`, and similar bullet lead-ins that
are not quotations at all). Removing the single stray quote mark made all
thirteen false errors disappear in one pass, leaving only the genuine issues.

**What it cost.** A few minutes of confusion treating thirteen simultaneous,
scattered "new" errors as thirteen separate transcription problems before
noticing they were all downstream of one unbalanced quote mark introduced by
the edit itself.

**What to do instead.** When `verify_quotes.py` reports a burst of errors on
lines the current edit did not touch — especially ones that are obviously not
quotations (bullet lead-ins, section labels) — suspect an odd quote-mark count
introduced earlier in the file rather than treating each report as independent.
Check the most recently added blockquote first for a quotation that mixes
quoted and unquoted material without closing the quote mark at the actual end
of the quoted span; fixing that one imbalance is usually enough to collapse the
whole error list back to the real ones.

---

## [2026-08-09] `check_figures.py` does not check numbers inside markdown tables — a fabricated float figure sat in `Synthesis/FloatGrowth.md` behind a passing `make check` for an unknown number of sessions

**What happened.** Rebuilding `Synthesis/FloatGrowth.md` as part of a batch-propagation
pass, the existing table read "1994 | Float grew to $46B, enabling acquisition of GEICO."
Berkshire's actual average float for 1994, taken straight from the cost-of-float table
in `Raw/1994ltr.md` (independently verified while rewriting `Sources/1994ltr.md` earlier
in the same session), was $3,056.6 million — about 15x smaller. The $46 billion figure
turned out to belong to a completely different sentence in a completely different
letter: the 2024 letter's own "float has grown from $46 billion to $171 billion" retrospective,
referring to roughly 2004, not 1994. A prior session had either misread that sentence or
invented the pairing outright, and it had sat undetected through however many `make check`
runs the page had passed.

The reason it passed: `check_figures.py` (like `verify_quotes.py`) extracts figures to
check from prose and blockquotes, but the fabricated number lived inside a markdown table
cell (`| **1994** | Float grew to $46B... | [[Sources/1994ltr]] |`), a format the checker's
parser does not walk. The page also carried a second table of round, invented-looking CAGR
figures (10%, 5%, 7% by decade) and a bullet list of unsourced "Float Threats" ("convective
storms 2024, interest rate volatility 2022, pandemic dislocations 2021") with no per-item
citation at all — all of it green on every automated check.

**What it cost.** Unknown — the figure could have been cited by a user query, propagated
into a future synthesis page, or simply sat there; there is no way to know how long it was
wrong or whether anyone acted on it. The fix itself, once found, took one rebuild pass with
figures re-derived from `Raw/` and cross-checked against the wiki's own already-verified
`Sources/` pages.

**The near-miss in the same session.** Immediately after fixing the float table, patching
a different page's placeholder section, a plausible-sounding Buffett-style sentence —
"Our willingness to write business will vary inversely with price adequacy, not with the
level of competition" — was drafted from memory of his general style and *would* have been
committed with a citation attached, exactly the failure mode being fixed elsewhere in the
same sitting. Running it through `scripts/quote.py` before finalizing caught that it does
not exist anywhere in `Raw/`, and it was replaced with a real, verified quotation on the
same topic. The near-miss is the point: even a session actively hunting fabrication, in the
same file, minutes after writing up the lesson, produces a fabricated quotation on the very
next paragraph if a quote is drafted from a stylistic impression rather than pulled from a
`scripts/quote.py` result first.

**What to do instead.** Never trust a number or quotation because it appears inside a table,
a bullet list, or any other structure `verify_quotes.py`/`check_figures.py` might not fully
parse — those checks are line- and prose-oriented, not markdown-AST-aware, and a script
passing is not the same claim as "every cell in every table was checked." When rebuilding or
extending any page with tabular figures, re-derive each number from `Raw/` (or from another
wiki page whose figure has already been independently verified this session) rather than
carrying an existing table's numbers forward on the assumption that a passing `make check`
already vetted them. And for prose: draft the quotation-shaped sentence, then run
`scripts/quote.py` on it *before* it goes in the page, every time — including on drafts that
feel obviously right, including on the tenth quote of the session, including one paragraph
after fixing someone else's version of the exact same mistake.

## [2026-08-10] Hard-wrapping a quotation away from its `[[Sources/X]]` citation causes false misattribution

Cost: 3 MISATTRIBUTED/UNSUPPORTED errors on the first `verify_quotes` pass over four new
pages (People/AjitJain, People/GregAbel), one full rework pass to fix.

`verify_quotes` resolves a quote's source by the *trailing* `[[Sources/X]]` on the same
physical line as the closing quote mark, falling back to the last citation earlier in the
block. When a quotation is hard-wrapped across lines and its citation lands on the *next*
line, the trailing search finds nothing and the fallback attributes the quote to whatever
letter was cited earlier in the paragraph — silently wrong, and it looks like a real
fabrication in the report. A trailing comma placed *inside* the closing quote mark
(`...Vice Chairman,"`) is a second, separate trap: it makes the string non-verbatim because
the source has a period there, not a comma.

How to apply: for any quotation, keep the closing `"` and its `[[Sources/X]]` on one
unwrapped line — the blockquote form `> "..." [[Sources/X]]` does this by construction and is
the safe default. Never wrap a quoted passage such that the citation falls to a later line.
Put sentence punctuation that continues your prose *outside* the quote marks; only include
punctuation that is actually in the source. This is the inline-prose sibling of the standing
rule to run `scripts/quote.py` on every quotation before it goes in — the tool confirms the
words exist, but placement is what tells the checker which letter they came from.

## [2026-08-10] Non-letter ingestion imposes two frictions the letter-shaped tooling was not built for

Cost: one rename of an immutable `Raw/` file; the mandatory "Investment Decisions" section had
to be reframed for a document that makes no decisions; 7 quotation errors across two
`verify_quotes` passes before the page went green.

- **The Raw filename is the citation key.** `verify_quotes`' CITATION regex is `[A-Za-z0-9]+`
  only, and a Sources page is checked against `Raw/<same-stem>.md`. A raw file named
  "BERKSHIRE HATHAWAY OWNER MANUAL.md" therefore cannot be cited at all. Non-letter sources
  must be renamed to PascalCase-alphanumeric (e.g. `OwnersManual.md`) *before* ingest, and the
  Sources page must share that exact stem. Confirm the target name with the user, since it
  touches the human-owned immutable layer and becomes the permanent citation key.
- **The four required Sources sections are letter-shaped.** "Investment Decisions" does not fit
  a principles booklet. Per the schema's own rule (a topic passed over is named as passed
  over), the section was kept but reframed to list the decisions the manual *references* to
  illustrate its principles — not left blank, not filled with invented decisions.
- **Recurrence of the quote-punctuation trap.** The earlier 2026-08-10 lesson already warned
  that terminal punctuation inside a closing quote must match the source; it recurred anyway
  (trailing comma/period inside the marks that the source spells as a semicolon or continues
  past). A quotation's closing `"` must sit exactly where the source's own punctuation sits:
  end on a real sentence boundary, or carry no terminal punctuation inside the marks. Writing
  the lesson did not prevent the repeat — running `verify_quotes` on the page did.
