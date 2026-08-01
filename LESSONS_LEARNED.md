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
