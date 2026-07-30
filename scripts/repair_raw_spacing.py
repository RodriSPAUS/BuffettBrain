#!/usr/bin/env python3
"""Restore word boundaries in Raw/ letters whose PDF extraction dropped spaces.

Eight letters in this collection came out of the PDF with the spaces gone on
justified lines:

    Berkshire'sgaininnetworthduring2013was$34.2billion.Thatgainwasafterour...

Nothing can be quoted verbatim from that, so an agent asked to cite those years
reconstructs the wording from memory instead — which is how the wiki ended up
with unsupported quotations concentrated almost exactly in these files.

The repair inserts spaces and nothing else. The invariant, asserted per file, is

    output.replace(whitespace, "") == input.replace(whitespace, "")

so no character is ever added, dropped, or changed: this cannot invent text, it
can only fail to split something, and unsplit runs are reported rather than
guessed at.

Word breaks come from a Viterbi search over a unigram and bigram model built
from the 40 letters in this same repository that extracted cleanly. That is the
right corpus: same author, same vocabulary, same proper nouns. A candidate split
is accepted only when every piece it produces is a word the corpus actually
contains and the corpus has seen those words adjacent, so an unknown name is
left glued rather than cut into plausible-looking nonsense.

    python3 scripts/repair_raw_spacing.py --dry-run   # report, change nothing
    python3 scripts/repair_raw_spacing.py             # rewrite in place
"""

from __future__ import annotations

import math
import re
import sys
from collections import Counter
from pathlib import Path

from wikilib import RAW

# Tokens at or above this length that the corpus does not know are candidates
# for splitting. Below it, a long-ish unknown token is usually a proper noun.
SUSPECT_LEN = 12

# A split is only accepted if it beats leaving the run alone by this margin,
# in log-probability terms, guarding against gratuitous splits.
MIN_GAIN = 1.0

# Occurrences in the clean corpus above which a word counts as everyday.
COMMON_COUNT = 20

# A vocabulary entry is only considered for pruning if it is this rare, and is
# pruned only when the spaced form outnumbers it by this factor.
GLUE_MAX_COUNT = 3
GLUE_RATIO = 10

WORD = re.compile(r"[A-Za-z]+")

# Runs are matched with the apostrophe included, so "Berkshire'sgaininnetworth"
# stays one run and the search can peel off "Berkshire's" as a single word.
# Splitting on the apostrophe first would strand a bare "s" that no dictionary
# contains, and the whole run would then be left glued.
RUN = re.compile(r"[A-Za-z][A-Za-z'’]*")


def fold(word: str) -> str:
    return word.lower().replace("’", "'")


def clean_sources() -> list[Path]:
    """Letters whose extraction preserved spaces, judged by mean word length."""
    good = []
    for path in sorted(RAW.glob("*.md")):
        words = WORD.findall(path.read_text(encoding="utf-8", errors="replace"))
        if words and sum(map(len, words)) / len(words) < 5.6:
            good.append(path)
    return good


def clean_lines(text: str) -> str:
    """The lines of a damaged file that survived, usable as extra vocabulary."""
    keep = []
    for line in text.splitlines():
        words = WORD.findall(line)
        if words and sum(map(len, words)) / len(words) < 6.0:
            keep.append(line)
    return "\n".join(keep)


