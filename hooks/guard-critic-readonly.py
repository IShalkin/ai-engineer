# -*- coding: utf-8 -*-
"""PreToolUse guard for the ai-engineer-critic subagent: refuse every mutation.

WHY THIS EXISTS. The critic's job is to refute claims by measurement, and it must
not "helpfully" fix what it finds -- a reviewer that edits the thing it reviews has
no independent standing. Its agent file already omits Write and Edit from `tools`,
which is a real mechanism. But it keeps Bash, and Bash can write: a heredoc, `>`,
`sed -i`, `cp` over a tracked file. So the tool allowlist alone does not close it.

This hook is the second half of that control. It reads the actual command and
denies the mutating ones, so the boundary is enforced at execution time rather than
by an instruction the model can decline. Where the working tree is not under
version control an overwrite is unrecoverable, which is why a deny-by-default
posture is worth the occasional false refusal.

Deliberately NOT blocked: writes under a temp directory. Mutation testing is how
this critic earns its findings -- it must be able to copy a file out of the repo,
patch the copy and run it. That is the documented method, so the guard permits it
and blocks writes back into a real tree.

Wiring: `hooks:` frontmatter in ~/.claude/agents/ai-engineer-critic.md. Subagent
hooks fire ONLY while that subagent runs and are removed when it finishes
(confirmed in docs/en/hooks: "Subagent hooks: Claude Code runs them only while that
subagent is running"), so this cannot leak into the main thread or a sibling agent.

Contract, from docs/en/hooks:
  stdin  -> {"tool_name": ..., "tool_input": {...}, "agent_type": ..., ...}
  stdout -> {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                    "permissionDecision": "deny"|"allow",
                                    "permissionDecisionReason": str}}
  exit 0 with JSON: the decision field governs. Exit 2 blocks unconditionally.
"""

import json
import os
import re
import sys
import threading

sys.stdout.reconfigure(encoding="utf-8")

STDIN_TIMEOUT_S = 2.0     # generous on purpose: a slow machine must not read as a timeout

# Writes here are legitimate: the critic mutates COPIES outside the repo.
TEMP_HINTS = ("/tmp/", "\\temp\\", "/temp/", "appdata\\local\\temp",
              "appdata/local/temp", "$tmpdir", "%temp%")

# The critic's own memory (`memory: user` in its agent file). Excused because the guard
# and that field otherwise CONTRADICT each other: a
# review found a new defect class, its own instructions told it to record the class, and
# it could not -- this directory is not a temp path. A critic that cannot keep its leads
# re-derives them every session, and a class found three sessions ago is the cheapest
# lead a review gets.
#
# Narrow on purpose. One directory, no repo content, nothing any pipeline reads, so a
# write here cannot damage an artefact. Note what is deliberately NOT excused:
# `~/.claude/hooks/` is also outside the repo and stays DENIED, because the hooks ARE
# the controls -- a reviewer must not edit the guard that is reviewing it.
WRITABLE_HINTS = TEMP_HINTS + ("\\.claude\\agent-memory", "/.claude/agent-memory")

# Each pattern is a way to change a file from a shell. Ordered roughly by how often
# a model reaches for it.
MUTATORS = [
    (r">>?\s*[^\s|&;>]", "output redirection"),
    (r"\btee\b", "tee"),
    (r"\bsed\b[^|]*-[a-zA-Z]*i", "sed -i (in-place edit)"),
    (r"\bcp\b", "cp"),
    (r"\bmv\b", "mv"),
    (r"\brm\b", "rm"),
    (r"\btruncate\b", "truncate"),
    (r"\bdd\b", "dd"),
    (r"\bchmod\b", "chmod"),
    (r"\binstall\b\s+-", "install"),
    (r"\btouch\b", "touch"),
    (r"\bmkdir\b", "mkdir"),
    # A heredoc into python/node/perl is the usual way a model writes a file while
    # looking like it is only running a script.
    (r"<<-?\s*'?\w*EOF", "heredoc"),
    # NOTE the missing \b before -c and -e. `\b-c\b` CANNOT MATCH ` -c `: \b needs a
    # word/non-word transition and space->hyphen is non-word->non-word. Measured:
    #   re.search(r'\b-c\b', 'python -c x') -> None
    #   re.search(r'-c\b',   'python -c x') -> match
    # so both of these patterns were dead, and `python -c "open('validators/v.py','w')"`
    # -- the canonical unrecoverable overwrite in a repo with no git, named in this
    # file's own opening paragraph -- was ALLOWED. Do not re-add the leading \b.
    # `py` is Windows' launcher and reaches the same interpreter.
    (r"\b(?:python\d?(?:\.\d+)?|py)\b[^|]*-c\b[^|]*\bopen\s*\([^)]*['\"][wax]", "python open(mode=w/a/x)"),
    (r"\b(?:python\d?(?:\.\d+)?|py)\b[^|]*\b(?:shutil|os\.remove|os\.rename|os\.replace|os\.unlink|os\.truncate|pathlib.*write|\.write_text|\.write_bytes)",
     "python filesystem call"),
    (r"\bnode\b[^|]*-e\b[^|]*\b(?:writeFile|appendFile|createWriteStream|unlink|rename)", "node filesystem call"),
    # perl -i and ruby -i are sed -i under another name.
    (r"\b(?:perl|ruby)\b[^|]*-[a-zA-Z]*i", "perl/ruby -i (in-place edit)"),
    # A symlink swap replaces a file's contents without writing to it.
    (r"\bln\b", "ln (symlink/hardlink)"),
    # Shelling out sideways defeats every pattern above, so the escape hatch itself
    # is a mutation candidate: these interpreters have their own write verbs.
    (r"\b(?:powershell|pwsh)\b[^|]*(?:Set-Content|Add-Content|Out-File|Remove-Item|Move-Item|Copy-Item|New-Item)",
     "PowerShell write cmdlet"),
    (r"\bcmd(?:\.exe)?\b[^|]*/c\b[^|]*\b(?:copy|move|del|ren|erase)\b", "cmd.exe write command"),
    (r"\bgit\s+(?:commit|push|checkout|reset|clean|restore|rm|mv|apply|stash)\b",
     "git state change"),
    (r"\bnpm\s+(?:install|ci|publish)\b", "npm install/publish"),
    (r"\bpip\d?\s+(?:install|uninstall)\b", "pip install"),
]

