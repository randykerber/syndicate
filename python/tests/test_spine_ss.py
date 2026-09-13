"""Spine — Signal Strength slice. Grammar, keying, checks, classification."""

from __future__ import annotations

import base64

from hedgeye.spine import eml, holdings, ss_checks, ss_extract, ss_roster


def test_subject_grammar_counts() -> None:
    s = ss_extract.parse_subject(
        "Signal Strength Stocks: 61 Stocks (3 Added, 12 Removed)"
    )
    assert (s["count"], s["added"], s["removed"]) == (61, 3, 12)
    assert s["recognized"] and not s["counts_absent"] and not s["update_wording"]


def test_subject_grammar_drift_variants() -> None:
    s = ss_extract.parse_subject(
        "Signal Strength Stocks Update: 59 Stocks (5 Added, 2 Removed)"
    )
    assert s["recognized"] and s["update_wording"]
    assert (s["count"], s["added"]) == (59, 5)
    s = ss_extract.parse_subject("Signal Strength Stocks: 71 Stocks")
    assert s["recognized"] and s["counts_absent"] and s["count"] == 71
    s = ss_extract.parse_subject(
        "signal Strength Stocks: 76 Stocks (7 Added, 2 Removed)"
    )
    assert s["recognized"] and s["added"] == 7


def test_subject_grammar_no_changes_variants() -> None:
    for subj in ("Signal Strength Stocks: 58 Stocks (No changes)",
                 "Signal Strength Stocks: 73 Stocks (no changes)",
                 "Signal Strength Stocks: 82 Stocks (0 Added, 0 Removed)"):  # fmt: skip
        s = ss_extract.parse_subject(subj)
        assert s["recognized"] and s["added"] == 0 and s["removed"] == 0


def test_subject_grammar_rejects_other() -> None:
    assert ss_extract.parse_subject(
        "Quick Start Guide for your Signal Strength Stocks Subscription"
    ) == {"recognized": False}


def test_changes_lists() -> None:
    text = "junk\nAdded: META, MRVL, AAPL\n\nRemoved: DGX, SXT, GTBIF\n"
    c = ss_extract.parse_changes(text)
    assert c["added"] == ["META", "MRVL", "AAPL"]
    assert c["removed"] == ["DGX", "SXT", "GTBIF"]


def test_changes_none_wording() -> None:
    c = ss_extract.parse_changes("Added: None\nRemoved: None\n")
    assert c["added"] == [] and c["removed"] == []
    assert c["added_line_present"]


def test_changes_absent() -> None:
    c = ss_extract.parse_changes("nothing here")
    assert c["added"] is None and c["removed"] is None


def test_feed_id_through_click_wrapper() -> None:
    token = (
        base64.b64encode(b"https://app.hedgeye.com/feed_items/187095")
        .decode()
        .rstrip("=")
    )
    text = f"see https://model2.hedgeye.com/click/47454872.195/{token}/abc"
    assert eml.feed_ids(text) == ["187095"]


def test_published_stamp() -> None:
    stamp = eml.parse_published("09/11/2026 03:03 PM EDT Signal Strength Stocks")
    assert stamp == "09/11/2026 03:03 PM EDT"
    assert eml.published_to_iso(stamp) == "2026-09-11T15:03"


def test_chart_url() -> None:
    html = '<img class="chart" src="https://d1yhils6iwh5l5.cloudfront.net/charts/resized/160173/original/SSS_9_11.png?src=email&amp;email=x" width="750">'
    c = ss_extract.find_chart(html)
    assert c == {"url": "https://d1yhils6iwh5l5.cloudfront.net/charts/resized/160173/original/SSS_9_11.png",
                 "chart_id": "160173", "variant": "original", "filename": "SSS_9_11.png"}  # fmt: skip


def _snap(
    fid: str, count: int, added: list[str], removed: list[str], tickers: list[str]
) -> dict:
    return {
        "feed_item_id": fid,
        "published_at": f"2026-09-{fid[-2:]}T10:00",
        "subject": "",
        "subject_parsed": {"recognized": True, "count": count, "added": len(added), "removed": len(removed)},
        "changes": {"added": added, "removed": removed},
        "roster": {"rows": [{"ticker": t, "best_idea_rank": "Bench", "analyst": "A",
                             "sector": "S", "signal_date": "1/1/2026", "entry_price": 1.0}
                            for t in tickers]},
    }  # fmt: skip


