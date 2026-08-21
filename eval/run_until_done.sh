#!/bin/sh
# Re-invoke the routing eval with --resume until every call is recorded.
#
# A full-corpus run takes hours, and anything that takes hours gets interrupted: a
# background-task limit, a laptop lid, a proxy hiccup. Each invocation picks up from the
# result log, so an interruption costs only the calls in flight, and this loop restarts
# where the last one stopped. Killing the loop is safe at any moment.
#
# Required in the environment (nothing account-specific belongs in this repository):
#   EVAL_MODEL and whatever else the runner needs; PY to point at the interpreter.
# Arguments:
#   $1 result log   $2 json report   $3 cases file   $4 repeats   $5 jobs   $6 ISO date
set -u

LOG=${1:?result log path}
REPORT=${2:?json report path}
CASES=${3:-eval/cases.jsonl}
N=${4:-5}
JOBS=${5:-6}
DATE=${6:?ISO date, e.g. 2026-08-22}
PY=${PY:-python}
ATTEMPT_LIMIT=${ATTEMPT_LIMIT:-40}

attempt=0
while [ "$attempt" -lt "$ATTEMPT_LIMIT" ]; do
    attempt=$((attempt + 1))
    set -- $("$PY" eval/progress.py "$LOG" "$CASES" "$N")
    done_count=$1
    total=$2
    echo "attempt $attempt: $done_count/$total calls recorded"
    if [ "$done_count" -ge "$total" ]; then
        echo "complete"
        exit 0
    fi
    "$PY" eval/run_routing_eval.py \
        --cases "$CASES" \
        --provider command \
        --command "$PY eval/providers/agent_provider.py" \
        -n "$N" --jobs "$JOBS" --date "$DATE" \
        --model "${EVAL_MODEL:-unset}" --effort "${EVAL_EFFORT:-medium}" \
        --result-log "$LOG" --resume \
        --json-out "$REPORT"
    # The child's exit status is deliberately not trusted: a killed child reports failure
    # having recorded real work, and the log is the only authority on what is done.
done

echo "gave up after $ATTEMPT_LIMIT attempts" >&2
exit 1
