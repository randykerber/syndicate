# Migration Plan: hedgeye-kb → syndicate

**Status**: Planning Phase
**Last Updated**: 2025-11-12

## Overview

Migrate the hedgeye-kb project into the syndicate monorepo as a data source and processing pipeline.

## Current State Analysis

### hedgeye-kb Project Structure

```
hedgeye-kb/
├── src/hedgeye_kb/          # Main package
│   ├── parse_eml.py         # Email parser (Risk Range)
│   ├── use_rr.py            # Data processing & plotting
│   ├── enhanced_plotting.py # Enhanced plots with FMP prices
│   ├── config_loader.py     # Config management
│   ├── symbol_canonicalization.py
│   └── pipeline.py          # Pipeline orchestration
├── scripts/
│   ├── run_full_pipeline.py
│   ├── parse_emails.py
│   ├── combine_data.py
│   ├── generate_plots.py
│   ├── parse_etf_pro.py           # ETF Pro parser (standalone)
│   ├── parse_portfolio_solutions.py # PS parser (standalone)
│   └── rename_hedgeye_emails.py   # Email organization
├── conf/
│   └── config.yaml           # All configuration
└── docs/                     # Documentation
```

### Data Files (External to Repo)

**Hedgeye Data:**
```
$HOME/d/downloads/hedgeye/
├── raw/eml/
│   ├── risk_range/          # Risk Range emails (78 files)
│   ├── etf_pro_weekly/      # ETF Pro weekly reports (2 files)
│   ├── etf_pro_updates/     # ETF Pro daily updates (8 files)
│   └── portfolio_solutions/ # Portfolio Solutions rankings (8 files)
├── prod/
│   ├── daily/               # Daily outputs (Risk Range only)
│   │   ├── csv/             # risk_range_YYYY-MM-DD.csv, change_events_YYYY-MM-DD.csv
│   │   └── md/              # Markdown outputs
│   ├── all/                 # Combined/aggregated data (Risk Range)
│   │   ├── csv/             # Combined CSV across all dates
│   │   └── plots_with_fmp_YYYYMMDD/  # Enhanced plots (36 active symbols)
│   ├── ps/                  # Portfolio Solutions outputs
│   ├── epp/                 # ETF Pro Plus outputs
│   └── rta/                 # Real Time Alerts (future)
```

**FMP (Financial Modeling Prep) Data:**
```
$HOME/d/downloads/fmp/
├── README.md
├── entities/                # Downloaded FMP entity data
├── entities-bu/             # Backup
├── entities2/               # Alternative entity data
├── he_to_fmp.csv           # **CRITICAL** Hedgeye→FMP symbol mapping
└── he_to_fmp.csv.backup*   # Backups of mapping file
```

**Price Data Sources:**
- **FMP API** - Primary (paid, with usage limits)
- **Yahoo Finance (yfinance)** - Fallback (free, not cached locally)

**Notes:**
- All email files use date-based naming: `{type}_{YYYY-MM-DD}.eml`
- `he_to_fmp.csv` is essential for symbol canonicalization and price fetching
- Yahoo Finance data is fetched on-demand, not cached

### Syndicate Project Structure

```
syndicate/
├── python/                  # Python implementation
│   ├── src/syndicate/      # Main package
│   │   ├── agents.py
│   │   ├── human_interface.py
│   │   ├── instruction_templates.py
│   │   ├── mcp_agent_configs.py
│   │   ├── sessions.py
│   │   └── shared_config.py
│   ├── servers/            # MCP servers
│   │   ├── accounts_server.py
│   │   ├── drafts_server.py
│   │   ├── human_input_server.py
│   │   ├── market_server.py
│   │   └── push_server.py
│   ├── data/               # Runtime data
│   │   ├── human_queue/
│   │   └── sessions/
│   └── pyproject.toml
├── js/                     # TypeScript/JavaScript implementation
│   └── src/
│       ├── agents/
│       ├── mcp/
│       └── tools/
├── config/                 # Configuration
│   └── mcp-config.json
├── context/                # AI context files
│   ├── ASSISTANT_BUNDLE.md
│   ├── profile.md
│   ├── preferences.md
│   └── projects/
└── docs/                   # Documentation
```

**Integration Point:** Hedgeye will likely fit under `python/src/syndicate/data_sources/hedgeye/`

## Pre-Migration Cleanup

### hedgeye-kb Cleanup Tasks

- [ ] **Commit recent work:**
  - Config changes (plotting threshold, path updates)
  - Enhanced plotting improvements (stale plot cleanup)
  - pyproject.toml updates

- [ ] **Organize standalone parsers:**
  - `scripts/parse_etf_pro.py`
  - `scripts/parse_portfolio_solutions.py`
  - Decision: Keep as scripts or refactor into package?

- [ ] **Documentation cleanup:**
  - Update README with current state
  - Document new parsers (ETF Pro, Portfolio Solutions)
  - Archive or update outdated docs

