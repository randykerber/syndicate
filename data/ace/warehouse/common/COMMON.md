# COMMON.md - Shared Context Across All AI Tools

**Last Updated**: 2025-12-12
**Purpose**: Core identity, environment, tools, and preferences shared by all AI assistants

---

## CRITICAL RULES

### TRUTH OVER SPEED (Non-Negotiable)

**RULE: TRUTH OVER SPEED IS NON-NEGOTIABLE.**

Under no circumstances should any response be fabricated, simplified, or stated as successful if the underlying action failed or is uncertain.
- **FAILURE MODE**: If code fails, state the failure and explicit reason (error trace, missing dependency)
- **PRIORITY**: Do not prioritize speed, convenience, or perceived user satisfaction over **technical correctness** or **factual integrity**

### Anti-Stale Information Mandate

- **Default Environment**: Assume the user operates on the **latest available stable release** of all software
- **Currency Constraint**: Solutions involving APIs, specific library versions, or tool settings **must be verified** using external search tools to account for changes since knowledge cutoff
- **Verification Failure**: If a solution cannot be immediately verified as current, begin with: **"WARNING: Stale Information Risk"**

---

## About Me

**Name**: Randy Kerber
**Mac username**: rk
**Location**: Cañon City, Colorado (America/Denver timezone)
**Expertise**: Python, Scala, Apache Spark, TypeScript/JavaScript, Knowledge Graphs, Data Pipelines, Finance/Investing
**Preferred Formats**: Parquet (dataframe persistence), Markdown (general text)

---

## Hardware & Operating Systems

### Primary Machine: Mac Studio (rstudio)
- **Chip**: Apple M4 Max (16-core CPU, 40-core GPU, 16-core Neural Engine)
- **Memory**: 64GB unified memory
- **Storage**: 1TB SSD
- **OS**: macOS 26 "Tahoe"
- **Hostname**: rstudio
- **Use**: Main development workstation, heavy compute, long-running processes

### Secondary Machine: MacBook Pro (idlewood)
- **Chip**: Intel
- **Memory**: 32GB
- **Storage**: 2TB SSD
- **OS**: macOS 15
- **Hostname**: idlewood
- **Use**: Mobile work, meetings, quick edits, legacy system access

### Mobile Devices
- **iPhone**: iPhone 15 Pro
- **iPad**: iPad Pro 2024 with Pencil Pro

---

## Development Tools & Environment

### Terminal & Shell
- **Terminal**: Warp (Pro) - primary terminal application
- **Shell**: zsh (interactive), bash (for shell scripts)

### Code Editors & IDEs
- **IntelliJ IDEA Ultimate**: Scala, Python, JavaScript, Shell init
- **Cursor Pro**: Python, JavaScript
- **Emacs**: General editing, file browsing, edit files over-interpreted by IDEs.

### Primary Productivity Tools
- **Web Browser**: Arc (default), Chrome, ChatGPT Atlas, Comet
- **Launcher**: Raycast - universal launcher across Mac/iPhone/iPad
- **Voice Input**: Superwhisper, Wispr Flow, Apple built-in
- **Task Management**: Things (horizon-based task grouping), Apple Reminders (alerts/deadlines only)
- **Passwords**: 1Password + Apple Passwords + Authy
- **Primary PKM**: Obsidian with Obsidian Sync (cross-device)
  - **Vaults**:
    - Tech: Computing & Technology
    - Fin: Financial & Investing
- **Secondary PKM**: Bear (personal info, non-Tech/non-Fin content)
- **Quick Capture Notes**: Drafts (universal inbox), Bear, Apple Notes (system integration)
- **Voice Input**: Superwhisper, Wispr Flow, Apple built-in


### AI Coding Tools & Roles
- **Claude Desktop (CD)**: Conversational work, file access, integrations, Task management (Things), Mac automation
- **Claude Code (CC)**: Development work, terminal-based coding, debugging, repository analysis
- **Cursor Composer**: Agentic AI coding for Python/JS
- **JetBrains Intellij IDEA Ultimate**: Coding, complex refactoring.
- **Warp AI**: Terminal-first workflows, command suggestions, shell scripting
- **Gemini**: Multi-platform access, large context window, compute-per-cost
- **Perplexity**: Web-search for current year topics, financial queries.
- **ChatGPT**: Default AI Assistant for personal, non-computing topics. High-level analysis and 
  planning.

---

## Development Stack

### Python (Primary Language)
- **Package Manager**: **uv** (MANDATORY - modern, fast, standard for all Python work)
- **NEVER use**: `pip install`, `python -m venv` - always use uv
- **Virtual Environments**: Managed by uv
- **Common Commands**:
  ```bash
  uv sync                    # Install dependencies from pyproject.toml
  uv add package-name        # Add new dependency
  uv remove package-name     # Remove dependency
  uv lock --upgrade && uv sync  # Update packages
  uv run python script.py    # Run with project venv
  uv run pytest              # Run tests
  uv run ipython             # Interactive Python
  ```
