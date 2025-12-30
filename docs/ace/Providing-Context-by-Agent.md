# How various AI Agent Hangle and use Context

## Gemini

### Gemini in Chrome

In Settings >> Personal Context:

Learn from past chats

Gemini learns from your past chats, understanding more about you and your world to personalize your experience. Gemini Apps Activity needs to be on to use this feature. You can manage and delete your past
chats, or turn this off anytime with this setting.

================================================

# Providing Context by Agent - Quick Reference

**Purpose**: Document how each AI agent/tool receives context, system instructions, and user preferences.

**Status**: Initial version - expand as we learn more about each tool.

**Last Updated**: 2025-12-21

---

## Claude Variants

### Claude Code (Terminal CLI)

**Context Method**: File-based (Markdown)

**How it works**:
- **Global**: Reads `~/.claude/CLAUDE.md` automatically on startup
- **Project-local**: Also reads `.claude/CLAUDE.md` if present in project
- **AGENTS.md convention**: Can use `~/.claude/AGENTS.md` (symlink `CLAUDE.md -> AGENTS.md`)
- **Format**: Markdown, user can edit directly
- **Persistence**: File-based, version controlled, syncs across machines via git

**Configuration**:
- Main file: `~/.claude/CLAUDE.md` (or AGENTS.md)
- Project overrides: `.claude/CLAUDE.md` in project root
- Can check with: `cat ~/.claude/CLAUDE.md`

**Advantages**:
- Version controlled (can track changes in git)
- Easily edited in any text editor
- Shareable across projects/machines
- Clear file to inspect/modify

**Limitations**:
- Must manually edit file (no UI)
- Requires understanding of file location
- Changes require file save (not instant)

---

### Claude Desktop (macOS/Windows App)

**Context Method**: UI-based custom instructions

**How it works**:
- **Custom Instructions**: Text box in Settings/Preferences
- **Per-project**: Can set different instructions per "project" in app
- **NOT file-based**: Does NOT read `~/.claude/CLAUDE.md` file
- **Format**: Plain text entered in settings UI
- **Persistence**: Stored in app settings, not user-accessible file

**Configuration**:
- Open Claude Desktop → Settings → Custom Instructions
- Enter instructions in text box
- Saved automatically

**MCP Servers**:
- Configured separately in Settings → MCP
- JSON config file at `~/Library/Application Support/Claude/claude_desktop_config.json`
- Enables local integrations (filesystem, Things, etc.)

**Advantages**:
- Easy UI access (no file hunting)
- Per-project customization
- MCP servers for local integrations

**Limitations**:
- Not version controlled (lives in app settings)
- Hard to sync across machines
- Can't edit with text editor
- No clear file to inspect

---

### Claude Web (claude.ai in browser)

**Context Method**: UI-based custom instructions

**How it works**:
- **Custom Instructions**: Settings → Custom Instructions
- **Format**: Text box in web UI
- **Persistence**: Saved to Anthropic cloud, tied to account
- **Available**: Across all conversations in web interface

**Configuration**:
- Click profile → Settings → Custom Instructions
- Enter text, save

**File Uploads**:
- Can upload files for specific conversation
- NOT persistent - files only available in that conversation
- Each conversation starts fresh

**Advantages**:
- Works on any device with browser
- Synced via cloud account
- No file management needed

**Limitations**:
- No file-based context
- Limited local integrations
- Files must be re-uploaded per conversation
- No MCP servers

---

## ChatGPT/OpenAI

**Context Method**: Hybrid (Custom Instructions + Memories)

### Custom Instructions
- **Location**: Settings → Personalization → Custom Instructions
- **Format**: Two text boxes:
  1. "What would you like ChatGPT to know about you?"
  2. "How would you like ChatGPT to respond?"
- **Persistence**: Saved to OpenAI account, available across conversations

### Memories System
- **How it works**: ChatGPT automatically saves facts when:
  - You say "remember that XYZ"
  - It infers something would be useful to remember
- **Persistence**: Available across ALL chats (not per-conversation)
- **Management**:
  - Ask: "What do you remember about me?"
  - Tell it: "Forget that I work at XYZ"
  - View/manage in Settings → Personalization → Memory
- **No file access**: Cannot edit memories file directly

**Advantages**:
- Automatic memory extraction (learns over time)
- Cross-conversation persistence
- Easy to query ("what do you remember?")

