"""Ticker canonicalization — hand-maintained `~/d/prod/hedgeye/ticker-aliases.json`.

Two relations, kept apart because they mean different things:

- **alias** — a legitimate alternate identifier of the same entity (UA / UAA). Not an
  error; a naming choice.
- **correction** — a string that is not a ticker at all, a typo in Hedgeye's output
  (AZTAF for ATZAF). An error in the source, recorded as such.

Native spellings are kept everywhere they arrive; the canonical form is used when
tickers are compared or loaded, with the native form and the relation kind stored
beside it. Per the resolver decree: record the native id, dedupe at query time.
"""

from __future__ import annotations

import json
from functools import lru_cache

from . import paths


@lru_cache(maxsize=1)
def _tables() -> tuple[dict[str, str], dict[str, str]]:
    p = paths.TICKER_ALIASES
    if not p.exists():
        return {}, {}
    data = json.loads(p.read_text())
    aliases = {k.upper(): v.upper() for k, v in data.get("aliases", {}).items()}
    corrections = {k.upper(): v.upper() for k, v in data.get("corrections", {}).items()}
    return aliases, corrections


def canon(ticker: str) -> str:
    t = ticker.strip().upper()
    aliases, corrections = _tables()
    return corrections.get(t) or aliases.get(t) or t


def kind(ticker: str) -> str | None:
    """'alias' | 'correction' | None for a native spelling."""
    t = ticker.strip().upper()
    aliases, corrections = _tables()
    if t in corrections:
        return "correction"
    if t in aliases:
        return "alias"
    return None


def canon_set(tickers: list[str] | None) -> set[str]:
    return {canon(t) for t in (tickers or [])}


def reload() -> None:
    _tables.cache_clear()
