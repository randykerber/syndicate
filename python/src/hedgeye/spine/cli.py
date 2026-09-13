"""`spine` — the hand-run commands. Every one is safe to rerun.

extract ss            emails -> snapshots/ss/<feed_item_id>.json (+ chart PNGs)
read-rosters          PNG -> roster rows via Sonnet 5 API, or --from-dir DIR to merge
                      files a Claude Code session/subagent read (subscription path)
check                 three consistency witnesses per snapshot, written back
load                  snapshots -> SQLite (~/d/prod/hedgeye/hedgeye.sqlite)
status                the one bell: what's on disk, what's stale, what failed
diff [A B]            roster + stable-field changes between two snapshots (default: last two)
query TICKER          in/out, status, history
holdings --fidelity CSV [--ibkr JSON]   compare holdings to the latest roster
render                write Fin/Areas/Hedgeye/gen/SS Stocks.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import db, paths, ss_checks, ss_extract, ss_roster


def _dump(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, default=str)


def _write_snapshot(snap: dict[str, Any]) -> None:
    ss_extract.snapshot_path(snap["feed_item_id"]).write_text(ss_roster.dump_json(snap))


def _latest_with_roster(snaps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [s for s in snaps if s.get("roster")]


def cmd_extract(a: argparse.Namespace) -> int:
    if a.stream != "ss":
        print(f"unknown stream {a.stream!r}; only 'ss' in this slice", file=sys.stderr)
        return 2
    summary = ss_extract.extract(fetch=not a.no_fetch)
    print(_dump(summary))
    with db.connect() as con:
        db.record_run(con, "extract ss", summary)
    return 0


def cmd_read_rosters(a: argparse.Namespace) -> int:
    snaps = ss_extract.load_snapshots()
    if a.from_dir:
        summary = ss_roster.merge_reads_from_dir(
            snaps,
            Path(a.from_dir).expanduser(),
            _write_snapshot,
            reader=a.reader,
            force=a.force,
        )
        print(_dump(summary))
        with db.connect() as con:
            db.record_run(con, "read-rosters --from-dir", summary)
        return 0
    if a.feed_item_id:
        snaps = [s for s in snaps if s["feed_item_id"] in a.feed_item_id]
    if a.latest:
        snaps = [s for s in snaps if (s.get("chart") or {}).get("local_path")][
            -a.latest :
        ]
    summary = ss_roster.read_rosters(
        snaps, _write_snapshot, force=a.force, limit=a.limit
    )
    print(_dump(summary))
    with db.connect() as con:
        db.record_run(con, "read-rosters", summary)
    return 0


def cmd_check(a: argparse.Namespace) -> int:
    snaps = ss_extract.load_snapshots()
    tally = ss_checks.run_checks(snaps)
    for s in snaps:
        _write_snapshot(s)
    print(_dump(tally))
    with db.connect() as con:
        db.record_run(con, "check", tally)
    return 0


def cmd_load(a: argparse.Namespace) -> int:
    snaps = ss_extract.load_snapshots()
    with db.connect() as con:
        summary = db.load_snapshots(snaps, con)
        db.record_run(con, "load", summary)
    print(_dump(summary))
    return 0


def _status() -> dict[str, Any]:
    snaps = ss_extract.load_snapshots()
    with_roster = _latest_with_roster(snaps)
    mail = sorted((paths.RAW_MAIL / paths.SS_MAILBOX).glob("*.eml"))
    unkeyed = list((paths.SNAPSHOTS_SS / "_unkeyed").glob("*.json"))
    failed_checks = [s["feed_item_id"] for s in with_roster
                     if s.get("checks") and s["checks"]["applicable"] and not s["checks"]["all_pass"]]  # fmt: skip
    chart_missing = [s["feed_item_id"] for s in snaps
                     if ((s.get("chart") or {}).get("fetch") or {}).get("status")
                     not in ("fetched", "cached")]  # fmt: skip
    runs: list[dict[str, Any]] = []
    if paths.DB_PATH.exists():
        with db.connect() as con:
            runs = [dict(r) for r in con.execute(
                "SELECT command, MAX(ran_at) AS last_run FROM runs GROUP BY command")]  # fmt: skip
    return {
        "mailbox_messages": len(mail),
        "last_email_file": mail[-1].name if mail else None,
        "snapshots": len(snaps),
        "unkeyed": len(unkeyed),
        "with_roster": len(with_roster),
        "without_roster": [s["feed_item_id"] for s in snaps if not s.get("roster")],
        "latest_snapshot": snaps[-1]["published_at"] if snaps else None,
        "latest_with_roster": with_roster[-1]["published_at"] if with_roster else None,
        "charts_missing": chart_missing,
        "checks_failing": failed_checks,
        "last_runs": {r["command"]: r["last_run"] for r in runs},
    }


def cmd_status(a: argparse.Namespace) -> int:
    print(_dump(_status()))
    return 0


def _pick(snaps: list[dict[str, Any]], fid: str | None, offset: int) -> dict[str, Any]:
    if fid:
        for s in snaps:
            if s["feed_item_id"] == fid:
                return s
        raise SystemExit(f"no snapshot with roster for feed_item_id {fid}")
    return snaps[offset]


def cmd_diff(a: argparse.Namespace) -> int:
    snaps = _latest_with_roster(ss_extract.load_snapshots())
    if len(snaps) < 2:
        print("need at least two snapshots with rosters", file=sys.stderr)
        return 1
    A = _pick(snaps, a.a, -2)
    B = _pick(snaps, a.b, -1)
    print(_dump(ss_checks.diff_rosters(A, B)))
    return 0


def cmd_query(a: argparse.Namespace) -> int:
    with db.connect() as con:
        for t in a.ticker:
            print(_dump(db.ticker_history(con, t)))
    return 0


def _holdings(fid_csv: Path, ibkr: Path | None) -> tuple[list[Any], dict[str, Any]]:
    from . import holdings as H

    hs = H.from_fidelity(fid_csv)
    if ibkr:
        hs += H.from_ibkr_json(ibkr)
    return H.merge(hs), {"fidelity": fid_csv.name, "ibkr": ibkr.name if ibkr else None}


def cmd_holdings(a: argparse.Namespace) -> int:
    from . import holdings as H

    snaps = _latest_with_roster(ss_extract.load_snapshots())
    if not snaps:
        print("no roster yet — run extract, read-rosters", file=sys.stderr)
        return 1
    latest = snaps[-1]
    hs, meta = _holdings(
        Path(a.fidelity).expanduser(), Path(a.ibkr).expanduser() if a.ibkr else None
    )
    cmp = H.compare_to_roster(hs, latest["roster"]["rows"])
    out = {"roster": {"feed_item_id": latest["feed_item_id"], "published_at": latest["published_at"]},
           "holdings": meta, "n_holdings": len(hs), **cmp}  # fmt: skip
    if a.classes:
        out = {"classes": [{"ticker": h.ticker, "class": h.asset_class, "why": h.class_reason,
                            "value": round(h.value)} for h in hs]}  # fmt: skip
    print(_dump(out))
    if a.save:
        p = paths.PROD / "holdings_vs_ss.json"
        p.write_text(_dump(out) + "\n")
        print(f"saved {p}", file=sys.stderr)
    return 0


def cmd_render(a: argparse.Namespace) -> int:
    from . import holdings as H, render

    snaps = _latest_with_roster(ss_extract.load_snapshots())
    if not snaps:
        print("no roster yet", file=sys.stderr)
        return 1
    latest = snaps[-1]
    diff = ss_checks.diff_rosters(snaps[-2], latest) if len(snaps) > 1 else None
    cmp = meta = None
    if a.fidelity:
        hs, meta = _holdings(
            Path(a.fidelity).expanduser(), Path(a.ibkr).expanduser() if a.ibkr else None
        )
        cmp = H.compare_to_roster(hs, latest["roster"]["rows"])
    text = render.render_ss_page(latest, diff, cmp, meta, _status())
    print(render.write_ss_page(text))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="spine", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)  # fmt: skip
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("extract")
    s.add_argument("stream")
    s.add_argument("--no-fetch", action="store_true")
    s.set_defaults(fn=cmd_extract)  # noqa: E702
    s = sub.add_parser("read-rosters")
    s.add_argument("--force", action="store_true")
    s.add_argument("--limit", type=int)
    s.add_argument("--latest", type=int, help="only the N most recent with images")
    s.add_argument("--feed-item-id", nargs="*")
    s.add_argument(
        "--from-dir",
        help="merge <feed_item_id>.json roster files read by a CC session/subagent "
        "instead of calling the API",
    )
    s.add_argument(
        "--reader",
        default="claude-code-session",
        help="provenance label for --from-dir",
    )
    s.set_defaults(fn=cmd_read_rosters)  # noqa: E702
    s = sub.add_parser("check")
    s.set_defaults(fn=cmd_check)  # noqa: E702
    s = sub.add_parser("load")
    s.set_defaults(fn=cmd_load)  # noqa: E702
    s = sub.add_parser("status")
    s.set_defaults(fn=cmd_status)  # noqa: E702
    s = sub.add_parser("diff")
    s.add_argument("a", nargs="?")
    s.add_argument("b", nargs="?")
    s.set_defaults(fn=cmd_diff)  # noqa: E702
    s = sub.add_parser("query")
    s.add_argument("ticker", nargs="+")
    s.set_defaults(fn=cmd_query)  # noqa: E702
    s = sub.add_parser("holdings")
    s.add_argument("--fidelity", required=True)
    s.add_argument("--ibkr")
    s.add_argument("--classes", action="store_true", help="just list asset classes")
    s.add_argument("--save", action="store_true")
    s.set_defaults(fn=cmd_holdings)  # noqa: E702
    s = sub.add_parser("render")
    s.add_argument("--fidelity")
    s.add_argument("--ibkr")
    s.set_defaults(fn=cmd_render)  # noqa: E702

    a = p.parse_args(argv)
    return int(a.fn(a))


if __name__ == "__main__":
    raise SystemExit(main())
