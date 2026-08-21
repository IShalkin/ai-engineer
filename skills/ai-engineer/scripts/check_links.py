#!/usr/bin/env python3
"""Report unreachable links in references/*.md. NEVER fails the build.

Exit status is always 0, deliberately. A link check measures the network between this
runner and someone else's server: a corporate TLS-inspecting proxy, a CDN blocking
datacentre ranges, or a site that is simply down for ten minutes all produce the same
red as a genuinely dead citation. Wiring that into a release gate teaches everyone to
ignore the gate, so this prints and stops there. Read the output; nothing reads it for
you.

What a WARN means: this runner could not confirm the URL resolves. What it does not
mean: the citation is wrong. A page can move while the instrument it cites is still in
force, and a page can stay up after its content is withdrawn -- only reading it tells
you which happened.

    python skills/ai-engineer/scripts/check_links.py [--timeout 8] [--json]
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REFERENCES = Path(__file__).resolve().parents[1] / "references"
# Markdown inline links only. Bare URLs in prose are not collected: they are usually
# examples ("https://api.example.com/v1") rather than citations.
LINK = re.compile(r"\]\((https?://[^\s)]+)\)")
UA = "ai-engineer-link-check"

# Some hosts answer HEAD with 403/405 while serving GET fine (arXiv and several docs
# CDNs do). Treating that as dead produces confident false reports.
RETRY_WITH_GET = (403, 405, 400)


def probe(url, timeout):
    """None when reachable, else a short reason string."""
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status and resp.status >= 400:
                    return "HTTP %d" % resp.status
                return None
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in RETRY_WITH_GET:
                continue
            return "HTTP %d" % exc.code
        except urllib.error.URLError as exc:
            # DNS failure, refused connection, TLS interception without the corporate
            # bundle. Environment, not content -- reported, never fatal.
            return "unreachable: %s" % str(getattr(exc, "reason", exc))[:80]
        except Exception as exc:  # socket timeouts, redirects loops, malformed URLs
            return "%s: %s" % (type(exc).__name__, str(exc)[:80])
    return None


def collect():
    """{url: [file:line, ...]} so one dead link is reported once, with every site."""
    found = {}
    for path in sorted(REFERENCES.glob("*.md")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for url in LINK.findall(line):
                found.setdefault(url, []).append("%s:%d" % (path.name, lineno))
    return found


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=float, default=8.0)
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    args = ap.parse_args(argv)

    links = collect()
    findings = []
    for url in sorted(links):
        reason = probe(url, args.timeout)
        if reason:
            findings.append({"url": url, "reason": reason, "cited_at": links[url]})

    if args.json:
        json.dump({"checked": len(links), "unconfirmed": findings}, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        for f in findings:
            print("LINKCHECK: WARN - %s -> %s (%s)" % (f["url"], f["reason"], ", ".join(f["cited_at"])))
        print("LINKCHECK: %d links checked, %d unconfirmed" % (len(links), len(findings)))
        if findings:
            print(
                "LINKCHECK: unconfirmed means this runner could not reach the URL. It does "
                "not mean the citation is wrong -- open each one before editing anything."
            )
    # Always 0. See the module docstring.
    return 0


if __name__ == "__main__":
    sys.exit(main())
