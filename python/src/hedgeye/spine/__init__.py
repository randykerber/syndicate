"""Hedgeye event spine — hand-run commands with inspectable files between steps.

Governing rule (rough-design-draft.md §4, 2026-09-12): every step runs on its own, by
hand, at any time; JSON files on disk between steps; schedule only what is unrecoverable
if missed. First slice (Hedgeye Build s1, 2026-09-13): Signal Strength Stocks.
"""
