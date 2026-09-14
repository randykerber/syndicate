"""Ticker canonicalization — hand-maintained `~/d/prod/hedgeye/ticker-aliases.json`.

Two relations, kept apart because they mean different things:

- **alias** — a legitimate alternate identifier of the same entity (UA / UAA). Not an
  error; a naming choice.
- **correction** — a string that is not a ticker at all, a typo in Hedgeye's output
  (AZTAF for ATZAF). An error in the source, recorded as such.

Entries may be date-ranged (`{"to": ..., "from": ..., "until": ...}`); a ranged entry
applies only to an observation dated inside the range. Corrections must be ranged, so a
future legitimate ticker spelled the same way is never rewritten (Randy, 2026-09-13).
Native spellings are kept everywhere they arrive; the canonical form is used when
tickers are compared or loaded, with the native form and the relation kind stored
beside it.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from functools import lru_cache
from typing import Any

from . import paths

Entry = tuple[str, str | None, str | None]  # (to, from, until) as ISO dates


def _norm_entry(v: Any) -> Entry:
    if isinstance(v, str):
        return v.upper(), None, None
    return str(v["to"]).upper(), v.get("from"), v.get("until")


@lru_cache(maxsize=1)
def _tables() -> tuple[dict[str, Entry], dict[str, Entry]]:
    p = paths.TICKER_ALIASES
    if not p.exists():
        return {}, {}
    data = json.loads(p.read_text())
    aliases = {k.upper(): _norm_entry(v) for k, v in data.get("aliases", {}).items()}
    corrections = {
        k.upper(): _norm_entry(v) for k, v in data.get("corrections", {}).items()
    }
    return aliases, corrections


def _day(at: str | date | datetime | None) -> str:
    if at is None:
        return date.today().isoformat()
    if isinstance(at, datetime):
        return at.date().isoformat()
    if isinstance(at, date):
        return at.isoformat()
    return str(at)[:10]


def _applies(e: Entry, day: str) -> bool:
    _, frm, until = e
    return (frm is None or day >= frm) and (until is None or day <= until)


def canon(ticker: str, at: str | date | datetime | None = None) -> str:
    """Canonical ticker for an observation dated `at` (default: today)."""
    t = ticker.strip().upper()
    aliases, corrections = _tables()
    day = _day(at)
    for table in (corrections, aliases):
        e = table.get(t)
        if e and _applies(e, day):
            return e[0]
    return t


def kind(ticker: str, at: str | date | datetime | None = None) -> str | None:
    """'alias' | 'correction' | None for a native spelling observed at `at`."""
    t = ticker.strip().upper()
    aliases, corrections = _tables()
    day = _day(at)
    e = corrections.get(t)
    if e and _applies(e, day):
        return "correction"
    e = aliases.get(t)
    if e and _applies(e, day):
        return "alias"
    return None


def canon_set(
    tickers: list[str] | None, at: str | date | datetime | None = None
) -> set[str]:
    return {canon(t, at) for t in (tickers or [])}


def reload() -> None:
    _tables.cache_clear()
