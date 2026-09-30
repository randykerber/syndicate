"""Import an Apple Mail mailbox into the raw archive — keeping EVERY message.

Promoted from `scratch/mail-import/` on 2026-09-30 (decision rough-design-draft §4-4;
the scratch copy was gitignored and so absent on idlewood). Same behaviour and, above
all, the **same file names**, so the two Macs' archives merge by union:

    ~/d/downloads/hedgeye/raw/mail/<mailbox>/YYYY-MM-DD_HHMMSS_<msgid8>.eml

- date/time: the message's `Date` header, formatted in its own timezone
- msgid8: first 8 hex chars of SHA-256 of the full `Message-ID`, angle brackets included
  (verified against the archive 2026-09-30). Same-second duplicates stay representable;
  re-runs are idempotent (an existing name is never rewritten).

Nothing is collapsed, nothing skipped (EXCEPTIONS.md X-0): the archive is the observed
canonical layer. Hand-run:

    uv run python -m hedgeye.mail.importer HE-PS --limit 12
    uv run python -m hedgeye.mail.importer "HE-The Call" --account iCloud
"""

from __future__ import annotations

import argparse
import email
import hashlib
import shutil
import subprocess
import sys
import tempfile
from email import policy
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

from ..spine import paths

HERE = Path(__file__).resolve().parent
EXPORTER = HERE / "export_mailbox.applescript"
DEST_ROOT = paths.RAW_MAIL


def archive_name(message_id: str, date_header: str) -> str | None:
    """The archive file name for a message, or None if the headers are unusable."""
    mid = (message_id or "").strip()
    if not mid or not date_header:
        return None
    try:
        dt = parsedate_to_datetime(date_header)
    except (TypeError, ValueError):
        return None
    stamp = dt.strftime("%Y-%m-%d_%H%M%S")
    return f"{stamp}_{hashlib.sha256(mid.encode()).hexdigest()[:8]}.eml"


def _headers(path: Path) -> tuple[str, str]:
    with open(path, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)
    return (msg.get("Message-ID") or "", msg.get("Date") or "")


def export(account: str, mailbox: str, staging: Path, limit: int) -> str:
    r = subprocess.run(
        ["osascript", str(EXPORTER), account, mailbox, str(staging), str(limit)],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"exporter failed: {(r.stderr or r.stdout).strip()[-400:]}")
    return r.stdout.strip()


def import_mailbox(
    mailbox: str, account: str = "iCloud", limit: int = 0, dry_run: bool = False
) -> dict[str, Any]:
    """Export the newest `limit` messages (0 = all) and file the new ones."""
    dest = DEST_ROOT / mailbox
    dest.mkdir(parents=True, exist_ok=True)
    before = len(list(dest.glob("*.eml")))
    staging = Path(tempfile.mkdtemp(prefix="he-mail-"))
    out: dict[str, Any] = {
        "mailbox": mailbox, "exported": 0, "new": 0, "already": 0,
        "unreadable": 0, "before": before, "after": before, "problems": [],
    }  # fmt: skip
    try:
        out["exported"] = int(export(account, mailbox, staging, limit) or 0)
        for f in sorted(staging.glob("*.eml")):
            try:
                mid, date = _headers(f)
            except Exception as e:  # noqa: BLE001 — record, never hide
                out["unreadable"] += 1
                out["problems"].append(f"{f.name}: {e}")
                continue
            name = archive_name(mid, date)
            if name is None:
                out["unreadable"] += 1
                out["problems"].append(f"{f.name}: missing Message-ID or Date")
                continue
            target = dest / name
            if target.exists():
                out["already"] += 1
                continue
            if not dry_run:
                shutil.move(str(f), str(target))
            out["new"] += 1
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    out["after"] = len(list(dest.glob("*.eml")))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("mailbox")
    ap.add_argument("--account", default="iCloud")
    ap.add_argument("--limit", type=int, default=0, help="newest N (0 = all)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    print(f"exporting {a.account}/{a.mailbox} …", flush=True)
    r = import_mailbox(a.mailbox, a.account, a.limit, a.dry_run)
    print(
        f"  exported {r['exported']}, new {r['new']}, already {r['already']}, "
        f"unreadable {r['unreadable']}  → {r['after']} in archive"
    )
    for p in r["problems"]:
        print("  ⚠️ ", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
