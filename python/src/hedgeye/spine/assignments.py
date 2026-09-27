"""HE sector assignments — who leads which Hedgeye sector, and since when.

**Source of record: the two markdown tables on the Fin vault page
`Areas/Hedgeye/Signal Strength Stocks.md`** (Randy, 2026-09-27), under the headings
`## HE sector assignments` and `## HE sector name aliases`. This module only reads them.
Every other appearance of the fact — analyst pages, HE-Sectors, the `gen/` page, the
SQLite tables — is a view. A change is a new row (or an End date) on that page; `load`
then carries it into SQLite and `render` regenerates the views. Never write the fact
anywhere else.

This is the spine's one case of reading a vault page as an input: a hand-maintained
fact table under a fixed heading, not prose.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from . import paths

HEADING_ASSIGNMENTS = "## HE sector assignments"
HEADING_ALIASES = "## HE sector name aliases"
_LINK = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class Assignment:
    sector: str
    analyst: str
    role: str  # lead | stand-in
    start: str  # ISO date
    end: str | None  # ISO date, None = current
    note: str

    def in_force(self, on: str) -> bool:
        d = on[:10]
        return self.start <= d and (self.end is None or d <= self.end)


@dataclass(frozen=True)
class SectorAlias:
    printed: str
    canonical: str
    start: str
    end: str | None
    note: str

    def in_force(self, on: str) -> bool:
        d = on[:10]
        return self.start <= d and (self.end is None or d <= self.end)


def _clean(cell: str) -> str:
    cell = _LINK.sub(r"\1", cell)
    return " ".join(cell.split()).strip()


def _table_under(text: str, heading: str) -> list[list[str]]:
    """Rows of the first pipe table after `heading`, header row included."""
    i = text.find(heading)
    if i < 0:
        return []
    rows: list[list[str]] = []
    started = False
    for line in text[i + len(heading) :].splitlines():
        s = line.strip()
        if s.startswith("|"):
            cells = [c for c in s.strip("|").split("|")]
            if all(set(c.strip()) <= set("-: ") for c in cells):
                continue  # the |---| separator
            rows.append([_clean(c) for c in cells])
            started = True
        elif started:
            break
    return rows


def _date(cell: str, what: str, problems: list[str]) -> str | None:
    c = cell.strip()
    if not c:
        return None
    if not _DATE.match(c):
        problems.append(f"{what}: bad date {c!r}")
        return None
    return c


def parse(text: str) -> dict[str, Any]:
    problems: list[str] = []
    assignments: list[Assignment] = []
    rows = _table_under(text, HEADING_ASSIGNMENTS)
    if not rows:
        problems.append(f"no table under {HEADING_ASSIGNMENTS!r}")
    for r in rows[1:]:
        if len(r) < 5:
            problems.append(f"assignment row too short: {r}")
            continue
        sector, analyst, role, start, end = r[:5]
        note = r[5] if len(r) > 5 else ""
        role = role.lower()
        if role not in ("lead", "stand-in"):
            problems.append(f"{sector}/{analyst}: role {role!r} not lead|stand-in")
        s = _date(start, f"{sector}/{analyst} start", problems)
        if s is None:
            problems.append(f"{sector}/{analyst}: start date required")
            continue
        assignments.append(
            Assignment(
                sector,
                analyst,
                role,
                s,
                _date(end, f"{sector}/{analyst} end", problems),
                note,
            )
        )
    aliases: list[SectorAlias] = []
    for r in _table_under(text, HEADING_ALIASES)[1:]:
        if len(r) < 4:
            problems.append(f"alias row too short: {r}")
            continue
        printed, canonical, start, end = r[:4]
        s = _date(start, f"alias {printed} start", problems) or "0001-01-01"
        aliases.append(
            SectorAlias(
                printed, canonical, s, _date(end, f"alias {printed} end", problems),
                r[4] if len(r) > 4 else "",
            )
        )  # fmt: skip
    # one lead per sector at any date
    leads = [a for a in assignments if a.role == "lead"]
    for i, a in enumerate(leads):
        for b in leads[i + 1 :]:
            if a.sector != b.sector:
                continue
            a_end, b_end = a.end or "9999-12-31", b.end or "9999-12-31"
            if a.start <= b_end and b.start <= a_end:
                problems.append(
                    f"{a.sector}: two leads overlap — {a.analyst} {a.start}..{a.end or ''} "
                    f"and {b.analyst} {b.start}..{b.end or ''}"
                )
    return {"assignments": assignments, "aliases": aliases, "problems": problems}


def load(path: Path = paths.SS_SOURCE_PAGE) -> dict[str, Any]:
    if not path.exists():
        return {"assignments": [], "aliases": [], "problems": [f"missing {path}"]}
    return parse(path.read_text())


def canonical_sector(
    printed: str | None, on: str, aliases: list[SectorAlias]
) -> str | None:
    if printed is None:
        return None
    for a in aliases:
        if a.printed.lower() == printed.lower() and a.in_force(on):
            return a.canonical
    return printed


def expected_analysts(sector: str, on: str, assignments: list[Assignment]) -> list[str]:
    """Lead and stand-ins in force for `sector` on `on` (lead first)."""
    inf = [
        a for a in assignments if a.sector.lower() == sector.lower() and a.in_force(on)
    ]
    inf.sort(key=lambda a: 0 if a.role == "lead" else 1)
    return [a.analyst for a in inf]


def current(assignments: list[Assignment], on: str | None = None) -> list[Assignment]:
    on = on or date.today().isoformat()
    return sorted(
        (a for a in assignments if a.in_force(on)),
        key=lambda a: (a.sector.lower(), 0 if a.role == "lead" else 1),
    )