DENY = ("This subagent is a read-only reviewer. %s is a mutation, and the critic "
        "must not change what it reviews -- a reviewer that edits its subject has "
        "no independent standing. Report the finding and the smallest fix in one "
        "sentence instead; someone else applies it. To mutation-test, copy the "
        "file to a temp path OUTSIDE the repo and patch the copy -- writes under a "
        "temp directory are permitted.")


def looks_temp(text):
    """True if this path is one the critic is permitted to write.

    Named for the original rule (temp copies) and now covers the critic's own memory
    directory too -- see WRITABLE_HINTS. Kept as one predicate rather than two so there
    is a single place where "may write here" is decided.
    """
    low = text.lower()
    return any(h in low for h in WRITABLE_HINTS)


# Forms containing `>` that cannot write a file. Removed before the redirection
# pattern runs, because they were producing REAL false denials: a review measured
# `md5sum x 2>/dev/null`, `grep -rn x validators/ 2>/dev/null` and inline Python
# containing `getsize(p)>600000` all refused, costing the critic Bash calls on a
# machine where each one is ~3s. Only the null device and numeric right-hand sides
# are excused -- `2>real_file.txt` still writes, so it is deliberately NOT here.
_NON_WRITING_GT = [
    re.compile(r"[0-9&]?>>?\s*/dev/null\b"),        # >/dev/null, 2>/dev/null, &>/dev/null
    re.compile(r"[0-9]?>&\s*[0-9-]"),               # 2>&1, >&-
    re.compile(r"[0-9&]?>>?\s*(?:NUL|nul)\b"),      # the Windows null device
    # A comparison against a literal number: `>600000`, `>= 2`, `1>2`. A digit may sit
    # on the LEFT too (`print(1>2)`), so the lookbehind excludes only letters and `_`
    # -- keeping a digit there made `1>2` read as redirection. What this gives up: a
    # shell redirection whose target filename is purely numeric (`echo x 1>2` writes a
    # file called "2") is now allowed. Accepted: that is not a repo file, and every
    # other numeric-fd form (`2>/dev/null`, `2>&1`) is handled by the patterns above,
    # while `2>errors.txt` is not excused at all.
    re.compile(r"(?<![a-zA-Z_])>=?\s*-?[0-9][0-9_.eE+]*"),
]


def strip_non_writing_gt(cmd):
    for rx in _NON_WRITING_GT:
        cmd = rx.sub(" ", cmd)
    return cmd


def classify(tool_name, tool_input):
    """Return a deny reason, or None to allow."""
    if tool_name in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        # Should be unreachable -- these are absent from the agent's `tools`. Kept
        # so the guard does not depend on that list staying correct.
        path = str(tool_input.get("file_path", ""))
        if looks_temp(path):
            return None
        return DENY % tool_name

    if tool_name != "Bash":
        return None

    cmd = str(tool_input.get("command", ""))
    if not cmd.strip():
        return None
    # Stripped for BOTH the mutator scan and the target parse below, so a discarded
    # `2>/dev/null` cannot come back as an unrecognised write target either.
    cmd = strip_non_writing_gt(cmd)

    # A command whose every write target is a temp path is the mutation-testing
    # workflow, which this critic needs. Judged on the whole command: a pipeline
    # that touches a temp file AND a repo file is refused, because deciding which
    # half wins is exactly the kind of guess a guard should not make.
    hits = [name for pat, name in MUTATORS if re.search(pat, cmd, re.I)]
    if not hits:
        return None
    if looks_temp(cmd) and not _touches_repo(cmd):
        return None
    return DENY % hits[0]


