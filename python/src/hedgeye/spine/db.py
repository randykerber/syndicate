"""SQLite — `load`: snapshot JSON files -> tables. Idempotent on feed_item_id.

Decision §4-3: a few fixed indexed columns plus a JSON `payload`; promote a key to a
column only when a cluster of queries earns it. `events` is the generic spine table;
`ss_snapshot` / `ss_roster_row` are the SS slice's first promoted projections.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from . import paths
from .aliases import canon, kind

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id            TEXT PRIMARY KEY,          -- <stream>:<feed_item_id>:<event_type>:<instrument>
    ts            TEXT NOT NULL,             -- publication time (ISO), arrival as fallback
    stream        TEXT NOT NULL,
    event_type    TEXT NOT NULL,
    instrument    TEXT,
    provenance    TEXT NOT NULL,             -- raw file the event came from
    confidence    REAL,
    payload       TEXT NOT NULL CHECK (json_valid(payload))
);
CREATE INDEX IF NOT EXISTS ix_events_ts ON events(ts);
CREATE INDEX IF NOT EXISTS ix_events_instrument ON events(instrument, ts);
CREATE INDEX IF NOT EXISTS ix_events_type ON events(stream, event_type, ts);

CREATE TABLE IF NOT EXISTS ss_snapshot (
    feed_item_id   TEXT PRIMARY KEY,
    published_at   TEXT,
    arrived_at     TEXT,
    message_id     TEXT,
    subject_count  INTEGER,
    subject_added  INTEGER,
    subject_removed INTEGER,
    roster_rows    INTEGER,
    has_roster     INTEGER NOT NULL,
    confidence     REAL,
    all_pass       INTEGER,
    chart_status   TEXT,
    source_path    TEXT,
    payload        TEXT NOT NULL CHECK (json_valid(payload))
);
CREATE INDEX IF NOT EXISTS ix_ss_snapshot_pub ON ss_snapshot(published_at);

CREATE TABLE IF NOT EXISTS ss_roster_row (
    feed_item_id     TEXT NOT NULL,
    ticker           TEXT NOT NULL,             -- canonical (ticker-aliases.json)
    ticker_native    TEXT,                      -- as printed in the image
    ticker_kind      TEXT,                      -- alias | correction | NULL
    days_on          INTEGER,
    signal_date      TEXT,
    entry_price      REAL,
    recent_price     REAL,
    pct_since_signal REAL,
    sector           TEXT,
    analyst          TEXT,
    best_idea_rank   TEXT,
    rank_kind        TEXT,
    PRIMARY KEY (feed_item_id, ticker)
);
CREATE INDEX IF NOT EXISTS ix_ss_roster_ticker ON ss_roster_row(ticker, feed_item_id);

CREATE TABLE IF NOT EXISTS roster_row (
    stream         TEXT NOT NULL,
    feed_item_id   TEXT NOT NULL,
    published_at   TEXT,
    ticker         TEXT NOT NULL,             -- canonical
    ticker_native  TEXT,
    side           TEXT NOT NULL,             -- long | short
    rank           INTEGER,
    payload        TEXT NOT NULL CHECK (json_valid(payload)),
    PRIMARY KEY (stream, feed_item_id, ticker, side)
);
CREATE INDEX IF NOT EXISTS ix_roster_row_ticker ON roster_row(ticker, stream, published_at);
CREATE INDEX IF NOT EXISTS ix_roster_row_pub ON roster_row(stream, published_at);

CREATE TABLE IF NOT EXISTS stream_snapshot (
    stream         TEXT NOT NULL,
    feed_item_id   TEXT NOT NULL,
    published_at   TEXT,
    subject        TEXT,
    n_rows         INTEGER,
    checks_pass    INTEGER,                   -- 1 all pass, 0 a failure, NULL none applicable
    exceptions     TEXT,
    payload        TEXT NOT NULL CHECK (json_valid(payload)),
    PRIMARY KEY (stream, feed_item_id)
);

CREATE TABLE IF NOT EXISTS runs (
    ran_at   TEXT NOT NULL,
    command  TEXT NOT NULL,
    summary  TEXT NOT NULL CHECK (json_valid(summary))
);
"""


