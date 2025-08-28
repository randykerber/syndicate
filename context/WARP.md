---
id: context.warp.global
owner: Randy Kerber
updated: 2025-08-26
scope: global
---

# Warp AI — Global Context (Randy Kerber)

## Who I Am
- **Name:** Randy Kerber
- **Location:** Cañon City, Colorado (America/Denver)
- **Role:** AI/Data Engineer & Software Developer
- **Stack:** Python, JavaScript/TypeScript, Scala
- **Bio (short):** Software developer with decades across AI, data engineering, and developer tooling.

## System & Dev Environment
- **OS:** macOS 15 (assume latest point release)
- **Shell:** `bash 5.3` (preferred over zsh)
- **Terminal:** Warp (Pro)
- **Editors/IDEs:** IntelliJ IDEA Ultimate (+ JetBrains suite), Emacs
- **Browsers:** Arc (primary), Chrome, Safari
- **Package managers:** `uv` (Python), `npm` (JS/TS), Homebrew (system)
- **Security:** 1Password + Apple Passwords + Authy (no secrets in shell history)

## Repositories & Paths (convention)
- Git root: `~/gh/randykerber/`
- Active projects:
  - `syndicate/` — Silo-Slayer Syndicate System (SSS)
  - `raycast-ext/` — Raycast extensions (TS)
  - `hedgeye-kb/` — Hedgeye Risk Range automation & KB

## Knowledge & Context
- **PKM:** Obsidian (iCloud). Vaults: **Main** (investing/finance) and **Tech** (computing/AI/tools).
- **Context Pack:** maintained as Markdown in `context/` inside the vault; deployed (copied) to:
  - `~/.claude/CLAUDE.md`
  - `~/.warp/WARP.md` (this file)
  - `~/gh/randykerber/syndicate/context/` (read-only consumer)

## Versions (assume latest unless I say otherwise)
- IntelliJ IDEA **2025.2** · Node **24.6.x** · npm **11.5.x** · TypeScript **5.9.x** · Python **3.13** · Obsidian **1.9.11**

---

## Behavior Contract (Warp AI)
> **Do not execute** destructive/system-wide changes without confirmation.

1) **Plan–Then–Run**
   - First output a **PLAN** (what, why, where), then a **COMMANDS** block.
   - Ask for **CONFIRM** before running anything that writes/installs/changes state.
   - Prefer `--dry-run`, `echo` > `tee`, and idempotent operations.

2) **Paths & Projects**
   - Default working dir to a project under `~/gh/randykerber/<project>`.
   - Never write into dotfiles or global config without approval.

3) **Python**
   - Use **`uv`** for environments and deps (no global installs).
   - Commands: `uv init`, `uv add`, `uv run`, `uv sync`.

4) **JavaScript / TypeScript**
   - Use **local** installs with `npm` (avoid global `-g` unless I say so).
   - Provide `npm scripts` when sensible.

5) **System Packages**
   - Use **Homebrew**; propose updates before running them.

6) **Secrets**
   - Pull via **1Password** (e.g., `op run -- <command>`) when needed; never print tokens.

7) **Mismatch Handling**
   - If steps don’t match my UI/version, **pause and ask** for a quick screen/dir listing.

---

## Common Commands & Snippets

### Git & bootstrap
```bash
cd ~/gh/randykerber/syndicate
git status
git add -A && git commit -m "…" && git pull --rebase && git push origin main
```

### Python (uv)
```bash
uv sync
uv add duckdb
uv add --dev ruff pytest
uv run python -m pytest -q
```

### JavaScript / TypeScript
```bash
npm install
npm run build
```

### Homebrew (propose first)
```bash
brew update
brew upgrade <formula>
```

---

## Preferences
- **Style:** brief, structured; Markdown headings & short lists; tables for structured output.
- **Explain when useful**, but prefer shipping commands + next steps.
- **Ask before** long-running or state-changing operations.
- Provide a short **Summary** at the end of non-trivial outputs.

## Focus Areas (current)
- SSS agent network (OpenAI Agents SDK; MCP tool integration; human-in-the-loop)
- Hedgeye Risk Range automation & KB
- Investing data warehouse (ticker-level)
- Context Engineering (shared context across assistants)
- Starlink evaluation
