"""`refresh`: the daily routine as one hand-run command, then a report.

Runs every code-only step of the Spine Guide §3 routine in order — pull mail, extract,
check, load, render — picking the newest Fidelity / IBKR exports itself, and ends with a
report of what changed and what is stale. It never does what needs a person or a
browser; it says so instead. Each step is still its own `spine` command, so this is a
wrapper, not the only way in (governing rule: every step hand-runnable).

The report is built for the alerting discipline (*one bell for a list, never twenty*):
- **new failures** — witness failures not present at the previous refresh; the bell.
- **standing failures** — known disagreements, listed, not rung.
- **stale** — a stage whose input is newer than its output (mail newer than snapshots,
  snapshots without a roster, holdings exports older than N days).
State between runs lives in `~/d/prod/hedgeye/refresh-state.json`.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from . import db, paths, ss_checks, ss_extract, ss_roster

MAILBOXES = {
    "ss": paths.SS_MAILBOX,
    "ps-daily": "HE-PS",
    "ep-changes": "HE-ETF-Pro",
    "ep-weekly": "ETF-weekly",
    "any10": "Anywhere-10",
}
IMPORTER = (
    Path(__file__).resolve().parents[3] / "scratch" / "mail-import" / "import_mail.py"
)
STATE = paths.PROD / "refresh-state.json"
HOLDINGS_STALE_DAYS = 3


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="minutes")


def newest(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def _age_days(p: Path | None) -> float | None:
    if p is None:
        return None
    return round((time.time() - p.stat().st_mtime) / 86400, 1)


def _count_eml(mailbox: str) -> int:
    return len(list((paths.RAW_MAIL / mailbox).glob("*.eml")))


def _newest_eml_stamp(mailbox: str) -> str | None:
    """The newest email's arrival, from the importer's `YYYY-MM-DD_HHMMSS_` filename."""
    files = sorted((paths.RAW_MAIL / mailbox).glob("*.eml"))
    if not files:
        return None
    stem = files[-1].name
    return f"{stem[:10]}T{stem[11:13]}:{stem[13:15]}"


def pull_mail(limit: int) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if not IMPORTER.exists():
        return {"error": f"importer not found: {IMPORTER}"}
    for mailbox in MAILBOXES.values():
        before = _count_eml(mailbox)
        cmd = [sys.executable, str(IMPORTER), mailbox, "--limit", str(limit)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        after = _count_eml(mailbox)
        out[mailbox] = {"before": before, "after": after, "new": after - before}
        if r.returncode != 0:
            out[mailbox]["error"] = (r.stderr or r.stdout).strip()[-400:]
    return out


def load_state() -> dict[str, Any]:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {}


def save_state(state: dict[str, Any]) -> None:
    STATE.write_text(json.dumps(state, indent=2, default=str) + "\n")


def split_failures(current: list[str], known: list[str]) -> dict[str, list[str]]:
    """The bell rings only for failures the previous refresh did not see."""
    k = set(known)
    return {
        "new": [f for f in current if f not in k],
        "standing": [f for f in current if f in k],
        "cleared": [f for f in known if f not in set(current)],
    }


def _write_ss(snap: dict[str, Any]) -> None:
    ss_extract.snapshot_path(snap["feed_item_id"]).write_text(ss_roster.dump_json(snap))


def run(
    no_mail: bool = False,
    limit: int = 12,
    fidelity: Path | None = None,
    ibkr: Path | None = None,
) -> dict[str, Any]:
    from . import etf_checks, holdings as H, render, render_etf, streams

    report: dict[str, Any] = {"ran_at": _now(), "steps": {}}
    t0 = time.time()

    # 1 — mail
    if no_mail:
        report["steps"]["mail"] = {"skipped": True}
    else:
        report["steps"]["mail"] = pull_mail(limit)

    # 2 — extract
    ex: dict[str, Any] = {"ss": ss_extract.extract()}
    for s in streams.STREAMS:
        ex[s] = streams.extract(s)
    report["steps"]["extract"] = {
        k: {kk: v.get(kk) for kk in ("messages", "written", "unkeyed", "unrecognized",
                                     "rosters_from_table") if v.get(kk) is not None}
        for k, v in ex.items()
    }  # fmt: skip

    # 3 — check
    ss_snaps = ss_extract.load_snapshots()
    tally = ss_checks.run_checks(ss_snaps)
    for s in ss_snaps:
        _write_ss(s)
    ps = streams.load_snapshots("ps-daily")
    ch = streams.load_snapshots("ep-changes")
    wk = streams.load_snapshots("ep-weekly")
    a10 = streams.load_snapshots("any10")
    etf = {
        "ep_weekly": etf_checks.check_ep_weekly(wk, ch),
        "ps": etf_checks.check_ps(ps, wk, ch),
        "any10": etf_checks.check_any10(a10, ps),
    }
    for stream, snaps in (("ps-daily", ps), ("ep-weekly", wk), ("any10", a10)):
        for s in snaps:
            streams.snapshot_path(stream, s["feed_item_id"]).write_text(
                streams._dump(s)
            )
    ss_failing = [f["feed_item_id"] for f in tally["with_failures"]]
    etf_failing = [
        f"{k}:{x.get('feed_item_id') or x.get('date') or i}"
        for k, v in etf.items()
        for i, x in enumerate(v.get("failures") or [])
        if isinstance(x, dict)
    ]
    report["steps"]["check"] = {
        "ss": {"checked": tally["checked"], "all_pass": tally["all_pass"]},
        "etf": {
            k: {
                "n_failures": len(v.get("failures") or []),
                **{kk: vv for kk, vv in v.items() if kk != "failures"},
            }
            for k, v in etf.items()
        },
    }

    # 4 — load
    with db.connect() as con:
        loaded: dict[str, Any] = {"ss-stocks": db.load_snapshots(ss_snaps, con)}
        for stream in streams.STREAMS:
            loaded[stream] = db.load_stream(stream, streams.load_snapshots(stream), con)
    report["steps"]["load"] = loaded

    # 5 — holdings inputs, then render
    fid = fidelity or newest(paths.FID_POSITIONS, "*.csv")
    ib = ibkr or newest(paths.IBKR_POSITIONS, "*.json")
    report["holdings_inputs"] = {
        "fidelity": {"file": fid.name if fid else None, "age_days": _age_days(fid)},
        "ibkr": {"file": ib.name if ib else None, "age_days": _age_days(ib)},
    }
    hs = meta = None
    if fid:
        hs = H.merge(H.from_fidelity(fid) + (H.from_ibkr_json(ib) if ib else []))
        meta = {"fidelity": fid.name, "ibkr": ib.name if ib else None}
    with_roster = [s for s in ss_snaps if ss_extract.roster_trusted(s)]
    rendered: dict[str, Any] = {}
    if with_roster:
        latest = with_roster[-1]
        diff = (
            ss_checks.diff_rosters(with_roster[-2], latest)
            if len(with_roster) > 1
            else None
        )
        cmp = H.compare_to_roster(hs, latest["roster"]["rows"]) if hs else None
        from .cli import _status

        rendered["ss"] = render.write_ss_page(
            render.render_ss_page(latest, diff, cmp, meta, _status())
        )
        rendered["ss_as_of"] = latest.get("published_at")
    text, s31 = render_etf.render(ps, wk, ch, a10, hs, meta)
    paths.GEN_DIR.mkdir(parents=True, exist_ok=True)
    (paths.GEN_DIR / "ETF Books.md").write_text(text)
    (paths.PROD / "s31_ps_vs_ep.json").write_text(
        json.dumps(s31, indent=2, default=str) + "\n"
    )
    rendered["etf"] = str(paths.GEN_DIR / "ETF Books.md")
    report["steps"]["render"] = rendered

    # 6 — staleness: input newer than output?
    stale: list[str] = []
    latest_snap: dict[str, str | None] = {}
    for stream, mailbox in MAILBOXES.items():
        snaps = ss_snaps if stream == "ss" else streams.load_snapshots(stream)
        last_pub = snaps[-1].get("published_at") if snaps else None
        latest_snap[stream] = last_pub
        newest_mail = _newest_eml_stamp(mailbox)
        if newest_mail and last_pub and newest_mail[:10] > last_pub[:10]:
            stale.append(
                f"{stream}: mail {newest_mail} newer than latest snapshot {last_pub}"
            )
    no_roster = [s["feed_item_id"] for s in ss_snaps if not s.get("roster")]
    if no_roster:
        stale.append(
            f"ss: {len(no_roster)} snapshot(s) without roster: {', '.join(no_roster)}"
        )
    if with_roster and ss_snaps and with_roster[-1] is not ss_snaps[-1]:
        stale.append(
            f"ss page rendered from {with_roster[-1]['feed_item_id']}, "
            f"not the latest snapshot {ss_snaps[-1]['feed_item_id']}"
        )
    for name, p in (("fidelity", fid), ("ibkr", ib)):
        age = _age_days(p)
        if p is None:
            stale.append(f"{name}: no export found")
        elif age is not None and age > HOLDINGS_STALE_DAYS:
            stale.append(f"{name}: {p.name} is {age} days old")
    report["latest_snapshot"] = latest_snap
    report["stale"] = stale

    # 7 — the bell: new vs standing failures
    state = load_state()
    known = list(state.get("failing", []))
    current = ss_failing + etf_failing
    report["failures"] = split_failures(current, known)
    report["unkeyed"] = {
        "ss": len(list((paths.SNAPSHOTS_SS / "_unkeyed").glob("*.json"))),
    }
    report["seconds"] = round(time.time() - t0, 1)

    save_state(
        {"ran_at": report["ran_at"], "failing": current, "latest_snapshot": latest_snap}
    )
    with db.connect() as con:
        db.record_run(
            con,
            "refresh",
            {
                "stale": stale,
                "failures": report["failures"],
                "seconds": report["seconds"],
            },
        )
    return report


def format_report(r: dict[str, Any]) -> str:
    lines = [f"spine refresh — {r['ran_at']} ({r['seconds']}s)"]
    mail = r["steps"]["mail"]
    if mail.get("skipped"):
        lines.append("mail      skipped (--no-mail)")
    elif "error" in mail:
        lines.append(f"mail      ERROR {mail['error']}")
    else:
        parts = [f"{mb} +{v['new']} ({v['after']})" + (" ERR" if "error" in v else "")
                 for mb, v in mail.items()]  # fmt: skip
        lines.append("mail      " + " · ".join(parts))
    ex = r["steps"]["extract"]
    lines.append("extract   " + " · ".join(
        f"{k} {v.get('written', 0)}" + (f" unkeyed {v['unkeyed']}" if v.get("unkeyed") else "")
        for k, v in ex.items()))  # fmt: skip
    ck = r["steps"]["check"]
    etf_bits = [
        f"{k} {'ok' if not v['n_failures'] else str(v['n_failures']) + ' disagree'}"
        for k, v in ck["etf"].items()
    ]
    lines.append(
        f"check     ss {ck['ss']['all_pass']}/{ck['ss']['checked']} pass · "
        + " · ".join(etf_bits)
    )
    rd = r["steps"]["render"]
    lines.append(f"render    SS Stocks.md as of {rd.get('ss_as_of')} · ETF Books.md")
    hi = r["holdings_inputs"]
    lines.append(
        f"holdings  Fidelity {hi['fidelity']['file']} ({hi['fidelity']['age_days']} d) · "
        f"IBKR {hi['ibkr']['file']} ({hi['ibkr']['age_days']} d)"
    )
    lines.append(
        "latest    " + " · ".join(f"{k} {v}" for k, v in r["latest_snapshot"].items())
    )
    f = r["failures"]
    if f["new"]:
        lines.append(
            f"NEW       failing checks since last refresh: {', '.join(f['new'])}"
        )
    else:
        lines.append("new       no new failing checks")
    if f["standing"]:
        groups: dict[str, int] = {}
        for x in f["standing"]:
            g = x.split(":", 1)[0] if ":" in x else "ss"
            groups[g] = groups.get(g, 0) + 1
        lines.append(
            "standing  "
            + " · ".join(f"{g} {n}" for g, n in groups.items())
            + " known disagreements (ids: --json, check, check-etf)"
        )
    if f["cleared"]:
        lines.append(f"cleared   {', '.join(f['cleared'])}")
    if r["stale"]:
        lines.append("STALE     " + "\n          ".join(r["stale"]))
    else:
        lines.append("stale     nothing")
    if r["unkeyed"]["ss"]:
        lines.append(f"unkeyed   ss {r['unkeyed']['ss']} (snapshots/ss/_unkeyed/)")
    return "\n".join(lines)
