"""A saved `.eml` -> a plain dict of what the spine needs.

Copied and trimmed from the closed Resolver prototype (`scratch/work-resolver/he/`):
RFC 2047 subjects, HTML-only messages, Hedgeye's publication stamp, and the
`feed_items/<id>` identifier hidden inside base64 click-tracking redirects.
"""

from __future__ import annotations

import base64
import email
import email.header
import email.utils
import re
from datetime import datetime
from email import policy
from email.message import EmailMessage
from pathlib import Path
from typing import Any

_PUBLISHED = re.compile(r"(\d{2}/\d{2}/\d{4})\s+(\d{1,2}:\d{2}\s*[AP]M)\s*([A-Z]{2,4})")
_FEED_ID = re.compile(r"app\.hedgeye\.com/feed_items/(\d+)")
_CLICK = re.compile(r"model2\.hedgeye\.com/click/[\d.]+/([A-Za-z0-9_\-=]+)")


def decode_subject(raw: str | None) -> str:
    if raw is None:
        return ""
    try:
        decoded = str(email.header.make_header(email.header.decode_header(raw)))
    except Exception:  # noqa: BLE001 — malformed headers are the supplier's problem
        decoded = raw
    return " ".join(decoded.split())


def _part_text(msg: EmailMessage, kind: str) -> str:
    body = msg.get_body((kind,))
    if body is None:
        return ""
    try:
        return body.get_content()
    except Exception:  # noqa: BLE001
        payload = body.get_payload(decode=True)
        return payload.decode("utf8", "replace") if isinstance(payload, bytes) else ""


def feed_ids(*texts: str) -> list[str]:
    """Every `feed_items/<id>` reachable, including through click-wrapped base64."""
    blob = " ".join(t for t in texts if t)
    found = set(_FEED_ID.findall(blob))
    for token in _CLICK.findall(blob):
        try:
            decoded = base64.b64decode(token + "=" * (-len(token) % 4)).decode(
                "utf8", "replace"
            )
        except Exception:  # noqa: BLE001 — not every tracking token is base64
            continue
        found.update(_FEED_ID.findall(decoded))
    return sorted(found, key=int)


def parse_published(text: str) -> str | None:
    """Hedgeye's own publication stamp, e.g. `09/11/2026 03:03 PM EDT`."""
    m = _PUBLISHED.search(text)
    return m.group(0) if m else None


def published_to_iso(stamp: str | None) -> str | None:
    if not stamp:
        return None
    m = _PUBLISHED.search(stamp)
    if not m:
        return None
    try:
        return datetime.strptime(
            f"{m.group(1)} {m.group(2).replace(' ', '')}", "%m/%d/%Y %I:%M%p"
        ).isoformat(timespec="minutes")
    except ValueError:
        return None


def read_eml(path: Path, root: Path | None = None) -> dict[str, Any]:
    """Everything a downstream parser might want, nothing interpreted."""
    with open(path, "rb") as fh:
        msg = email.message_from_binary_file(fh, policy=policy.default)
    assert isinstance(msg, EmailMessage)

    raw_date = msg.get("Date")
    arrived_at: str | None = None
    if raw_date:
        try:
            arrived_at = email.utils.parsedate_to_datetime(raw_date).isoformat()
        except (TypeError, ValueError):
            arrived_at = None

    text = _part_text(msg, "plain")
    html = _part_text(msg, "html")
    published = parse_published(text) or parse_published(html)

    return {
        "source_path": str(path.relative_to(root)) if root else str(path),
        "message_id": (msg.get("Message-ID") or "").strip(),
        "in_reply_to": (msg.get("In-Reply-To") or "").strip() or None,
        "references": (msg.get("References") or "").split() or None,
        "arrived_at": arrived_at,
        "subject": decode_subject(msg.get("Subject")),
        "published_stamp": published,
        "published_at": published_to_iso(published),
        "feed_item_ids": feed_ids(text, html),
        "mime_shape": "text/plain" if text else ("text/html" if html else "none"),
        "text": text,
        "html": html,
    }
