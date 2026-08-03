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
