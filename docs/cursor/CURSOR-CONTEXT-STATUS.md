# Cursor Context Status

**Last Updated**: 2026-01-10  
**Purpose**: Quick reference for future sessions about Cursor's context setup

---

## Current Setup (as of 2026-01-10)

### What Cursor Loads Automatically

| File | Loaded? | Notes |
|------|---------|-------|
| `AGENTS.md` | ✅ Yes | Cross-tool context (192 lines) |
| `.cursor/rules/always.mdc` | ✅ Yes | Safety, secrets, BSD commands |
| `.cursor/rules/python.mdc` | ✅ When `**/*.py` | Python conventions, uv |
| `.cursor/rules/hedgeye.mdc` | ✅ When `**/hedgeye/**` | Pipeline specifics |
| `CLAUDE.md` | ❌ No | Claude Code only, Cursor ignores it |

### What Cursor Does NOT Load

- `CLAUDE.md` - Not read by Cursor (Claude Code specific)
- `data/ace/*` - Not auto-loaded (warehouse/factory)
- `context/*` - Not auto-loaded

---

## Key Files

```
syndicate/
├── AGENTS.md                    # ← Cursor reads this (cross-tool)
├── CLAUDE.md                    # ← Cursor IGNORES this
├── .cursor/
│   └── rules/
│       ├── always.mdc           # Always loaded
│       ├── python.mdc           # Glob: **/*.py
│       └── hedgeye.mdc          # Glob: **/hedgeye/**
├── .cursorrules.deprecated.*    # Old format, archived
└── data/ace/
    └── warehouse/               # Source parts (not auto-loaded)
```

---

## Known Issues / Uncertainties

⚠️ **Not fully verified:**

1. **Conflict resolution**: When rules conflict, which wins? (Probably more specific wins)
2. **CLAUDE.md reading**: Web search said Cursor CLI reads it, but IDE might not
3. **Global rules**: Only in Settings UI, no file-based global rules confirmed

---

## Relationship to ACE Warehouse

The ACE warehouse (`data/ace/warehouse/`) is a **parts factory**, not directly loaded by Cursor.

- `warehouse/projects/syndicate/AGENTS.md` → Source for `./AGENTS.md`
- `.cursor/rules/*.mdc` → Native format, NOT copied back to warehouse
- `warehouse/agents/cursor/CURSOR-specific.md` → ⚠️ May be stale, overlaps with `.cursor/rules/`

---

## If You Need to Update Context

1. **Cross-tool changes** → Edit `AGENTS.md` (and update warehouse copy)
2. **Cursor-specific** → Edit `.cursor/rules/*.mdc` directly
3. **Global preferences** → Cursor Settings → General → Rules for AI

---

## Deprecated / Superseded

| File | Status | Notes |
|------|--------|-------|
| `.cursorrules` | ❌ Deprecated | Renamed to `.cursorrules.deprecated.2026-01-10` |
| `ship/cursor/CURSORRULES.md` | ⚠️ Stale | Old ACE output, superseded by modular approach |
| `warehouse/agents/cursor/CURSOR-specific.md` | ⚠️ Overlaps | Content now in `.cursor/rules/` |

---

## Quick Verification

To check if Cursor loaded your context, ask:
- "What context files did you load?"
- "What's in AGENTS.md?"
- Add a canary phrase and test if it's recognized

---

**See also**: `docs/ace/Context-in-Cursor.md` for detailed explanation of how Cursor handles context.
