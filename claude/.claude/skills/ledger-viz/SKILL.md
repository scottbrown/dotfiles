---
name: ledger-viz
description: >
  Generate a self-contained, animated static HTML page that visualizes a Ledger
  CLI journal over time. A daily timeline scrubs through the fiscal year and
  animates four views: cumulative spending by category, net worth & cashflow,
  account balances, and a transaction-flow timeline. The output is a single
  dependency-free .html file with play/pause, step, reset, and speed controls.
  Use when asked to visualize, animate, or chart a ledger/journal file over time.
when_to_use: >
  Visualize a ledger file over time, animate spending or net worth across a year,
  ledger timeline animation, "show me this year's finances visually", bar-race of
  expense categories, net-worth-over-time chart, single-file HTML finance
  visualization from a .ledger journal.
allowed-tools: Read Bash
user-invocable: true
---

# Ledger Year-in-Motion Visualization

This skill turns any single-year [Ledger CLI](https://ledger-cli.org) journal into
a **single, self-contained, animated HTML file**. It is dependency-free (vanilla JS
+ canvas), runs by double-clicking, and computes every chart in-browser — no data
leaves the file.

The viewer gets a daily scrubber + Play/Pause that sweeps Jan→Dec, plus Reset and
single-day Step forward/back, a speed selector (¼× · ½× · 1× · 2×), and four tabs:

| Tab | What it animates |
|-----|------------------|
| **Spending by category** | A bar-race of cumulative expenses per `expenses:<cat>` |
| **Net worth & cashflow** | Net worth (assets + liabilities) and the chequing balance drawing in as lines |
| **Account balances** | Diverging bars — assets vs liabilities — per balance-sheet account |
| **Transaction flow** | Every posting as a dot on a log-amount timeline, with a live "this day" feed |

## How it works

The HTML is split into a generic engine and a small embedded data model:

- **`template.html`** (next to this file) — the entire animation engine plus two
  placeholders, `__DATA__` (the posting stream as JSON) and `__YEAR__` (the fiscal
  year). **Never hand-edit the placeholders or output HTML directly.**
- **`generate.py`** (next to this file) — runs `ledger -f <file> csv`, keeps only
  real `$` postings (dropping virtual `(gst…)`/`(stats…)` postings and `kWh`/`GJ`/
  `m3` statistic units), derives the year from the data, and injects everything
  into the template. It is fully deterministic — there is nothing to author by
  hand.

All per-day balances, category totals, and net worth are recomputed in the browser
by replaying the posting stream, so the embedded data stays small.

## Procedure

### Step 1 — Identify the ledger file

Use the file the user points at (e.g. `2026.ledger`). If they don't specify one and
several `*.ledger` files exist, ask which year. The journal should cover a single
fiscal year; if it spans multiple years the generator picks the most common year and
ignores the rest (it will say so).

### Step 2 — Generate

Run the bundled generator from the directory where you want the output written
(typically the ledger's directory):

```bash
python3 "$HOME/.claude/skills/ledger-viz/generate.py" <ledger-file> [output.html]
```

- The output path is optional; it defaults to `<year>-ledger.html` in the current
  directory.
- Requires the `ledger` CLI on PATH and `python3` (standard library only).
- The script prints the year, posting count, and output size, and exits non-zero on
  any failure (missing file, `ledger` not installed, no `$` postings) — check the
  exit status.

### Step 3 — Verify before claiming done

Confirm the embedded JavaScript parses:

```bash
python3 - "$OUT" <<'PY'
import re, sys
h = open(sys.argv[1]).read()
open("/tmp/ledger-viz-check.js", "w").write(re.search(r"<script>(.*)</script>", h, re.S).group(1))
PY
node --check /tmp/ledger-viz-check.js && echo "JS OK"
```

Optionally spot-check that the in-browser totals match Ledger itself, e.g. the
year's total expenses:

```bash
ledger -f <ledger-file> bal ^expenses | tail -1
```

should match the "Total spent to date" shown at the end of the Spending view.

### Step 4 — Hand off

Tell the user the output path and offer to open it (`open <path>` on macOS). If the
browser shows a stale copy after a regenerate, remind them to hard-reload (⌘⇧R).

## Assumptions & notes

- **Single fiscal year**, dates within that year. Leap years are handled (366 days).
- The **cashflow line** auto-detects an account matching `chequing`/`checking`/
  `current`; if none exists it stays flat at zero.
- **Net worth = assets + liabilities** (liabilities are negative). Mark-to-market
  brokerage postings land as lumps, so that line can be jumpy — that is the real
  data, not a bug.
- If real entries stop partway through the year (e.g. only Jan–Jun populated, rest
  placeholders), the lines visibly flatten after that point — also expected.
- Account roots used for classification: `assets`, `liabilities`, `expenses`,
  `income`. `EQUITY` and other roots are excluded from net worth.

## Output

A single `.html` file. No build step, no network, no dependencies. Opens in any
browser with the timeline controls described above.
