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


# Matches a procedure ID: exactly three uppercase letters, a hyphen, exactly two digits,
# with no word character on either side -- ARC-01, JDG-04, FIN-07. Deliberately does NOT
# match prose or version-like neighbours: lowercase (`arc-01`), two or four letters
# (`ML-01`, `EVAL-01`), one or three digits (`ARC-1`, `ARC-001`), a longer run it is part of
# (`XARC-01`, `ARC-01A`, `GPT-4o-01`), or anything with the hyphen spelled differently
# (`ARC 01`, `ARC_01`). Any real ID that fails this pattern is a naming bug, not a false
# negative to widen the regex for.
ID_PATTERN = re.compile(r"(?<![0-9A-Za-z])([A-Z]{3}-[0-9]{2})(?![0-9A-Za-z])")


def _skill_regions(skill_text: str) -> "dict[str, str]":
    """The three parts of SKILL.md that can select a procedure, keyed by path name."""
    router, loading, boundary = [], [], []
    section = None
    fenced = False
    for line in skill_text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if line.startswith("## "):
            section = line[3:].strip()
        if section == "Task Router" and line.startswith("|"):
            router.append(line)
        elif section == "Context Loading Protocol" and re.match(r"\s*\d+\.", line):
            loading.append(line)
        elif line.startswith("Preserve these compound boundaries"):
            boundary.append(line)
    return {
        "task-router row": "\n".join(router),
        "compound-boundary paragraph": "\n".join(boundary),
        "context-loading step": "\n".join(loading),
    }


def check_addressing(
    index_text: str,
    skill_text: str,
    read_module,
    index_name: str = "references/procedure-index.md",
    skill_name: str = "SKILL.md",
) -> "tuple[list[str], dict[str, int]]":
    """Enforce the ID addressing contract. `read_module(filename)` returns module text or None.

    Returns (errors, counts) where counts reports how many IDs each reachability path
    selects -- printed even on success, because the maintainer reads those numbers.
    """
    errors: list[str] = []
    rows: list[tuple[str, str]] = []
    seen: dict[str, int] = {}

    for line in index_text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        match = ID_PATTERN.fullmatch(cells[0])
        if not match:
            continue
        procedure_id, canonical = match.group(1), cells[2]
        seen[procedure_id] = seen.get(procedure_id, 0) + 1
        if seen[procedure_id] > 1:
            errors.append(
                f"{index_name}: {procedure_id} appears in {seen[procedure_id]} table rows; "
                "delete the duplicates so one ID names one canonical file"
            )
            continue
        rows.append((procedure_id, canonical))

    # Fail closed: an unparseable table must never read as a silent pass.
    if not rows:
        errors.append(
            f"{index_name}: 0 procedure rows parsed -- the ID table is missing or its "
            "format changed; a row must be `| XXX-NN | trigger | file.md | output |`"
        )
        return errors, {}

    for procedure_id, canonical in rows:
        module_text = read_module(canonical)
        if module_text is None:
            errors.append(
                f"{index_name}: {procedure_id} names canonical file {canonical!r} which does "
                f"not exist; fix the row or add the module"
            )
            continue
        if not any(
            line.startswith("#") and procedure_id in ID_PATTERN.findall(line)
            for line in module_text.splitlines()
        ):
            errors.append(
                f"{canonical}: no heading contains {procedure_id}, but {index_name} makes it "
                f"that ID's canonical home; restore the heading or repoint the index row"
            )

    indexed = {procedure_id for procedure_id, _ in rows}
    regions = _skill_regions(skill_text)
    reached_by = {name: set(ID_PATTERN.findall(text)) for name, text in regions.items()}
    reachable = set().union(*reached_by.values())

    for name, ids in sorted(reached_by.items()):
        if not ids:
            errors.append(
                f"{skill_name}: no procedure ID is reachable through any {name}; that "
                "selection path was deleted or reworded -- restore it, or delete this "
                "arm of the check so its count stops reading as coverage"
            )

    for procedure_id in sorted(indexed - reachable):
        errors.append(
            f"{skill_name}: {procedure_id} is unreachable -- it is in {index_name} but in no "
            "task-router row, no compound-boundary sentence and no context-loading step; add "
            "it to one or delete the index row"
        )
    for procedure_id in sorted(set(ID_PATTERN.findall(skill_text)) - indexed):
        errors.append(
            f"{skill_name}: mentions {procedure_id}, which has no row in {index_name}; add "
            "the index row and its module heading, or drop the mention"
        )

    counts = {name: len(ids) for name, ids in reached_by.items()}
    counts["indexed"] = len(indexed)
    counts["reachable"] = len(reachable & indexed)
    return errors, counts


def _index_rows(index_text: str) -> "list[tuple[str, str, str, int]]":
    """Procedure-index rows as (id, canonical file, required output, 1-based line number).

    Shared by checks A/B/C/D so one table-shape assumption is written once. Duplicate IDs are
    left in: check_addressing already reports them, and dropping them here would hide a
    duplicate's bad Load column or bad done-test.
    """
    rows = []
    for number, line in enumerate(index_text.splitlines(), start=1):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        match = ID_PATTERN.fullmatch(cells[0])
        if match:
            rows.append((match.group(1), cells[2], cells[3], number))
    return rows


