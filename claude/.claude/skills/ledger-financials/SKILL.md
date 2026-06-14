---
name: ledger-financials
description: >
  Generate a self-contained, interactive static HTML page that lets a
  non-technical person browse and search a Ledger CLI journal. A two-pane layout
  shows individual transactions (searchable by payee, account, amount, date,
  cardholder, or receipt filename) on the left and aggregate account balances —
  like `ledger bal`, with a net-worth summary — on the right. The output is a
  single dependency-free .html file that works on mobile and desktop.
  Use when asked to make a ledger browsable/searchable for someone who does not
  use the command line.
when_to_use: >
  Make a ledger file browsable or searchable, build a human-friendly financials
  page from a .ledger journal, "let my partner look through the books",
  searchable transaction list with running balances, single-file HTML ledger
  browser, non-technical view of a fiscal-year journal.
allowed-tools: Read Bash
user-invocable: true
---

# Ledger Financials Browser

This skill turns any single-year [Ledger CLI](https://ledger-cli.org) journal into
a **single, self-contained, interactive HTML file** that a non-technical person can
read. It is dependency-free (vanilla JS, no canvas, no network), runs by
double-clicking, and computes nothing it does not need to — the data is embedded.

It is the static, browsable counterpart to the `ledger-viz` skill (which animates a
year over time). Use `ledger-financials` when the goal is **searching and reading
entries**, not watching a timeline.

The viewer gets a **two-pane layout**:

| Pane | Contents |
|------|----------|
| **Left — Entries** | Every transaction, grouped by month. A search box filters by payee, account, amount, date, cardholder, or receipt filename; a month dropdown narrows further. Tap an entry to expand its postings. `File:` and `cardholder:` annotations show as chips ("no receipt" is flagged for `MISSING`/`NOT PROVIDED`). |
| **Right — Balances** | Summary cards (Net worth, Assets, Liabilities, Income, Expenses) plus a collapsible account tree sorted by magnitude, like `ledger bal`. Clicking an account name filters the entries to transactions touching it. |

On a narrow screen the panes collapse into **Entries / Balances tabs** and reflow to
a single column.

## How it works

The HTML is split into a generic engine and a small embedded data model:

- **`template.html`** (next to this file) — the entire browser plus two
  placeholders, `__DATA__` (transactions + balances as JSON) and `__YEAR__` (the
  fiscal year). **Never hand-edit the placeholders or output HTML directly.**
- **`generate.py`** (next to this file) — parses the journal for faithful
  transactions and runs `ledger` for accurate balances, then injects both into the
  template.

Two distinct data sources are used on purpose:

- **Entries (left)** come from parsing the raw journal text, so they show exactly
  what is written — including the `; File:` receipt association, `; cardholder:`
  tag, and virtual `(stats:…)` consumption postings (shown italic). A single elided
  posting per transaction is resolved by balancing the real `$` postings.
- **Balances (right)** come from `ledger reg --limit 'commodity == "$"'`, summed
  per account to each account's **own** total, which the browser rolls up through
  the `account:sub:sub` hierarchy. (`bal --flat` is deliberately *not* used: it
  prints rolled-up totals for every posted account, so a posted parent that also
  has a posted child would be double-counted.) Only `$` is included; `kWh`/`GJ`/
  `m3` consumption stats and other commodities stay out of the money tree but
  remain visible inside the entries.

## Procedure

### Step 1 — Identify the ledger file

Use the file the user points at (e.g. `2026.ledger`). If they don't specify one and
several `*.ledger` files exist, ask which year. The journal should cover a single
fiscal year; the year is taken from the first 4-digit run in the filename.

### Step 2 — Generate

Run the bundled generator from the directory where you want the output written
(typically the ledger's directory):

```bash
python3 "$HOME/.claude/skills/ledger-financials/generate.py" <ledger-file> [output.html]
```

- The output path is optional; it defaults to `<year>-financials.html` in the
  current directory.
- Requires the `ledger` CLI on PATH and `python3` (standard library only).
- The script prints the transaction count, account count, and output size, and
  exits non-zero on any failure (missing file, no transactions, `ledger` not
  installed) — check the exit status.

To batch several years, loop:

```bash
for y in 2024 2025 2026; do
  python3 "$HOME/.claude/skills/ledger-financials/generate.py" "$y.ledger"
done
```

### Step 3 — Verify before claiming done

Confirm the embedded JavaScript parses:

```bash
python3 - "$OUT" <<'PY'
import re, sys
h = open(sys.argv[1]).read()
open("/tmp/ledger-fin-check.js", "w").write(re.search(r"<script>(.*)</script>", h, re.S).group(1))
PY
node --check /tmp/ledger-fin-check.js && echo "JS OK"
```

Spot-check that the net worth shown in the summary matches Ledger itself:

```bash
ledger -f <ledger-file> bal assets liabilities --collapse --limit 'commodity == "$"' | tail -1
```

should equal the **Net worth** card.

### Step 4 — Hand off

Tell the user the output path and offer to open it (`open <path>` on macOS). If the
browser shows a stale copy after a regenerate, remind them to hard-reload (⌘⇧R).

## Assumptions & notes

- **Single fiscal year.** Short `MM/DD` dates are expanded with the year from the
  filename; full `YYYY/MM/DD` dates are used as written.
- **Account-name casing varies across years** (older journals capitalize
  `Assets:`/`Liabilities:`); the summary classification is case-insensitive.
- **Net worth = assets + liabilities** (liabilities are negative). Mark-to-market
  brokerage lumps are real data, not a bug.
- **USD and other commodities** in older journals are excluded from the `$` balance
  tree but their postings still appear in the entry detail.
- The headline amount on each entry is the sum of its positive real `$` postings
  (i.e. what the transaction "cost" or moved); expand the entry for the full
  double-entry detail.

## Output

A single `.html` file named `<year>-financials.html` by default. No build step, no
network, no dependencies. Opens in any browser.
