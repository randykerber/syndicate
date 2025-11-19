# Cursor Trial Setup Guide

**Trial Period**: Nov 16 - Nov 24 (1 week before JetBrains renewal)
**Goal**: Evaluate Cursor v2.0 for Python/JS greenfield development vs. JetBrains

---

## Installation

### 1. Download and Install Cursor

```bash
# Visit https://cursor.com and download for macOS
# Or use Homebrew:
brew install --cask cursor
```

### 2. Initial Launch

On first launch, Cursor will:
- Import VS Code settings (if you have VS Code installed)
- Ask about telemetry preferences
- Offer to sign in (optional for trial)

**Recommendation**: Sign in with GitHub to unlock full features

### 3. Open Syndicate Project

```bash
# From terminal:
cursor /Users/rk/gh/randykerber/syndicate

# Or: File > Open Folder > Select syndicate directory
```

---

## Python Setup

### 1. Install Python Extension

Cursor is based on VS Code, so use the same extensions:

1. Open Extensions: `Cmd + Shift + X`
2. Search "Python"
3. Install "Python" extension by Microsoft
4. Install "Pylance" extension (language server)

### 2. Select Python Interpreter

1. Open command palette: `Cmd + Shift + P`
2. Type "Python: Select Interpreter"
3. Choose: `/Users/rk/gh/randykerber/syndicate/python/.venv/bin/python`

**Verify**: Bottom left of window should show "Python 3.13.x ('.venv')"

### 3. Configure Linting and Formatting

Cursor will read your `pyproject.toml` settings:
- Black formatter (line-length: 88)
- Ruff linter
- MyPy type checking

**Test**: Open `enrich_position_ranges.py` and verify:
- Syntax highlighting works
- Imports resolve correctly
- No red squiggles on valid code

---

## JavaScript/TypeScript Setup

### 1. Extensions Already Built-In

Cursor includes TypeScript support by default. No additional extensions needed.

### 2. Verify TypeScript Configuration

1. Navigate to `js/` directory
2. Open `src/agents/reminder-agent.ts`
3. Check that:
   - IntelliSense works (hover over functions)
   - Type errors show up
   - Imports autocomplete

---

## Cursor-Specific Configuration

### 1. Project Rules (.cursorrules)

A `.cursorrules` file has been created in the project root with:
- Python/TypeScript best practices
- Project-specific context (Hedgeye pipeline, SSS agents)
- Code style preferences
- Security guidelines

**Location**: `/Users/rk/gh/randykerber/syndicate/.cursorrules`

### 2. Cursor Ignore (.cursorignore)

Similar to `.gitignore`, tells Cursor what to exclude from AI context:
- `node_modules/`, `.venv/`, build artifacts
- Large data files in `/Users/rk/d/downloads/hedgeye/`

**Location**: `/Users/rk/gh/randykerber/syndicate/.cursorignore`

### 3. Cursor Settings

Open Cursor Settings: `Cmd + Shift + J`

**Recommended Settings**:

**Features > Cursor Tab:**
- ✅ Enable Cursor Tab (AI autocomplete)
- ✅ Enable partial accepts (Cmd + Right Arrow)
- ✅ Enable prediction for edit flow

**Features > Chat:**
- ✅ Auto scroll chat
- ❌ Default to no context (we WANT context)
- ✅ Show chat history when starting new chat

**Beta Features:**
- ✅ Long Context Chat (for large codebases)
- ✅ Composer (the new agentic model)

**Models:**
- Default model: Claude 3.5 Sonnet (best for code understanding)
- Fast model: cursor-small (unlimited, good for simple tasks)
- For long context: claude-3.5-sonnet-200k

---

## Core Cursor Features to Learn

### 1. Chat (Cmd + L)

**What it does**: Conversational AI about your code
**When to use**:
- "Explain how enrich_position_ranges.py works"
- "What does this error mean?"
- "How do I add a new data source?"

**Try now**:
1. Press `Cmd + L`
2. Type: "Explain the Hedgeye data pipeline flow"
3. Watch it reference CLAUDE.md and ranges-flow.md

### 2. Inline Edit (Cmd + K)

**What it does**: Edit code at cursor position
**When to use**:
- Quick refactors
- Writing new functions
- Fixing bugs

**Try now**:
1. Open `fetch_prices.py`
2. Place cursor in `fetch_current_prices()` function
3. Press `Cmd + K`
4. Type: "Add logging for each price fetch attempt"
5. Review the diff, press `Cmd + Enter` to accept

### 3. Cursor Tab (Tab key)

**What it does**: AI-powered autocomplete (like GitHub Copilot++)
**When to use**: Always active while typing

**Try now**:
1. Create new file: `test_cursor.py`
2. Type: `def fetch_stock_price(symbol: str):`
3. Press Enter and wait ~1 second
4. Cursor will suggest the function body as grey text
5. Press Tab to accept, or Esc to reject

### 4. Composer (NEW in v2.0)

**What it does**: Multi-file agentic coding (like Claude Code, but in IDE)
**When to use**:
- Complex refactors across multiple files
- Building new features
- Large-scale changes

**Try when ready**: This is the "killer feature" - we'll test it when new EPP email arrives

---

## Keyboard Shortcuts (Essential)

