"""Stream registry + the generic `extract <stream>`: mailbox -> one snapshot per email.

Every snapshot shares the same envelope as the Signal Strength ones (identity, timing,
subject, provenance, checks, exceptions); the stream's parser fills the payload. Keyed by
Hedgeye's own `feed_items/<id>`; messages without exactly one id go to `_unkeyed/`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from . import parse_any10, parse_ep, parse_ps, paths
from .eml import read_eml


@dataclass(frozen=True)
class Stream:
    stream_id: str
    mailbox: str
    parse: Callable[[dict[str, Any], str], dict[str, Any]]
    note: str = ""


def _ps(rec: dict[str, Any], path: str) -> dict[str, Any]:
    return parse_ps.parse(rec)


def _ep_changes(rec: dict[str, Any], path: str) -> dict[str, Any]:
    return parse_ep.parse_change_email(rec)


def _ep_weekly(rec: dict[str, Any], path: str) -> dict[str, Any]:
    return parse_ep.parse_weekly_email(rec, path)


def _any10(rec: dict[str, Any], path: str) -> dict[str, Any]:
    return parse_any10.parse(rec)


STREAMS: dict[str, Stream] = {
    "ps-daily": Stream("ps-daily", "HE-PS", _ps, "Portfolio Solutions re-rank (long-only; cash row FDRXX)"),
    "ep-changes": Stream("ep-changes", "HE-ETF-Pro", _ep_changes, "ETF Pro Plus real-time adds/removes, long and short"),
    "ep-weekly": Stream("ep-weekly", "ETF-weekly", _ep_weekly, "ETF Pro Plus weekly roster with trend ranges"),
    "any10": Stream("any10", "Anywhere-10", _any10, "10 ETF Go-Anywhere portfolio"),
}  # fmt: skip


def snapshot_path(stream: str, fid: str) -> Path:
    return paths.snapshots_dir(stream) / f"{fid}.json"


def _dump(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, default=str) + "\n"


def extract(stream_id: str) -> dict[str, Any]:
    st = STREAMS[stream_id]
    out_dir = paths.snapshots_dir(stream_id)
    unkeyed_dir = out_dir / "_unkeyed"
    unkeyed_dir.mkdir(parents=True, exist_ok=True)
    root = paths.RAW_MAIL
    summary: dict[str, Any] = {"stream": stream_id, "messages": 0, "written": 0, "unkeyed": 0,
                               "unrecognized": 0, "duplicates": 0, "with_exceptions": 0}  # fmt: skip
    for eml in sorted((root / st.mailbox).glob("*.eml")):
        summary["messages"] += 1
        rec = read_eml(eml, root)
        ids = rec["feed_item_ids"]
        fid = ids[0] if len(ids) == 1 else (max(ids, key=int) if ids else None)
        payload = st.parse(rec, str(eml))
        if len(ids) > 1:
            payload.setdefault("exceptions", []).append(
                f"{len(ids)} feed ids in message; keyed by the highest ({fid})"
            )
        snap: dict[str, Any] = {
            "stream": stream_id,
            "feed_item_id": fid,
            "feed_item_ids_seen": ids,
            "mailbox": st.mailbox,
            "source_path": rec["source_path"],
            "message_id": rec["message_id"],
            "in_reply_to": rec["in_reply_to"],
            "references": rec["references"],
            "arrived_at": rec["arrived_at"],
            "published_stamp": rec["published_stamp"],
            "published_at": rec["published_at"],
            "subject": rec["subject"],
            "checks": None,
        }
        snap.update(payload)
        snap.setdefault("exceptions", [])
        recognized = payload.get("subject_parsed", {}).get("recognized", True)
        if fid is None or not recognized:
            snap["exceptions"].append(
                "unkeyed: no single feed_item_id"
                if fid is None
                else "subject not in stream grammar"
            )
            (unkeyed_dir / (eml.stem + ".json")).write_text(_dump(snap))
            summary["unkeyed" if fid is None else "unrecognized"] += 1
            continue
        out = snapshot_path(stream_id, fid)
        if out.exists():
            prev = json.loads(out.read_text())
            if prev.get("message_id") and prev["message_id"] != snap["message_id"]:
                prev.setdefault("duplicate_message_ids", [])
                if snap["message_id"] not in prev["duplicate_message_ids"]:
                    prev["duplicate_message_ids"].append(snap["message_id"])
                    out.write_text(_dump(prev))
                summary["duplicates"] += 1
                continue
            if prev.get("checks") is not None:
                snap["checks"] = prev["checks"]
        if snap["exceptions"]:
            summary["with_exceptions"] += 1
        out.write_text(_dump(snap))
        summary["written"] += 1
    return summary


def load_snapshots(stream_id: str) -> list[dict[str, Any]]:
    d = paths.snapshots_dir(stream_id)
    snaps = [json.loads(p.read_text()) for p in d.glob("*.json")] if d.exists() else []
    snaps.sort(key=lambda s: (s.get("published_at") or s.get("arrived_at") or ""))
    return snaps