def connect(path: Path = paths.DB_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def load_snapshots(
    snaps: list[dict[str, Any]], con: sqlite3.Connection
) -> dict[str, Any]:
    n_snap = n_rows = n_events = 0
    for s in snaps:
        fid = s["feed_item_id"]
        sp = s["subject_parsed"]
        ck = s.get("checks") or {}
        roster = s.get("roster")
        ts = s.get("published_at") or s.get("arrived_at")
        con.execute(
            """INSERT OR REPLACE INTO ss_snapshot VALUES
               (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                fid, ts, s.get("arrived_at"), s.get("message_id"),
                sp.get("count"), sp.get("added"), sp.get("removed"),
                len(roster["rows"]) if roster else None, 1 if roster else 0,
                ck.get("confidence"), None if not ck else int(bool(ck.get("all_pass"))),
                ((s.get("chart") or {}).get("fetch") or {}).get("status"),
                s.get("source_path"), json.dumps(s, default=str),
            ),
        )  # fmt: skip
        n_snap += 1
        con.execute("DELETE FROM ss_roster_row WHERE feed_item_id = ?", (fid,))
        if roster:
            for r in roster["rows"]:
                con.execute(
                    "INSERT OR REPLACE INTO ss_roster_row VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        fid, canon(r["ticker"]), r["ticker"].upper(), kind(r["ticker"]), r.get("days_on"), r.get("signal_date"),
                        r.get("entry_price"), r.get("recent_price"),
                        r.get("pct_since_signal"), r.get("sector"), r.get("analyst"),
                        r.get("best_idea_rank"), r.get("rank_kind"),
                    ),
                )  # fmt: skip
                n_rows += 1
        # RosterChange events from the publisher's own text (independent of the image)
        conf = ck.get("confidence")
        for action, key in (("add", "added"), ("remove", "removed")):
            for t in s["changes"].get(key) or []:
                eid = f"ss-stocks:{fid}:RosterChange:{canon(t)}:{action}"
                con.execute(
                    "INSERT OR REPLACE INTO events VALUES (?,?,?,?,?,?,?,?)",
                    (
                        eid, ts, "ss-stocks", "RosterChange", canon(t),
                        s["source_path"], conf,
                        json.dumps({"action": action, "portfolio": "ss-stocks",
                                    "feed_item_id": fid, "stated_by": "email-text", "ticker_native": t.upper(), "ticker_kind": kind(t)}),
                    ),
                )  # fmt: skip
                n_events += 1
    con.commit()
    return {"snapshots": n_snap, "roster_rows": n_rows, "events": n_events}


def record_run(con: sqlite3.Connection, command: str, summary: dict[str, Any]) -> None:
    from datetime import datetime, timezone

    con.execute(
        "INSERT INTO runs VALUES (?,?,?)",
        (datetime.now(timezone.utc).isoformat(timespec="seconds"), command,
         json.dumps(summary, default=str)),
    )  # fmt: skip
    con.commit()


def latest_snapshot_id(con: sqlite3.Connection) -> str | None:
    row = con.execute(
        "SELECT feed_item_id FROM ss_snapshot WHERE has_roster = 1 "
        "ORDER BY published_at DESC LIMIT 1"
    ).fetchone()
    return row[0] if row else None


def ticker_history(con: sqlite3.Connection, ticker: str) -> dict[str, Any]:
    t = canon(ticker)
    latest = latest_snapshot_id(con)
    now = None
    if latest:
        now = con.execute(
            "SELECT r.*, s.published_at FROM ss_roster_row r JOIN ss_snapshot s USING "
            "(feed_item_id) WHERE r.feed_item_id = ? AND r.ticker = ?",
            (latest, t),
        ).fetchone()
    events = con.execute(
        "SELECT ts, payload->>'$.action' AS action, provenance FROM events "
        "WHERE stream='ss-stocks' AND instrument=? ORDER BY ts",
        (t,),
    ).fetchall()
    presence = con.execute(
        "SELECT MIN(s.published_at) AS first_seen, MAX(s.published_at) AS last_seen, "
        "COUNT(*) AS snapshots FROM ss_roster_row r JOIN ss_snapshot s USING (feed_item_id) "
        "WHERE r.ticker = ?",
        (t,),
    ).fetchone()
    return {
        "ticker": t,
        "latest_snapshot": latest,
        "in_current_roster": now is not None,
        "current": dict(now) if now else None,
        "events": [dict(e) for e in events],
        "presence": dict(presence) if presence else None,
    }


def load_stream(
    stream: str, snaps: list[dict[str, Any]], con: sqlite3.Connection
) -> dict[str, Any]:
    """ETF streams -> stream_snapshot + roster_row + events (PortfolioTransaction /
    RosterChange from the publisher's own text). Idempotent per feed_item_id."""
    n_rows = n_events = 0
    con.execute("DELETE FROM roster_row WHERE stream = ?", (stream,))
    con.execute("DELETE FROM events WHERE stream = ?", (stream,))
    for s in snaps:
        fid, ts = s["feed_item_id"], s.get("published_at") or s.get("arrived_at")
        ck = s.get("checks") or {}
        passes = [
            v.get("pass")
            for v in ck.values()
            if isinstance(v, dict)
            and v.get("pass") is not None
            and not v.get("pass_with_lag1")
        ]
        rows: list[tuple[str, str, dict[str, Any]]] = []
        if stream in ("ps-daily", "any10"):
            rows = [("long", r["ticker"], r) for r in s.get("roster", [])]
        elif stream == "ep-weekly":
            rows = [("long", r["ticker"], r) for r in s.get("long", [])] + [
                ("short", r["ticker"], r) for r in s.get("short", [])
            ]
        for side, t, r in rows:
            con.execute(
                "INSERT OR REPLACE INTO roster_row VALUES (?,?,?,?,?,?,?,?)",
                (
                    stream,
                    fid,
                    ts,
                    canon(t),
                    t.upper(),
                    side,
                    r.get("rank"),
                    json.dumps(r, default=str),
                ),
            )
            n_rows += 1
        if stream == "ps-daily":
            for i, t in enumerate(s.get("transactions", [])):
                eid = f"ps-daily:{fid}:PortfolioTransaction:{canon(t['ticker'])}:{i}"
                con.execute(
                    "INSERT OR REPLACE INTO events VALUES (?,?,?,?,?,?,?,?)",
                    (eid, ts, stream, "PortfolioTransaction", canon(t["ticker"]), s["source_path"], None,
                     json.dumps({"action": t["action"], "bps": t["bps"], "portfolio": "ps", "feed_item_id": fid,
                                 "ticker_native": t["ticker"].upper(), "sentence": t["sentence"]})),
                )  # fmt: skip
                n_events += 1
        elif stream in ("ep-changes", "any10"):
            portfolio = "etf-pro" if stream == "ep-changes" else "any10"
            for i, c in enumerate(s.get("changes", [])):
                eid = f"{stream}:{fid}:RosterChange:{canon(c['ticker'])}:{c['action']}:{i}"
                con.execute(
                    "INSERT OR REPLACE INTO events VALUES (?,?,?,?,?,?,?,?)",
                    (eid, ts, stream, "RosterChange", canon(c["ticker"]), s["source_path"], None,
                     json.dumps({"action": c["action"], "side": c.get("side"), "portfolio": portfolio,
                                 "feed_item_id": fid, "ticker_native": c["ticker"].upper(),
                                 "name": c.get("name"), "range": c.get("range")})),
                )  # fmt: skip
                n_events += 1
        con.execute(
            "INSERT OR REPLACE INTO stream_snapshot VALUES (?,?,?,?,?,?,?,?)",
            (stream, fid, ts, s.get("subject"), len(rows),
             None if not passes else int(all(passes)), json.dumps(s.get("exceptions", [])),
             json.dumps(s, default=str)),
        )  # fmt: skip
    con.commit()
    return {
        "stream": stream,
        "snapshots": len(snaps),
        "roster_rows": n_rows,
        "events": n_events,
    }


def ticker_books(con: sqlite3.Connection, ticker: str) -> dict[str, Any]:
    """Current membership + history of a ticker across the ETF books."""
    t = canon(ticker)
    out: dict[str, Any] = {"ticker": t}
    for stream in ("ps-daily", "ep-weekly", "any10"):
        latest = con.execute(
            "SELECT feed_item_id, published_at FROM stream_snapshot WHERE stream=? AND n_rows>0 "
            "ORDER BY published_at DESC LIMIT 1", (stream,)).fetchone()  # fmt: skip
        if not latest:
            continue
        row = con.execute(
            "SELECT side, rank, payload FROM roster_row WHERE stream=? AND feed_item_id=? AND ticker=?",
            (stream, latest[0], t)).fetchone()  # fmt: skip
        pres = con.execute(
            "SELECT MIN(published_at), MAX(published_at), COUNT(*) FROM roster_row WHERE stream=? AND ticker=?",
            (stream, t)).fetchone()  # fmt: skip
        out[stream] = {
            "as_of": latest[1],
            "in": row is not None,
            "side": row[0] if row else None,
            "rank": row[1] if row else None,
            "detail": json.loads(row[2]) if row else None,
            "first_seen": pres[0], "last_seen": pres[1], "snapshots": pres[2],
        }  # fmt: skip
    out["events"] = [dict(r) for r in con.execute(
        "SELECT ts, stream, event_type, payload->>'$.action' AS action, payload->>'$.side' AS side, "
        "payload->>'$.bps' AS bps FROM events WHERE instrument=? AND stream != 'ss-stocks' ORDER BY ts", (t,))]  # fmt: skip
    return out