def check_router_load_columns(
    index_text: str,
    skill_text: str,
    index_name: str = "references/procedure-index.md",
    skill_name: str = "SKILL.md",
) -> "list[str]":
    """CHECK A: every ID named in the router must be named by at least one row that also
    loads the module defining it.

    Naming ARC-04 while no router row that names it loads framework-selection.md sends the
    agent to a control it cannot read -- the ID resolves in the index but the text never
    arrives in context. Asserted against column 3 of that ID's index row, so no module name
    or ID is written here.

    Deliberately per ID, not per (row, ID) pair: a row may name a secondary ID whose home is
    loaded by that ID's own row or by the expansion rule in the Context Loading Protocol, and
    requiring the home in every row that mentions it would force Load cells past the
    two-module budget the same SKILL.md states. What is not tolerated is an ID no row ever
    pairs with its own module.
    """
    errors: list[str] = []
    canonical = {row[0]: row[1] for row in _index_rows(index_text)}
    if not canonical:
        errors.append(
            f"{index_name}: 0 procedure rows parsed while checking router Load columns; "
            "the ID table is missing or its format changed"
        )
        return errors

    rows = [
        line for line in _skill_regions(skill_text)["task-router row"].splitlines()
        if line.startswith("|")
    ]
    pairs = 0
    paired: dict[str, bool] = {}
    for line in rows:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        ids_cell, load_cell = cells[1], cells[2]
        for procedure_id in sorted(set(ID_PATTERN.findall(ids_cell))):
            module = canonical.get(procedure_id)
            if module is None:
                continue  # check_addressing reports an unindexed mention
            pairs += 1
            paired[procedure_id] = paired.get(procedure_id, False) or module in load_cell
    for procedure_id, ok in sorted(paired.items()):
        if not ok:
            errors.append(
                f"{skill_name}: {procedure_id} is named in the Task Router but no row that "
                f"names it loads {canonical[procedure_id]}, the canonical module that defines "
                "it; add the module to one of those rows or drop the ID"
            )
    if not pairs:
        errors.append(
            f"{skill_name}: 0 router-row/ID pairs parsed; the Task Router table is missing or "
            "its columns changed -- a row must be `| task | IDs | Load |`"
        )
    return errors


def check_module_reachability(
    index_text: str,
    skill_text: str,
    module_names: "list[str]",
    skill_name: str = "SKILL.md",
) -> "list[str]":
    """CHECK B: every runtime module in references/ must be routed to.

    Reverse of check_addressing, which only proves IDs are reachable. A module nothing loads
    is dead weight in a package that claims progressive loading.

    Every .md file is required, not only the canonical homes: the version overlays
    (current-corrections-2026.md, current-standards.md) are named in exactly one protocol step
    each and own no ID, so a derived "canonical homes only" exemption made orphaning a live
    overlay invisible. The one exemption is named here with its reason -- routing-checklist.md
    is a maintainer test list, not runtime content the agent is ever meant to load.
    """
    exempt = {"routing-checklist.md"}
    errors: list[str] = []
    if not module_names:
        errors.append("references/: 0 module files found; the directory is missing or empty")
        return errors
    canonical = {row[1] for row in _index_rows(index_text)}
    if not canonical:
        errors.append(
            "references/procedure-index.md: 0 procedure rows parsed while checking module "
            "reachability; the ID table is missing or its format changed"
        )
        return errors

    regions = _skill_regions(skill_text)
    addressed = regions["task-router row"] + "\n" + regions["context-loading step"]
    if not addressed.strip():
        errors.append(
            f"{skill_name}: no Task Router rows and no Context Loading Protocol steps parsed; "
            "nothing routes to any module"
        )
        return errors

    for name in sorted(set(module_names) - exempt):
        if name not in addressed:
            errors.append(
                f"{skill_name}: references/{name} is a runtime module but is named in no "
                "Load column and no Context Loading Protocol step; route to it or fold it "
                "into a module that is routed to"
            )
    return errors


# A done-test has to be falsifiable by reading the output. Two shapes make it so: an explicit
# integer count, or an enumeration -- a comma-separated list of at least two named deliverables,
# which a reader can count off. A bare quantifier does NOT: "all relevant items covered",
# "every material aspect handled", "no issues remain" are the vacuous phrasings this check
# exists to reject, and they are written in exactly that vocabulary, so accepting
# all/each/every/no made the check pass its own target class. A quantifier is still fine when it
# rides along with a count or an enumeration ("all 10 steps, 5 gates each passed").
# The qualitative escapes are the second arm; published guidance for the target model is that
# instructions are read literally, so "appropriate controls documented" is satisfied by anything
# the model already did. Both halves are content classes, not lists of cells.
_COUNT = re.compile(r"\b[0-9]+\b")
_QUALITATIVE_ESCAPES = (
    "appropriate",
    "reasonable",
    "as needed",
    "as applicable",
    "where relevant",
    "if useful",
    "looks fine",
    "looks good",
    "high quality",
)


