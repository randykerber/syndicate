"""ETF Pro Plus — the change ledger (daily "UPDATE: N New ETF Pro Changes") and the
weekly roster ("ETF Pro Plus - New Weekly Report"; older "Levels" issues are image-only).

Change-email grammar drift (344 messages, Dec-2024 → now): section headers with/without
a side (`We are REMOVING:` before shorts were split out), non-breaking spaces, case, and
the first entry inline on the header line; entries `Name (TICKER)` optionally followed by
`- (low - high)`, plus two 2024/25 shapes `(EWO) Austria` and `CTA (Name)`. Some subjects
carry the whole action (`UPDATE: Remove WGMI`, `UPDATE: Add LONG QQQ`). Two messages are
HTML-only. A recap block ("IN CASE YOU MISSED IT") repeats earlier changes and is cut.
"""

from __future__ import annotations

import re
from typing import Any

_SUBJECT = re.compile(
    r"^\s*(?P<corr>Correction|UPDATE)\s*:\s*(?:(?P<n>\d+)\s+New ETF Pro Changes?"
    r"|(?P<verb>Remove|Removing|Add|Adding)\s+(?:(?P<vside>LONG|SHORT)\s+)?"
    r"(?:[^()]*\()?(?P<one>[A-Z][A-Z0-9.\-]{0,6})\)?)\s*$",
    re.I,
)
_HEADER = re.compile(
    r"^\s*We\s+are\s+(?P<action>ADDING|REMOVING)(?:\s+(?P<side>LONG|SHORT))?\s*:?\s*(?P<rest>.*)$",
    re.I,
)
_ENTRY = re.compile(
    r"^\s*(?P<name>.+?)\s*\((?P<ticker>[A-Z][A-Z0-9.\-]{0,6})\)"
    r"(?:\s*-\s*\(\s*(?P<lo>[\d.]+)\s*-\s*(?P<hi>[\d.]+)\s*\))?\s*$"
)
_ENTRY_TICKER_FIRST = re.compile(
    r"^\s*\((?P<ticker>[A-Z][A-Z0-9.\-]{0,6})\)\s*(?P<name>.+?)\s*$"
)
_ENTRY_NAME_IN_PARENS = re.compile(
    r"^\s*(?P<ticker>[A-Z][A-Z0-9.\-]{0,6})\s*\((?P<name>[^)]*[a-z][^)]*)\)\s*$"
)
_END = re.compile(
    r"^\s*(How to Use ETF Pro Plus Updates|Please visit|©|IN CASE YOU MISSED IT|Thank you"
    r"|TAKE THE SURVEY|Do you have 3 minutes)",
    re.I,
)
_WEEKLY_SUBJECT = re.compile(
    r"ETF Pro Plus\s*-\s*(New Weekly Report|Levels)|ETF Pro Plus:\s*\w+ Update", re.I
)
_MONTHLY_LINE = re.compile(
    r"^\s*(?P<side>Long|Short):\s*(?P<list>[A-Z0-9.\-,\s]+?)\s*$", re.M
)


def parse_change_subject(subject: str) -> dict[str, Any]:
    m = _SUBJECT.search(subject)
    if not m:
        return {"recognized": False}
    verb = (m.group("verb") or "").lower()
    return {
        "recognized": True,
        "is_correction": m.group("corr").lower() == "correction",
        "count": int(m.group("n")) if m.group("n") else (1 if m.group("one") else None),
        "subject_change": (
            {
                "action": "remove" if verb.startswith("remov") else "add",
                "side": (m.group("vside") or "").lower() or None,
                "ticker": m.group("one"),
            }
            if m.group("one")
            else None
        ),
    }


