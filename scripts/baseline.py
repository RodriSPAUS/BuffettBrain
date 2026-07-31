"""Known-failing files, so the lint gate can only ratchet downwards.

The wiki is being repaired one block of letters at a time, and until that
finishes `make lint` reports hundreds of errors in the pages not yet rewritten.
A check that is red on every push is a check nobody reads, and it cannot catch
the thing that actually matters -- a *new* error introduced by today's edit.

So the gate compares against a recorded baseline instead of against zero. A file
may keep the errors it already had; it may not gain one, and a file that is
clean today may never stop being clean. Fixing pages lowers the baseline and can
never raise it, which is the whole point: the number only goes one way.

    make lint          fail only on regressions (what CI runs)
    make lint-strict   fail on any error at all, ignoring the baseline
    make baseline      re-record after fixing pages, so the gate tightens
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

BASELINE_PATH = Path(__file__).resolve().parent / "baseline.json"

# Every finding names the file it belongs to at the start of the message.
FILE_IN_MESSAGE = re.compile(r"((?:wiki|Raw|scripts)/[\w./-]+\.md)")


def file_of(message: str) -> str:
    match = FILE_IN_MESSAGE.search(message)
    return match.group(1) if match else "(no file)"


def tally(messages: list[str]) -> Counter[str]:
    return Counter(file_of(m) for m in messages)


def load() -> dict[str, dict[str, int]]:
    if not BASELINE_PATH.exists():
        return {}
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


def save(counts: dict[str, Counter[str]]) -> None:
    ordered = {
        check: dict(sorted(files.items()))
        for check, files in sorted(counts.items())
        if files
    }
    BASELINE_PATH.write_text(
        json.dumps(ordered, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def compare(check: str, current: Counter[str]) -> tuple[list[str], list[str]]:
    """Return (regressions, improvements) for one check against the baseline."""
    allowed = load().get(check, {})
    regressions, improvements = [], []
    for path, count in sorted(current.items()):
        budget = allowed.get(path, 0)
        if count > budget:
            regressions.append(
                f"{path}: {count} errors, baseline allows {budget}"
                + (" (this file was clean)" if budget == 0 else "")
            )
        elif count < budget:
            improvements.append(f"{path}: {budget} -> {count}")
    for path, budget in sorted(allowed.items()):
        if path not in current and budget:
            improvements.append(f"{path}: {budget} -> 0")
    return regressions, improvements
