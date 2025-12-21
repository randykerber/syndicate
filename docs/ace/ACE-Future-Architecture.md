# ACE Future Architecture - Planning Notes

**Date**: 2025-12-21
**Status**: Discovery/Planning (not implemented)
**Purpose**: Preserve findings about agent variants and future config-driven architecture

---

## The Problem: Agent Variant Explosion

### Current Landscape (Dec 2025)

**Claude (Anthropic)** - 3 variants:
- Web (claude.ai) - Basic conversational, no local access
- Desktop - Conversational + MCP servers + local integrations
- Code - Terminal CLI, coding-focused, git workflows

**ChatGPT/OpenAI** - 5+ variants:
- Web (chatgpt.com)
- Desktop app
- Browser extension
- Operator - AI web browser (NEW)
- Codex/coding integrations

**Gemini (Google)** - 4+ variants:
- Web (gemini.google.com)
- Workspace (Docs, Gmail)
- Project Mariner - Chrome agent (NEW, experimental)
- CLI (if exists)

**Perplexity** - 2 variants:
- Web
- Perplexity Browser (NEW)

**Others**:
- Arc (browser with AI)
- Warp (terminal)
- Cursor (editor)
- Windsurf (Codeium editor)
- GitHub Copilot

### Emerging Categories (Capability-Based, Not Product-Based)

1. **Basic conversational** - Web chat, minimal context
2. **Enhanced conversational** - Desktop apps with MCP/local integrations
3. **Browser agents** - Navigate/interact with web (Operator, Mariner)
4. **Coding assistants** - IDEs, terminals (Cursor, Code, Warp)
5. **Workspace-integrated** - In productivity tools (Gemini in Docs)

**Key insight**: Can't organize by product ("Claude", "Gemini") - each has 3-5 variants with different needs.

---

## Core Distinction: What vs How/Where/When

### The "What" - Information That Just Exists

Data about user:
- Core identity (name, location, expertise)
- Preferences (coding style, response format)
- Background/context (tools, subscriptions, projects)
- Personal (hobbies, interests)
- Environment (hardware, software versions)

This information is **invariant** - it doesn't change based on which tool accesses it.

### The "How/Where/When" - Delivery Mechanism

**Different tools want same information delivered differently**:

1. **ACF file** (Claude Code, Cursor)
   - Markdown file in config directory
   - Read on startup

2. **Memories UI** (ChatGPT, Gemini conversational)
   - JSON uploaded via API
   - Stored in cloud, retrieved on-demand

3. **Settings panel** (Cursor, IDEs)
   - Pasted into preferences UI
   - Stored in app settings

4. **Don't want it** (Some coding tools)
   - Only need coding context, not personal

5. **MCP Server** (Future)
   - Real-time query via Memory-as-a-Tool
   - Retrieved when needed, not loaded upfront

**Problem**: Same data, 5 different delivery mechanisms.

---

## The Right Solution (Eventually): Config-Driven System

### Vision: YAML/JSON Manifests

Each agent variant gets a config specifying:
- What content to include
- How to format it
- Where to deliver it
- When to update it

```yaml
# claude-code.yaml
agent_id: claude-code
profile: coding-assistant

content:
  include:
    - core-identity
    - coding-preferences
    - subscriptions
    - scratch-directory-practices
  exclude:
    - personal
    - hobbies

format:
  type: markdown
  sections: [common, agent-specific, info]

deployment:
  method: file
  path: ~/.claude/AGENTS.md
  symlink: CLAUDE.md -> AGENTS.md
  backup: true

update:
  trigger: manual  # or: on-commit, daily, etc.
```

```yaml
# chatgpt-web.yaml
agent_id: chatgpt-web
profile: conversational

content:
  include:
    - core-identity
    - personal
    - hobbies
  exclude:
    - coding-details
    - scratch-practices

format:
  type: json-memories

deployment:
  method: api-upload
  endpoint: https://api.openai.com/v1/memories

update:
  trigger: on-change
```

### Builder Architecture

```
ACE Build System:
├── content/ (the "what")
│   ├── core-identity.md
│   ├── preferences.md
│   ├── subscriptions.md
│   └── ...
├── profiles/ (capability templates)
│   ├── coding-assistant.yaml
│   ├── conversational.yaml
│   └── browser-agent.yaml
├── agents/ (specific configs)
│   ├── claude-code.yaml
│   ├── claude-desktop.yaml
│   ├── chatgpt-web.yaml
│   └── ...
└── builders/
    ├── markdown_builder.py
    ├── json_builder.py
    ├── api_uploader.py
    └── ...
```

**Process**:
1. Read agent config (claude-code.yaml)
2. Gather content files per include/exclude rules
3. Select builder based on format
4. Build artifact
5. Deploy via specified method

---

## Why We're NOT Doing This Now

**Reality check**:
- This is **days/weeks of work**
- Only have 1 agent variant actually deployed (Claude Code)
- Other variants are hypothetical/future
- **Adds to productivity deficit** instead of reducing it
- Classic yak shaving - infrastructure over real wins

**Current need**:
- Get subscriptions.md into Claude Code build (1 hour)
- Get back to Drafts/productivity wins (hours to days of saved time)

**Right time to build config system**:
- Have 3+ agent variants **actually deployed** (not planned)
- Manual approach becomes painful (maintaining 3+ builds by hand)
- Have real productivity wins banked (not just infrastructure)
- User has dedicated time for infrastructure (not stealing from productivity)

---

## Minimal Viable Today (To Ship)

**Goal**: Improve Claude Code context without architecture project

**Scope**:
1. Add subscriptions.md to Claude Code build
   - Extend builder to include `info/` files
   - Or inline subscriptions into COMMON.md
2. Rebuild CLAUDE.md with updated content
   - Max subscription info
   - Scratch directory practices (already in COMMON.md)
3. Deploy to ~/.claude/AGENTS.md (follow convention)
   - Symlink CLAUDE.md -> AGENTS.md

**Then STOP** and return to Drafts productivity wins.

---

## Memory Types Taxonomy (From Google Report)

**Google report says**:
- **Declarative Memory**: "Knowing what" - facts, preferences, relationships
- **Procedural Memory**: "Knowing how" - workflows, patterns, behaviors

**Problem**: Report conflates "preferences" with all declarative memory, but examples include facts and context too.

**Our more granular taxonomy**:
1. **Core Identity** - Immutable facts (name, location, expertise, hardware)
2. **Preferences** - How they want things done (style, format, workflows)
3. **Background/Context** - What they use/know (tools, projects, not preferences)
4. **Personal** - Non-work interests (hobbies, recreation)
5. **Environment** - Current state (installed software, active projects)

This is clearer than lumping everything into "Declarative Memory = Preferences."

---

## Open Questions (For Future)

1. **AGENTS.md adoption**: When will Claude/Anthropic officially support it?
2. **Warehouse structure**: How to organize for shared content across variants?
   - Option: `warehouse/agents/claude/common/` + `code/`, `desktop/`, `web/`
3. **Memory retrieval**: When to use MCP Memory-as-a-Tool vs ACF files?
4. **Update frequency**: How often to rebuild ACFs? Manual? On git commit?
5. **Multi-machine**: How to sync ACFs across machines (rstudio, idlewood)?

---

## References

- Google Context Engineering whitepaper (Nov 2025)
- AGENTS.md spec: https://agents.md/
- ACE documentation: `docs/ace/INDEX-Context-Engineering.md`

---

**Next Action**: Implement minimal viable (subscriptions.md in builder), then pivot to Drafts productivity wins.

**Last Updated**: 2025-12-21
