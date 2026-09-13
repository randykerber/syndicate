"""`derive-rosters`: rebuild a day's roster from the ledger when no true image exists.

Case: Hedgeye replaced the chart under a feed item with a *later* day's table (flagged
`roster_untrusted` in overrides.json). Membership for the day is still exact from what
we trust: previous trusted roster, plus every stated add/remove since. Stable fields
(rank, analyst, sector, signal date) are carried forward for continuing tickers and
taken from the next trusted image for newly added ones; prices stay null. The later-day
image reading is kept beside the derivation, never discarded.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .aliases import canon
from .ss_checks import MAX_REPLAY_GAP_DAYS, _days_between
from .ss_roster import rank_kind

CARRY = ("signal_date", "entry_price", "sector", "analyst", "best_idea_rank")


def _rows_by_ticker(snap: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {canon(r["ticker"]): r for r in (snap.get("roster") or {}).get("rows", [])}


def derive_one(
    snap: dict[str, Any],
    prev: dict[str, Any],
    between: list[dict[str, Any]],
    later: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Return the derived roster dict, or None if the gap is too long to trust."""
    gap = _days_between(prev.get("published_at"), snap.get("published_at"))
    if gap is None or gap > MAX_REPLAY_GAP_DAYS:
        return None
    members = set(_rows_by_ticker(prev))
    for mid in between + [snap]:
        members -= {canon(t) for t in (mid["changes"]["removed"] or [])}
        members |= {canon(t) for t in (mid["changes"]["added"] or [])}
    prev_rows = _rows_by_ticker(prev)
    day_delta = int(round(gap))
    rows: list[dict[str, Any]] = []
    for t in members:
        base = prev_rows.get(t)
        if base is not None:
            row = {k: base.get(k) for k in CARRY}
            row["days_on"] = (base.get("days_on") or 0) + day_delta
            row["field_source"] = f"carried from {prev['feed_item_id']}"
        else:
            src = next((s for s in later if t in _rows_by_ticker(s)), None)
            if src is not None:
                b = _rows_by_ticker(src)[t]
                row = {k: b.get(k) for k in CARRY}
                row["field_source"] = f"from next image {src['feed_item_id']}"
            else:
                row = {k: None for k in CARRY}
                row["field_source"] = "unknown"
            row["days_on"] = 0
        row.update(
            {"ticker": t, "recent_price": None, "pct_since_signal": None,
             "rank_kind": rank_kind(row.get("best_idea_rank"))}
        )  # fmt: skip
        rows.append(row)
    rows.sort(key=lambda r: (-(r["days_on"] or 0), r["ticker"]))
    return {
        "column_headers": ["derived"],
        "row_count_reported": len(rows),
        "rows": rows,
        "notes": [
            f"derived: {prev['feed_item_id']} + stated changes of "
            f"{[m['feed_item_id'] for m in between + [snap]]}; prices unknown"
        ],
    }


def derive_rosters(
    snaps: list[dict[str, Any]], write: Any, force: bool = False
) -> dict[str, Any]:
    """Fill every untrusted (or roster-less) snapshot that a trusted neighbour can derive."""
    trusted_idx = [i for i, s in enumerate(snaps) if _is_trusted_image(s)]
    done = skipped = 0
    for i, snap in enumerate(snaps):
        chart = snap.get("chart") or {}
        untrusted = bool(chart.get("roster_untrusted"))
        if not untrusted and snap.get("roster"):
            continue
        if (snap.get("roster_source") or {}).get("kind") == "derived" and not force:
            skipped += 1
            continue
        prev_i = max((j for j in trusted_idx if j < i), default=None)
        if prev_i is None:
            skipped += 1
            continue
        between = [s for s in snaps[prev_i + 1 : i]]
        later = [snaps[j] for j in trusted_idx if j > i][:5]
        derived = derive_one(snap, snaps[prev_i], between, later)
        if derived is None:
            skipped += 1
            continue
        if (
            untrusted
            and snap.get("roster")
            and not (snap.get("roster_source") or {}).get("kind") == "derived"
        ):
            snap["roster_from_later_image"] = snap["roster"]
            snap["roster_from_later_image_source"] = snap.get("roster_source")
        snap["roster"] = derived
        snap["roster_source"] = {
            "kind": "derived",
            "model": None,
            "prompt_version": None,
            "derived_from": snaps[prev_i]["feed_item_id"],
            "via": [s["feed_item_id"] for s in between],
            "derived_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "confidence_note": "membership exact if the stated changes are complete; "
            "stable fields carried; prices unknown",
        }
        write(snap)
        done += 1
        print(
            f"  derived {snap['feed_item_id']} {snap.get('published_at')} rows={len(derived['rows'])}"
        )
    return {"derived": done, "skipped": skipped}


def _is_trusted_image(snap: dict[str, Any]) -> bool:
    return (
        bool(snap.get("roster"))
        and not (snap.get("chart") or {}).get("roster_untrusted")
        and (snap.get("roster_source") or {}).get("kind") != "derived"
    )