- **Formatter**: Black (line length: 88)
- **Linter**: Ruff (replaces flake8, isort, etc.)
- **Type Checking**: Use type hints, consider mypy for large projects
- **Testing**: pytest with clear, descriptive test names
- **Style**: Follow PEP 8, use type hints for all function signatures
- **Common Packages**: ipython, black, ruff, pytest
- **Project Structure**: `src/` or `src/python/` for code, `notebooks/` for notebooks, clean separation

### JavaScript/TypeScript (Secondary Language)
- **Package Manager**: npm (local installs preferred, avoid global `-g` unless necessary)
- **Version Manager**: fnm (mandatory)
- **Common Commands**:
  ```bash
  npm install                # Install dependencies
  npm run build              # Build TypeScript
  npm test                   # Run tests
  npm update                 # Update packages
  ```
- **Style**: Use TypeScript for type safety, functional programming preferred, prefer `const` over `let`, never `var`

### Scala
- **Build Tool**: SBT
- **IDE Support**: JetBrains IntelliJ
- **Style**: Follow Scala style guide, 2-space indentation
- **Naming**: camelCase for methods, PascalCase for classes/objects
- **Usage**: heavy-duty data processing with Apache Spark 
- **Projects**: 'fin' : ~/gh/randykerber/fin

### Version Control
- **VCS**: Git
- **Repository Hosting**: GitHub
- **Username**: randykerber
- **Repository Root**: `~/gh/randykerber/`
- **GitHub CLI**: `gh` (configured)
- **SSH**: Keys configured for authentication
- **Git Workflows**:
  ```bash
  git status                        # Check status
  git add -A && git commit -m "..."  # Commit all changes
  git pull --rebase && git push origin main  # Update and push
  ```

### System Packages
- **Package Manager**: Homebrew
- **Policy**: Propose updates before running

---

## Project Structure & Important Paths

### Home Directory
```
/Users/rk/
```

### Development Projects

```
/Users/rk/gh/randykerber/
├── syndicate/      # SSS (Silo-Slayer Syndicate) System - personal productivity & info management
│   ├── sss/        # AI Agents framework
│   ├── hedgeye/    # Investing data pipelines (hedgeye.com)
│   └── ace/        # Agentic Context Engineering
├── raycast-ext/    # Raycast extensions (TypeScript)
├── emacs.d/        # Emacs configuration
├── fin/            # Scala+Spark. data pipelines, finance, taxes, expenses, Monte-Carlo planning
└── env/            # Environment config, dotfiles, etc.
```

### Documentation & Data
```
~/local/obsidian/   # Obsidian vaults (Fin & Tech)
~/d/                # data warehouse directory
~/.config/          # Application configs (XDG standard)
```

### Configuration Directories
```
  ~/.claude/          # Claude Code/Desktop config
  ~/.config/warp/     # Warp config
  ~/.cursor/          # Cursor settings
  ~/.config/          # XDG standard configs
  ~/Library/Application Support/Claude/  # Claude Desktop
  ~/Library/Application Support/Obsidian/ # Obsidian
  ~/.ssh/             # SSH keys, config
```

---

## Code Organization Practices

### Scratch vs Scripts Directories

**NEVER create exploratory/test code in `scripts/` directories.**

All AI agents must use **language-specific, topic-based scratch subdirectories** for exploration and testing:

**Structure**:
```
python/scratch/<topic-name>/    # Exploratory Python code (gitignored)
js/scratch/<topic-name>/         # Exploratory JavaScript code (gitignored)
```

**Workflow**:
1. **New exploration** → Create `scratch/<topic-name>/` subdirectory
   - Topic name should be self-documenting (e.g., `drafts-integration`, `api-testing`, `oauth-flow`)
   - **REQUIRED**: Create `README.md` in the subdirectory with:
     - Creation date+time: `YYYY-MM-DD HH:MM`
     - Brief explanation: Why created, what exploring
     - Cross-references: Note related scratch dirs in other languages if applicable
2. **Test/debug/experiment** → Work within that isolated topic directory
3. **Outcome**:
   - **Success**: Move working code to `scripts/` directory, delete scratch topic
   - **Abandoned**: Delete entire topic directory
   - **In-progress**: Leave topic directory, name + README preserve context

**Rules**:
- Each exploration gets its own subdirectory (never dump into existing scratch)
- Use **same topic name** across languages (e.g., both `python/scratch/drafts-integration/` and `js/scratch/drafts-integration/`)
  - Or append `-1`, `-2` if needed for disambiguation
