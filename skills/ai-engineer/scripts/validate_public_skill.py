#!/usr/bin/env python3
"""Validate the standalone public ai-engineer package."""

from pathlib import Path
import re
import sys


SKILL = Path(__file__).resolve().parents[1]
SKILLS = SKILL.parent
REPO = SKILLS.parent


def main() -> int:
    errors: list[str] = []
    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    if "name: ai-engineer" not in skill_text:
        errors.append("SKILL.md must declare name: ai-engineer")

    forbidden = ("C:" + "\\Users\\", "gh" + "p_", "CONTEXT7" + "_API_KEY=")
    for path in REPO.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in forbidden:
            if marker in text:
                errors.append(f"{path.relative_to(REPO)} contains forbidden marker {marker!r}")

    # A relative link may point up out of its own skill -- the fork skills (ai-eval,
    # ai-agent-design, ai-regulated) are bodies of `../ai-engineer/references/*` links by
    # design. What must not happen is a link escaping the repository: that is the
    # dependency on an absent sibling this check originally existed to catch, and it fails
    # only on the installing machine, where the target happens not to exist.
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in REPO.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for target in link_pattern.findall(text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            if not resolved.exists():
                errors.append(f"{path.relative_to(REPO)} has broken link: {target}")
                continue
            if not resolved.is_relative_to(REPO):
                errors.append(
                    f"{path.relative_to(REPO)} links outside the repository: {target}"
                )
            elif SKILLS in path.parents and not resolved.is_relative_to(SKILLS):
                errors.append(
                    f"{path.relative_to(REPO)} links out of skills/: {target}"
                )

    required_docs = (
        REPO / "README.md",
        REPO / "docs" / "methods.md",
        REPO / "docs" / "usage.md",
        SKILLS / "ai-eval" / "SKILL.md",
        SKILLS / "ai-agent-design" / "SKILL.md",
        SKILLS / "ai-regulated" / "SKILL.md",
        REPO / "agents" / "ai-engineer.md",
        REPO / "agents" / "ai-engineer-critic.md",
    )
    for path in required_docs:
        if not path.is_file():
            errors.append(f"missing public documentation: {path.relative_to(REPO)}")

    # The critic's read-only guarantee has exactly two valid shapes: no Bash at all
    # (hook-free profile), or Bash plus the PreToolUse guard. Bash without the guard is
    # read-only by instruction only, and that is the shape this check exists to forbid.
    critic = REPO / "agents" / "ai-engineer-critic.md"
    if critic.is_file():
        parts = critic.read_text(encoding="utf-8").split("---", 2)
        front = parts[1] if len(parts) > 2 else ""
        tools = next((l for l in front.splitlines() if l.startswith("tools:")), "")
        if "Bash" in tools and "hooks:" not in front:
            errors.append(
                "ai-engineer-critic has Bash without the PreToolUse read-only guard"
            )
        for banned in ("Write", "Edit"):
            if banned in tools:
                errors.append(f"ai-engineer-critic must not have {banned} in tools")

    if errors:
        print("PUBLIC_SKILL: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PUBLIC_SKILL: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
