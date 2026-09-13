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
    ticker           TEXT NOT NULL,
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
                    "INSERT OR REPLACE INTO ss_roster_row VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        fid, r["ticker"].upper(), r.get("days_on"), r.get("signal_date"),
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
                eid = f"ss-stocks:{fid}:RosterChange:{t.upper()}:{action}"
                con.execute(
                    "INSERT OR REPLACE INTO events VALUES (?,?,?,?,?,?,?,?)",
                    (
                        eid, ts, "ss-stocks", "RosterChange", t.upper(),
                        s["source_path"], conf,
                        json.dumps({"action": action, "portfolio": "ss-stocks",
                                    "feed_item_id": fid, "stated_by": "email-text"}),
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
    t = ticker.upper()
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