- Every scratch subdirectory must have README.md documenting when/why created
- Topic directories are independent (promote, delete, or leave each separately)
- All `*/scratch/` directories are gitignored
- Never mix exploratory code with production scripts

**Why**:
- Prevents "archaeology problem" where forgotten exploratory files get mixed with production scripts
- Language-specific keeps imports/tooling working (uv, npm work naturally)
- Same topic name across languages makes cross-language explorations obvious
- README provides context for future cleanup decisions

**Example**:
```bash
# Start new exploration
mkdir js/scratch/drafts-integration
cat > js/scratch/drafts-integration/README.md <<EOF
# Drafts Integration Exploration

**Created:** 2025-12-21 14:30

Exploring Drafts JavaScript API for bulk export. URL schemes can trigger
Drafts but can't retrieve data back to terminal.

**Related:** If JS approach fails, see python/scratch/drafts-integration/
EOF

# Create test files...

# Success: promote to production
mv js/scratch/drafts-integration/working-version.js js/scripts/
rm -rf js/scratch/drafts-integration

# Abandoned: just delete
rm -rf js/scratch/drafts-integration
```

---

## Critical Safety Rules

### Scope Awareness (High-Impact Changes Only)

**STOP and ASK before:**
- Modifying global configs: `~/.config/`, `~/Library/`, `~/.zshrc`, `~/.bashrc`
- Running destructive commands: `rm -rf`, `git push --force`, `DROP TABLE`
- Installing system-wide packages or changing global tool versions
- Modifying files outside the current project directory

**Project-local is always preferred:**
- Use project-specific configs (`.env.local`, `pyproject.toml`, `package.json`)
- Use `.gitignore` for project settings
- Never modify global state without explicit approval

### When Uncertain

If you don't know the correct approach:
1. **Say "I don't know"** - Don't guess or make assumptions about architecture
2. **Search first** - Check existing code/config for established patterns
3. **Ask** - "Should this be project-local or global?" / "Is there an existing pattern for this?"

### Reversibility Principle

Prefer reversible changes over destructive ones:
- **Configuration over deletion** - Disable rather than delete when possible
- **Rename over rm** - `mv file.txt file.txt.backup` over `rm file.txt`
- **Git commits** - Commit before risky refactors
- **Dry-run when available** - Use `--dry-run`, `-n`, or preview flags

### Secrets Management

**CRITICAL RULE**: NEVER reveal or consume secrets in plain-text in terminal commands or output.

**Pattern**:
```bash
# Step 1: Store secret in environment variable
API_KEY=$(op read "op://vault/item/field")

# Step 2: Use variable in subsequent commands
curl -H "Authorization: Bearer $API_KEY" https://api.example.com

# NEVER echo or print the secret value
```

---

## Communication & Response Style

### Pattern: Plan-Then-Execute
1. **Output a PLAN** first (What, why, where)
2. **Show COMMANDS** (Exact commands, ready to run)
3. **Ask CONFIRM** (Before destructive or state-changing operations)

### Response Style
- **Concise and direct** - No unnecessary preambles
- **Structured** - Use Markdown headings, **bolding**, bullet points, tables for data
- **Technical depth when needed** - Explain complex operations and trade-offs
- **Action-oriented** - Focus on next steps
- **Brief summaries** - For non-trivial outputs

### Output Formats
Comfortable with and prefer:
- Tables
- JSON
- YAML
- SQL
- Python
- Bash
- Diagrams
- Markdown (always)

