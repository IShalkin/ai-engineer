#!/usr/bin/env python3
"""Validate the standalone public ai-engineer package."""

from pathlib import Path
import re
import sys


SKILL = Path(__file__).resolve().parents[1]
SKILLS = SKILL.parent
REPO = SKILLS.parent


def _frontmatter_tools(text: str) -> "set[str] | None":
    """Tool names granted by an agent file, in either YAML spelling.

    Both `tools: Read, Grep` and a block sequence of `- Read` lines are legal, and a
    substring test over the single `tools:` line reads the block form as granting nothing --
    which passed an agent holding Bash. Hand-parsed rather than via PyYAML so the validator
    keeps working with a bare standard library, in CI and on an offline machine alike.
    """
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    front = text[3:end] if end != -1 else text[3:]

    lines = front.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("tools:"):
            continue
        inline = line.split(":", 1)[1].strip().strip("[]")
        names = {n.strip() for n in inline.split(",") if n.strip()}
        for following in lines[index + 1:]:
            stripped = following.strip()
            if stripped.startswith("- "):
                names.add(stripped[2:].strip())
                continue
            if stripped and not following.startswith((" ", "\t")):
                break
        return {n for n in names if n and n not in ("[", "]")}
    return None


def main() -> int:
    errors: list[str] = []
    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    if "name: ai-engineer" not in skill_text:
        errors.append("SKILL.md must declare name: ai-engineer")

    # One spelling of a machine home directory is not a leak check: different tools write
    # the drive-letter form with either separator and either case, and the forward-slash
    # spelling is the one that survives being pasted into YAML. Matched case-insensitively
    # on both separators, plus the token prefixes worth refusing outright. Deliberately no
    # example path in this comment -- the scan reads this file too.
    forbidden = (
        re.compile(r"[a-z]:[\\/]users[\\/]", re.I),
        re.compile(r"[\\/]home[\\/](?!user\b|USER\b)[a-z0-9._-]+[\\/]", re.I),
        re.compile("gh" + "[pousr]_[A-Za-z0-9]{16}"),
        re.compile("sk-ant-" + "[A-Za-z0-9_-]{8}"),
        re.compile(r"\bAKIA[0-9A-Z]{12}"),
        re.compile("CONTEXT7" + "_API_KEY="),
    )
    for path in REPO.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in forbidden:
            hit = marker.search(text)
            if hit:
                errors.append(
                    f"{path.relative_to(REPO)} contains a forbidden marker matching "
                    f"{marker.pattern!r}"
                )

    # The class behind a defect that shipped: three modules told the agent to load
    # book-derived sibling skills this package does not contain, so the agent found
    # nothing and synthesized instead of reporting blocked_missing_source. Absent
    # artifacts are invisible to a link check, because they were never links.
    for path in SKILL.rglob("*.md"):
        if "sibling skill" in path.read_text(encoding="utf-8"):
            errors.append(
                f"{path.relative_to(REPO)} instructs loading a sibling skill this package "
                "does not ship; route through source-extension.md (COV-01) instead"
            )

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

    # The critic is read-only because of what it was never granted. Asserted as a class:
    # its tools must be a SUBSET of a read-only allowlist. A denylist of two names passed a
    # critic holding Bash, MultiEdit or Task, which is the "assert the instance" defect the
    # package tells other people not to ship.
    CRITIC_ALLOWED = {"Read", "Grep", "Glob", "Skill", "ToolSearch", "WebFetch"}
    critic = REPO / "agents" / "ai-engineer-critic.md"
    if critic.is_file():
        granted = _frontmatter_tools(critic.read_text(encoding="utf-8"))
        if granted is None:
            errors.append("ai-engineer-critic declares no tools: field")
        else:
            for tool in sorted(granted - CRITIC_ALLOWED):
                errors.append(
                    f"ai-engineer-critic must not be granted {tool}: the read-only "
                    f"allowlist is {sorted(CRITIC_ALLOWED)}"
                )

    if errors:
        print("PUBLIC_SKILL: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PUBLIC_SKILL: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