- [ ] **Sample data files:**
  - Move CSV samples to docs/examples/ or delete
  - Keep PRD docs in docs/

### syndicate Cleanup Tasks

- [ ] **Resolve uncommitted changes:**
  - Review `.claude/settings.local.json` changes
  - Review `config/mcp-config.json` changes
  - Clean up backup files

- [ ] **Prepare integration point:**
  - Decide on directory structure for data sources
  - Plan configuration strategy
  - Review dependencies

## Proposed Integration Structure

### Analysis: Where Does Hedgeye Fit?

Looking at syndicate's architecture:
- `python/src/syndicate/` - Core agent/session framework
- `python/servers/` - MCP servers (accounts, drafts, human_input, market, push)
- `python/data/` - Runtime data (human_queue, sessions)

**Hedgeye is a data source** that could:
1. Be accessed via an MCP server (like market_server.py)
2. Be integrated as a syndicate module
3. Both - module for processing, server for agent access

### Recommended Structure: Hybrid Approach

```
syndicate/python/
├── src/syndicate/
│   ├── data_sources/              # NEW: Data source integrations
│   │   ├── __init__.py
│   │   └── hedgeye/
│   │       ├── __init__.py
│   │       ├── parsers/           # Email parsing
│   │       │   ├── __init__.py
│   │       │   ├── base.py        # Common parser interface
│   │       │   ├── risk_range.py
│   │       │   ├── etf_pro.py
│   │       │   └── portfolio_solutions.py
│   │       ├── processors/        # Data processing
│   │       │   ├── __init__.py
│   │       │   ├── risk_range.py  # Combining, analysis
│   │       │   └── plotting.py    # Plot generation
│   │       ├── models/            # Data models
│   │       │   ├── __init__.py
│   │       │   └── schemas.py     # Pydantic models
│   │       ├── config.py          # Hedgeye-specific config
│   │       └── utils/
│   │           ├── __init__.py
│   │           ├── symbol_canonicalization.py
│   │           └── fmp_integration.py
│   │
│   ├── agents.py                  # Existing
│   ├── sessions.py                # Existing
│   └── shared_config.py           # Existing
│
├── servers/
│   ├── hedgeye_server.py          # NEW: MCP server for hedgeye data
│   ├── market_server.py           # Existing (could integrate)
│   └── ...
│
├── scripts/                       # NEW: Utility scripts
│   ├── hedgeye/
│   │   ├── run_pipeline.py        # Risk Range pipeline
│   │   ├── parse_emails.py        # Email parsing
│   │   └── rename_emails.py       # Email organization
│   └── ...
│
├── data/                          # Runtime/cache data
│   ├── hedgeye/                   # NEW: Hedgeye cache
│   │   ├── cache/                 # Processed data cache
│   │   └── plots/                 # Generated plots
│   └── ...
│
├── config/
│   └── hedgeye.yaml               # NEW: Hedgeye configuration
│
├── docs/
│   └── data_sources/              # NEW: Data source docs
│       └── hedgeye/
│           ├── README.md
│           ├── parsers.md
│           └── pipeline.md
│
└── pyproject.toml                 # Merge dependencies

# Data files stay external
$HOME/d/downloads/hedgeye/         # Email source files
```

### Key Design Decisions

**1. Module Organization**
- `data_sources/hedgeye/` - Clear separation of concerns
- Parsers use common interface for consistency
- Processors handle data transformation/analysis
- Models define data schemas (Pydantic)

**2. MCP Server Strategy**
- `hedgeye_server.py` - Dedicated MCP server for hedgeye data
- Exposes tools like:
  - `get_risk_range` - Get current risk range for symbol(s)
  - `get_portfolio_rankings` - Get latest PS rankings
  - `check_range_breaches` - Alert on symbols outside range
  - `run_pipeline` - Trigger data processing

**3. Configuration**
- `config/hedgeye.yaml` - All hedgeye settings
- Environment variables for sensitive data (API keys)
- Integrated with syndicate's config system

**4. Scripts Location**
- `scripts/hedgeye/` - Standalone utilities
- Can be run independently or imported as modules
- Useful for cron jobs, manual processing

**5. Data Management**
- Source emails: `$HOME/d/downloads/hedgeye/` (external)
- Processed cache: `python/data/hedgeye/cache/`
- Generated plots: `python/data/hedgeye/plots/`
- Or: Keep all in external location, cache in data/

## Migration Strategy

### Phase 1: Direct Integration (Quick)

Copy hedgeye-kb into syndicate as-is, minimal changes:

```
syndicate/python/data_sources/hedgeye/
├── src/hedgeye/              # Current hedgeye_kb code
├── scripts/                  # Current scripts
├── conf/                     # Current config
└── docs/                     # Current docs
```

