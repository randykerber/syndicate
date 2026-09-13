"""Ticker canonicalization — hand-maintained `~/d/prod/hedgeye/ticker-aliases.json`.

Native spellings are kept everywhere they arrive (roster reads, email text); the
canonical form is applied when tickers are *compared* or *loaded*, and the native form
is stored beside it. Per the resolver decree: record the native id, dedupe at query time.
"""

from __future__ import annotations

import json
from functools import lru_cache

from . import paths


@lru_cache(maxsize=1)
def _table() -> dict[str, str]:
    p = paths.TICKER_ALIASES
    if not p.exists():
        return {}
    data = json.loads(p.read_text())
    return {k.upper(): v.upper() for k, v in data.get("aliases", {}).items()}


def canon(ticker: str) -> str:
    t = ticker.strip().upper()
    return _table().get(t, t)


def canon_set(tickers: list[str] | None) -> set[str]:
    return {canon(t) for t in (tickers or [])}


def reload() -> None:
    _table.cache_clear()
