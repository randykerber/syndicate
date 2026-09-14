"""Portfolio Solutions daily re-rank email -> roster + Keith's transactions.

Witnesses in one email: the ordered "Macro ETFs by Rank:" line (every message since
Dec-2024), an HTML rank table with entry date / asset class / sizing (mid-2026 onward),
and Keith's Commentary, whose bps grammar is regular enough for code (decision §4-6).
Unparsed commentary sentences are a required output, not a failure.
"""

from __future__ import annotations

import re
from typing import Any

_SUBJECT = re.compile(
    r"^\s*(?P<corr>\(CORRECTION\)\s*)?(?:PORTFOLIO SOLUTIONS:\s*)?(?:Portfolio Solutions:\s*)?"
    r"(?P<cadence>Daily|Weekly)\s+ETF\s+Re-Rank\s*\((?P<m>\d{1,2})[/_](?P<d>\d{1,2})[/_](?P<y>\d{4})\)",
    re.I,
)
_RANK_LINE = re.compile(
    r"(?:Macro )?ETFs by Rank:\s*(?P<list>[A-Z0-9.\-,\s]+?)(?:\n\s*\n|\s{2,}Keith|$)",
    re.S,
)
_COMMENTARY = re.compile(r"Keith's Commentary:\s*[\"“](?P<text>.*?)[\"”]", re.S)
_TICKER = re.compile(r"^[A-Z][A-Z0-9.\-]{0,6}$")
_MOVERS = re.compile(r"Top Movers:\s*(?P<list>(?:[A-Z0-9.\-]+\s*\([+-]?\d+\),?\s*)+)")

CASH = {"FDRXX", "SPAXX", "CORE", "FZFXX"}


def parse_subject(subject: str) -> dict[str, Any]:
    m = _SUBJECT.search(subject)
    if not m:
        return {"recognized": False}
    return {
        "recognized": True,
        "cadence": m.group("cadence").lower(),
        "report_date": f"{m.group('y')}-{int(m.group('m')):02d}-{int(m.group('d')):02d}",
        "is_correction": bool(m.group("corr")),
    }


def _tickers(raw: str) -> list[str]:
    out: list[str] = []
    for tok in re.split(r"[,\s]+", raw.strip()):
        tok = tok.strip().strip(".;")
        if tok and _TICKER.match(tok):
            out.append(tok)
    return out


def parse_rank_line(text: str) -> list[str]:
    m = _RANK_LINE.search(text)
    if not m:
        return []
    return _tickers(m.group("list"))