| Command | Shortcut | What It Does |
|---------|----------|--------------|
| Chat | `Cmd + L` | Open AI chat pane |
| Inline Edit | `Cmd + K` | Edit code at cursor |
| Accept Suggestion | `Tab` | Accept Cursor Tab suggestion |
| Reject Suggestion | `Esc` | Reject Cursor Tab suggestion |
| Partial Accept | `Cmd + →` | Accept next word only |
| Command Palette | `Cmd + Shift + P` | Search all commands |
| Cursor Settings | `Cmd + Shift + J` | Open Cursor-specific settings |
| Go to File | `Cmd + P` | Quick file navigation |
| Toggle Terminal | `Ctrl + \`` | Show/hide integrated terminal |

---

## JetBrains Migration Tips

### What You'll Miss from IntelliJ

1. **Deep refactoring tools**: Cursor has basic refactoring, not IntelliJ-level
2. **Database tools**: No DataGrip equivalent (but you weren't using it anyway)
3. **Advanced static analysis**: Cursor relies more on AI, less on compile-time checks
4. **Scala support**: Cursor + Metals works, but not as polished as IntelliJ

### What You Gain with Cursor

1. **AI-first workflow**: Chat, Tab, Composer are seamless
2. **Speed**: Lighter weight, faster startup, faster search
3. **Multi-language**: Python + JS + TypeScript in one tool
4. **Composer**: Agentic coding that actually works well
5. **Free tier**: Can try without paying first

### Muscle Memory Changes

| JetBrains | Cursor | Action |
|-----------|--------|--------|
| `Cmd + Option + L` | `Shift + Option + F` | Format document |
| `Shift Shift` | `Cmd + P` | Search everywhere |
| `Cmd + E` | `Ctrl + R` | Recent files |
| `Cmd + B` | `F12` | Go to definition |
| `Cmd + Option + B` | `Shift + F12` | Go to implementation |

**Tip**: You can customize these in Settings > Keyboard Shortcuts

---

## Trial Evaluation Checklist

Use this to track your experience over the week:

### Day 1-2: Basic Familiarity
- [ ] Set up Python interpreter and verify code runs
- [ ] Set up TypeScript and verify builds work
- [ ] Try Chat (Cmd + L) on 3+ different questions
- [ ] Try Inline Edit (Cmd + K) for small changes
- [ ] Get comfortable with Tab autocomplete

### Day 3-4: Real Work
- [ ] Process new EPP email (when it arrives) using Cursor
- [ ] Use Composer for multi-file task
- [ ] Compare speed vs. JetBrains for Python work
- [ ] Test refactoring tools (rename, extract method)

### Day 5-7: Deep Evaluation
- [ ] Build something new (e.g., new data enrichment feature)
- [ ] Fix a bug using AI assistance
- [ ] Evaluate: Does AI compensate for missing IDE features?
- [ ] Evaluate: 30-40% productivity gain claimed - true for you?

### Deal-Breakers to Watch For
- [ ] Does Cursor slow down with large files?
- [ ] Do subtle bugs from AI suggestions waste more time than they save?
- [ ] Do you constantly wish you had IntelliJ refactoring?
- [ ] Is the VS Code paradigm too different from JetBrains?

---

## When New EPP Email Arrives

This is your **key test**. Last time you:
1. Ran `process_etf_pro_weekly.py` (email → CSV)
2. Ran `merge_position_ranges.py` (merge data sources)
3. Ran `enrich_position_ranges.py` (fetch prices, calculate ranges)

**Try this workflow in Cursor:**

1. Open Chat (Cmd + L)
2. Prompt: "New EPP email arrived at [path]. Run the full pipeline: parse email → merge ranges → enrich with prices. Explain what you're doing at each step."
3. Watch Composer work across files
4. Compare to how you'd do it in IntelliJ + Claude Code

**Questions to ask yourself:**
- Was Composer faster than switching between IntelliJ and terminal?
- Did the AI understand the pipeline without you explaining?
- Did it make mistakes that IntelliJ's type checking would have caught?

---

## Getting Help

**Cursor Documentation**: https://cursor.com/docs
**Cursor Forum**: https://forum.cursor.com
**Awesome Cursor Rules**: https://github.com/PatrickJS/awesome-cursorrules

**Common Issues:**
- **Slow autocomplete**: Try switching to cursor-small model
- **Wrong file context**: Use @ symbol in Chat to specify files
- **AI not understanding project**: Check .cursorrules is being used

---

## Decision Framework (Nov 24)

### Option A: Cursor Pro + IntelliJ IDEA
**Cost**: $240/year + $149/year = $389/year
**Use**: Cursor for Python/JS, IntelliJ for Scala
**Choose if**: Cursor feels transformative for Python/JS work

### Option B: Keep JetBrains All Products Pack
**Cost**: $179/year
**Use**: IntelliJ/PyCharm, Claude Code on side
**Choose if**: Cursor didn't click or need more evaluation time

### Key Questions
1. Did Cursor make Python development noticeably faster?
2. Do you feel confident debugging without IntelliJ's tools?
3. Was Composer worth $240/year?
4. Can you see yourself using Cursor daily for 6+ months?

If 3+ answers are "yes" → Try Option A
If 2 or fewer → Stick with Option B for another year

---

## Quick Start Checklist

Before you dive in:
- [ ] Install Cursor
- [ ] Open Syndicate project
- [ ] Select Python interpreter (.venv)
- [ ] Install Python extension
- [ ] Verify TypeScript works
- [ ] Review .cursorrules file
- [ ] Try Chat (Cmd + L) with a question
- [ ] Try Inline Edit (Cmd + K) on a small change
- [ ] Enable Cursor Tab and test autocomplete
- [ ] Read through keyboard shortcuts

**You're ready!** Start using Cursor for real work and track your experience.
