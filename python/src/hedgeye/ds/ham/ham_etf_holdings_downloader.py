import hashlib
import os
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ETF_HOLDINGS_URL = "https://hedgeye.s3.us-east-1.amazonaws.com/ham/ETF_Holdings.csv"
MOUNTAIN = ZoneInfo("America/Denver")


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_file(path: Path) -> str:
    return _hash_bytes(path.read_bytes())


def _parse_last_modified(response: requests.Response):
    """Return aware datetime from S3 Last-Modified header, or None."""
    header = response.headers.get("Last-Modified")
    if header:
        try:
            return parsedate_to_datetime(header)
        except Exception:
            pass
    return None


def _latest_saved(output_dir: Path) -> Path | None:
    files = sorted(output_dir.glob("ham_holdings_*.csv"), key=lambda p: p.name)
    return files[-1] if files else None


def download_etf_holdings(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    response = requests.get(ETF_HOLDINGS_URL, timeout=30)
    response.raise_for_status()

    content = response.content
    new_hash = _hash_bytes(content)

    latest = _latest_saved(output_dir)
    if latest and _hash_file(latest) == new_hash:
        print(f"No change (already have {latest.name})")
        return

    pub_dt = _parse_last_modified(response)
    if pub_dt:
        pub_mt = pub_dt.astimezone(MOUNTAIN)
        date_str = pub_mt.strftime("%Y-%m-%d")
        time_str = pub_mt.strftime("%H%M")
        mtime = pub_dt.timestamp()
    else:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        pub_mt = now.astimezone(MOUNTAIN)
        date_str = pub_mt.strftime("%Y-%m-%d")
        time_str = "0000"
        mtime = now.timestamp()

    dest = output_dir / f"ham_holdings_{date_str}_{time_str}.csv"
    dest.write_bytes(content)
    os.utime(dest, (mtime, mtime))

    row_count = content.count(b"\n")
    print(f"Saved {dest.name} ({row_count} rows)  [{pub_mt.strftime('%Y-%m-%d %H:%M %Z')}]")
