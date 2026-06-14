#!/usr/bin/env python3
"""Generate a self-contained, interactive financials browser from a Ledger journal.

Usage:
    generate.py <ledger-file> [output.html]

The output is a single dependency-free HTML file with a two-pane layout:
  * left  - searchable list of individual transactions (faithful to the journal)
  * right - aggregate account balances (computed with `ledger`)
It is designed to be readable by a non-technical person on mobile or desktop.

Requires the `ledger` CLI on PATH and python3 (standard library only).
The template lives in template.html next to this script; __DATA__ and __YEAR__
are the only placeholders. Never hand-edit the placeholders or output HTML.
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MONTHS = ["", "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

TEMPLATE = Path(__file__).with_name("template.html")


def parse_amount(token):
    """Parse a Ledger amount token into (value, commodity, display).

    Handles: $35585.38, -$1324.38, $-415.21, 801 kWh, 12.18 GJ, 15 "m3".
    Returns (None, None, None) if the token is not an amount.
    """
    token = token.strip()
    if not token:
        return None, None, None

    m = re.match(r'^(-?)\$(-?)([\d,]+(?:\.\d+)?)$', token)
    if m:
        sign = -1 if (m.group(1) == '-') ^ (m.group(2) == '-') else 1
        value = sign * float(m.group(3).replace(',', ''))
        return value, '$', format_money(value)

    m = re.match(r'^(-?[\d,]+(?:\.\d+)?)\s+"?([^"]+)"?$', token)
    if m:
        value = float(m.group(1).replace(',', ''))
        commodity = m.group(2).strip()
        return value, commodity, f"{trim_num(value)} {commodity}"

    return None, None, None


def trim_num(value):
    if value == int(value):
        return str(int(value))
    return f"{value:g}"


def format_money(value):
    return f"-${abs(value):,.2f}" if value < 0 else f"${value:,.2f}"


def parse_journal(path, year):
    """Parse transactions from a Ledger journal (faithful to what is written)."""
    transactions = []
    pending_file = None
    current = None

    def flush():
        nonlocal current
        if current is not None:
            elided = [p for p in current['postings'] if p['amount'] is None]
            if len(elided) == 1:
                total = sum(p['amount'] for p in current['postings']
                            if p['amount'] is not None and not p['virtual']
                            and p['commodity'] == '$')
                value = round(-total, 2)
                elided[0]['amount'] = value
                elided[0]['commodity'] = '$'
                elided[0]['display'] = format_money(value)
                elided[0]['elided'] = True
            transactions.append(current)
            current = None

    date_re = re.compile(
        r'^(\d{4}[/-]\d{2}[/-]\d{2}|\d{2}[/-]\d{2})\s+'
        r'(?:([*!])\s+)?(?:\(([^)]*)\)\s+)?(.*)$')

    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.rstrip()

        if not line.strip():
            flush()
            continue

        if line.lstrip().startswith(';'):
            comment = line.lstrip()[1:].strip()
            if comment.lower().startswith('file:'):
                pending_file = comment.split(':', 1)[1].strip()
            continue

        if re.match(r'^(year|include|account|commodity|tag|define|P|=|N|D|C)\b',
                    line.strip()):
            flush()
            continue

        indented = line[0] in ' \t'

        if not indented:
            m = date_re.match(line.strip())
            if not m:
                continue
            flush()
            datestr, state, code, payee = m.groups()
            datestr = datestr.replace('-', '/')
            if len(datestr) == 5:  # MM/DD - prepend the active fiscal year
                datestr = f"{year}/{datestr}"
            y, mo, d = (int(x) for x in datestr.split('/'))
            current = {
                'date': f"{y:04d}-{mo:02d}-{d:02d}",
                'month': f"{y:04d}-{mo:02d}",
                'monthName': MONTHS[mo],
                'payee': payee.strip(),
                'state': state or '',
                'code': code or '',
                'file': pending_file,
                'cardholder': None,
                'postings': [],
            }
            pending_file = None
            continue

        if current is None:
            continue
        body = line.strip()
        if body.startswith(';'):
            comment = body[1:].strip()
            mm = re.match(r'(?i)cardholder:\s*(.+)', comment)
            if mm:
                current['cardholder'] = mm.group(1).strip()
            continue

        parts = re.split(r'\s{2,}', body, maxsplit=1)
        account = parts[0].strip()
        virtual = account.startswith('(') and account.endswith(')')
        if virtual:
            account = account[1:-1].strip()
        amount_token = parts[1].strip() if len(parts) > 1 else ''
        amount_token = amount_token.split(';', 1)[0].strip()
        value, commodity, display = parse_amount(amount_token)
        current['postings'].append({
            'account': account,
            'amount': value,
            'commodity': commodity,
            'display': display,
            'virtual': virtual,
        })

    flush()
    return transactions


def ledger_balances(path):
    """Return [{account, amount}] of each account's OWN $ balance.

    Uses `ledger reg` (one row per posting) rather than `bal --flat`: the latter
    prints rolled-up totals for every posted account, so when a posted parent
    (e.g. `…:td visa`) also has a posted child (`…:td visa:scott`), summing the
    rows double-counts. Aggregating per-posting amounts gives each account's own
    total, which the browser then rolls up through the hierarchy correctly.
    """
    fmt = "%(account)|%(quantity(scrub(amount)))\n"
    out = subprocess.run(
        ["ledger", "-f", str(path), "reg",
         "--limit", 'commodity == "$"', "--format", fmt],
        capture_output=True, text=True, check=True).stdout
    own = {}
    for line in out.splitlines():
        if '|' not in line:
            continue
        account, qty = line.rsplit('|', 1)
        account = account.strip()
        if not account:
            continue
        try:
            own[account] = own.get(account, 0.0) + float(qty)
        except ValueError:
            continue
    rows = [{'account': a, 'amount': round(v, 2)}
            for a, v in own.items() if round(v, 2) != 0]
    rows.sort(key=lambda r: r['account'])
    return rows


def build(ledger_file, out_arg=None):
    path = Path(ledger_file)
    if not path.exists():
        sys.exit(f"error: {path} not found")
    m = re.search(r'(\d{4})', path.stem)
    if not m:
        sys.exit(f"error: cannot determine fiscal year from {path.name}")
    year = int(m.group(1))

    transactions = parse_journal(path, year)
    for i, t in enumerate(transactions):
        t['id'] = i
    if not transactions:
        sys.exit(f"error: no transactions parsed from {path.name}")

    balances = ledger_balances(path)
    if not balances:
        sys.exit(f"error: no $ balances produced from {path.name}")

    data = {
        'year': year,
        'generated': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'transactions': transactions,
        'balances': balances,
    }

    html = (TEMPLATE.read_text(encoding='utf-8')
            .replace('__YEAR__', str(year))
            .replace('__DATA__', json.dumps(data, ensure_ascii=False)))
    out_path = Path(out_arg) if out_arg else Path(f"{year}-financials.html")
    out_path.write_text(html, encoding='utf-8')
    print(f"wrote {out_path}  ({len(transactions)} transactions, "
          f"{len(balances)} accounts, {len(html):,} bytes)")
    return out_path


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        sys.exit(__doc__)
    build(argv[0], argv[1] if len(argv) > 1 else None)


if __name__ == "__main__":
    main(sys.argv[1:])
