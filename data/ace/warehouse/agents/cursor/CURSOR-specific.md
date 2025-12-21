# CURSOR-specific Context

Cursor-specific patterns, workflows, and project awareness.

---


## Cursor-Specific Workflows

### File Context Usage
- Use **@ symbol** to reference specific files in chat
- Example: `@agents.py` to reference the agents module
- Consider the full pipeline, not just individual functions
- Read related files (imports, tests, docs) when analyzing code

### Code Suggestions
- **Follow existing patterns** in the codebase
- **Preserve type hints and docstrings** when modifying code
- **Match formatting** (Black for Python, Prettier for JS)
- **Don't introduce new dependencies** without discussion
- Check existing code before suggesting new patterns

### Refactoring Patterns
- **Incremental changes**, not massive rewrites
- **Preserve existing functionality** during refactors
- **Add tests** for refactored code
- **Update documentation** to match changes
- Test end-to-end after changes

---

## Syndicate-Specific Patterns

### Session Persistence
- All agents inherit from `SyndicateAgent` for SQLite session storage
- Conversation history preserved across turns
- Use `SQLiteSession` for multi-turn workflows

### Human-in-the-Loop
- Use `ask_human_choice()` and `ask_human_text()` from `human_interface.py`
- Push notifications via `push_server.py` for mobile alerts
- File-based async queue for human responses

### Instruction Templates
- Use templates from `instruction_templates.py`
- Don't hardcode agent instructions
- Focus on parameter extraction patterns

---

## Hedgeye Pipeline Specifics

### File Naming Conventions
- Input emails: `*.eml` in `/Users/rk/d/downloads/hedgeye/raw/eml/`
- Processed CSVs: `*_YYYY-MM-DD.csv` in `/Users/rk/d/downloads/hedgeye/prod/`
- Always include date in output filenames for version tracking

### CSV Processing
- Use pandas for all CSV operations
- Read with `dtype=str` first, then convert types explicitly
- Include `report_date` column in all outputs
- Use snake_case for column names

### Price Fetching
- Three-tier fallback: FMP mapping → FMP direct → yfinance
- Use `he_to_fmp.csv` for special symbols (commodities, forex, indexes)
- Fall back to `rr_prev_close` when live price unavailable
- Cache daily prices in JSON format

---

## MCP Configuration

### Server Locations
- Global registry: `~/.config/mcp/servers/`
- Project config: `./config/mcp-config.json`
- Python servers: `./python/servers/`

### Usage in Code
- Use `mcp_params.py` for agent-specific server configurations
- Reference shared config via `shared_config.py`
- Don't hardcode server URLs or paths

---

## Testing Requirements

### Python Tests
- Use pytest
- Test files: `test_*.py` in `python/tests/`
- Use fixtures for common setup
- Test edge cases and error conditions

### Coverage Goals
- Core functions: 80%+ coverage
- Critical paths: 100% coverage
- Edge cases: Document why untested if skipped

---

## Common Pitfalls to Avoid

1. **Don't mix data formats**: Pick CSV or JSON for a workflow, not both
2. **Don't skip error handling**: Always handle file not found, API failures
3. **Don't use magic numbers**: Define constants with descriptive names
4. **Don't commit large files**: Use `.gitignore` for data, logs, caches
5. **Don't assume file locations**: Use config files for paths
6. **Don't forget logging**: Use `print()` for user messages, logging for debugging
7. **Don't break existing pipelines**: Test end-to-end after changes

---

## Key Files to Know

### Hedgeye Pipeline
- `merge_position_ranges.py`: Combines EPP + PS + RR data
- `enrich_position_ranges.py`: Fetches prices and calculates proxy ranges
- `fetch_prices.py`: Multi-source price fetching with fallbacks
- `he_to_fmp.csv`: Symbol mapping for special asset types

### Syndicate Framework
- `agents.py`: Base SyndicateAgent class
- `human_interface.py`: Human-AI interaction system
- `instruction_templates.py`: Reusable agent instruction patterns
- `mcp_params.py`: MCP server configurations

---

## Remember

This project is about empowering users through AI-assisted information liberation. Code should be clear, maintainable, and focused on solving real workflow problems.

---

**End of CURSOR-specific.md**
