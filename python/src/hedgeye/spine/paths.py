"""Where the spine reads and writes. One place, so every command agrees."""

from __future__ import annotations

from pathlib import Path

HOME = Path.home()
D = HOME / "d"

RAW_MAIL = D / "downloads" / "hedgeye" / "raw" / "mail"
RAW_CHARTS_SS = D / "downloads" / "hedgeye" / "raw" / "charts" / "ss"
CHART_OVERRIDES_SS = RAW_CHARTS_SS / "overrides.json"

PROD = D / "prod" / "hedgeye"
SNAPSHOTS = PROD / "snapshots"
SNAPSHOTS_SS = SNAPSHOTS / "ss"
DB_PATH = PROD / "hedgeye.sqlite"
RUNS_LOG = PROD / "runs.jsonl"
TICKER_ALIASES = PROD / "ticker-aliases.json"

FID_POSITIONS = D / "downloads" / "fid" / "positions"  # Fidelity Positions export
IBKR_POSITIONS = D / "downloads" / "ibkr" / "positions"  # saved IBKR connector snapshot

FIN_VAULT = HOME / "local" / "obsidian" / "Fin"
GEN_DIR = FIN_VAULT / "Areas" / "Hedgeye" / "gen"

SS_MAILBOX = "HE-SS-Stocks"


def snapshots_dir(stream: str) -> Path:
    return SNAPSHOTS / stream


def ensure_dirs() -> None:
    for p in (RAW_CHARTS_SS, SNAPSHOTS_SS, PROD):
        p.mkdir(parents=True, exist_ok=True)