def build_model(
    clean: list[str],
) -> tuple[dict[str, float], Counter, set[str]]:
    """Unigram and bigram model from the cleanly extracted letters only.

    Deliberately excludes the file being repaired. Its surviving lines look like
    an attractive source of that year's proper nouns, but they also carry glue
    fragments — "AtBerkshire", "metalwas" — and once one of those is vocabulary,
    the run matches itself and is never split. Two and a half megabytes of the
    same author is plenty; a name unique to one damaged year is left glued,
    which is the honest outcome.
    """
    counts: Counter[str] = Counter()
    bigrams: Counter[tuple[str, str]] = Counter()
    for text in clean:
        words = [fold(w) for w in RUN.findall(text)]
        counts.update(words)
        bigrams.update(zip(words, words[1:]))
    total = sum(counts.values())
    # A one-letter "word" is nearly always a segmentation artifact, so drop the
    # counts the corpus accumulated for them. They come back below at a fixed
    # low probability, which is enough to peel the "C" off "P/Cgainexceeded"
    # without letting the search shred longer runs into initials.
    for letter in "bcdefghjklmnopqrstuvwxyz":
        counts.pop(letter, None)
    # Glued runs from a damaged file can themselves reach the vocabulary via
    # that file's surviving lines. Left in, they let a run "match" itself and
    # never get split. No English word in this corpus is 19 characters long,
    # and a rare long word is far likelier to be glue than genuine vocabulary.
    for word in [
        w
        for w in counts
        if len(w) > 18
        or (len(w) > 14 and counts[w] < 4)
        # A short word seen once in 2.5 MB is a stray from some other
        # extraction glitch ("raph"), and admitting it lets the search cut a
        # genuine word in half.
        or (len(w) <= 5 and counts[w] < 3)
    ]:
        del counts[word]

    logp = {w: math.log(c / total) for w, c in counts.items()}
    rare = math.log(1 / total)
    for letter in "abcdefghijklmnopqrstuvwxyz":
        logp.setdefault(letter, rare)
    # Words frequent enough that seeing them side by side needs no corroboration.
    common = {w for w, c in counts.items() if c >= COMMON_COUNT}

    for glued in self_glued(counts, bigrams, common):
        del logp[glued]
        common.discard(glued)
    return logp, bigrams, common


def self_glued(
    counts: Counter, bigrams: Counter, common: set[str]
) -> list[str]:
    """Vocabulary entries that are themselves glue, found using the vocabulary.

    Even the letters that extracted cleanly have the occasional lost space, so
    "atberkshire" and "metalwas" enter the dictionary as words. Once there, a
    run containing one matches itself and is never split — the contamination
    silently caps how much text the repair can recover.

    The tell is not that an entry *can* be split: "marketplace" splits into
    "market" and "place", and "forgetting" into "for" and "getting", and both
    are real words that must survive. The tell is the ratio between the two
    forms. This author writes "at Berkshire" constantly and "atberkshire" once,
    so the spaced form outnumbers the glued one by orders of magnitude. He
    writes "marketplace" regularly and "market place" essentially never.
    """
    suspect = []
    for word, count in counts.items():
        if len(word) < 9 or count > GLUE_MAX_COUNT:
            continue
        pieces = greedy_common_split(word, common)
        if not pieces:
            continue
        spaced = min(bigrams[pair] for pair in zip(pieces, pieces[1:]))
        if spaced >= GLUE_RATIO * count:
            suspect.append(word)
    return suspect


def greedy_common_split(word: str, common: set[str]) -> list[str] | None:
    """Split `word` into two or three everyday words, or give up."""
    for i in range(2, len(word) - 1):
        head, tail = word[:i], word[i:]
        if head not in common:
            continue
        if tail in common:
            return [head, tail]
        for j in range(2, len(tail) - 1):
            if tail[:j] in common and tail[j:] in common:
                return [head, tail[:j], tail[j:]]
    return None


def segment(
    run: str,
    logp: dict[str, float],
    bigrams: Counter | None = None,
    common: set[str] | None = None,
) -> list[str] | None:
    """Viterbi word-break over `run`; None when any piece would be unknown."""
    n = len(run)
    lower = fold(run)
    best = [(-math.inf, 0)] * (n + 1)
    best[0] = (0.0, 0)
    for end in range(1, n + 1):
        for start in range(max(0, end - 20), end):
            score, _ = best[start]
            if score == -math.inf:
                continue
            word = lower[start:end]
            cost = logp.get(word)
            if cost is None:
                continue
            # A small constant per word keeps the search from shredding a long
            # unknown name into a chain of short real words.
            candidate = score + cost - 2.0
            if candidate > best[end][0]:
                best[end] = (candidate, start)
    if best[n][0] == -math.inf:
        return None
    pieces, cursor = [], n
    while cursor > 0:
        prev = best[cursor][1]
        pieces.append(run[prev:cursor])
        cursor = prev
    pieces.reverse()

    pieces = fuse_implausible(pieces, bigrams, common or set())
    return pieces if len(pieces) > 1 else None


