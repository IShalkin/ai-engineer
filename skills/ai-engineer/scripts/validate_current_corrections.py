#!/usr/bin/env python3
"""Deterministically verify that the 2026 corrections remain wired into runtime."""

from datetime import date
from pathlib import Path
import re
import sys


# A `verified <date>` label ages silently: nothing recomputes it, so a stale marker keeps
# reading as evidence. Warned rather than failed on purpose -- a date passing this horizon
# is not a defect in the pull request that happens to run the check.
STALE_AFTER_DAYS = 180
VERIFIED = re.compile(r"verified (\d{4})-(\d{2})-(\d{2})")


def check_staleness() -> list[str]:
    today = date.today()
    warnings: list[str] = []
    for path in sorted((ROOT / "references").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for year, month, day in VERIFIED.findall(text):
            try:
                stamped = date(int(year), int(month), int(day))
            except ValueError:
                warnings.append(f"{path.name}: unparseable date {year}-{month}-{day}")
                continue
            age = (today - stamped).days
            if age > STALE_AFTER_DAYS:
                warnings.append(
                    f"{path.name}: 'verified {stamped}' is {age} days old "
                    f"(horizon {STALE_AFTER_DAYS}); re-verify against primary docs"
                )
    return warnings


ROOT = Path(__file__).resolve().parents[1]

REQUIRED = {
    "SKILL.md": ["current-corrections-2026.md", "supersedes conflicting book examples"],
    "references/current-corrections-2026.md": [
        "langchain.agents.create_agent",
        "equal-compute or equal-thinking-token single-agent baseline",
        "Faithfulness",
        "thread-scoped execution state",
        "There is no single sanitization gateway",
    ],
    "references/framework-selection.md": ["langchain.agents.create_agent", "pinned legacy dependency"],
    "references/context-prompt-engineering.md": ["same-task focused-versus-bloated-context"],
    "references/data-rag-search.md": ["backend-specific", "not world factuality"],
    "references/agents-tools-protocols.md": ["not complete memory", "equal-compute"],
    "references/security-governance.md": ["There is no single sanitization gateway", "stored prompt injection"],
    "references/evaluation-testing.md": ["not truth about the world", "progressively bloated context"],
    "references/production-operations.md": ["thread-scoped checkpoint state", "cross-thread Store"],
    "references/completeness-provenance.md": [
        "Current-document maintenance loop",
        "Context7 is optional",
        "documentation_update_status",
    ],
}


def main() -> int:
    errors: list[str] = []
    for relative, needles in REQUIRED.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{relative}: missing required correction marker: {needle!r}")

    if errors:
        print("CURRENT_CORRECTIONS: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    for warning in check_staleness():
        print(f"CURRENT_CORRECTIONS: WARN - {warning}")

    print(f"CURRENT_CORRECTIONS: PASS ({len(REQUIRED)} runtime files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