def test_checks_all_pass() -> None:
    a = _snap("101", 3, [], [], ["A", "B", "C"])
    b = _snap("102", 3, ["D"], ["A"], ["B", "C", "D"])
    tally = ss_checks.run_checks([a, b])
    assert tally["all_pass"] == 2
    assert b["checks"]["results"]["replay"]["pass"]


def test_checks_catch_image_disagreement() -> None:
    a = _snap("101", 3, [], [], ["A", "B", "C"])
    b = _snap("102", 3, ["D"], ["A"], ["B", "C", "E"])  # image says E, text says D
    ss_checks.run_checks([a, b])
    r = b["checks"]["results"]["replay"]
    assert not r["pass"]
    assert r["expected_but_absent"] == ["D"] and r["present_but_unexpected"] == ["E"]
    assert b["checks"]["confidence"] < 1


def test_diff_stable_fields() -> None:
    a = _snap("101", 2, [], [], ["A", "B"])
    b = _snap("102", 2, [], [], ["A", "B"])
    b["roster"]["rows"][0]["best_idea_rank"] = "3/6"
    b["roster"]["rows"][0]["days_on"] = 99  # volatile, must not count
    d = ss_checks.diff_rosters(a, b)
    assert d["stable_field_changes"] == [
        {
            "ticker": "A",
            "field": "best_idea_rank",
            "from": "Bench",
            "to": "3/6",
            "significance": "kind",
        }
    ]


def test_rank_kind() -> None:
    assert ss_roster.rank_kind("3/6") == "ranked"
    assert ss_roster.rank_kind("Bench") == "bench"
    assert ss_roster.rank_kind("KM Signal") == "km-signal"
    assert ss_roster.rank_kind(None) == "unknown"


def test_classify_bonds_and_funds() -> None:
    assert (
        holdings.classify(
            "912797SA6", "UNITED STATES TREAS BILLS ZERO CPN 0.00000% 10/01/2026"
        )[0]
        == "bond-tbill"
    )
    assert (
        holdings.classify(
            "912810QV3", "UNITED STATES TREAS BDS 0.75000% 02/15/2042 TIPS"
        )[0]
        == "bond-tips"
    )
    assert (
        holdings.classify(
            "91282CEZ0", "UNITED STATES TREAS NTS SER D-2032 0.62500% 07/15/2032"
        )[0]
        == "bond-tnote"
    )
    assert (
        holdings.classify(
            "91282CQH7", "UNITED STATES TREAS SER AZ-2028 3.87500% 03/31/2028 NTS NOTE"
        )[0]
        == "bond-tnote"
    )
    assert holdings.classify("FDRXX", "HELD IN MONEY MARKET")[0] == "cash"
    assert holdings.classify("EWZ", "ISHARES MSCI BRAZIL ETF")[0] == "etf"
    assert (
        holdings.classify("92189F403", "VANECK ETF TRUST VANECK RUSSIA ET")[0] == "etf"
    )
    assert holdings.classify("JPM", "JPMORGAN CHASE &CO. COM")[0] == "stock"
    assert (
        holdings.classify("SRUUF", "SPROTT PHYSICAL URANIUM TR TRUST UNIT")[0] == "fund"
    )


def test_changes_empty_list_followed_by_image_link() -> None:
    c = ss_extract.parse_changes(
        "Added: LEVI\n\nRemoved: (VIEW LARGER IMAGE <https://x/y.png>)\n"
    )
    assert c["added"] == ["LEVI"] and c["removed"] == []


def test_diff_missing_column_is_not_a_change() -> None:
    a = _snap("101", 1, [], [], ["A"])
    b = _snap("102", 1, [], [], ["A"])
    a["roster"]["rows"][0]["best_idea_rank"] = None  # five-column image
    d = ss_checks.diff_rosters(a, b)
    assert d["stable_field_changes"] == []
    assert d["fields_unavailable_one_side"] == {"best_idea_rank": 1}


