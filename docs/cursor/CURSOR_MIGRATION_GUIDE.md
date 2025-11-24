# Cursor Migration Guide - JetBrains to Cursor

**Date**: November 2025  
**From**: JetBrains IntelliJ Ultimate + Claude Code  
**To**: Cursor IDE

---

## ✅ Pre-Migration Checklist

### Already Complete
- ✅ Cursor installed (`/opt/homebrew/bin/cursor`)
- ✅ Python environment set up with `uv` (Python 3.13.9)
- ✅ Dependencies synced (`uv sync` completed)
- ✅ `.cursorrules` configured (400+ lines of project context)
- ✅ `.cursorignore` configured (optimized AI context)
- ✅ Context7 MCP server configured in `~/.cursor/mcp.json`

---

## 🚀 Step-by-Step Migration

### Step 1: Open Project in Cursor

```bash
# From terminal:
cursor /Users/rk/gh/randykerber/syndicate

# Or: File > Open Folder in Cursor
```

### Step 2: Configure Python Interpreter

1. **Open Command Palette**: `Cmd + Shift + P`
2. **Type**: "Python: Select Interpreter"
3. **Choose**: `/Users/rk/gh/randykerber/syndicate/python/.venv/bin/python`

**Verify**: Bottom-left corner should show "Python 3.13.9 ('.venv')"

### Step 3: Install Python Extensions

1. **Open Extensions**: `Cmd + Shift + X`
2. **Install**:
   - "Python" by Microsoft
   - "Pylance" by Microsoft (language server)

**Why**: Cursor is based on VS Code, so it uses VS Code extensions for language support.

### Step 4: Verify TypeScript/JavaScript

1. Open `js/src/agents/reminder-agent.ts`
2. Hover over functions - IntelliSense should work
3. Check for type errors (should show in Problems panel)

**Note**: TypeScript support is built into Cursor, no extension needed.

### Step 5: Test Package Management with `uv`

**Important**: Always use `uv` commands, never `pip` or `python -m venv`.

```bash
# Install dependencies (already done, but for reference):
cd python
uv sync

# Add new package:
uv add package-name

# Add dev dependency:
uv add --dev package-name

# Run Python script:
uv run python scripts/hedgeye/run_full_pipeline.py

# Run with specific Python version:
uv run --python 3.13 python script.py
```