def implausible(
    left: str, right: str, bigrams: Counter | None, common: set[str]
) -> bool:
    """Would putting a space between these two pieces invent a reading?

    Two artifacts to catch. A word the corpus has never seen ("polygraph"
    appears only in the damaged 2014 letter) can be "covered" by chaining
    letters that do exist, so a single lowercase letter next to anything is
    suspect unless it is "a" or "I". One size up, "untouchable" is absent from
    the corpus while "un", "touch" and "able" are all present, and the search
    happily produces "un touch able".

    Real prose never puts those pairs together, so the test is whether the
    corpus has ever seen the two words adjacent. It is applied only when one
    side is short, because that is where invention happens; ordinary phrasing
    like "of the" or "we are" passes trivially, having occurred thousands of
    times.
    """
    for piece in (left, right):
        if len(piece) == 1 and piece not in "aAiI" and not piece.isupper():
            return True
    if bigrams is None or min(len(left), len(right)) > 4:
        return False
    if (fold(left), fold(right)) in bigrams:
        return False
    # An unseen pair of two everyday words is just a phrase this author never
    # happened to write ("no match", "metal was"); an unseen pair involving a
    # rare fragment is the invention. Only the second is worth blocking, and
    # distinguishing them is what keeps "nomatch" from surviving the repair.
    return not (fold(left) in common and fold(right) in common)


def fuse_implausible(
    pieces: list[str], bigrams: Counter | None, common: set[str]
) -> list[str]:
    """Glue back only the suspect joins, keeping the rest of the segmentation.

    Rejecting the whole run because one join looks wrong throws away the other
    fourteen correct words in a line-length run. Fusing just the bad pair leaves
    that fragment exactly as the extraction produced it — still glued, still
    reported, never invented.

    A fused fragment is sealed afterwards. Without that, fusing "the"+"S" into
    "theS" creates a pair ("owned", "theS") the corpus has obviously never seen
    either, and the fuse walks left until it has eaten the whole run — turning
    one bad join into a total failure to split.
    """
    parts = [(piece, False) for piece in pieces]
    changed = True
    while changed and len(parts) > 1:
        changed = False
        for i in range(len(parts) - 1):
            (left, left_sealed), (right, right_sealed) = parts[i], parts[i + 1]
            sealed = left_sealed or right_sealed
            if implausible(left, right, None if sealed else bigrams, common):
                parts[i : i + 2] = [(left + right, True)]
                changed = True
                break
    return [piece for piece, _ in parts]


def split_punctuation(token: str) -> str:
    """Re-space around punctuation the extraction glued shut."""
    # Sentence punctuation followed by a letter: "requirement.In" -> ". In".
    # Requiring two letters before the mark protects initials such as "U.S."
    # and "H.J.", which must stay glued.
    token = re.sub(r"([A-Za-z]{2}[.,;:!?])(?=[A-Za-z])", r"\1 ", token)
    # "$134,973,arateof" -> the second comma ends a number and starts a word.
    # A comma or point between two digits is a separator and is left alone.
    token = re.sub(r"(?<=[0-9])([.,])(?=[A-Za-z])", r"\1 ", token)
    # Number/word boundaries: "was$34.2billion" -> "was $34.2 billion".
    token = re.sub(r"(?<=[a-zA-Z])(?=[$])", " ", token)
    token = re.sub(r"(?<=[0-9])(?=[A-Za-z])", " ", token)
    token = re.sub(r"(?<=[a-zA-Z])(?=[0-9])", " ", token)
    # "19.7%compounded", "(an amount)that" -> split after a closing marker.
    token = re.sub(r"(?<=[%)\]])(?=[A-Za-z])", " ", token)
    return token


