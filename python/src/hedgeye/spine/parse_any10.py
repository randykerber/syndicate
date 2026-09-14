"""10 ETF Go-Anywhere Portfolio email -> open positions, recently closed, stated changes."""

from __future__ import annotations

import re
from typing import Any

_CHANGE = re.compile(
    r"WE ARE (?P<action>ADDING|REMOVING)\s+(?P<ticker>[A-Z][A-Z0-9.\-]{0,6})\s*\((?P<name>[^)]*)\)"
)
_SUBJECT = re.compile(r"10 ETF Go-Anywhere Portfolio", re.I)


def _tables(html: str) -> list[tuple[list[str], list[list[str]]]]:
    from bs4 import BeautifulSoup

    out = []
    soup = BeautifulSoup(html, "html.parser")
    for tb in soup.find_all("table"):
        rows = tb.find_all("tr")
        if not rows:
            continue
        hdr = [c.get_text(" ", strip=True) for c in rows[0].find_all(["th", "td"])]
        if "Ticker" not in hdr:
            continue
        body = [
            [c.get_text(" ", strip=True) for c in r.find_all(["td", "th"])]
            for r in rows[1:]
        ]
        out.append((hdr, [b for b in body if len(b) >= len(hdr)]))
    return out


def _pct(v: str | None) -> float | None:
    if not v:
        return None
    try:
        return float(v.replace("%", "").replace("+", "").replace(",", ""))
    except ValueError:
        return None


def _money(v: str | None) -> float | None:
    if not v:
        return None
    try:
        return float(v.replace("$", "").replace(",", ""))
    except ValueError:
        return None


def parse(rec: dict[str, Any]) -> dict[str, Any]:
    text, html = rec["text"] or "", rec["html"] or ""
    open_rows, closed_rows = [], []
    for hdr, body in _tables(html):
        rec_rows = [dict(zip(hdr, b)) for b in body]
        if "Date Removed" in hdr:
            closed_rows = [
                {"ticker": r["Ticker"], "name": r.get("Name"), "asset_class": r.get("Asset Class"),
                 "date_added": r.get("Date Added"), "date_removed": r.get("Date Removed"),
                 "total_return_pct": _pct(r.get("Total Return ‡") or r.get("Total Return"))}
                for r in rec_rows
            ]  # fmt: skip
        else:
            open_rows = [
                {"rank": int(r["#"]) if r.get("#", "").isdigit() else None, "ticker": r["Ticker"],
                 "name": r.get("Name"), "asset_class": r.get("Asset Class"),
                 "entry_price": _money(r.get("Entry Price")),
                 "total_return_pct": _pct(r.get("Total Return ‡") or r.get("Total Return")),
                 "date_added": (r.get("Date Added") or "").rstrip("*") or None}
                for r in rec_rows
            ]  # fmt: skip
    changes: list[dict[str, Any]] = []
    head = text.split("Current Open Positions", 1)[0].replace("\xa0", " ")
    for m in re.finditer(
        r"WE ARE (?P<action>ADDING|REMOVING)\s+(?P<body>.*?)(?=WE ARE (?:ADDING|REMOVING)|$)",
        head,
        re.S,
    ):
        action = "add" if m.group("action") == "ADDING" else "remove"
        for t, name in re.findall(
            r"([A-Z][A-Z0-9.\-]{0,6})\s*\(([^)]*)\)", m.group("body")
        ):
            changes.append({"action": action, "ticker": t, "name": name.strip()})
    exceptions = []
    if not open_rows:
        exceptions.append("no open-positions table")
    elif len(open_rows) != 10:
        exceptions.append(f"open positions = {len(open_rows)}, not 10")
    return {
        "subject_parsed": {"recognized": bool(_SUBJECT.search(rec["subject"]))},
        "roster": open_rows,
        "closed": closed_rows,
        "changes": changes,
        "exceptions": exceptions,
    }
