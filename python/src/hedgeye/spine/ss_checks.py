"""Signal Strength Stocks — `check`: three independent witnesses per snapshot.

1. subject count == number of roster rows read from the image
2. previous roster + Added − Removed == this roster (set identity)
3. Added/Removed text counts == subject's (n Added, m Removed)

Disagreement is recorded, never smoothed (§0). `confidence` is the fraction of
applicable checks that passed; a snapshot with no prior is checked on 1 and 3 only.
"""

from __future__ import annotations

import re
from typing import Any

STABLE_FIELDS = ("signal_date", "entry_price", "sector", "analyst", "best_idea_rank")
VOLATILE_FIELDS = ("days_on", "recent_price", "pct_since_signal")


def roster_tickers(snap: dict[str, Any]) -> set[str] | None:
    roster = snap.get("roster")
    if not roster:
        return None
    return {r["ticker"].upper() for r in roster["rows"]}


MAX_REPLAY_GAP_DAYS = 14


def _days_between(a: str | None, b: str | None) -> float | None:
    if not a or not b:
        return None
    from datetime import datetime

    try:
        return (
            datetime.fromisoformat(b) - datetime.fromisoformat(a)
        ).total_seconds() / 86400
    except ValueError:
        return None


def check_snapshot(
    snap: dict[str, Any],
    prev: dict[str, Any] | None,
    between: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """`between` = snapshots after `prev` and before `snap` whose rosters could not
    serve as baseline (untrusted / missing); their stated changes still count."""
    sp = snap["subject_parsed"]
    ch = snap["changes"]
    tick = roster_tickers(snap)
    results: dict[str, Any] = {}

    # 1 — subject count vs image rows
    if tick is not None:
        rows = len(snap["roster"]["rows"])
        dup = rows - len(tick)
        results["count_vs_rows"] = {
            "pass": rows == sp["count"] and dup == 0,
            "subject": sp["count"],
            "rows": rows,
            "duplicate_tickers_in_image": dup,
        }

    # 3 — text lists vs subject counts (independent of the image)
    if ch["added"] is not None or ch["removed"] is not None:
        a, r = ch["added"] or [], ch["removed"] or []
        results["text_vs_subject"] = {
            "pass": len(a) == sp["added"] and len(r) == sp["removed"],
            "added_text": len(a),
            "added_subject": sp["added"],
            "removed_text": len(r),
            "removed_subject": sp["removed"],
        }
    elif sp["added"] == 0 and sp["removed"] == 0:
        results["text_vs_subject"] = {"pass": True, "note": "no-change day, no lists"}

    # 2 — replay previous roster through every stated change since it
    prev_tick = roster_tickers(prev) if prev else None
    gap = _days_between(
        prev.get("published_at") if prev else None, snap.get("published_at")
    )
    if (
        tick is not None
        and prev_tick is not None
        and gap is not None
        and gap > MAX_REPLAY_GAP_DAYS
    ):
        results["replay_skipped"] = {
            "reason": f"gap of {gap:.0f} days since previous trusted roster",
            "prev_feed_item_id": prev["feed_item_id"],
        }
    elif tick is not None and prev_tick is not None:
        expected = set(prev_tick)
        for mid in (between or []) + [snap]:
            mc = mid["changes"]
            expected -= {t.upper() for t in (mc["removed"] or [])}
            expected |= {t.upper() for t in (mc["added"] or [])}
        a = {t.upper() for t in (ch["added"] or [])}
        r = {t.upper() for t in (ch["removed"] or [])}
        missing = sorted(expected - tick)  # expected but not in image
        extra = sorted(tick - expected)  # in image but not expected
        results["replay"] = {
            "pass": not missing and not extra,
            "prev_feed_item_id": prev["feed_item_id"],
            "via": [m["feed_item_id"] for m in (between or [])],
            "expected_but_absent": missing,
            "present_but_unexpected": extra,
            "added_not_in_image": sorted(a - tick),
            "removed_still_in_image": sorted(r & tick),
        }

    applicable = [v for v in results.values() if "pass" in v]
    passed = sum(1 for v in applicable if v["pass"])
    return {
        "results": results,
        "applicable": len(applicable),
        "passed": passed,
        "confidence": round(passed / len(applicable), 3) if applicable else None,
        "all_pass": bool(applicable) and passed == len(applicable),
    }


def run_checks(snaps: list[dict[str, Any]]) -> dict[str, Any]:
    """Snapshots must already be in publication order."""
    prev: dict[str, Any] | None = None
    between: list[dict[str, Any]] = []
    tally = {"checked": 0, "all_pass": 0, "with_failures": []}
    for snap in snaps:
        snap["checks"] = check_snapshot(snap, prev, between)
        tally["checked"] += 1
        if snap["checks"]["all_pass"]:
            tally["all_pass"] += 1
        elif snap["checks"]["applicable"]:
            tally["with_failures"].append(
                {
                    "feed_item_id": snap["feed_item_id"],
                    "published_at": snap.get("published_at"),
                    "failed": [
                        k for k, v in snap["checks"]["results"].items() if not v["pass"]
                    ],
                }
            )
        if snap.get("roster") and not (snap.get("chart") or {}).get("roster_untrusted"):
            prev = snap
            between = []
        else:
            between.append(snap)
    return tally


def diff_rosters(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Roster and stable-field changes from snapshot `a` to snapshot `b`."""
    ra = {r["ticker"].upper(): r for r in (a.get("roster") or {}).get("rows", [])}
    rb = {r["ticker"].upper(): r for r in (b.get("roster") or {}).get("rows", [])}
    added = sorted(set(rb) - set(ra))
    removed = sorted(set(ra) - set(rb))
    field_changes: list[dict[str, Any]] = []
    unavailable: dict[str, int] = {}
    for t in sorted(set(ra) & set(rb)):
        for f in STABLE_FIELDS:
            va, vb = ra[t].get(f), rb[t].get(f)
            if va is None or vb is None:
                # A column missing from one image (Apr-2026 charts carried only five
                # columns) is "unavailable", not a change — never an alert.
                if _norm(va) != _norm(vb):
                    unavailable[f] = unavailable.get(f, 0) + 1
                continue
            if _norm(va) != _norm(vb):
                change = {"ticker": t, "field": f, "from": va, "to": vb}
                change["significance"] = _significance(f, va, vb)
                field_changes.append(change)
    return {
        "from": {
            "feed_item_id": a["feed_item_id"],
            "published_at": a.get("published_at"),
        },
        "to": {
            "feed_item_id": b["feed_item_id"],
            "published_at": b.get("published_at"),
        },
        "added": [rb[t] for t in added],
        "removed": [ra[t] for t in removed],
        "stated_added": b["changes"].get("added"),
        "stated_removed": b["changes"].get("removed"),
        "stable_field_changes": field_changes,
        "fields_unavailable_one_side": unavailable,
    }


_RANK = re.compile(r"^\s*(\d+)\s*(?:/|of)\s*(\d+)\s*$")


def _significance(field: str, va: Any, vb: Any) -> str:
    """What kind of change this is — so an alert can ignore the noise.

    - best_idea_rank: `kind` (Bench <-> ranked <-> KM Signal) · `position` (numerator
      moved) · `denominator` (the analyst's list grew or shrank; the stock did not move)
    - entry_price: `rounding` when equal at one decimal (some images print one decimal)
    - everything else: `value`
    """
    if field == "best_idea_rank":
        from .ss_roster import rank_kind

        ka, kb = rank_kind(va), rank_kind(vb)
        if ka != kb:
            return "kind"
        pa, pb = _RANK.match(str(va)), _RANK.match(str(vb))
        if pa and pb:
            return "position" if pa.group(1) != pb.group(1) else "denominator"
        return "value"
    if (
        field == "entry_price"
        and isinstance(va, (int, float))
        and isinstance(vb, (int, float))
    ):
        return "rounding" if round(va, 1) == round(vb, 1) else "value"
    return "value"


def _norm(v: Any) -> Any:
    if isinstance(v, str):
        return " ".join(v.split()).lower()
    if isinstance(v, float):
        return round(v, 2)
    return v