def repair_token(token, logp, stats, bigrams=None, common=None) -> str:
    if len(token) < SUSPECT_LEN:
        return token
    if fold(token) in logp:
        return token

    out = []
    for piece in split_punctuation(token).split(" "):
        runs = list(RUN.finditer(piece))
        rebuilt, cursor = [], 0
        for match in runs:
            rebuilt.append(piece[cursor : match.start()])
            run = match.group()
            cursor = match.end()
            if len(run) < 5 or fold(run) in logp:
                rebuilt.append(run)
                continue
            pieces = segment(run, logp, bigrams, common)
            if pieces is None or len(pieces) < 2:
                stats["unresolved"] += 1
                rebuilt.append(run)
                continue
            # Splitting a run the corpus has never seen is always an
            # improvement, so the margin test only applies when the glued form
            # is itself a real word — "shareholder" must not become "share
            # holder" just because both halves exist.
            known = logp.get(fold(run))
            if known is not None:
                gain = sum(logp.get(fold(p), -25.0) for p in pieces) - known
                if gain < MIN_GAIN:
                    stats["unresolved"] += 1
                    rebuilt.append(run)
                    continue
            stats["split"] += 1
            stats["words_recovered"] += len(pieces) - 1
            rebuilt.append(" ".join(pieces))
        rebuilt.append(piece[cursor:])
        out.append("".join(rebuilt))
    return " ".join(out)


def repair(text, logp, stats, bigrams=None, common=None) -> str:
    lines = []
    for line in text.splitlines():
        lines.append(
            " ".join(
                repair_token(tok, logp, stats, bigrams, common)
                for tok in line.split(" ")
            )
        )
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def strip_ws(text: str) -> str:
    return re.sub(r"\s+", "", text)


def needs_repair(text: str) -> bool:
    words = WORD.findall(clean_lines(text) or text)
    prose = WORD.findall(text)
    if not prose:
        return False
    return sum(map(len, prose)) / len(prose) > 5.6


def main() -> int:
    dry = "--dry-run" in sys.argv
    good = clean_sources()
    damaged = [p for p in sorted(RAW.glob("*.md")) if p not in good]
    if not damaged:
        print("no damaged files in Raw/")
        return 0

    base_texts = [p.read_text(encoding="utf-8", errors="replace") for p in good]
    logp, bigrams, common = build_model(base_texts)
    print(
        f"vocabulary from {len(good)} cleanly extracted letters: "
        f"{len(logp)} words, {len(bigrams)} bigrams"
    )

    total = Counter()
    for path in damaged:
        text = path.read_text(encoding="utf-8", errors="replace")
        stats: Counter[str] = Counter()
        fixed = repair(text, logp, stats, bigrams, common)

        assert strip_ws(fixed) == strip_ws(text), f"{path.name}: content changed"

        words = WORD.findall(fixed)
        mean = sum(map(len, words)) / len(words)
        before = WORD.findall(text)
        mean_before = sum(map(len, before)) / len(before)
        print(
            f"  {path.name}: {stats['split']} runs split, "
            f"{stats['words_recovered']} words recovered, "
            f"{stats['unresolved']} left glued | "
            f"mean word length {mean_before:.2f} -> {mean:.2f}"
        )
        total.update(stats)
        if not dry:
            path.write_text(fixed, encoding="utf-8")

    print(
        f"\n{len(damaged)} files, {total['words_recovered']} words recovered, "
        f"{total['unresolved']} runs left untouched"
        + (" (dry run, nothing written)" if dry else "")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