def _countable(required: str) -> bool:
    if _COUNT.search(required):
        return True
    return len([part for part in required.split(",") if part.strip()]) >= 2


def check_required_output_shape(
    index_text: str, index_name: str = "references/procedure-index.md"
) -> "list[str]":
    """CHECK C: column 4 of every procedure-index row must be a checkable done-test."""
    errors: list[str] = []
    rows = _index_rows(index_text)
    if not rows:
        errors.append(
            f"{index_name}: 0 procedure rows parsed while checking Required output cells; "
            "the ID table is missing or its format changed"
        )
        return errors

    for procedure_id, _, required, number in rows:
        if not required:
            errors.append(
                f"{index_name}:{number}: {procedure_id} has an empty Required output cell"
            )
            continue
        if not _countable(required):
            errors.append(
                f"{index_name}:{number}: {procedure_id} Required output {required!r} states no "
                "integer count and enumerates fewer than two named deliverables, so nothing "
                "can be counted against it; a bare quantifier is not a count -- state the "
                "number or list the items"
            )
        for escape in _QUALITATIVE_ESCAPES:
            if escape in required.lower():
                errors.append(
                    f"{index_name}:{number}: {procedure_id} Required output {required!r} "
                    f"contains the qualitative escape {escape!r}; a literal reader satisfies "
                    "it with anything -- state the observable instead"
                )
    return errors


_SEGMENT = re.compile(r"[.;!?\n]|(?:^|\n)\s*[-*+]\s")


def _count_statements(text: str) -> int:
    """Sentence- or bullet-sized segments of at least three words."""
    total = 0
    for segment in _SEGMENT.split(text):
        words = [w for w in re.split(r"\s+", re.sub(r"[|`*_#>\[\]()]", " ", segment)) if w]
        if len(words) >= 3:
            total += 1
    return total


def check_procedure_bodies(
    index_text: str,
    read_module,
    index_name: str = "references/procedure-index.md",
    min_statements: int = 3,
) -> "list[str]":
    """CHECK D: the section under each ID's canonical heading must have a body.

    check_addressing proves the heading exists; a heading with nothing under it satisfies
    every other check in this file. `min_statements` is the maintainer's bar (unchanged in
    value from the line-count bar it replaces), exposed as an argument rather than buried in
    the body.

    The unit is a statement, not a line: counting non-empty lines measured the author's
    wrapping, so three lines reading `TODO` passed while a two-paragraph state machine failed.
    A statement is a sentence- or bullet-sized segment of at least three words, which is the
    smallest thing that can state part of a procedure.
    """
    errors: list[str] = []
    rows = _index_rows(index_text)
    if not rows:
        errors.append(
            f"{index_name}: 0 procedure rows parsed while checking procedure bodies; the ID "
            "table is missing or its format changed"
        )
        return errors

    for procedure_id, canonical, _, _ in rows:
        module_text = read_module(canonical)
        if module_text is None:
            continue  # check_addressing reports the missing file
        lines = module_text.splitlines()
        heading = next(
            (
                index for index, line in enumerate(lines)
                if line.startswith("#") and procedure_id in ID_PATTERN.findall(line)
            ),
            None,
        )
        if heading is None:
            continue  # check_addressing reports the missing heading
        level = len(lines[heading]) - len(lines[heading].lstrip("#"))
        kept = []
        for line in lines[heading + 1:]:
            if line.startswith("#") and len(line) - len(line.lstrip("#")) <= level:
                break
            kept.append(line)
        body = _count_statements("\n".join(kept))
        if body < min_statements:
            errors.append(
                f"{canonical}: section {procedure_id} states {body} statement(s) of three or "
                f"more words under its heading, fewer than {min_statements}; the index "
                "addresses a procedure whose body does not state one"
            )
    return errors


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

    references = SKILL / "references"

    def read_module(name: str) -> "str | None":
        path = references / name
        if not path.is_file() or not path.resolve().is_relative_to(references):
            return None
        return path.read_text(encoding="utf-8")

    index_path = references / "procedure-index.md"
    if not index_path.is_file():
        errors.append("missing references/procedure-index.md: nothing addresses procedure IDs")
    else:
        index_text = index_path.read_text(encoding="utf-8")
        addressing_errors, counts = check_addressing(index_text, skill_text, read_module)
        errors.extend(addressing_errors)
        for name, count in counts.items():
            print(f"ADDRESSING: {name}: {count}")

        module_names = sorted(p.name for p in references.glob("*.md"))
        errors.extend(check_router_load_columns(index_text, skill_text))
        errors.extend(check_module_reachability(index_text, skill_text, module_names))
        errors.extend(check_required_output_shape(index_text))
        errors.extend(check_procedure_bodies(index_text, read_module))

    if errors:
        print("PUBLIC_SKILL: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PUBLIC_SKILL: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
