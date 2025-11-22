# Hedgeye Pipeline Refactoring Priorities

**Goal**: Clean up codebase and data directories, establish consistent naming, reduce duplication.

## Current State Analysis

### Naming Conventions Status
- ✅ **RR (Risk Range)**: Fully renamed with `rr_` prefix
- ✅ **CR (Combo Ranges)**: Fully renamed with `cr_` prefix
- ❌ **EP (ETF Pro)**: Still using inconsistent names (`process_`, `parse_`, `enrich_`)
- ❌ **PS (Portfolio Solutions)**: Still using generic `process_` prefix

### Issues Identified

#### 1. EP Pipeline Files (Need `ep_` prefix)
- `process_etf_pro_weekly.py` → `ep_process_weekly.py` or `ep_pipeline.py`
- `parse_etf_pro_weekly.py` → `ep_parse_weekly.py` or `ep_parse_eml.py`
- `enrich_etf_pro.py` → `ep_enrich.py`
- Script: `parse_etf_pro.py` → `parse_ep_emails.py` or `run_ep_pipeline.py`

#### 2. PS Pipeline Files (Need `ps_` prefix)
- `process_portfolio_solutions.py` → `ps_process.py` or `ps_pipeline.py`
- Script: `parse_portfolio_solutions.py` → `parse_ps_emails.py` or `run_ps_pipeline.py`

#### 3. Unclear/Duplicate Module Names
- `parser.py` - Generic name, unclear purpose (legacy?)
- `process_etf_pro_weekly.py` vs `parse_etf_pro_weekly.py` - Unclear distinction
- Both may be doing similar work, need to clarify responsibilities

#### 4. Data Directory Organization
- External data: `/Users/rk/d/downloads/hedgeye/`
- Need to understand what cleanup is needed (old files, duplicates, etc.)

#### 5. Configuration & Documentation
- Multiple config files? (`hedgeye.yaml`, `config_loader.py`)
- Documentation scattered across multiple files

#### 6. Price Fetching Code Duplication
- `fetch_prices.py` and `price_cache.py` have redundant logic
- **Duplicated functions:**
  - `is_market_closed_et()` - identical market hours detection
  - `is_weekend_date()` - identical weekend detection
  - `should_cache_today()` - identical caching logic
- **Different use cases justify separation:**
  - `fetch_prices.py`: Current/latest prices (Dict, FMP+yfinance, JSON cache)
  - `price_cache.py`: Historical time-series (DataFrame, yfinance only, CSV cache)
- **Refactoring opportunity:**
  - Extract shared logic to `price_utils.py` module
  - Keep both modules but remove duplication
  - Single source of truth for market hours/weekend detection

## Recommended Refactoring Order

### Phase 1: EP Pipeline Renaming (Low Risk)
**Priority**: HIGH - Completes naming convention, minimal dependencies
**Time**: 1-2 hours
**Risk**: Low - EP is isolated from other pipelines

