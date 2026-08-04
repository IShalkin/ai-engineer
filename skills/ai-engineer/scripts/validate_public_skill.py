#!/usr/bin/env python3
"""Validate the standalone public ai-engineer package."""

from pathlib import Path
import re
import sys


SKILL = Path(__file__).resolve().parents[1]
REPO = SKILL.parents[1]


def main() -> int:
    errors: list[str] = []
    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    if "name: ai-engineer" not in skill_text:
        errors.append("SKILL.md must declare name: ai-engineer")
    sibling_prefix = "../" + "../"
    if sibling_prefix in "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in SKILL.rglob("*.md")
    ):
        errors.append("public skill contains a dependency on an absent sibling skill")

    forbidden = ("C:" + "\\Users\\", "gh" + "p_", "CONTEXT7" + "_API_KEY=")
    for path in REPO.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in forbidden:
            if marker in text:
                errors.append(f"{path.relative_to(REPO)} contains forbidden marker {marker!r}")

    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in SKILL.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for target in link_pattern.findall(text):
            if target.startswith(("http://", "https://", "#")):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            if not resolved.exists():
                errors.append(f"{path.relative_to(REPO)} has broken link: {target}")

    required_docs = (REPO / "README.md", REPO / "docs" / "methods.md", REPO / "docs" / "usage.md")
    for path in required_docs:
        if not path.is_file():
            errors.append(f"missing public documentation: {path.relative_to(REPO)}")

    if errors:
        print("PUBLIC_SKILL: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PUBLIC_SKILL: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