**Cursor Integration**: When you run scripts in Cursor's terminal, use `uv run` prefix:
- ✅ `uv run python script.py`
- ❌ `python script.py` (won't use project venv)

### Step 6: Configure Cursor Settings

**Open Cursor Settings**: `Cmd + Shift + J`

**Recommended Settings**:

**Features > Cursor Tab:**
- ✅ Enable Cursor Tab (AI autocomplete)
- ✅ Enable partial accepts (`Cmd + →`)
- Model: `cursor-small` for speed (unlimited) or `claude-3.5-sonnet` for quality

**Features > Chat:**
- ✅ Auto scroll chat
- ✅ Show chat history when starting new chat
- Default model: `claude-3.5-sonnet`

**Beta Features:**
- ✅ Long Context Chat
- ✅ Composer (multi-file agentic coding)

### Step 7: Test Core Cursor Features

#### A. Chat (`Cmd + L`)
Try: "Explain how the Hedgeye data pipeline works from email to enriched CSV"

#### B. Inline Edit (`Cmd + K`)
1. Open `python/src/syndicate/data_sources/hedgeye/fetch_prices.py`
2. Place cursor in a function
3. `Cmd + K`
4. Type: "Add a comment explaining the three-tier fallback strategy"
5. Review diff, `Cmd + Enter` to accept

#### C. Tab Autocomplete
1. Create new file: `test_cursor.py`
2. Type: `def calculate_percentage_from_range(current: float, low: float, high: float) -> float:`
3. Press Enter, wait ~1 second
4. Tab to accept grey suggestion

---

## 🔄 JetBrains to Cursor Workflow Mapping

### Package Management

| JetBrains | Cursor |
|-----------|--------|
| PyCharm package manager | `uv add package-name` |
| Terminal: `python script.py` | Terminal: `uv run python script.py` |
| Run configuration | Use `uv run` in terminal or create tasks |

### Running Scripts

**JetBrains**: Right-click → Run  
**Cursor**: 
- Terminal: `uv run python scripts/hedgeye/run_full_pipeline.py`
- Or create task in `.vscode/tasks.json` (optional)

### Debugging

**JetBrains**: Built-in debugger with breakpoints  
**Cursor**: 
- Install "Python Debugger" extension
- Use `F5` to start debugging
- Set breakpoints by clicking left margin

### Refactoring

**JetBrains**: `Shift + F6` (Rename), `Cmd + Option + M` (Extract Method)  
**Cursor**: 
- Use Chat (`Cmd + L`): "Rename this function to X"
- Use Inline Edit (`Cmd + K`): "Extract this into a separate function"
- Or use VS Code refactoring: `F2` (Rename), `Cmd + Shift + R` (Refactor)

### File Navigation

| JetBrains | Cursor |
|-----------|--------|
| `Shift Shift` (Search Everywhere) | `Cmd + P` (Quick Open) |
| `Cmd + E` (Recent Files) | `Ctrl + R` (Recent Files) |
| `Cmd + B` (Go to Definition) | `F12` (Go to Definition) |
| `Cmd + Option + B` (Implementations) | `Shift + F12` (Find References) |

---

## 🧪 Testing Your Migration

### Test 1: Python Script Execution

```bash
cd /Users/rk/gh/randykerber/syndicate/python
uv run python -c "from hedgeye.pipeline import run_full_pipeline; print('✓ Import works')"
```

### Test 2: Hedgeye Pipeline

When you have a new EPP email:
1. Open Chat (`Cmd + L`)
2. Say: "New EPP email at [path]. Run the full pipeline: parse → merge → enrich"
3. Watch Composer handle it (or guide it step-by-step)

### Test 3: Type Checking

```bash
cd python
uv run mypy src/syndicate/data_sources/hedgeye/fetch_prices.py
```

### Test 4: Formatting

```bash
cd python
uv run black --check src/
uv run ruff check src/
```

---

## 📝 Environment Variables

Make sure these are set in your shell or `.env` files:

```bash
# Check if set:
echo $CONTEXT7_API_KEY
echo $TAVILY_API_KEY
echo $BRAVE_API_KEY

# If not set, add to ~/.zshrc or project .env file
```

**For Cursor**: Environment variables from your shell are inherited. For scripts, use `python-dotenv` to load from `.env` files.

---

## 🎯 Daily Workflow in Cursor

### Starting Work
1. Open Cursor: `cursor /Users/rk/gh/randykerber/syndicate`
2. Verify Python interpreter (bottom-left)
3. Open terminal: `` Ctrl + ` ``
4. Navigate to python: `cd python`

### Running Scripts
```bash
# Always use uv run:
uv run python scripts/hedgeye/parse_emails.py
uv run python scripts/hedgeye/run_full_pipeline.py

# Or run modules:
uv run python -m hedgeye.pipeline
```

### Using AI Features
- **Quick question**: `Cmd + L` → Ask about code
- **Edit code**: `Cmd + K` → Describe change
- **Multi-file task**: Use Composer (beta feature)
- **Autocomplete**: Just type, Tab to accept

### Debugging
1. Set breakpoint (click left margin)
2. `F5` to start debugging
3. Select "Python Debugger"
4. Choose script to debug

---

## ⚠️ Common Issues & Solutions

### Issue: "Python interpreter not found"
**Solution**: 
1. `Cmd + Shift + P` → "Python: Select Interpreter"
2. Choose: `python/.venv/bin/python`

### Issue: "Module not found" when running scripts
**Solution**: Always use `uv run python script.py` instead of `python script.py`

### Issue: "uv: command not found"
**Solution**: 
```bash
brew install uv
# Or: curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Issue: AI doesn't understand project context
**Solution**: 
- Check `.cursorrules` exists in project root
- Use `@filename` in Chat to reference specific files
- Restart Cursor if needed

### Issue: Slow autocomplete
**Solution**: 
- Settings (`Cmd + Shift + J`) → Models
- Switch to `cursor-small` for faster, unlimited suggestions

---

## 📊 Migration Success Criteria

After 1 week, you should be able to:
- ✅ Run all Hedgeye pipeline scripts using `uv run`
- ✅ Use Chat to understand and modify code
- ✅ Use Inline Edit for quick changes
- ✅ Navigate codebase efficiently
- ✅ Debug Python code effectively
- ✅ Feel productive (or know it's not for you)

---

## 🔗 Quick Reference

**Essential Shortcuts**:
- Chat: `Cmd + L`
- Inline Edit: `Cmd + K`
- Accept Tab: `Tab`
- Command Palette: `Cmd + Shift + P`
- Go to File: `Cmd + P`
- Terminal: `` Ctrl + ` ``

**Package Management** (always use `uv`):
- `uv sync` - Install dependencies
- `uv add package` - Add package
- `uv run python script.py` - Run script
- `uv run black .` - Format code
- `uv run ruff check .` - Lint code

**Documentation**:
- Quick Start: `docs/cursor-quick-start.md`
- Setup Guide: `docs/cursor-trial-setup.md`
- Evaluation: `docs/cursor-vs-jetbrains-evaluation.md`

---

## ✨ Next Steps

1. **Complete Steps 1-7 above** (15 minutes)
2. **Test core features** (10 minutes)
3. **Try real work**: Process an EPP email using Cursor
4. **Track experience**: Fill in `docs/cursor-vs-jetbrains-evaluation.md` daily
5. **Decide by Nov 24**: Option A, B, or C

**Remember**: This is a trial. Use Cursor for real work, track honestly, and decide based on your actual productivity.

Good luck! 🚀

