"""Signal Strength Stocks — `check`: three independent witnesses per snapshot.

1. subject count == number of roster rows read from the image
2. previous roster + Added − Removed == this roster (set identity)
3. Added/Removed text counts == subject's (n Added, m Removed)

Disagreement is recorded, never smoothed (§0). `confidence` is the fraction of
applicable checks that passed; a snapshot with no prior is checked on 1 and 3 only.
"""

from __future__ import annotations

from typing import Any

STABLE_FIELDS = ("signal_date", "entry_price", "sector", "analyst", "best_idea_rank")
VOLATILE_FIELDS = ("days_on", "recent_price", "pct_since_signal")


def roster_tickers(snap: dict[str, Any]) -> set[str] | None:
    roster = snap.get("roster")
    if not roster:
        return None
    return {r["ticker"].upper() for r in roster["rows"]}


def check_snapshot(snap: dict[str, Any], prev: dict[str, Any] | None) -> dict[str, Any]:
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

    # 2 — replay previous roster through the stated changes
    prev_tick = roster_tickers(prev) if prev else None
    if tick is not None and prev_tick is not None:
        a = {t.upper() for t in (ch["added"] or [])}
        r = {t.upper() for t in (ch["removed"] or [])}
        expected = (prev_tick - r) | a
        missing = sorted(expected - tick)  # expected but not in image
        extra = sorted(tick - expected)  # in image but not expected
        results["replay"] = {
            "pass": not missing and not extra,
            "prev_feed_item_id": prev["feed_item_id"],
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
    tally = {"checked": 0, "all_pass": 0, "with_failures": []}
    for snap in snaps:
        snap["checks"] = check_snapshot(snap, prev)
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
        if snap.get("roster"):
            prev = snap
    return tally


def diff_rosters(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Roster and stable-field changes from snapshot `a` to snapshot `b`."""
    ra = {r["ticker"].upper(): r for r in (a.get("roster") or {}).get("rows", [])}
    rb = {r["ticker"].upper(): r for r in (b.get("roster") or {}).get("rows", [])}
    added = sorted(set(rb) - set(ra))
    removed = sorted(set(ra) - set(rb))
    field_changes: list[dict[str, Any]] = []
    for t in sorted(set(ra) & set(rb)):
        for f in STABLE_FIELDS:
            va, vb = ra[t].get(f), rb[t].get(f)
            if _norm(va) != _norm(vb):
                field_changes.append({"ticker": t, "field": f, "from": va, "to": vb})
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
    }


def _norm(v: Any) -> Any:
    if isinstance(v, str):
        return " ".join(v.split()).lower()
    if isinstance(v, float):
        return round(v, 2)
    return v
