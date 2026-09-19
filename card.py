"""The card's address, built from a report.

Its own file rather than a heredoc inside the action: a Python block indented
to sit inside a YAML block scalar is a Python block with the wrong
indentation, and the two escaping rules cannot both be satisfied. It is also
the only part of the action with logic worth testing on its own.

    python3 card.py report.json [owner/repo] -> https://cqx.bio/card.svg?...

Prints nothing and exits 0 when there is nothing to draw, so the caller can
treat an empty line as "no card" rather than as a failure.
"""

import json
import sys
import urllib.parse

BASE = "https://cqx.bio/card.svg"


def address(report: dict, repo: str | None = None) -> str:
    scores = report.get("scores") or {}
    if not scores:
        return ""
    was = (report.get("against") or {}).get("scores") or {}

    parts = []
    for name, value in scores.items():
        moved = value - was[name] if name in was else 0
        # A delta of zero is left out rather than drawn as "0": nothing moved
        # is already said by the absence of an arrow.
        parts.append(f"{name}:{value}:{moved}" if moved else f"{name}:{value}")

    query = {"scores": ",".join(parts)}

    # What the run cost, said the same way the terminal says it. `scan` is
    # where cqx records it; older reports have only the line count at the top
    # level, so that is the fallback rather than nothing.
    scan = report.get("scan") or {}
    for key in ("files", "lines", "ms"):
        if scan.get(key):
            query[key] = scan[key]
    if "lines" not in query and report.get("lines"):
        query["lines"] = report["lines"]
    if scan.get("cqx"):
        query["v"] = scan["cqx"]
    against = (report.get("against") or {}).get("ref")
    if against:
        query["against"] = against[:12]
    if repo:
        query["repo"] = repo
    return BASE + "?" + urllib.parse.urlencode(query)


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as handle:
        print(address(json.load(handle), sys.argv[2] if len(sys.argv) > 2 else None))
