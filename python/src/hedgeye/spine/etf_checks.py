"""Cross-stream witnesses for the ETF books (S31 machinery).

Streams: `ps-daily` (Portfolio Solutions, long-only roster every day) · `ep-changes`
(ETF Pro Plus real-time adds/removes, the ledger) · `ep-weekly` (ETF Pro Plus roster,
weekly anchor; older Levels issues are image-only) · `any10` (10-ETF portfolio).

Checks
- ep_weekly_vs_replay   previous anchor + every change since == this anchor (long, short)
- ps_vs_ep_long         PS roster (ex cash) == EP long state as of PS time, or by end of day
- ps_txn_vs_roster      previous PS roster through Keith's stated transactions == today's
- any10_subset_ps       the ten are inside PS's long book (nearest PS roster on/before)

Disagreements are recorded, never smoothed (§0). Nothing here writes anywhere but the
snapshot's `checks` field.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from .aliases import canon
from .parse_ps import CASH

MAX_ANCHOR_GAP_DAYS = 45


def _ts(s: dict[str, Any]) -> datetime | None:
    v = s.get("published_at") or s.get("arrived_at")
    if not v:
        return None
    try:
        return datetime.fromisoformat(v[:16])
    except ValueError:
        return None


# ---------------------------------------------------------------- EP state timeline ----


def ep_anchors(weekly: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Weekly reports with a real roster. Levels issues have none (image only) and the
    monthly updates' "Long:" line is a stale snapshot written before that week's changes
    (Mar-2026 and Jun-2026 both listed tickers already sold), so they are not anchors.
    """
    return [
        s
        for s in weekly
        if s.get("long") and _ts(s) and s["subject_parsed"].get("kind") == "weekly"
    ]


def apply_changes(
    long: set[str], short: set[str], changes: list[dict[str, Any]], notes: list[str]
) -> None:
    for c in changes:
        t = canon(c["ticker"])
        side = c.get("side")
        if c["action"] == "add":
            side = side or "long"
            (long if side == "long" else short).add(t)
            (short if side == "long" else long).discard(t) if False else None
        else:
            if side == "long":
                long.discard(t)
            elif side == "short":
                short.discard(t)
            elif t in long:
                long.discard(t)
            elif t in short:
                short.discard(t)
            else:
                notes.append(f"remove {t}: not in either book")


