---
id: project.sss
updated: 2025-08-26
scope: project
---

# Silo-Slayer Syndicate System (SSS)

**Mission:** “Information liberation” — break app/data silos via AI agents + MCP tools; use English-as-Programming to extract parameters, call tools, and resolve ambiguity via human-in-the-loop.

## Architecture (hybrid)
- **Python**: agent orchestration, MCP servers, session persistence.
- **JavaScript/TypeScript**: native integrations (Raycast, Drafts, Obsidian), UI.
- **MCP**: language-agnostic bridge to tools.

## Core Patterns
- **Parameter extraction** → multi-turn clarification when needed.
- **Human queue** (file-based async) + push via Pushover.
- **Session persistence** (SQLite): keep cross-turn memory.

## Repos & Paths
- Main repo: `~/gh/randykerber/syndicate/`
- Drafts triage; Obsidian (**Main** & **Tech** vaults on iCloud)

## Now / Next
- **Now:** end-to-end demo with simulated disambiguation → real tool calls.
- **Next:** connect production tool chain (Drafts → Obsidian/Bear/1Password); validate push flow; expand agent templates.

## Success Metrics
1) Parameter extraction accuracy  
2) Human collaboration effectiveness  
3) Tool execution reliability  
4) Reduction in “silo friction”
