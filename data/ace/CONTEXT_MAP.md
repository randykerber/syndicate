# Context Map

**Version**: 2025-12-31
**Purpose**: Master index of Randy's context sources. Copy to any AI surface as a seed document.

---

## How to Use This Map

1. When a topic comes up, check this table
2. Read the relevant file(s) BEFORE answering
3. Use content from files, not training data guesses
4. Canary tests verify files were actually loaded

---

## Context Sources

### Identity & Preferences

| Topic | Location | Format |
|-------|----------|--------|
| Profile (name, location, role) | `context/profile.md` | YAML frontmatter + Markdown |
| Tools & apps | `context/tools.md` | Markdown list |
| Response preferences | `context/preferences.md` | Markdown |

### Project-Specific

| Topic | Location | Format |
|-------|----------|--------|
| Syndicate overview | `CLAUDE.md` (project root) | Markdown |
| Hedgeye pipeline | `docs/hedgeye/PIPELINE_QUICK_REFERENCE.md` | Markdown |
| ACE factory | `data/ace/README.md` | Markdown |

### Skills (Dynamic Context)

| Skill | Location | Trigger |
|-------|----------|---------|
| Context engineering state | `data/ace/skills/context-engineering-state/SKILL.md` | Memory, Skills, context portability questions |
| Randy's basic context | `data/ace/skills/randy-context/SKILL.md` | Environment, setup questions |

### External Data (Absolute Paths)

| Topic | Location |
|-------|----------|
| Hedgeye raw data | `/Users/rk/d/downloads/hedgeye/` |
| Hedgeye production | `/Users/rk/d/downloads/hedgeye/prod/` |

---

## Surface Visibility Matrix

| Context Source | Cursor | Claude Code | Claude Desktop | API |
|----------------|--------|-------------|----------------|-----|
| Project `CLAUDE.md` | ✅ Auto | ✅ Auto | ❌ | ❌ |
| `~/.claude/CLAUDE.md` | ❌ | ✅ Auto | ❌ | ❌ |
| `~/.claude/skills/*` | ❌ | ✅ Auto | ❌ | ❌ |
| Project files (on demand) | ✅ Read | ✅ Read | ❌ | ❌ |
| userMemories | ❌ | ❌ | ✅ Auto | ❌ |
| Claude Desktop Skills | ❌ | ❌ | ⚠️ Maybe | ❌ |
| MCP Servers | ✅ | ✅ | ✅ | ✅ |

**Legend**: ✅ Auto = loaded automatically | ✅ Read = can read on demand | ⚠️ = conditional | ❌ = not available

---

## Canary Tests

Verify context was actually loaded:

| Context | Question | Expected Answer |
|---------|----------|-----------------|
| Context engineering skill | "What's the context engineering canary?" | `pineapple-telescope-42` |
| Profile | "What timezone is Randy in?" | America/Denver |
| Tools | "What terminal does Randy use?" | Warp |

---

## Sync Strategy (Future)

**Goal**: This map available everywhere, with local cache for offline.

**Options under consideration**:
1. GitHub public repo (version controlled, fetchable)
2. Google Drive (cross-device sync, offline support)
3. AWS S3 (URL-fetchable, scriptable)
4. MCP "context server" (dynamic, queryable)

**Current state**: Local file in syndicate project. Copy manually to other locations as needed.

---

## Changelog

- 2025-12-31: Initial version created from Cursor session