def parse_rank_table(html: str) -> list[dict[str, Any]]:
    """The HTML table (Rank · Ticker · 1-Week · 1-Month · Entry Date · Asset Class ·
    Position Sizing) — present from mid-2026; empty list when absent."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    for tb in soup.find_all("table"):
        rows = tb.find_all("tr")
        if not rows:
            continue
        hdr = [c.get_text(" ", strip=True) for c in rows[0].find_all(["th", "td"])]
        if "Ticker" not in hdr or "Rank" not in hdr:
            continue
        out = []
        for r in rows[1:]:
            cells = [c.get_text(" ", strip=True) for c in r.find_all(["td", "th"])]
            if len(cells) < len(hdr):
                continue
            rec = dict(zip(hdr, cells))
            out.append(
                {
                    "rank": int(rec["Rank"]) if rec["Rank"].isdigit() else None,
                    "ticker": rec["Ticker"].strip(),
                    "week_change": _change(rec.get("1-Week Change")),
                    "month_change": _change(rec.get("1-Month Change")),
                    "entry_date": _date(rec.get("Entry Date")),
                    "asset_class": rec.get("Asset Class"),
                    "sizing": rec.get("Position Sizing"),
                }
            )
        return out
    return []


def _change(v: str | None) -> int | None:
    if not v:
        return None
    v = v.replace("–", "-").strip()
    if v in {"-", "–", "N/A", ""}:
        return None
    m = re.match(r"^(?:(?P<up>▲)|(?P<down>▼))?\s*(?P<n>\d+)$", v)
    if not m:
        return None
    n = int(m.group("n"))
    return -n if m.group("down") else n


def _date(v: str | None) -> str | None:
    if not v:
        return None
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{2,4})$", v.strip())
    if not m:
        return None
    y = int(m.group(3))
    y = y + 2000 if y < 100 else y
    return f"{y}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"


# --- Keith's Commentary: the bps grammar ------------------------------------------------

_LIST = (
    r"(?P<list>[A-Z][A-Z0-9.\-]{0,6}(?:\s*(?:,|and|,\s*and)\s*[A-Z][A-Z0-9.\-]{0,6})*)"
)
_PRE = r"^(?:in the pa today,?\s*)?(?:i\s+)?"
_BPS = r"(?P<bps>\d+)\s*(?:bps|bp|ps)"
_MY = r"(?:of\s+)?(?:my\s+|the\s+)?"
_SENTENCES = [
    ("buy", re.compile(rf"{_PRE}bought\s+{_BPS}\s+(?:of\s+)?{_LIST}\s*\.?$", re.I)),
    ("sell", re.compile(rf"{_PRE}sold\s+{_BPS}\s+(?:of\s+)?{_LIST}\s*\.?$", re.I)),
    ("sell-all", re.compile(rf"{_PRE}sold\s+all\s+{_MY}{_LIST}(?:\s+i had left(?:\s+at my min)?)?\s*\.?$", re.I)),
    ("sell-all", re.compile(rf"{_PRE}sold\s+the\s+last\s+of\s+my\s+{_LIST}\s*\.?$", re.I)),
    ("add-min", re.compile(rf"{_PRE}(?:added|bought)\s+{_LIST}\s+at\s+(?:my\s+|their\s+)?min(?:s|imum|imums)?\s*\.?$", re.I)),
    ("sell-to-min", re.compile(rf"{_PRE}sold\s+{_LIST}\s+down\s+to\s+(?:my\s+)?mins?\s*\.?$", re.I)),
    ("add", re.compile(rf"{_PRE}added\s+{_LIST}\s*\.?$", re.I)),
    ("buy", re.compile(rf"{_PRE}bought\s+{_LIST}\s*\.?$", re.I)),
    ("sell", re.compile(rf"{_PRE}sold\s+{_LIST}\s*\.?$", re.I)),
]  # fmt: skip
_NOTE = re.compile(
    r"^(?:in the pa today,?\s*)?(?:there were\s+)?no changes|^#|^reiterat|^(?:i\s+)?(?:am|remain)\b",
    re.I,
)


def parse_commentary(
    text: str,
) -> tuple[str | None, list[dict[str, Any]], list[str], list[str]]:
    """-> (commentary text, transactions, unparsed sentences, note sentences).

    "sold the last of my QQQ and all of EWW" is split on " and all of " first, so both
    halves reach the sell-all rule.
    """
    m = _COMMENTARY.search(text)
    if not m:
        return None, [], [], []
    body = " ".join(m.group("text").split())
    txns: list[dict[str, Any]] = []
    unparsed: list[str] = []
    notes: list[str] = []
    for sent in re.split(r"(?<=[.!])\s+", body):
        sent = sent.strip()
        if not sent:
            continue
        if _NOTE.search(sent):
            notes.append(sent)
            continue
        # trailing parenthetical: "Sold 100bps GLD and AAAU (both positions at my MIN)."
        core = re.sub(r"\s*\([^)]*\)\s*\.?$", ".", sent).strip()
        pieces = re.split(r"\s+and\s+all\s+of\s+", core)
        if len(pieces) > 1:
            pieces = [pieces[0].rstrip(".") + "."] + [
                "sold all of " + x for x in pieces[1:]
            ]
        matched = True
        for piece in pieces:
            for action, rx in _SENTENCES:
                mm = rx.match(piece)
                if mm:
                    gd = mm.groupdict()
                    bps = int(gd["bps"]) if gd.get("bps") else None
                    for t in _tickers(gd["list"].replace(" and ", ",")):
                        txns.append(
                            {
                                "action": action,
                                "ticker": t,
                                "bps": bps,
                                "sentence": sent,
                            }
                        )
                    break
            else:
                matched = False
        if not matched:
            unparsed.append(sent)
    return body, txns, unparsed, notes


def parse_movers(text: str) -> list[dict[str, Any]]:
    out = []
    m = _MOVERS.search(text)
    if m:
        for t, n in re.findall(r"([A-Z0-9.\-]+)\s*\(([+-]?\d+)\)", m.group("list")):
            out.append({"ticker": t, "change": int(n)})
    return out


def parse(rec: dict[str, Any]) -> dict[str, Any]:
    """Email record (from eml.read_eml) -> PS payload."""
    text, html = rec["text"], rec["html"]
    subject = parse_subject(rec["subject"])
    order = parse_rank_line(text)
    if not order and html:
        from bs4 import BeautifulSoup

        order = parse_rank_line(BeautifulSoup(html, "html.parser").get_text("\n"))
    table = parse_rank_table(html) if html else []
    by_t = {r["ticker"]: r for r in table}
    roster = []
    for i, t in enumerate(order, start=1):
        row = {"rank": i, "ticker": t, "is_cash": t in CASH}
        if t in by_t:
            row.update(
                {
                    k: by_t[t][k]
                    for k in (
                        "entry_date",
                        "asset_class",
                        "sizing",
                        "week_change",
                        "month_change",
                    )
                }
            )
        roster.append(row)
    commentary, txns, unparsed, notes = parse_commentary(text)
    exceptions = []
    if not order:
        exceptions.append("no rank line")
    if table and {r["ticker"] for r in table} != set(order):
        exceptions.append("html table tickers != rank line")
    if unparsed:
        exceptions.append(f"{len(unparsed)} unparsed commentary sentence(s)")
    return {
        "subject_parsed": subject,
        "roster": roster,
        "roster_source": "rank-line" + ("+table" if table else ""),
        "commentary": commentary,
        "transactions": txns,
        "unparsed": unparsed,
        "commentary_notes": notes,
        "top_movers": parse_movers(text),
        "exceptions": exceptions,
    }