def _touches_repo(cmd):
    """True if the command names a path that is not obviously temp.

    Conservative on purpose: an unrecognised relative path counts as the repo,
    because the critic's cwd IS the repo.
    """
    # Redirection targets and the tail arguments of cp/mv are the write positions.
    targets = re.findall(r">>?\s*([^\s|&;]+)", cmd)
    targets += re.findall(r"\b(?:cp|mv|install)\b\s+(?:-\S+\s+)*\S+\s+([^\s|&;]+)", cmd)
    targets += re.findall(r"\b(?:rm|truncate|touch|chmod)\b\s+(?:-\S+\s+)*([^\s|&;]+)", cmd)
    # sed -i writes its LAST argument, after a script that may be quoted and may
    # itself contain slashes. Parsed separately because the script is not a path,
    # and treating it as one made every temp-copy patch look repo-bound.
    targets += re.findall(
        r"\bsed\b\s+(?:-[a-zA-Z]*i[a-zA-Z]*\S*\s+)(?:'[^']*'|\"[^\"]*\"|\S+)\s+([^\s|&;]+)",
        cmd)
    for t in targets:
        if not looks_temp(t):
            return True
    # No explicit target parsed (a heredoc, an inline python write): treat as repo.
    return not targets


def read_stdin_bounded(timeout=STDIN_TIMEOUT_S):
    """Read stdin as bytes, or return None if the read is still parked after `timeout`.

    Measured: with stdin held open and never written, `json.load(sys.stdin)` here hung
    past 8s and had to be killed -- a known shape on Windows, where a wrapper swallows
    the piped JSON so EOF never arrives. This runs on EVERY Bash the
    critic issues, so that is the whole 15s hook timeout, per call.

    A thread, because `signal.alarm` is POSIX-only and `select()` on Windows accepts
    sockets, not pipes. `sys.stdin.buffer` rather than `sys.stdin`, because the text
    wrapper decodes with the locale codepage and would mojibake a UTF-8 path before
    this code could see it.

    The reader may still be parked when this returns None; it is a daemon, and the
    caller leaves via os._exit so interpreter shutdown cannot block closing a stdin
    nobody will write to.
    """
    box = []

    def _reader():
        try:
            box.append(sys.stdin.buffer.read())
        except Exception:
            box.append(b"")

    t = threading.Thread(target=_reader, daemon=True)
    t.start()
    t.join(timeout)
    return box[0] if box else None


def deny(reason):
    """Refuse, and exit 0 so the decision is read as a decision rather than a crash."""
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    sys.stdout.flush()
    os._exit(0)


def main():
    raw = read_stdin_bounded()
    if raw is None:
        # DENY, not allow -- this is the opposite choice from remind-critic.py, and
        # deliberately so: that hook is advisory, so its worst failure is a missing
        # message; this one is a boundary, so a timeout that permitted the call would
        # let an unread command through unexamined. os._exit because the reader thread
        # is still inside read().
        deny("guard-critic-readonly timed out reading the hook payload, so the command "
             "was never examined. Refusing rather than permitting an unread command.")

    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    try:
        payload = json.loads(raw.decode("utf-8", "replace"))
        if not isinstance(payload, dict):
            raise ValueError("payload is not an object")
    except Exception:
        # A guard that fails open is not a guard. Exit 2 blocks unconditionally.
        print("guard-critic-readonly could not parse the hook payload", file=sys.stderr)
        sys.exit(2)

    try:
        # `payload.get("tool_input") or {}` was not enough: a NON-EMPTY non-dict passes
        # that guard and `.get()` then raised AttributeError, exiting 1 -- neither the
        # documented exit 2 nor a deny decision, on a command never examined. Measured:
        #   tool_input as str  -> rc=1, "'str' object has no attribute 'get'"
        #   tool_input as list -> rc=1, "'list' object has no attribute 'get'"
        # Deliberately NOT fixed by coercing a bad tool_input to `{}`: that classifies
        # as "no command", i.e. ALLOW, which is the wrong direction for a boundary hook.
        # Malformed input to a guard is refused, so the except below is the whole fix.
        reason = classify(payload.get("tool_name", ""), payload.get("tool_input") or {})
    except Exception:
        # Same argument as the timeout path: the command has not been examined, so it is
        # refused rather than permitted.
        deny("guard-critic-readonly could not examine this command (malformed tool_input), "
             "so it was never checked. Refusing rather than permitting an unexamined command.")

    out = {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny" if reason else "allow",
    }}
    if reason:
        out["hookSpecificOutput"]["permissionDecisionReason"] = reason
    print(json.dumps(out))
    sys.exit(0)


if __name__ == "__main__":
    main()