def parse_changes(text: str) -> tuple[list[dict[str, Any]], list[str]]:
    """-> (changes, unparsed lines inside sections)."""
    changes: list[dict[str, Any]] = []
    unparsed: list[str] = []
    action = side = None
    in_section = False
    for raw in text.replace("\xa0", " ").splitlines():
        line = raw.strip()
        if not line:
            continue
        if _END.match(line):
            break
        h = _HEADER.match(line)
        if h:
            action = "add" if h.group("action").upper() == "ADDING" else "remove"
            side = (h.group("side") or "").lower() or None
            in_section = True
            line = h.group("rest").strip()
            if not line:
                continue
        if not in_section:
            continue
        e = (
            _ENTRY.match(line)
            or _ENTRY_TICKER_FIRST.match(line)
            or _ENTRY_NAME_IN_PARENS.match(line)
        )
        if e:
            gd = e.groupdict()
            changes.append(
                {
                    "action": action,
                    "side": side,
                    "ticker": gd["ticker"],
                    "name": (gd.get("name") or "").strip() or None,
                    "range": (
                        [float(gd["lo"]), float(gd["hi"])] if gd.get("lo") else None
                    ),
                }
            )
        else:
            unparsed.append(line)
    return changes, unparsed


def html_to_text(html: str) -> str:
    """HTML-only emails (all ETF Pro changes since ~2026): block elements become line
    breaks, inline elements do not. BeautifulSoup's get_text("\n") put every <span> on
    its own line, so `We are ADDING <span>Short</span>:` lost its side (found 2026-09-28:
    two short adds read as long adds and PS≠EP rang falsely)."""
    import html as _html

    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html or "")
    t = re.sub(r"(?i)<br\s*/?>|</(p|div|li|tr|h[1-6]|ul|ol|table|blockquote)>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = _html.unescape(t).replace("\xa0", " ")
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n", t).strip()


def parse_change_email(rec: dict[str, Any]) -> dict[str, Any]:
    subject = parse_change_subject(rec["subject"])
    text = rec["text"] or html_to_text(rec["html"])
    changes, unparsed = parse_changes(text)
    if subject.get("subject_change") and not changes:
        changes = [
            {
                **subject["subject_change"],
                "name": None,
                "range": None,
                "from": "subject",
            }
        ]
    exceptions = []
    if subject.get("count") is not None and subject["count"] != len(changes):
        exceptions.append(
            f"subject says {subject['count']} changes, parsed {len(changes)}"
        )
    if unparsed:
        exceptions.append(f"{len(unparsed)} unparsed line(s) in change sections")
    if any(c["side"] is None for c in changes):
        exceptions.append("side unspecified on some changes (resolved at check time)")
    return {
        "subject_parsed": subject,
        "changes": changes,
        "unparsed": unparsed,
        "text_source": "text/plain" if rec["text"] else "html",
        "exceptions": exceptions,
    }


def parse_weekly_email(rec: dict[str, Any], path: str) -> dict[str, Any]:
    subj = rec["subject"]
    kind = None
    if _WEEKLY_SUBJECT.search(subj):
        kind = (
            "weekly"
            if "Weekly" in subj
            else ("levels" if "Levels" in subj else "monthly")
        )
    payload: dict[str, Any] = {
        "subject_parsed": {"recognized": kind is not None, "kind": kind},
        "long": [],
        "short": [],
        "exceptions": [],
    }
    if kind == "weekly":
        from hedgeye.ds.ep.parse_etf_pro_weekly import parse_eml

        try:
            _, positions = parse_eml(path)
        except Exception as e:  # noqa: BLE001
            payload["exceptions"].append(f"weekly table parse failed: {e}")
            return payload
        for p in positions:
            row = {
                "ticker": p.ticker,
                "name": p.description,
                "date_added": p.date_added,
                "recent_price": p.recent_price,
                "trend_low": p.trend_low,
                "trend_high": p.trend_high,
                "asset_class": p.asset_class,
            }
            payload["long" if p.position_type == "LONG" else "short"].append(row)
        payload["roster_source"] = "html-table"
    elif kind == "monthly":
        for mm in _MONTHLY_LINE.finditer(rec["text"] or ""):
            rows = [
                {"ticker": t}
                for t in re.split(r"[,\s]+", mm.group("list").strip())
                if t
            ]
            payload["long" if mm.group("side").lower() == "long" else "short"].extend(
                rows
            )
        payload["roster_source"] = "monthly-text"
        if not payload["long"]:
            payload["exceptions"].append("monthly update without Long: line")
    elif kind == "levels":
        payload["exceptions"].append("Levels issue: roster only as an image (not read)")
        payload["roster_source"] = "image-only"
    return payload
