#!/usr/bin/env python3
"""Re-invoke the routing eval with --resume until every call is recorded.

A full-corpus run takes hours, and anything that takes hours gets interrupted: a
background-task limit, a closed lid, a proxy hiccup. Each invocation picks up from the
result log, so an interruption costs only the calls in flight and this loop restarts
where the last one stopped. Killing the loop is safe at any moment.

This is Python rather than shell for one measured reason: on the machine this was built
for, `sh` does not inherit exported environment variables -- `export X=1; sh -c 'echo
$X'` prints nothing. A shell wrapper therefore ran the whole eval with EVAL_MODEL unset,
failed 4127 calls in eight attempts, and buried 137 real results under error lines.
Python inherits the environment it was started with, and passes it to its children,
which is the entire requirement here.

Two guards, both learned from that incident:

* refuse to start when the runner cannot possibly work (no EVAL_MODEL)
* stop when an attempt records no new results, because a retry loop is only justified
  while retrying achieves something -- an attempt that records nothing means the failure
  is configuration, not interruption, and repeating it turns a broken setup into a bill

    EVAL_MODEL=... python eval/run_until_done.py --result-log run.jsonl \
        --json-out report.json --date 2026-08-22 [-n 5] [--jobs 6]
"""

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.join(HERE, "run_routing_eval.py")
PROVIDER = os.path.join(HERE, "providers", "agent_provider.py")


def recorded(log, cases, repeats):
    """(successful calls, total expected). Errors are not "done": --resume retries them."""
    with open(cases, encoding="utf-8") as fh:
        total = sum(1 for line in fh if line.strip()) * repeats
    done = 0
    if os.path.exists(log):
        with open(log, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue  # tail truncated by a kill; that call re-runs
                if rec.get("error") is None:
                    done += 1
    return done, total


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--result-log", required=True)
    ap.add_argument("--json-out", required=True)
    ap.add_argument("--cases", default=os.path.join("eval", "cases.jsonl"))
    ap.add_argument("-n", type=int, default=5)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--date", required=True)
    ap.add_argument("--attempts", type=int, default=40)
    args = ap.parse_args(argv)

    model = os.environ.get("EVAL_MODEL")
    if not model:
        sys.stderr.write("EVAL_MODEL is not set; the runner would fail every call\n")
        return 2
    effort = os.environ.get("EVAL_EFFORT", "medium")

    last_done = -1
    for attempt in range(1, args.attempts + 1):
        done, total = recorded(args.result_log, args.cases, args.n)
        print("attempt %d: %d/%d calls recorded" % (attempt, done, total), flush=True)
        if done >= total:
            print("complete", flush=True)
            return 0
        if done <= last_done:
            sys.stderr.write(
                "attempt %d recorded no new results; stopping rather than retrying a "
                "failure that is not an interruption\n" % attempt
            )
            return 3
        last_done = done
        subprocess.run(
            [
                sys.executable,
                HARNESS,
                "--cases", args.cases,
                "--provider", "command",
                # JSON array, not a string: sys.executable contains a space on Windows
                # and whitespace splitting silently handed half of its own path to the
                # interpreter as a script argument.
                "--command", json.dumps([sys.executable, PROVIDER]),
                "-n", str(args.n),
                "--jobs", str(args.jobs),
                "--date", args.date,
                "--model", model,
                "--effort", effort,
                "--result-log", args.result_log,
                "--resume",
                "--json-out", args.json_out,
            ],
            env=os.environ.copy(),
        )
        # The child's exit status is deliberately ignored: a killed child reports failure
        # having recorded real work, and the log is the only authority on what is done.

    sys.stderr.write("gave up after %d attempts\n" % args.attempts)
    return 1


if __name__ == "__main__":
    sys.exit(main())
