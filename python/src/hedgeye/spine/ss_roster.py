"""Signal Strength Stocks — `read-rosters`: the PNG table -> structured rows.

The roster exists nowhere but the image, so this is the one LLM step in the slice
(decision §4-6: Sonnet 5, structured outputs, prompt version recorded on every result).
The image alone is iffy (Randy); `ss_checks.py` cross-checks every roster against the
subject count and the Added/Removed text before anything downstream trusts it.
"""

from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

MODEL = "claude-sonnet-5"
PROMPT_VERSION = "ss-roster-v1"

_PROMPT = """This image is Hedgeye's "Signal Strength Stocks" table. Transcribe EVERY \
data row exactly as printed, top to bottom, one object per row. Do not skip, merge, \
reorder, or invent rows. Column meanings (header wording varies between issues):
- days_on: integer in the first column
- ticker: the symbol (uppercase, as printed)
- signal_date: as printed, M/D/YYYY
- entry_price: "Entry Price" or "Prior Close of Signal Price" column, number
- recent_price: "Recent Price" or "Last Close Price" column, number
- pct_since_signal: the % column as a number (negative if red/minus), no % sign
- sector: as printed
- analyst: full name as printed
- best_idea_rank: exactly as printed — a rank like "3/6", or "Bench", or "KM Signal"
Also report column_headers (the header labels you saw, left to right) and \
row_count (how many data rows you transcribed). If any cell is unreadable, put null \
and add a note in notes."""


class RosterRow(BaseModel):
    days_on: int | None
    ticker: str
    signal_date: str | None
    entry_price: float | None
    recent_price: float | None
    pct_since_signal: float | None
    sector: str | None
    analyst: str | None
    best_idea_rank: str | None


class Roster(BaseModel):
    column_headers: list[str]
    row_count: int
    rows: list[RosterRow]
    notes: list[str] = Field(default_factory=list)


def rank_kind(rank: str | None) -> str:
    """`n/m` -> "ranked"; Bench; KM Signal; else unknown."""
    if not rank:
        return "unknown"
    r = rank.strip().lower()
    if r == "bench":
        return "bench"
    if r.startswith("km"):
        return "km-signal"
    if "/" in r:
        return "ranked"
    return "unknown"


def read_roster_image(png: Path) -> tuple[Roster, dict[str, Any]]:
    """One image -> Roster, plus provenance for the snapshot."""
    import anthropic

    client = anthropic.Anthropic()
    data = base64.standard_b64encode(png.read_bytes()).decode("utf-8")
    response = client.messages.parse(
        model=MODEL,
        max_tokens=16000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": data,
                        },
                    },
                    {"type": "text", "text": _PROMPT},
                ],
            }
        ],
        output_format=Roster,
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"model refused: {response.stop_details}")
    roster = response.parsed_output
    if roster is None:
        raise RuntimeError("no parsed output")
    provenance = {
        "model": MODEL,
        "prompt_version": PROMPT_VERSION,
        "image": str(png),
        "read_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
        "stop_reason": response.stop_reason,
    }
    return roster, provenance


def read_rosters(
    snapshots: list[dict[str, Any]],
    write: "callable[[dict[str, Any]], None]",
    force: bool = False,
    limit: int | None = None,
) -> dict[str, Any]:
    """Fill `roster` on every snapshot that has an image and no roster yet."""
    done = skipped = failed = 0
    for snap in snapshots:
        if limit is not None and done >= limit:
            break
        chart = snap.get("chart") or {}
        local = chart.get("local_path")
        if not local or not Path(local).exists():
            skipped += 1
            continue
        if snap.get("roster") and not force:
            skipped += 1
            continue
        try:
            roster, prov = read_roster_image(Path(local))
        except Exception as e:  # noqa: BLE001 — record, never hide
            snap.setdefault("exceptions", []).append(f"roster read failed: {e}")
            write(snap)
            failed += 1
            continue
        rows = [r.model_dump() for r in roster.rows]
        for r in rows:
            r["rank_kind"] = rank_kind(r["best_idea_rank"])
        snap["roster"] = {
            "column_headers": roster.column_headers,
            "row_count_reported": roster.row_count,
            "rows": rows,
            "notes": roster.notes,
        }
        snap["roster_source"] = prov
        write(snap)
        done += 1
        print(
            f"  {snap['feed_item_id']}  {snap.get('published_at')}  "
            f"rows={len(rows)}  subject={snap['subject_parsed'].get('count')}"
        )
    return {"read": done, "skipped": skipped, "failed": failed}


def merge_reads_from_dir(
    snapshots: list[dict[str, Any]],
    read_dir: Path,
    write: "callable[[dict[str, Any]], None]",
    reader: str,
    force: bool = False,
) -> dict[str, Any]:
    """Fold hand- or agent-produced roster files into snapshots.

    Each `<feed_item_id>.json` in `read_dir` must satisfy the `Roster` schema (the same
    one the API path uses); it is validated, tagged with `reader` as provenance, and
    written into the matching snapshot. This is the subscription path: a Claude Code
    session or subagent reads the PNG with its own vision and writes the file.
    """
    by_id = {s["feed_item_id"]: s for s in snapshots}
    merged = skipped = invalid = unmatched = 0
    problems: list[dict[str, Any]] = []
    for f in sorted(read_dir.glob("*.json")):
        fid = f.stem
        snap = by_id.get(fid)
        if snap is None:
            unmatched += 1
            problems.append({"file": f.name, "problem": "no snapshot with that id"})
            continue
        if snap.get("roster") and not force:
            skipped += 1
            continue
        try:
            roster = Roster.model_validate(json.loads(f.read_text()))
        except Exception as e:  # noqa: BLE001 — report, never hide
            invalid += 1
            problems.append({"file": f.name, "problem": str(e)[:300]})
            continue
        rows = [r.model_dump() for r in roster.rows]
        for r in rows:
            r["rank_kind"] = rank_kind(r["best_idea_rank"])
        snap["roster"] = {
            "column_headers": roster.column_headers,
            "row_count_reported": roster.row_count,
            "rows": rows,
            "notes": roster.notes,
        }
        snap["roster_source"] = {
            "model": reader,
            "prompt_version": "cc-vision-read-v1",
            "image": (snap.get("chart") or {}).get("local_path"),
            "read_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "read_file": str(f),
        }
        write(snap)
        merged += 1
    return {"merged": merged, "skipped_has_roster": skipped, "invalid": invalid,
            "unmatched": unmatched, "problems": problems}  # fmt: skip


def dump_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, default=str) + "\n"
