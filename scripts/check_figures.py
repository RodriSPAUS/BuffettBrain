#!/usr/bin/env python3
"""Check that the numbers on a page appear in the source it cites.

`verify_quotes` protects everything inside quotation marks. Nothing protected
the figures outside them, and figures are where fabrication does the most damage:
LESSONS_LEARNED records invented metrics presented as fact ("market share ~35%",
"cost per unit 20% below industry average"), and the 2003 summary claimed float
"grew to over $44 billion" when the letter says only that float grew by 41%.

A number is cheap to verify and expensive to get wrong, so this checks every one
of them: money, percentages and any figure of four digits or more get looked up
in the cited Raw/ file.

What it deliberately does not catch, because no string match can: a page that
copies two correct numbers and draws the wrong conclusion from them. The 2003
page reported 21.0% for Berkshire and 28.7% for the S&P — both right — and called
that "outperforming". Verified figures narrow the surface where judgment is
still required; they do not remove it.

    python3 scripts/check_figures.py                     # every summary
    python3 scripts/check_figures.py Sources/2003ltr     # one
"""

from __future__ import annotations

import re
import sys

from wikilib import RAW, WIKI, Report, split_frontmatter

# $13.6 billion, 21.0%, 2,338,961,000, $1,340 million.
FIGURE = re.compile(
    r"\$\s?[\d,]+(?:\.\d+)?(?:\s?(?:billion|million|thousand))?"
    r"|[\d,]+(?:\.\d+)?\s?(?:billion|million)"
    r"|\d+(?:\.\d+)?\s?%"
    # The decimal part is not optional decoration: a table cell reading 1,392.7
    # matched as "1,392" is then compared against the source's 1392.7 and misses
    # by 0.7, which is wider than the tolerance four significant figures allow.
    # Every summary that reproduces a dollar table in thousands hit this.
    r"|\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b"
)

# Years, and small round numbers that mean nothing on their own.
YEAR = re.compile(r"^(?:19|20)\d\d$")


def normalise(figure: str) -> str:
    """Compare on digits and unit only: '$13.6 billion' and '13.6 billion' match."""
    text = figure.lower().replace("$", "").replace(",", "").replace(" ", "")
    return text.rstrip("%")


def figures(text: str) -> list[str]:
    out, seen = [], set()
    for match in FIGURE.findall(text):
        key = normalise(match)
        digits = key.rstrip("abcdefghijklmnopqrstuvwxyz")
        if not digits or YEAR.match(digits) or key in seen:
            continue
        # A bare one- or two-digit number is not a claim worth tracing.
        if len(digits.replace(".", "")) < 3 and "%" not in match and not key[-1].isalpha():
            continue
        seen.add(key)
        out.append(match.strip())
    return out


SCALE = {"thousand": 1_000, "million": 1_000_000, "billion": 1_000_000_000}

# Any number in the source, with or without a scale word attached.
RAW_NUMBER = re.compile(r"([\d,]+(?:\.\d+)?)\s*(billion|million|thousand)?", re.I)


def value_of(text: str) -> float | None:
    """The number a written figure denotes, in units."""
    key = normalise(text)
    unit = next((u for u in SCALE if key.endswith(u)), None)
    digits = key[: -len(unit)].strip() if unit else key
    if not re.fullmatch(r"\d+(?:\.\d+)?", digits or ""):
        return None
    return float(digits) * (SCALE[unit] if unit else 1)


def raw_values(raw_text: str) -> set[float]:
    """Every number the source states, scale words applied.

    A table column headed "(000s omitted)" is not read here, so the same figure
    may legitimately appear at 1000x. Those scalings are generated on the wiki
    side instead, in raw_has.
    """
    out = set()
    for digits, unit in RAW_NUMBER.findall(raw_text):
        digits = digits.replace(",", "")
        if not re.fullmatch(r"\d+(?:\.\d+)?", digits):
            continue
        out.add(float(digits) * (SCALE[unit.lower()] if unit else 1))
    return out


def raw_has(values: set[float], figure: str) -> bool:
    """Does the source state this figure, allowing for rounding and units?

    A summary writes "$21.9 million" for a letter's "$21,904,000". String
    matching cannot see that they are the same claim, and a checker that reports
    43 correct pages as wrong is one nobody runs. So compare numerically, and
    accept any source figure that rounds to what the page says -- at the page's
    own precision, so "21.9" accepts 21,850,000 to 21,949,999 and "21.94" does
    not.
    """
    wanted = value_of(figure)
    if wanted is None:
        return True
    decimals = len(figure.partition(".")[2].rstrip("%abcdefghijklmnopqrstuvwxyz "))
    significant = len(re.sub(r"\D", "", figure.partition(".")[0])) + decimals
    # Scaling down is how a letter's "(000s omitted)" table states the same
    # figure, but it must stop before the number becomes small enough to match
    # anything: $44 billion divided to 44 finds a "44" in any long document, and
    # that is how a real error passed. Below 100 a coincidence is likelier than a
    # match.
    scales = (1, 1_000, 1_000_000, 1_000_000_000)
    targets = [wanted * s for s in scales]
    targets += [wanted / s for s in scales[1:] if wanted / s >= 100]
    for target in targets:
        tolerance = abs(target) * (10 ** -significant) * 5 if significant else 0.5
        if any(abs(v - target) <= max(tolerance, 0.5) for v in values):
            return True
    return False


def main() -> int:
    argv = [a for a in sys.argv[1:] if not a.startswith("-")]
    wanted = {a.split("/")[-1].removesuffix(".md") for a in argv}

    report = Report("check_figures: numbers on the page vs the source it cites")
    for page in sorted((WIKI / "Sources").glob("*.md")):
        if wanted and page.stem not in wanted:
            continue
        raw = RAW / f"{page.stem}.md"
        if not raw.exists():
            continue
        text = page.read_text(encoding="utf-8", errors="replace")
        if "> TODO:" in text:
            continue
        _, body = split_frontmatter(text)
        values = raw_values(raw.read_text(encoding="utf-8", errors="replace"))

        missing = [f for f in figures(body) if not raw_has(values, f)]
        for figure in missing[:8]:
            # A summary legitimately cites a figure from another year when it
            # cross-references. Absent from its own letter is worth a look;
            # absent from all 48 is the fabrication signal.
            elsewhere = sorted(
                other.stem
                for other in RAW.glob("*.md")
                if other != raw and raw_has(raw_values(other.read_text(encoding="utf-8", errors="replace")), figure)
            )
            if elsewhere:
                report.warn(f"{page.stem}: {figure} is not in this letter (it is in {elsewhere[0]})")
            else:
                report.warn(f"{page.stem}: {figure} appears in NO letter in the corpus")

    return report.finish(limit=60, warn_only=True)


if __name__ == "__main__":
    sys.exit(main())
