"""Signal Strength Stocks — `extract`: emails -> one JSON snapshot per message.

What an SS email carries (surveyed 2026-09-13, 136 messages):
- subject: `Signal Strength Stocks: 61 Stocks (3 Added, 12 Removed)` — or `(No changes)`
- text body: `Added: META, MRVL, AAPL` / `Removed: DGX, ...` lines (absent on no-change days)
- the full roster **only as a PNG** on a public CloudFront URL (three size variants;
  the email links `original`, the sharpest). Hedgeye may replace the image after sending
  under the same chart id with a new filename (seen 2026-09-02: `sss_9_2.png` -> 403,
  `sss_fix_micc.png` on the feed page); `overrides.json` in the chart folder maps
  feed_item_id -> replacement URL, hand-maintained.

Nothing here interprets the image. That is `ss_roster.py`, a separate hand-run step.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from . import paths
from .eml import read_eml

# Grammar drift seen in the corpus: "Signal Strength Stocks Update: 59 Stocks (...)"
# (Apr 2026), "Signal Strength Stocks: 71 Stocks" (no change clause, 2026-05-26),
# "(No changes)" / "(no changes)", and a lowercase "signal".
_SUBJECT = re.compile(
    r"Signal Strength Stocks(?P<update>\s+Update)?:\s*(?P<count>\d+)\s*Stocks\s*"
    r"(?:\((?:(?P<added>\d+)\s*Added,\s*(?P<removed>\d+)\s*Removed"
    r"|(?P<nochange>no changes))\))?\s*$",
    re.I,
)
_ADDED = re.compile(r"^\s*Added:\s*(?P<list>.*?)\s*$", re.I | re.M)
_REMOVED = re.compile(r"^\s*Removed:\s*(?P<list>.*?)\s*$", re.I | re.M)
_CHART = re.compile(
    r'src="(?P<url>https://d1yhils6iwh5l5\.cloudfront\.net/charts/resized/'
    r"(?P<chart_id>\d+)/(?P<variant>\w+)/(?P<filename>[^\"?]+))"
)
_TICKER = re.compile(r"^[A-Z][A-Z0-9.\-]{0,7}$")


def parse_subject(subject: str) -> dict[str, Any]:
    m = _SUBJECT.search(subject)
    if not m:
        return {"recognized": False}
    has_counts = m.group("added") is not None
    return {
        "recognized": True,
        "count": int(m.group("count")),
        "added": int(m.group("added")) if has_counts else 0,
        "removed": int(m.group("removed")) if has_counts else 0,
        "no_change_wording": bool(m.group("nochange")),
        "counts_absent": not has_counts and not m.group("nochange"),
        "update_wording": bool(m.group("update")),
    }


def _ticker_list(raw: str) -> list[str]:
    # An empty list is sometimes followed on the same line by "(VIEW LARGER IMAGE <url>)"
    raw = raw.split("(", 1)[0]
    if not raw or raw.strip().lower() in {"none", "n/a", "-", "—"}:
        return []
    out: list[str] = []
    for tok in re.split(r"[,\s]+", raw.strip()):
        tok = tok.strip().strip(".;")
        if tok and _TICKER.match(tok):
            out.append(tok)
    return out


def parse_changes(text: str) -> dict[str, Any]:
    a = _ADDED.search(text)
    r = _REMOVED.search(text)
    return {
        "added": _ticker_list(a.group("list")) if a else None,
        "removed": _ticker_list(r.group("list")) if r else None,
        "added_line_present": a is not None,
        "removed_line_present": r is not None,
    }


def find_chart(html: str) -> dict[str, Any] | None:
    m = _CHART.search(html)
    if not m:
        return None
    return {
        "url": m.group("url"),
        "chart_id": m.group("chart_id"),
        "variant": m.group("variant"),
        "filename": m.group("filename"),
    }


def load_overrides() -> dict[str, str]:
    p = paths.CHART_OVERRIDES_SS
    if not p.exists():
        return {}
    data = json.loads(p.read_text())
    return {str(k): str(v) for k, v in data.get("by_feed_item_id", {}).items()}


def fetch_chart(url: str, dest: Path) -> dict[str, Any]:
    """Download once; a file already on disk is never re-fetched."""
    if dest.exists() and dest.stat().st_size > 0:
        return {"status": "cached", "http_status": None, "bytes": dest.stat().st_size}
    req = urllib.request.Request(url, headers={"User-Agent": "hedgeye-spine/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        return {"status": "http_error", "http_status": e.code, "bytes": 0}
    except (urllib.error.URLError, TimeoutError) as e:
        return {"status": "network_error", "http_status": None, "error": str(e)}
    dest.write_bytes(data)
    return {"status": "fetched", "http_status": 200, "bytes": len(data)}


def snapshot_path(feed_item_id: str) -> Path:
    return paths.SNAPSHOTS_SS / f"{feed_item_id}.json"


def build_snapshot(rec: dict[str, Any], mailbox: str) -> dict[str, Any]:
    ids = rec["feed_item_ids"]
    subject = parse_subject(rec["subject"])
    changes = parse_changes(rec["text"] or rec["html"])
    chart = find_chart(rec["html"])
    return {
        "stream": "ss-stocks",
        "feed_item_id": ids[0] if len(ids) == 1 else None,
        "feed_item_ids_seen": ids,
        "mailbox": mailbox,
        "source_path": rec["source_path"],
        "message_id": rec["message_id"],
        "in_reply_to": rec["in_reply_to"],
        "references": rec["references"],
        "arrived_at": rec["arrived_at"],
        "published_stamp": rec["published_stamp"],
        "published_at": rec["published_at"],
        "subject": rec["subject"],
        "subject_parsed": subject,
        "changes": changes,
        "chart": chart,
        "roster": None,
        "roster_source": None,
        "checks": None,
        "exceptions": [],
    }


def extract(mailbox: str = paths.SS_MAILBOX, fetch: bool = True) -> dict[str, Any]:
    """Every `.eml` in the mailbox -> `snapshots/ss/<feed_item_id>.json`.

    Rerunnable: an existing snapshot keeps its `roster`/`roster_source`/`checks`; only
    the email-derived fields are refreshed. Messages without exactly one feed id, or
    whose subject is not the SS grammar, land in `snapshots/ss/_unkeyed/`.
    """
    paths.ensure_dirs()
    unkeyed_dir = paths.SNAPSHOTS_SS / "_unkeyed"
    unkeyed_dir.mkdir(exist_ok=True)
    overrides = load_overrides()
    root = paths.RAW_MAIL
    summary: dict[str, Any] = {
        "messages": 0, "written": 0, "unkeyed": 0, "duplicates": 0,
        "charts_fetched": 0, "charts_cached": 0, "charts_failed": 0,
        "overrides_applied": 0, "failed": [],
    }  # fmt: skip

    for eml in sorted((root / mailbox).glob("*.eml")):
        summary["messages"] += 1
        rec = read_eml(eml, root)
        snap = build_snapshot(rec, mailbox)
        fid = snap["feed_item_id"]

        if fid is None or not snap["subject_parsed"]["recognized"]:
            snap["exceptions"].append(
                "unkeyed: no single feed_item_id"
                if fid is None
                else "subject not SS grammar"
            )
            (unkeyed_dir / (eml.stem + ".json")).write_text(_dump(snap))
            summary["unkeyed"] += 1
            continue

        out = snapshot_path(fid)
        if out.exists():
            prev = json.loads(out.read_text())
            if prev.get("message_id") and prev["message_id"] != snap["message_id"]:
                # publisher double-send: same Work, second Message-ID — keep the first
                prev.setdefault("duplicate_message_ids", [])
                if snap["message_id"] not in prev["duplicate_message_ids"]:
                    prev["duplicate_message_ids"].append(snap["message_id"])
                    out.write_text(_dump(prev))
                summary["duplicates"] += 1
                continue
            for k in ("roster", "roster_source", "checks"):
                snap[k] = prev.get(k)
            snap["exceptions"] = prev.get("exceptions", [])

        if snap["chart"] is not None:
            chart = snap["chart"]
            url = chart["url"]
            if fid in overrides:
                url = overrides[fid]
                chart["override_url"] = url
                summary["overrides_applied"] += 1
            local = paths.RAW_CHARTS_SS / f"{fid}__{Path(url).name}"
            chart["local_path"] = str(local)
            if fetch:
                r = fetch_chart(url, local)
                chart["fetch"] = r
                key = {"fetched": "charts_fetched", "cached": "charts_cached"}.get(
                    r["status"], "charts_failed"
                )
                summary[key] += 1
                if key == "charts_failed":
                    summary["failed"].append({"feed_item_id": fid, **r})
                    if "chart unavailable" not in snap["exceptions"]:
                        snap["exceptions"].append("chart unavailable")
        else:
            snap["exceptions"].append("no chart image in html")

        out.write_text(_dump(snap))
        summary["written"] += 1
    return summary


def _dump(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, default=str) + "\n"


def load_snapshots() -> list[dict[str, Any]]:
    """All keyed snapshots, ordered by publication time (arrival as fallback)."""
    snaps = [json.loads(p.read_text()) for p in paths.SNAPSHOTS_SS.glob("*.json")]
    snaps.sort(key=lambda s: (s.get("published_at") or s.get("arrived_at") or ""))
    return snaps
