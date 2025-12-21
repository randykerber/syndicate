# Context File Curation Summary

**Date**: 2025-12-12
**Task**: Distill all context files into COMMON.md + agent-specific files

---

## ✅ COMPLETED

### COMMON.md (414 lines)
**Purpose**: Shared context across ALL AI tools

**Content included**:
- Identity: Randy Kerber (rk), Cañon City, Colorado
- Hardware: Mac Studio (rstudio), MacBook Pro (idlewood), iPhone 15 Pro, iPad Pro
- OS: macOS 26 Tahoe, iOS 18, iPadOS 18
- Tools: Warp, IntelliJ, Cursor, Arc, Raycast, Obsidian, Things, etc.
- Python/uv (MANDATORY), JavaScript/npm, Scala/SBT
- Git/GitHub (randykerber, ~/gh/randykerber/)
- Safety rules, response patterns, code style
- Projects: Syndicate/SSS, Financial Data Warehouse
- Philosophy: Speed, Quality, Learning, Pragmatism, Clarity

---

## 🔧 AGENT-SPECIFIC FILES NEEDED

### CLAUDE-specific.md
**Already exists**: `/warehouse/agents/claude/CLAUDE-specific.md` (61 lines)

**Content**:
- Claude Desktop vs Claude Code roles
- CD/CC abbreviations
- MCP servers for Claude (Filesystem, Things, Context7, Postman, Apple Notes)
- `.claude/` directory paths
- Verification tests (TEST_LOAD_DATE, TEST_FAVORITE_COLOR, TEST_VERIFICATION_CODE)
- Favorite color: magenta
- Claude Code specific instructions (testing, file creation, debugging)
- Integration preferences (MCP priorities)

---

### WARP-specific.md
**Already exists**: `/warehouse/agents/warp/WARP-specific.md` (112 lines)

**Content**:
- Warp AI Behavior Contract (plan-then-execute pattern)
- Response style for terminal context
- Git with `--no-pager` for Warp compatibility
- Secrets management (redacted input handling with {{SECRET_NAME}})
- Warp-specific features (keybindings, workflows)
- Command suggestions workflow
- Error explanations pattern
- Configuration paths (`~/.config/warp/`, keybindings.yaml)

---

### GEMINI-specific.md
**Already exists**: `/warehouse/agents/gemini/GEMINI-specific.md` (minimal)

**Content**:
- Sandboxing constraint: never attempt to read/modify files outside CWD unless @filename referenced
- (Very minimal - only 7 lines)

---

### CURSOR-specific.md
**NEEDS TO BE CREATED**

**Content should include**:
- Project context awareness (Syndicate/SSS)
- File context usage with @ symbol
- Refactoring patterns (incremental, preserve functionality)
- Code suggestions (follow existing patterns, preserve type hints)
- Testing requirements for refactored code
- Syndicate-specific patterns (human-interface, agents, MCP servers)
- Hedgeye pipeline knowledge (external data paths, CSV structure)
- Never introduce new dependencies without discussion

**Content to EXCLUDE** (already in COMMON):
- General Python/uv patterns
- General code style (Black, Ruff, type hints)
- General safety rules
- General project structure

---

### CHATGPT-specific.md
**NEEDS TO BE CREATED**

**Content should include**:
- "Bias:" keyword usage (Bias: deep → thorough, Bias: quick → concise)
- Role as reconciler/source of truth when merging context across AI tools
- ChatGPT MD plugin in Obsidian
- Memory export capability
- Multi-AI ecosystem coordinator role
- Context reconciliation workflow

**Content to EXCLUDE** (already in COMMON):
- General tools, preferences (already covered)
- Projects (already in COMMON)
- General response patterns

---

## 📝 MISC.md
**NEEDS TO BE CREATED**

**Purpose**: Valuable info that doesn't fit common or agent-specific categories

**Content should include**:
- Machine migration context (Nov 2025: idlewood → rstudio, COMPLETE)
- Editor choice decision rationale ($359/year: Cursor $20/mo + IntelliJ $119/yr)
- Retired tools (PyCharm, JetBrains All Products Pack)
- Sync strategy (Git for code, iCloud/Drive for docs, Obsidian Sync)
- Completed setup checklist
- Creekview flora/fauna project details (scientific names, pest vs beneficial tracking)
- Recreation interests details (mountain biking, SUP, skiing, camping, cooking/smoked meats)

---

## 🗑️ excess.md
**NEEDS TO BE CREATED**

**Purpose**: Content from source files NOT included in final outputs (for review/rescue)

**Potential content**:
- Outdated version numbers or paths
- Redundant sections that overlapped with better phrasing
- Project-specific details that are too granular
- Example verification tests/codes
- Outdated status information
- Any content I judged not valuable enough but user might want to rescue

---

## 📊 ANALYSIS SUMMARY

### Source Files Analyzed:
1. WARP.md (438 lines) - Most comprehensive
2. CLAUDE.md (471 lines) - Comprehensive, Claude-focused
3. CHATGPT.md (187 lines) - Unique perspective, structured
4. CURSORRULES.md (346 lines) - Project-specific, code-focused
5. COMMON.md from Gemini (103 lines) - Rules-heavy, strict
6. GEMINI-specific.md (7 lines) - Minimal

### Content Distribution:
- **COMMON.md**: ~80% of valuable content (414 lines)
- **Agent-specific files**: ~15% (truly unique features per tool)
- **MISC.md**: ~5% (valuable but uncategorized)
- **excess.md**: Content I excluded but available for review

### Key Insights:
1. **Massive overlap** across files - same info repeated with different phrasing
2. **WARP.md was most comprehensive** - had detailed environment/tool info
3. **CURSORRULES.md was most project-specific** - Syndicate/Hedgeye details
4. **CHATGPT.md had unique patterns** - "Bias:" keyword, reconciler role
5. **GEMINI files were minimal** - just sandboxing constraint

---

## 🎯 NEXT STEPS

User should review this summary, then I'll create the remaining files:
1. CURSOR-specific.md
2. CHATGPT-specific.md
3. MISC.md
4. excess.md

Then test builds for all 5 agents to ensure everything works.

---

**End of CURATION-SUMMARY.md**