**Timeline:** 1-2 hours
**Pros:** Fast, low risk, maintains working code
**Cons:** Doesn't follow syndicate patterns, duplicate configs

### Phase 2: Proper Integration (Refactored)

Implement the recommended structure above.

**Timeline:** 1-2 days
**Pros:** Clean architecture, follows patterns, maintainable
**Cons:** More work, requires testing

### Phase 3: Agent Integration (Enhanced)

Add MCP server and agent capabilities.

**Timeline:** 2-3 days
**Includes:**
- `hedgeye_server.py` MCP server
- Agent tools for querying data
- Automated pipeline triggers
- Obsidian integration for analysis

**Pros:** Full syndicate integration, agent-accessible
**Cons:** Requires understanding agent system, more complex

## Decision Points

### 1. Parser Organization

**Options:**
- A. Keep standalone scripts (current state)
- B. Refactor into unified parser framework
- C. Create parser classes with common interface

**Recommendation:** Start with A (quick), evolve to C

### 2. Configuration Strategy

**Options:**
- A. Keep separate config.yaml
- B. Merge into syndicate config system
- C. Hybrid: hedgeye section in syndicate config

**Recommendation:** C (hybrid approach)

### 3. Data Location

**Options:**
- A. Keep data in ~/d/downloads/hedgeye/
- B. Move to syndicate data directory
- C. Use environment variable for flexibility

**Recommendation:** C (add HEDGEYE_DATA_DIR env var)

### 4. Dependency Management

**Options:**
- A. Separate pyproject.toml for hedgeye
- B. Merge all deps into syndicate
- C. Use optional dependency groups

**Recommendation:** B or C (depending on syndicate setup)

## Migration Steps

### Preparation (Both Repos)

1. **hedgeye-kb:**
   ```bash
   # Clean up and commit
   git add conf/config.yaml src/hedgeye_kb/enhanced_plotting.py
   git commit -m "Enhanced plotting: symbol filtering and cleanup"

   # Organize parsers
   mkdir -p docs/examples
   mv *.csv docs/examples/  # Move sample CSVs

   # Update docs
   # ... edit README, add parser docs

   git add .
   git commit -m "Pre-migration cleanup and documentation"
   git push
   ```

2. **syndicate:**
   ```bash
   # Review and commit changes
   git add .claude/settings.local.json config/mcp-config.json
   git commit -m "Configuration updates"

   # Clean up backups
   rm config/*.backup.* config/*.bak.*

   git push
   ```

### Phase 1: Quick Integration

1. **Create data sources structure:**
   ```bash
   cd syndicate
   mkdir -p data_sources/hedgeye
   ```

2. **Copy hedgeye-kb:**
   ```bash
   # From hedgeye-kb root
   cp -r src/ scripts/ conf/ docs/ ../syndicate/data_sources/hedgeye/
   ```

3. **Update imports and paths:**
   - Rename package: `hedgeye_kb` → `hedgeye`
   - Update config paths
   - Test pipeline

4. **Commit migration:**
   ```bash
   git add data_sources/hedgeye/
   git commit -m "Initial migration: hedgeye-kb as data source"
   git push
   ```

5. **Archive hedgeye-kb repo:**
   - Add README noting migration
   - Archive on GitHub
   - Keep local copy for reference

## Testing Plan

### Post-Migration Tests

- [ ] Run Risk Range pipeline
- [ ] Verify CSV outputs
- [ ] Check plot generation
- [ ] Test ETF Pro parser
- [ ] Test Portfolio Solutions parser
- [ ] Verify FMP API integration
- [ ] Check symbol canonicalization

### Validation

- [ ] Compare outputs before/after migration
- [ ] Verify all 36 active symbols plot correctly
- [ ] Check stale symbol filtering
- [ ] Validate date-based file naming

## Rollback Plan

If migration fails:

1. Keep hedgeye-kb repo active
2. Revert syndicate changes
3. Continue using standalone hedgeye-kb
4. Document issues and re-plan

## Future Enhancements

Post-migration improvements:

- [ ] Agent-based pipeline triggers
- [ ] Automated email processing
- [ ] Real-time alerts for range breaches
- [ ] Obsidian integration for analysis
- [ ] Portfolio tracking integration
- [ ] Multi-source data fusion

## Notes

- Parsers currently "throwaway" - may need cleanup/refactor
- ETF Pro has two types: weekly reports + daily updates
- Pipeline uses FMP API (paid) with Yahoo Finance fallback
- Risk Range data stored in Obsidian (separate from syndicate)

## Questions to Resolve

- [ ] Where does hedgeye data fit in syndicate architecture?
- [ ] Should parsers be async?
- [ ] How to handle scheduled pipeline runs?
- [ ] Integration with existing syndicate agents?
- [ ] Unified logging strategy?

---

**Next Steps:**
1. Review this plan
2. Complete cleanup tasks
3. Make Phase 1/2/3 decision
4. Execute migration
5. Test and validate