**Steps**:
1. Audit current EP files to understand what each does
2. Rename modules with `ep_` prefix:
   - `parse_etf_pro_weekly.py` → `ep_parse_eml.py` (or similar)
   - `process_etf_pro_weekly.py` → `ep_pipeline.py` (or similar, if it's orchestration)
   - `enrich_etf_pro.py` → `ep_enrich.py`
3. Rename scripts:
   - `parse_etf_pro.py` → `run_ep_pipeline.py` or `parse_ep_emails.py`
4. Update all imports
5. Test EP pipeline end-to-end

**Dependencies**: None (EP is independent)

### Phase 2: PS Pipeline Renaming (Low Risk)
**Priority**: HIGH - Completes naming convention, minimal dependencies
**Time**: 1 hour
**Risk**: Low - PS is isolated from other pipelines

**Steps**:
1. Rename `process_portfolio_solutions.py` → `ps_pipeline.py` (or `ps_process.py`)
2. Rename script: `parse_portfolio_solutions.py` → `run_ps_pipeline.py` or `parse_ps_emails.py`
3. Update all imports
4. Test PS pipeline end-to-end

**Dependencies**: None (PS is independent)

### Phase 3: Code Consolidation (Medium Risk)
**Priority**: MEDIUM - Reduces confusion, but requires careful testing
**Time**: 2-3 hours
**Risk**: Medium - Need to verify no functionality is lost

**Steps**:
1. Audit `parser.py` - What does it do? Is it used?
2. Clarify distinction between `process_etf_pro_weekly.py` and `parse_etf_pro_weekly.py`:
   - If duplicate: Merge into single module
   - If different: Rename to clarify purpose
3. Check for other duplicate/unclear modules

**Dependencies**: After Phase 1-2 (EP/PS renaming)

### Phase 4: Data Directory Cleanup (Low Risk, Manual Work)
**Priority**: MEDIUM - Not blocking, but improves maintainability
**Time**: 2-4 hours (depends on data size)
**Risk**: Low if we're careful (backup first)

**Steps**:
1. Audit `/Users/rk/d/downloads/hedgeye/` structure
2. Identify:
   - Old/unused files
   - Duplicates
   - Files that should be archived
   - Missing organization
3. Create backup
4. Organize/clean up
5. Document final structure

**Dependencies**: None (can be done anytime)

### Phase 5: Configuration & Documentation Consolidation (Low Risk)
**Priority**: MEDIUM - Improves maintainability
**Time**: 2-3 hours
**Risk**: Low

**Steps**:
1. Review all config files
2. Consolidate if needed
3. Update documentation:
   - Create/maintain README.md in each pipeline directory
   - Update main project README
   - Ensure workflow docs are accurate
4. Add inline documentation to key modules

**Dependencies**: After Phase 1-3 (need stable structure first)

### Phase 6: Price Fetching Code Consolidation (Medium Risk)
**Priority**: MEDIUM - Reduces duplication, improves maintainability
**Time**: 1-2 hours
**Risk**: Medium - Need to verify both price fetching systems still work

**Steps**:
1. Create `price_utils.py` module with shared logic:
   - `is_market_closed_et()` - Market hours detection
   - `is_weekend_date()` - Weekend detection
   - `should_cache_today()` - Caching logic
2. Update `fetch_prices.py` to use `price_utils`
3. Update `price_cache.py` to use `price_utils`
4. Test both systems (enrichment + time-series plotting)
5. Verify caching behavior (markets open vs closed)

**Dependencies**: None (can be done anytime, but test thoroughly)

**Note**: Both modules serve different purposes (current prices vs historical time-series), so they should remain separate. This phase just removes duplication in shared logic.

### Phase 7: Code Quality Improvements (Ongoing)
**Priority**: LOW - Can be done incrementally
**Time**: Ongoing
**Risk**: Low (do incrementally)

**Areas**:
- Type hints (add where missing)
- Error handling (standardize)
- Logging (improve consistency)
- Testing (add tests for critical paths)
- Performance (optimize if needed)

**Dependencies**: None (can be done anytime)

## Decision Points

### Naming Convention Questions
1. **EP Pipeline Orchestration**: Should we have:
   - `ep_pipeline.py` (like `rr_pipeline.py`) for orchestration?
   - Or keep `ep_process_weekly.py` as the main entry point?

2. **Parse vs Process**: What's the distinction?
   - `parse_*.py` = Parse EML files into CSVs?
   - `process_*.py` = Orchestrate parsing + other steps?
   - Need to clarify and document

3. **Script Naming**: Should scripts mirror module names?
   - `parse_ep_emails.py` vs `run_ep_pipeline.py`
   - Current pattern: `run_full_rr_pipeline.py` (orchestration), `parse_rr_emails.py` (single step)

### Data Directory Structure
- What's the current structure? Need audit first
- What cleanup is needed? (old files, duplicates, etc.)

## Recommended Starting Point

**Option A: Start with EP Renaming** (Safest, Most Complete)
- Completes naming convention for one pipeline
- Low risk (EP is isolated)
- Quick win
- Sets pattern for PS renaming

**Option B: Start with Code Audit** (Most Thorough)
- Understand what each file does first
- Make informed decisions
- Takes longer before visible progress

**Option C: Start with Data Directory Cleanup** (Most Practical)
- Improves daily workflow immediately
- Not dependent on code changes
- Can be done in parallel with code refactoring

## Questions to Answer Before Starting

1. **What's the distinction between `process_etf_pro_weekly.py` and `parse_etf_pro_weekly.py`?**
   - Are they doing different things, or is one legacy?
   
2. **What does `parser.py` do?**
   - Is it used, or legacy?
   
3. **What cleanup is needed in data directories?**
   - Old files to archive?
   - Duplicates to remove?
   - Missing organization?

4. **Should we create pipeline orchestration files for EP/PS?**
   - Like `ep_pipeline.py` and `ps_pipeline.py` (similar to `rr_pipeline.py` and `cr_merge_ranges.py`)?

5. **Priority: Speed vs. Thoroughness?**
   - Quick renames now, then consolidate later?
   - Or audit everything first, then refactor holistically?

## Next Steps

1. **Audit Current EP/PS Files** (30 min)
   - Understand what each module does
   - Document current structure
   - Identify duplicates/unclear code

2. **Decide on Starting Point** (15 min)
   - Choose Option A, B, or C based on priorities

3. **Execute First Phase** (1-4 hours depending on choice)

4. **Test & Iterate**