def test_replay_carries_changes_across_untrusted_snapshot() -> None:
    a = _snap("101", 2, [], [], ["A", "B"])
    mid = _snap("102", 3, ["C"], [], ["X", "Y", "Z"])  # later-state image, untrusted
    mid["chart"] = {"roster_untrusted": "later state"}
    b = _snap("103", 3, ["D"], ["A"], ["B", "C", "D"])
    tally = ss_checks.run_checks([a, mid, b])
    r = b["checks"]["results"]["replay"]
    assert r["pass"] and r["via"] == ["102"] and r["prev_feed_item_id"] == "101"
    assert tally["checked"] == 3


def test_replay_skipped_over_long_gap() -> None:
    a = _snap("101", 1, [], [], ["A"])
    a["published_at"] = "2025-04-21T08:00"
    b = _snap("102", 1, [], [], ["B"])
    b["published_at"] = "2026-02-02T08:00"
    ss_checks.run_checks([a, b])
    assert "replay" not in b["checks"]["results"]
    assert "replay_skipped" in b["checks"]["results"]


def test_diff_significance_classes() -> None:
    a = _snap("101", 3, [], [], ["A", "B", "C"])
    b = _snap("102", 3, [], [], ["A", "B", "C"])
    a["roster"]["rows"][0]["best_idea_rank"] = "4/4"
    b["roster"]["rows"][0]["best_idea_rank"] = "4/5"  # denominator only
    a["roster"]["rows"][1]["best_idea_rank"] = "3/6"
    b["roster"]["rows"][1]["best_idea_rank"] = "1/6"  # position
    a["roster"]["rows"][2]["entry_price"] = 23.44
    b["roster"]["rows"][2]["entry_price"] = 23.4  # rounding
    sig = {
        (c["ticker"], c["field"]): c["significance"]
        for c in ss_checks.diff_rosters(a, b)["stable_field_changes"]
    }
    assert sig == {
        ("A", "best_idea_rank"): "denominator",
        ("B", "best_idea_rank"): "position",
        ("C", "entry_price"): "rounding",
    }


def test_aliases_canonicalize_replay(tmp_path, monkeypatch) -> None:
    from hedgeye.spine import aliases, paths

    f = tmp_path / "ticker-aliases.json"
    f.write_text('{"aliases": {"UAA": "UA"}, "corrections": {"RC": "RCL"}}')
    monkeypatch.setattr(paths, "TICKER_ALIASES", f)
    aliases.reload()
    try:
        a = _snap("101", 1, [], [], ["A"])
        b = _snap("102", 2, ["RC"], [], ["A", "RCL"])  # email typo, image correct
        ss_checks.run_checks([a, b])
        assert b["checks"]["results"]["replay"]["pass"]
        assert aliases.kind("RC") == "correction"
        assert aliases.kind("UAA") == "alias"
        assert aliases.kind("RCL") is None
        assert aliases.canon("uaa") == "UA"
    finally:
        aliases.reload()


def test_derive_roster_from_ledger() -> None:
    from hedgeye.spine import ss_derive

    a = _snap("101", 2, [], [], ["A", "B"])
    a["published_at"] = "2026-04-24T12:00"
    mid = _snap("102", 3, ["C"], [], ["X", "Y", "Z"])  # later-state image
    mid["published_at"] = "2026-04-27T09:00"
    mid["chart"] = {"roster_untrusted": "later state"}
    nxt = _snap("103", 3, [], [], ["A", "B", "C"])
    nxt["published_at"] = "2026-04-27T11:00"
    nxt["roster"]["rows"][2]["best_idea_rank"] = "KM Signal"
    written = []
    out = ss_derive.derive_rosters([a, mid, nxt], written.append)
    assert out["derived"] == 1
    rows = {r["ticker"]: r for r in mid["roster"]["rows"]}
    assert set(rows) == {"A", "B", "C"}
    assert rows["A"]["days_on"] == 3 and rows["A"]["best_idea_rank"] == "Bench"
    assert rows["C"]["days_on"] == 0 and rows["C"]["best_idea_rank"] == "KM Signal"
    assert mid["roster_source"]["kind"] == "derived"
    assert mid["roster_from_later_image"]["rows"][0]["ticker"] == "X"
    assert ss_extract.roster_trusted(mid)
