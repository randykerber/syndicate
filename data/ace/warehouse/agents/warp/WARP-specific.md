# WARP-specific Context

Warp-specific configuration, behavior patterns, and features.

---

## Terminal & Shell

- **Terminal**: Warp (Pro)
- **Shell**: zsh (interactive), bash (for shell scripts)

---

## Warp AI Behavior Contract

### Plan-Then-Execute Pattern

1. **Output a PLAN** first — What, why, where
2. **Show COMMANDS** — Exact commands to run
3. **Ask CONFIRM** — Before destructive/state-changing operations
4. **Prefer safety** — Use `--dry-run`, `echo > tee`, idempotent ops

### Response Style

- **Concise and direct** — No unnecessary preambles
- **Structured** — Markdown headings, bullet points, tables for data
- **Technical depth when needed** — Explain complex operations
- **Action-oriented** — Focus on next steps
- **Brief summaries** — For non-trivial outputs

### Path Handling

- **Default working dir**: Projects under `~/gh/randykerber/<project>`
- **Never write** into dotfiles or global config without approval
- **Use relative paths** when in project context
- **Use absolute paths** for system-level files

---

## Git with Warp

**Use `--no-pager`** for Warp compatibility:
```bash
git --no-pager diff
git --no-pager log --oneline -10
```

---

## Secrets Management

**Critical Rule**: NEVER reveal or consume secrets in plain-text in terminal commands.

**Pattern**:
```bash
# Step 1: Store secret in environment variable
API_KEY=$(op read "op://vault/item/field")

# Step 2: Use variable in subsequent commands
curl -H "Authorization: Bearer $API_KEY" https://api.example.com

# NEVER echo or print the secret value
```

**For redacted user input**: If user provides `***`, replace with `{{SECRET_NAME}}` placeholder in suggestions.

---

## Warp-Specific Features

### Keybindings

Custom keybinding configured in `~/.config/warp/keybindings.yaml`:
- `tab` → Open completion suggestions

### Workflows

- **Command suggestions** — Prefer showing exact commands over explanations
- **Multi-step operations** — Break into discrete, reviewable steps
- **Dangerous operations** — Always show plan + confirmation request
- **Error explanations** — Parse errors and suggest fixes

---

## Warp AI Role

### When to Use Warp AI

- Terminal-first workflows
- Command suggestions and explanations
- Shell scripting assistance
- System administration tasks
- Quick coding tasks in terminal context

### Context Files

- **Global**: `~/.config/warp/WARP.md`
- **Project**: `<project>/.warp/WARP.md`

---

## Configuration Paths

```
~/.config/warp/                               # Warp config directory
~/.config/warp/WARP.md                        # This context file
~/.config/warp/keybindings.yaml               # Custom keybindings
~/Library/Preferences/dev.warp.Warp-Stable.plist  # Warp preferences (binary)
```

---

**End of WARP-specific.md**