**Limitations**:
- No file-based editing (opaque system)
- Can't version control
- Must interact via chat to modify
- Memories can be inaccurate (LLM-inferred)

---

## Gemini (Google)

**Context Method**: Memories system (similar to ChatGPT)

**How it works**:
- Can tell Gemini "remember this"
- Saves facts about user, preferences
- Available across conversations
- Workspace integration has additional context (Gmail, Docs, etc.)

**Configuration**:
- No visible custom instructions field (as of Dec 2024)
- Memories managed through conversation
- Can ask "what do you know about me?"

**Status**: Less mature than ChatGPT memories, evolving rapidly

---

### Gemini in Chrome

In Settings >> Personal Context:

Learn from past chats

Gemini learns from your past chats, understanding more about you and your world to personalize your experience. Gemini Apps Activity needs to be on to use this feature. You can manage and delete your past
chats, or turn this off anytime with this setting.

---

## Cursor (AI Code Editor)

**Context Method**: File-based rules

**How it works**:
- **Project rules**: `.cursorrules` file in project root
- **Format**: Plain text or markdown
- **Scope**: Applied to AI interactions within that project
- **Persistence**: File-based, can version control

**Configuration**:
- Create `.cursorrules` in project root
- Add rules/preferences for AI behavior
- Cursor reads automatically when providing AI suggestions

**Advantages**:
- Project-specific context
- Version controlled
- Clear file to edit

**Limitations**:
- Project-only (no global user context?)
- Less documentation on format/capabilities

---

## Warp (AI Terminal)

**Context Method**: File-based (similar to Claude Code)

**How it works**:
- **WARP.md** file (location TBD - verify)
- **AGENTS.md** support (follows convention)
- **Format**: Markdown

**Status**: Need to verify exact file locations and behavior

---

## Comparison Matrix

| Agent | Method | Format | Scope | Version Control | Edit Method |
|-------|--------|--------|-------|-----------------|-------------|
| Claude Code | File | Markdown | Global + Project | Yes | Text editor |
| Claude Desktop | UI | Text | Per-project | No | Settings UI |
| Claude Web | UI | Text | Account | No | Web UI |
| ChatGPT | Hybrid | Text + Memories | Account | No | Settings + Chat |
| Gemini | Memories | Inferred | Account | No | Chat |
| Cursor | File | Text | Project | Yes | .cursorrules file |
| Warp | File | Markdown | TBD | Yes | Text editor |

---

## Key Distinctions

### File-based vs UI-based
- **File-based** (Claude Code, Cursor, Warp): User edits files directly, version controlled
- **UI-based** (Claude Desktop, Claude Web, ChatGPT): Enter in settings UI, stored in app

### Global vs Project vs Account
- **Global**: Applies to all projects on machine (Claude Code global file)
- **Project**: Specific to one codebase (Cursor .cursorrules, Claude Code project file)
- **Account**: Tied to cloud account, across devices (ChatGPT, Gemini, Claude Web)

### Static vs Dynamic
- **Static**: Fixed instructions in file/settings (Claude variants, Cursor)
- **Dynamic**: AI learns/infers over time (ChatGPT/Gemini memories)

### Editability
- **Direct file edit**: Claude Code, Cursor, Warp
- **UI settings**: Claude Desktop, Claude Web
- **Conversational**: ChatGPT, Gemini (tell it what to remember/forget)

---

## ACE Strategy Implications

Given this landscape, ACE (Agentic Context Engineering) needs to handle:

1. **File-based agents** (Claude Code, Warp, Cursor)
   - Generate/update markdown/text files
   - Deploy to specific locations
   - Support version control

2. **UI-based agents** (Claude Desktop, Claude Web)
   - Provide text for manual copy-paste
   - No automated deployment (requires user action)

3. **Memories-based agents** (ChatGPT, Gemini)
   - Generate JSON for API upload (if API available)
   - Or provide "seed conversation" to prime memories
   - Less amenable to file-based ACE

**This is why config-driven approach is needed** - different deployment methods per agent type.

---

## TODO: Research/Verify

- [ ] Warp file location and format (WARP.md vs AGENTS.md)
- [ ] Cursor global vs project context
- [ ] Gemini custom instructions (if added since last check)
- [ ] ChatGPT Code variant context handling
- [ ] Operator browser context mechanism
- [ ] Windsurf (Codeium) context handling

---

**Next steps**: Expand as we deploy to more agents and learn their mechanisms.