def ep_state_at(
    when: datetime,
    anchors: list[dict[str, Any]],
    changes: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """EP long/short sets as of `when`: latest anchor at/before, plus changes since."""
    prior = [a for a in anchors if _ts(a) <= when]
    if not prior:
        return None
    anchor = prior[-1]
    a_ts = _ts(anchor)
    if (when - a_ts).days > MAX_ANCHOR_GAP_DAYS:
        return None
    long = {canon(r["ticker"]) for r in anchor["long"]}
    short = {canon(r["ticker"]) for r in anchor["short"]}
    notes: list[str] = []
    applied = [c for c in changes if a_ts < (_ts(c) or a_ts) <= when]
    for snap in applied:
        apply_changes(long, short, snap["changes"], notes)
    return {
        "anchor": anchor["feed_item_id"],
        "anchor_at": anchor.get("published_at"),
        "changes_applied": [c["feed_item_id"] for c in applied],
        "long": long,
        "short": short,
        "notes": notes,
    }


# ------------------------------------------------------------------------- checks ----


def check_ep_weekly(
    weekly: list[dict[str, Any]], changes: list[dict[str, Any]]
) -> dict[str, Any]:
    anchors = ep_anchors(weekly)
    tally = {"checked": 0, "pass": 0, "failures": []}
    for prev, cur in zip(anchors, anchors[1:]):
        if cur["subject_parsed"].get("kind") != "weekly":
            continue
        state = ep_state_at(_ts(cur), anchors[: anchors.index(cur)], changes)
        if state is None or state["anchor"] != prev["feed_item_id"]:
            cur["checks"] = {
                "ep_weekly_vs_replay": {
                    "pass": None,
                    "reason": "no usable previous anchor",
                }
            }
            continue
        long = {canon(r["ticker"]) for r in cur["long"]}
        short = {canon(r["ticker"]) for r in cur["short"]}
        res = {
            "pass": state["long"] == long and state["short"] == short,
            "prev_anchor": prev["feed_item_id"],
            "changes_applied": len(state["changes_applied"]),
            "long_expected_absent": sorted(state["long"] - long),
            "long_unexpected": sorted(long - state["long"]),
            "short_expected_absent": sorted(state["short"] - short),
            "short_unexpected": sorted(short - state["short"]),
            "notes": state["notes"],
        }
        cur["checks"] = {"ep_weekly_vs_replay": res}
        tally["checked"] += 1
        if res["pass"]:
            tally["pass"] += 1
        else:
            tally["failures"].append({"feed_item_id": cur["feed_item_id"], "at": cur.get("published_at"),
                                      "long-": res["long_expected_absent"], "long+": res["long_unexpected"],
                                      "short-": res["short_expected_absent"], "short+": res["short_unexpected"]})  # fmt: skip
    return tally


def ps_tickers(snap: dict[str, Any]) -> set[str]:
    return {
        canon(r["ticker"])
        for r in snap.get("roster", [])
        if not r.get("is_cash") and canon(r["ticker"]) not in CASH
    }


def check_ps(
    ps: list[dict[str, Any]],
    weekly: list[dict[str, Any]],
    changes: list[dict[str, Any]],
) -> dict[str, Any]:
    anchors = ep_anchors(weekly)
    tally = {"checked": 0, "vs_ep_pass": 0, "vs_ep_pass_eod": 0, "vs_ep_fail": 0, "vs_ep_skipped": 0,
             "txn_checked": 0, "txn_pass": 0, "failures": []}  # fmt: skip
    prev: dict[str, Any] | None = None
    for snap in ps:
        results: dict[str, Any] = {}
        when = _ts(snap)
        mine = ps_tickers(snap)
        # --- PS vs EP long book
        if when is not None:
            st_now = ep_state_at(when, anchors, changes)
            eod = when.replace(hour=23, minute=59)
            st_eod = ep_state_at(eod, anchors, changes)
            if st_now is None:
                results["ps_vs_ep_long"] = {
                    "pass": None,
                    "reason": "no EP anchor within reach",
                }
                tally["vs_ep_skipped"] += 1
            else:
                only_ps = sorted(mine - st_now["long"])
                only_ep = sorted(st_now["long"] - mine)
                eod_only_ps = sorted(mine - st_eod["long"]) if st_eod else only_ps
                eod_only_ep = sorted(st_eod["long"] - mine) if st_eod else only_ep
                at_time = not only_ps and not only_ep
                by_eod = not eod_only_ps and not eod_only_ep
                results["ps_vs_ep_long"] = {
                    "pass": at_time or by_eod,
                    "equal_at_ps_time": at_time,
                    "equal_by_end_of_day": by_eod,
                    "only_ps": only_ps,
                    "only_ep": only_ep,
                    "only_ps_eod": eod_only_ps,
                    "only_ep_eod": eod_only_ep,
                    "ep_anchor": st_now["anchor"],
                    "ep_long_size": len(st_now["long"]),
                    "ps_size": len(mine),
                }
                tally[
                    (
                        "vs_ep_pass"
                        if at_time
                        else ("vs_ep_pass_eod" if by_eod else "vs_ep_fail")
                    )
                ] += 1
        # --- PS transactions vs roster diff
        gap_ok = (
            when is not None and _ts(prev) is not None and (when - _ts(prev)).days <= 4
            if prev
            else False
        )
        if prev is not None and snap.get("transactions") is not None and not gap_ok:
            results["ps_txn_vs_roster"] = {
                "pass": None,
                "reason": "gap > 4 days since previous PS report",
            }
        if prev is not None and snap.get("transactions") is not None and gap_ok:
            before = ps_tickers(prev)
            expected = set(before)
            for t in snap["transactions"]:
                tk = canon(t["ticker"])
                if t["action"] in ("sell-all",):
                    expected.discard(tk)
                elif t["action"] in ("add-min", "add", "buy") and tk not in before:
                    expected.add(tk)
            stated_out = sorted(before - expected)
            stated_in = sorted(expected - before)
            actual_out = sorted(before - mine)
            actual_in = sorted(mine - before)
            res = {
                "pass": expected == mine,
                "prev_feed_item_id": prev["feed_item_id"],
                "stated_in": stated_in,
                "stated_out": stated_out,
                "actual_in": actual_in,
                "actual_out": actual_out,
                "unexplained_in": sorted(set(actual_in) - set(stated_in)),
                "unexplained_out": sorted(set(actual_out) - set(stated_out)),
                "stated_but_not_seen": sorted(
                    (set(stated_in) - set(actual_in))
                    | (set(stated_out) - set(actual_out))
                ),
                "gap_days": (when - _ts(prev)).days if when and _ts(prev) else None,
            }
            results["ps_txn_vs_roster"] = res
            tally["txn_checked"] += 1
            if res["pass"]:
                tally["txn_pass"] += 1
        snap["checks"] = results
        tally["checked"] += 1
        if snap.get("roster"):
            prev = snap
    _annotate_lags(ps)
    for snap in ps:
        fails = [
            k
            for k, v in (snap.get("checks") or {}).items()
            if v.get("pass") is False and not v.get("pass_with_lag1")
        ]
        if fails:
            tally["failures"].append(
                {
                    "feed_item_id": snap["feed_item_id"],
                    "at": snap.get("published_at"),
                    "failed": fails,
                }
            )
    tally["txn_pass_lag1"] = sum(
        1
        for s in ps
        if (s.get("checks") or {}).get("ps_txn_vs_roster", {}).get("pass_with_lag1")
    )
    lags: dict[str, int] = {}
    for s in ps:
        r = (s.get("checks") or {}).get("ps_vs_ep_long", {})
        if r.get("pass") is False:
            k = str(r.get("resolved_after_days"))
            lags[k] = lags.get(k, 0) + 1
    tally["vs_ep_resolved_after_days"] = lags
    return tally


def _annotate_lags(ps: list[dict[str, Any]]) -> None:
    """Second pass. (a) A PS transaction stated on day D but visible in the roster only
    on the next report is a one-report lag, not a contradiction: `pass_with_lag1`.
    (b) For PS-vs-EP disagreements, how many days until the disagreeing tickers clear.
    """
    for i, snap in enumerate(ps):
        ck = snap.get("checks") or {}
        t = ck.get("ps_txn_vs_roster")
        if t and t["pass"] is False and i + 1 < len(ps):
            nxt = (ps[i + 1].get("checks") or {}).get("ps_txn_vs_roster") or {}
            late = set(t["stated_but_not_seen"])
            seen_next = set(nxt.get("unexplained_in", [])) | set(
                nxt.get("unexplained_out", [])
            )
            if (
                late
                and late <= seen_next
                and not t["unexplained_in"]
                and not t["unexplained_out"]
            ):
                t["pass_with_lag1"] = True
                nxt["explained_by_previous_report"] = sorted(late)
                if (
                    set(nxt.get("unexplained_in", []))
                    | set(nxt.get("unexplained_out", []))
                    <= late
                ):
                    nxt["pass_with_lag1"] = True
        r = ck.get("ps_vs_ep_long")
        if r and r["pass"] is False:
            bad = set(r["only_ps_eod"]) | set(r["only_ep_eod"])
            r["resolved_after_days"] = None
            for later in ps[i + 1 : i + 12]:
                rr = (later.get("checks") or {}).get("ps_vs_ep_long") or {}
                if rr.get("pass") is None:
                    continue
                still = bad & (
                    set(rr.get("only_ps_eod", [])) | set(rr.get("only_ep_eod", []))
                )
                if not still:
                    a, b = _ts(snap), _ts(later)
                    r["resolved_after_days"] = (b - a).days if a and b else None
                    break


def check_any10(
    any10: list[dict[str, Any]], ps: list[dict[str, Any]]
) -> dict[str, Any]:
    tally = {"checked": 0, "pass": 0, "failures": []}
    prev: dict[str, Any] | None = None
    for snap in any10:
        when = _ts(snap)
        mine = {canon(r["ticker"]) for r in snap.get("roster", [])}
        results: dict[str, Any] = {}
        cands = [
            p
            for p in ps
            if _ts(p)
            and _ts(p) <= when + timedelta(hours=12)
            and (when - _ts(p)).days <= 4
        ]
        if cands:
            p = cands[-1]
            pt = ps_tickers(p)
            results["any10_subset_ps"] = {"pass": mine <= pt, "ps_feed_item_id": p["feed_item_id"],
                                          "ps_at": p.get("published_at"), "not_in_ps": sorted(mine - pt)}  # fmt: skip
        if prev is not None:
            before = {canon(r["ticker"]) for r in prev.get("roster", [])}
            stated_in = {
                canon(c["ticker"])
                for c in snap.get("changes", [])
                if c["action"] == "add"
            }
            stated_out = {
                canon(c["ticker"])
                for c in snap.get("changes", [])
                if c["action"] == "remove"
            }
            expected = (before - stated_out) | stated_in
            results["any10_replay"] = {"pass": expected == mine, "unexpected": sorted(mine - expected),
                                       "expected_absent": sorted(expected - mine)}  # fmt: skip
        snap["checks"] = results
        tally["checked"] += 1
        if all(v.get("pass") for v in results.values()):
            tally["pass"] += 1
        else:
            tally["failures"].append({"feed_item_id": snap["feed_item_id"], "at": snap.get("published_at"),
                                      "failed": [k for k, v in results.items() if not v.get("pass")]})  # fmt: skip
        prev = snap
    return tally
