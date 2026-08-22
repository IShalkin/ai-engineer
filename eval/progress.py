#!/usr/bin/env python3
"""How much of a routing-eval run is recorded. Prints "done total" on one line.

Split out of the retry loop because a shell doing JSON accounting inside a command
substitution is how the loop silently miscounts, and a miscount either stops a run
early or loops forever. Errored calls are NOT counted as done: --resume retries them,
so counting them would end the loop with cases missing from every denominator.

    python eval/progress.py <result-log> <cases-file> <repeats>
"""

import json
import os
import sys


def main(argv):
    if len(argv) != 4:
        sys.stderr.write(__doc__)
        return 2
    log, cases, repeats = argv[1], argv[2], int(argv[3])
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
    print("%d %d" % (done, total))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
