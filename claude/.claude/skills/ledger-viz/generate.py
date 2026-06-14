#!/usr/bin/env python3
"""Generate a self-contained interactive HTML visualization from a Ledger journal.

Usage:
    python3 generate.py <ledger-file> [output.html]

Runs `ledger -f <file> csv`, keeps only real $ postings, derives the fiscal year
from the data, and injects the posting stream into template.html (alongside this
script). All charts are computed in-browser; the output is a single dependency-free
HTML file. Exit status is non-zero on any error so callers can detect failure.
"""
import csv
import io
import json
import os
import subprocess
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "template.html")


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        die("usage: generate.py <ledger-file> [output.html]")

    ledger_file = sys.argv[1]
    if not os.path.isfile(ledger_file):
        die(f"ledger file not found: {ledger_file}")
    if not os.path.isfile(TEMPLATE):
        die(f"template not found: {TEMPLATE}")

    try:
        proc = subprocess.run(
            ["ledger", "-f", ledger_file, "csv"],
            capture_output=True, text=True, check=True,
        )
    except FileNotFoundError:
        die("the `ledger` CLI is not installed or not on PATH")
    except subprocess.CalledProcessError as e:
        die(f"ledger failed:\n{e.stderr.strip()}")

    rows = list(csv.reader(io.StringIO(proc.stdout)))

    # Determine the fiscal year: the most common year among posting dates.
    years = Counter()
    for r in rows:
        if len(r) >= 1 and "/" in r[0]:
            years[r[0].split("/")[0]] += 1
    if not years:
        die("no dated postings found in ledger output")
    year = years.most_common(1)[0][0]
    other_years = {y for y in years if y != year}

    postings = []
    skipped_units = 0
    for r in rows:
        if len(r) < 6:
            continue
        date, _flag, payee, acct, comm, amt = r[0], r[1], r[2], r[3], r[4], r[5]
        if not date.startswith(year + "/"):
            continue                      # ignore postings from other years
        if comm != "$":                   # skip kWh / GJ / m3 statistic units
            skipped_units += 1
            continue
        if acct.startswith("("):          # skip virtual (gst / stats) postings
            continue
        try:
            v = round(float(amt), 2)
        except ValueError:
            continue
        md = date[len(year) + 1:].replace("/", "")   # YYYY/MM/DD -> MMDD
        postings.append({"d": md, "p": payee, "a": acct, "v": v})

    if not postings:
        die(f"no $ postings found for year {year}")

    data = json.dumps(postings, separators=(",", ":"))
    html = open(TEMPLATE, encoding="utf-8").read()
    html = html.replace("__DATA__", data).replace("__YEAR__", year)

    out = sys.argv[2] if len(sys.argv) > 2 else f"{year}-ledger.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"wrote {out}")
    print(f"  year        {year}")
    print(f"  postings    {len(postings)}")
    if skipped_units:
        print(f"  (skipped {skipped_units} non-$ statistic postings)")
    if other_years:
        print(f"  note: ignored postings from other years: {', '.join(sorted(other_years))}")
    print(f"  size        {len(html):,} bytes")


if __name__ == "__main__":
    main()
