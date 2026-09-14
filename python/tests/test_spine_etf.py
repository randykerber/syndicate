"""Spine — ETF streams: PS commentary grammar, ETF Pro change grammar, Any10."""

from __future__ import annotations

from hedgeye.spine import parse_ep, parse_ps


def _txns(sentence: str) -> list[tuple[str, str, int | None]]:
    _, txns, unparsed, _ = parse_ps.parse_commentary(
        f'Keith\'s Commentary: "{sentence}"'
    )
    assert not unparsed, unparsed
    return [(t["action"], t["ticker"], t["bps"]) for t in txns]


def test_ps_commentary_core_forms() -> None:
    assert _txns("In the PA today, I bought 50bps of IVOL and SIL. Sold 50bps VGK.") == [
        ("buy", "IVOL", 50), ("buy", "SIL", 50), ("sell", "VGK", 50)]  # fmt: skip
    assert _txns("Sold all FXB.") == [("sell-all", "FXB", None)]
    assert _txns("In the PA today, I added XLP and SIL at my mins.") == [
        ("add-min", "XLP", None), ("add-min", "SIL", None)]  # fmt: skip
    assert _txns("Bought 100bps TUA, FXE, BTAL.") == [
        ("buy", "TUA", 100), ("buy", "FXE", 100), ("buy", "BTAL", 100)]  # fmt: skip


def test_ps_commentary_drift_forms() -> None:
    assert _txns("In the PA today, I sold all my FXC and HBDC.") == [
        ("sell-all", "FXC", None), ("sell-all", "HBDC", None)]  # fmt: skip
    assert _txns("Sold 50ps NORW and COM.") == [
        ("sell", "NORW", 50),
        ("sell", "COM", 50),
    ]
    assert _txns("Bought 100bp CLOX.") == [("buy", "CLOX", 100)]
    assert _txns("Sold 100bps GLD and AAAU (both positions at my MIN).") == [
        ("sell", "GLD", 100), ("sell", "AAAU", 100)]  # fmt: skip
    assert _txns("Sold VGK, EWG, and EWO down to my mins.") == [
        ("sell-to-min", "VGK", None), ("sell-to-min", "EWG", None), ("sell-to-min", "EWO", None)]  # fmt: skip
    assert _txns("In the PA today, I sold the last of my QQQ and all of EWW.") == [
        ("sell-all", "QQQ", None), ("sell-all", "EWW", None)]  # fmt: skip
    assert _txns("In the PA today, I bought ETHA at my min.") == [
        ("add-min", "ETHA", None)
    ]
    assert _txns("In the PA today, I sold all the CLOZ I had left at my min.") == [
        ("sell-all", "CLOZ", None)
    ]


def test_ps_commentary_notes_and_unparsed() -> None:
    body, txns, unparsed, notes = parse_ps.parse_commentary(
        'Keith\'s Commentary: "In the PA today there were no changes! #RidingWinners"'
    )
    assert txns == [] and unparsed == [] and len(notes) == 2
    _, txns, unparsed, _ = parse_ps.parse_commentary(
        'Keith\'s Commentary: "GLD, AAAU."'
    )
    assert txns == [] and unparsed == ["GLD, AAAU."]


def test_ps_subject() -> None:
    s = parse_ps.parse_subject(
        "(CORRECTION) Portfolio Solutions: Daily ETF Re-Rank (5/4/2026) | Top Movers: X"
    )
    assert s["recognized"] and s["is_correction"] and s["report_date"] == "2026-05-04"
    s = parse_ps.parse_subject(
        "PORTFOLIO SOLUTIONS: Portfolio Solutions: Weekly ETF Re-Rank (12/20/2024)"
    )
    assert s["recognized"] and s["cadence"] == "weekly"


def test_ep_changes_modern() -> None:
    text = """Dear ETF Pro Plus Subscriber,
We are ADDING Long:
US Free Cash Flow (VFLO)
Brazil (EWZ)
We are ADDING Short:
India (INDA)
We are REMOVING Long:
US TIPS (VTIP) - (49.6 - 49.87)
How to Use ETF Pro Plus Updates:
Addition to the Long Side: ...
"""
    ch, un = parse_ep.parse_changes(text)
    assert un == []
    assert [(c["action"], c["side"], c["ticker"]) for c in ch] == [
        ("add", "long", "VFLO"), ("add", "long", "EWZ"), ("add", "short", "INDA"), ("remove", "long", "VTIP")]  # fmt: skip
    assert ch[3]["range"] == [49.6, 49.87]


def test_ep_changes_old_variants() -> None:
    text = "We are\xa0ADDING Long: Natural Gas (FCG)\nFinancials (XLF)\nWe are\xa0REMOVING: Simplify Interest Rate Hedge (PFIX)\n(EWO) Austria\nCTA (Simplify Managed Futures Strategy ETF)\nIN CASE YOU MISSED IT\nWe are ADDING Long:\nOld (OLD)\n"
    ch, un = parse_ep.parse_changes(text)
    assert un == []
    assert [(c["action"], c["side"], c["ticker"]) for c in ch] == [
        ("add", "long", "FCG"), ("add", "long", "XLF"), ("remove", None, "PFIX"),
        ("remove", None, "EWO"), ("remove", None, "CTA")]  # fmt: skip


def test_ep_subjects() -> None:
    assert parse_ep.parse_change_subject("UPDATE: 8 New ETF Pro Changes")["count"] == 8
    assert parse_ep.parse_change_subject("Correction: 5 New ETF Pro Changes")[
        "is_correction"
    ]
    s = parse_ep.parse_change_subject("UPDATE: Remove WGMI")
    assert s["subject_change"] == {"action": "remove", "side": None, "ticker": "WGMI"}
    s = parse_ep.parse_change_subject("UPDATE: Add LONG QQQ")
    assert s["subject_change"] == {"action": "add", "side": "long", "ticker": "QQQ"}
    s = parse_ep.parse_change_subject("UPDATE: Removing Global X Uranium ETF (URA)")
    assert (
        s["subject_change"]["ticker"] == "URA"
        and s["subject_change"]["action"] == "remove"
    )