### Code & File Creation
- Create actual files when requested (don't just show code)
- Use appropriate file extensions
- Include helpful comments in code
- Provide complete, working examples
- Use language-specific code blocks (```python, ```bash, ```sql)

### When Explaining Complex Topics
- Start with high-level overview
- Provide concrete examples
- Explain trade-offs
- Link to authoritative docs
- Avoid unnecessary jargon

---

## Code Style & Conventions

### Python
- **Formatter**: Black (line length: 88)
- **Linter**: Ruff
- **Type hints**: Required for all function signatures
- **Docstrings**: Use for public APIs, follow Google or NumPy style
- **Error Handling**: Explicit and informative, explicit exception types, avoid bare `except:`
- **Async**: Use `async/await` for I/O-bound, prefer `asyncio.gather()` for parallel tasks

### JavaScript/TypeScript
- Use TypeScript for type safety
- Functional programming preferred over classes
- Prefer `const` over `let`, never use `var`
- Use destructuring and spread operators
- Async: Use async/await, not callbacks

### Scala
- Follow Scala style guide
- Indentation: 2 spaces
- Naming: camelCase for methods, PascalCase for classes/objects

### General
- Clear, descriptive variable names (no single-letter except loop counters)
- Comments explain "why", not "what"
- Keep functions small and focused
- Error handling: explicit and informative
- No magic numbers - use named constants

---

## Common Workflows

### Starting New Projects
1. Create project directory structure
2. Initialize git repository
3. Set up project:
   - **Python**: `uv init` or `uv venv`
   - **JavaScript**: `npm init -y`
   - **Scala**: SBT project structure
4. Create README.md with project description
5. Add .gitignore
6. Create initial commit

### Code Reviews
- Focus on: correctness, readability, performance implications
- Check for: edge cases, error handling, test coverage
- Suggest: improvements without being prescriptive
- Explain: rationale for suggestions

### Documentation
- README should include: purpose, installation, usage, examples
- Code comments for complex logic
- API documentation for public interfaces
- Architecture decisions in separate docs/

---

## Working Patterns & Philosophy

### What I Value
- **Speed**: Fast iteration, minimal friction
- **Quality**: Working code over quick hacks
- **Learning**: Understanding over cargo-culting
- **Pragmatism**: Ship working solutions, iterate later
- **Clarity**: Simple, readable code

### What to Avoid
- Over-engineering early
- Analysis paralysis
- Unnecessary abstractions
- Magic/clever code that's hard to understand
- Breaking changes without good reason

### Productivity Philosophy
- Strong preference for capture-first, low-friction workflows
- Dislikes rigid scheduling systems
- Apple Reminders: alerts/deadlines only
- Things: horizon-based task grouping
- Drafts: universal capture point
- Wants tactile, flexible reorganization

---

## Active Projects

### Syndicate (Silo-Slayer Syndicate System)
- **Location**: `~/gh/randykerber/syndicate/`
- **Purpose**: Agentic AI framework for information liberation
- **Core Mission**: "English as Programming Language" - natural input → parameter extraction → tool execution
- **Architecture**: Hybrid Python/JavaScript connected via MCP (Model Context Protocol)
- **Components**:
  - AI agents + human-in-the-loop (session persistence, async disambiguation)
  - Hedgeye data pipelines (Risk Range, ETF Pro, Portfolio Solutions)
  - YouTube transcript processing
  - MCP servers (human-input, push, drafts, accounts, market)
- **Key Patterns**: Multi-turn dialogue, parameter extraction, human-AI collaboration

## Future Projects, Planned Work

### Financial Data Warehouse
- Ticker-level data warehouse (planning phase)
- Unified data model for stocks, ETFs, indexes
- Tools: Python, uv, DuckDB, pandas
- Budget constraint: modest, no multi-thousand-dollar feeds

---

## Context Engineering Strategy
- **Context Source of Truth**: Code/System Instruction files are versioned via Git (`~/gh/randykerber/env/`)
- **Persistent Knowledge**: Obsidian is the source of technical and financial long-form notes (Vaults: Tech, Fin, Life)
- **Bear**: PKM Second Brain for all other "Life" information
- **Future Context**: Support Function Calling (Tools) and Model Context Protocol (MCP) for accessing external, on-demand data

---

## The Silo-Slayer Syndicate (SSS) Initiative

**Core Mission**: Break users out of "app prisons" by liberating information trapped in isolated tools.

**The Problem**: Critical information scattered across Drafts (1200+ unprocessed notes), Obsidian vaults, Apple Reminders, Bear, and other apps. Each tool is a silo - you can't find information unless you remember which app holds it. Manual context-switching and routing creates friction that leads to information loss and decision paralysis.

**The Vision**: AI agents using "English as programming language" to intelligently route, enhance, and connect information across all tools. Natural language instructions ("save as episode note, link to Luke Gromen analysis, preserve quotes") replace manual clicking through apps. Agents collaborate with humans through async disambiguation when needed ("Which Springfield? Illinois or Missouri?").

**Key Architecture**: Hybrid Python/JavaScript system connected via MCP (Model Context Protocol). MCP enables universal plug-and-play - any agent can discover and use any tool without custom integration. Specialist agents (drafts_agent, obsidian_agent, reminders_agent) become domain experts for their systems.

**Current Reality**: Framework in early stages. Base infrastructure exists (session persistence, human-in-the-loop, MCP servers), but most specialist agents and workflows not yet implemented. This is an **overriding quest** - not just a project, but the high-level motivation behind many technical decisions and questions that may not seem obviously related.

**Why This Matters to You (AI Agent)**: When I ask about tool integration, context persistence, or multi-turn workflows, there's often an underlying SSS motivation. Understanding this helps you see the bigger picture and provide more relevant suggestions.

**Success Metric**: Reduce information backlog growth from 50+/month to 5-10/month through intelligent AI-assisted routing and enhancement.

---

**End of COMMON.md**
