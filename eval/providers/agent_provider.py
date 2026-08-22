#!/usr/bin/env python3
"""Layer-2 provider that runs the real agent and OBSERVES which modules it opened.

Contract with run_routing_eval.py (--provider command): the case request arrives on
stdin, exactly one JSON object with primary/modules/boundary_ids/mode goes to stdout,
everything else goes to stderr. Anything else on stdout is a harness error there, so
this script prints nothing at all when it cannot produce a complete answer.

Why this exists rather than a single chat/completions call: `modules` is meant to be
the set of procedure files whose text actually entered the model's context. A chat
call can only report what the model SAYS it would read, which turns module_recall
into a seventh name-matching metric. Here `modules` is read off the transcript's
Read tool calls -- observation, not declaration. `primary`, `boundary_ids`
and `mode` are still self-reported, because no tool call reveals them.

The package under test is loaded as a session-scoped plugin built from this
repository, so nothing in the operator's own ~/.claude installation is read or
written, and user settings are switched off (--setting-sources "") so installed
hooks, memory files and same-named skills cannot contribute.

Operator-supplied environment (nothing about a provider or an account is committed
to this repository):

    EVAL_MODEL            required, e.g. us.anthropic.claude-sonnet-5
    EVAL_EFFORT           optional, default "medium"
    EVAL_CLAUDE_SETTINGS  optional path to a settings JSON holding whatever
                          credentials/provider env the CLI needs on this machine.
                          Keep it outside this repository.
    EVAL_TIMEOUT          optional per-case seconds, default 600
    EVAL_KEEP_TRANSCRIPT  optional directory; each run's raw stream-json is written
                          there as <sha1-of-request>.jsonl, which joins to cases.jsonl
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKILLS = os.path.join(REPO, "skills")
AGENTS = os.path.join(REPO, "agents")
REFERENCES = os.path.join("skills", "ai-engineer", "references")

PLUGIN_NAME = "ai-engineer-eval"
SKILL_COMMAND = "/%s:ai-engineer" % PLUGIN_NAME

# Appended to the request. The four keys the harness scores are not all observable:
# ask for the three that are not, and say nothing about which modules to read, since
# that is the behaviour under test.
REPORT_INSTRUCTION = (
    "When you have finished, end your reply with one line containing only a JSON "
    'object: {"primary": "<the single procedure ID you routed to>", '
    '"boundary_ids": ["<any compound-boundary procedure IDs that fired, [] if none>"], '
    '"mode": "<the operating mode you selected>"}'
)

# Only Read puts a module body into context. See modules_from_tool_use.
READ_TOOLS = ("Read",)


def log(msg):
    sys.stderr.write("agent_provider: %s\n" % msg)


def build_plugin(root):
    """Copy the package under test into a session-scoped plugin skeleton."""
    shutil.copytree(SKILLS, os.path.join(root, "skills"))
    shutil.copytree(AGENTS, os.path.join(root, "agents"))
    manifest = {
        "name": PLUGIN_NAME,
        "version": "0.0.0",
        "description": "Eval copy of the ai-engineer skill package.",
        "skills": "./skills/",
        # A string here fails validation with "agents: Invalid input"; the field
        # takes a list of files.
        "agents": [
            "./agents/%s" % name
            for name in sorted(os.listdir(AGENTS))
            if name.endswith(".md")
        ],
    }
    meta = os.path.join(root, ".claude-plugin")
    os.makedirs(meta)
    with open(os.path.join(meta, "plugin.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh)
    return root


def build_argv(plugin_dir):
    model = os.environ.get("EVAL_MODEL")
    if not model:
        log("EVAL_MODEL is not set; refusing to guess a model")
        return None
    argv = [
        "claude",
        "-p",
        "--verbose",  # stream-json requires it
        "--model",
        model,
        "--effort",
        os.environ.get("EVAL_EFFORT", "medium"),
        # No user/project/local settings: installed hooks, CLAUDE.md memory and a
        # same-named installed skill would otherwise be inside the measurement.
        "--setting-sources",
        "",
        "--plugin-dir",
        plugin_dir,
        "--add-dir",
        plugin_dir,
        # Read-only by grant. The routing behaviour under test needs nothing else,
        # and a case must not be able to change the machine.
        "--allowedTools",
        "Read",
        "Grep",
        "Glob",
        "--no-session-persistence",
        "--output-format",
        "stream-json",
    ]
    settings = os.environ.get("EVAL_CLAUDE_SETTINGS")
    if settings:
        argv += ["--settings", settings]
    return argv


def modules_from_tool_use(block):
    """Module basenames whose TEXT this tool call put into context, as observed.

    Only `Read` qualifies. `Glob` returns a list of filenames and no file content, so
    counting it as a load credits the agent for discovering that a module exists; worse,
    its argument is a pattern, and `references/*.md` was being recorded as a module named
    `*.md`, which the harness correctly rejected as a file that does not exist. `Grep`
    returns matching lines rather than the procedure, and its target is usually a
    directory, so it cannot establish that any particular module was read either.

    The consequence is deliberate: an agent that greps for a control instead of opening
    the module scores module_recall 0. That is the intended reading -- the procedure is
    the module body, and a matched line is not the body.
    """
    if block.get("name") != "Read":
        return []
    path = (block.get("input") or {}).get("file_path")
    if not isinstance(path, str):
        return []
    norm = path.replace("\\", "/")
    if REFERENCES.replace("\\", "/") not in norm:
        return []
    base = os.path.basename(norm)
    return [base] if base.endswith(".md") and "*" not in base else []


def parse_stream(lines):
    """Return (modules, final_text). Raises ValueError when the run failed."""
    modules = []
    final_text = None
    saw_result = False
    for line in lines:
        line = line.strip()
        if not line.startswith("{"):
            if line:
                log("non-JSON stream line: %s" % line[:200])
            continue
        try:
            event = json.loads(line)
        except ValueError:
            log("unparseable stream line: %s" % line[:200])
            continue
        etype = event.get("type")
        if etype == "system" and event.get("subtype") == "init":
            if event.get("plugin_errors"):
                raise ValueError(
                    "plugin failed to load: %s" % json.dumps(event["plugin_errors"])
                )
            skills = event.get("skills") or []
            if SKILL_COMMAND.lstrip("/") not in skills:
                raise ValueError(
                    "the skill under test is not registered in this session; "
                    "found: %s" % ", ".join(sorted(skills)[:12])
                )
        elif etype == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    modules.extend(modules_from_tool_use(block))
                elif block.get("type") == "text":
                    final_text = block.get("text") or final_text
        elif etype == "result":
            saw_result = True
            if event.get("is_error"):
                raise ValueError("run reported is_error: %s" % str(event.get("result"))[:300])
            if event.get("result"):
                final_text = str(event["result"])
    if not saw_result:
        raise ValueError("stream ended with no result event")
    # dedupe, keep first-seen order
    seen = set()
    ordered = [m for m in modules if not (m in seen or seen.add(m))]
    return ordered, final_text


def last_json_object(text):
    """The last balanced {...} in the text, parsed. None if there is none."""
    if not text:
        return None
    for start in range(len(text) - 1, -1, -1):
        if text[start] != "{":
            continue
        depth = 0
        for end in range(start, len(text)):
            if text[end] == "{":
                depth += 1
            elif text[end] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[start : end + 1])
                    except ValueError:
                        break
                    if isinstance(obj, dict) and "primary" in obj:
                        return obj
                    break
    return None


def main():
    request = sys.stdin.read().strip()
    if not request:
        log("empty request on stdin")
        return 1
    root = tempfile.mkdtemp(prefix="ai-engineer-eval-")
    try:
        plugin_dir = build_plugin(os.path.join(root, "plugin"))
        argv = build_argv(plugin_dir)
        if argv is None:
            return 1
        prompt = "%s %s\n\n%s\n" % (SKILL_COMMAND, request, REPORT_INSTRUCTION)
        try:
            proc = subprocess.run(
                argv,
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=float(os.environ.get("EVAL_TIMEOUT", "600")),
            )
        except OSError as exc:
            log("could not start the CLI: %s" % exc)
            return 1
        except subprocess.TimeoutExpired as exc:
            # Keep whatever the session produced before the clock ran out. A timeout with
            # no transcript is unexplainable, and the interesting question -- what was it
            # doing for ten minutes -- is answerable only from the partial stream.
            partial = exc.stdout or b""
            if isinstance(partial, bytes):
                partial = partial.decode("utf-8", "replace")
            keep_dir = os.environ.get("EVAL_KEEP_TRANSCRIPT")
            if keep_dir and partial:
                os.makedirs(keep_dir, exist_ok=True)
                digest = hashlib.sha1(request.encode("utf-8")).hexdigest()[:12]
                path = os.path.join(keep_dir, "%s.timeout.jsonl" % digest)
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(partial)
                log("timed out after %ss; partial transcript: %s" % (
                    os.environ.get("EVAL_TIMEOUT", "600"), path))
            else:
                log("timed out after %ss with no output captured"
                    % os.environ.get("EVAL_TIMEOUT", "600"))
            return 1
        keep = os.environ.get("EVAL_KEEP_TRANSCRIPT")
        if keep:
            os.makedirs(keep, exist_ok=True)
            # Named by a digest of the request, because the harness contract hands this
            # runner the request and nothing else. A transcript named after the process id
            # cannot be tied back to a case, which is exactly what you need it for when a
            # metric drops; the digest joins to `cases.jsonl` on the request text.
            digest = hashlib.sha1(request.encode("utf-8")).hexdigest()[:12]
            path = os.path.join(keep, "%s.jsonl" % digest)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(proc.stdout)
            log("transcript: %s" % path)
        try:
            modules, text = parse_stream(proc.stdout.splitlines())
        except ValueError as exc:
            log("%s" % exc)
            if proc.stderr.strip():
                log("cli stderr: %s" % proc.stderr.strip()[:300])
            return 1
        reported = last_json_object(text)
        if reported is None:
            log("no final JSON object with a 'primary' key in the reply")
            return 1
        boundary = reported.get("boundary_ids", [])
        if not isinstance(boundary, list):
            log("boundary_ids is not a list")
            return 1
        out = {
            "primary": str(reported.get("primary", "")),
            "modules": modules,
            "boundary_ids": [str(b) for b in boundary],
            "mode": str(reported.get("mode", "")),
        }
        sys.stdout.write(json.dumps(out))
        return 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
