# SSS Use Case: Daily Portfolio Updates

**Status:** Conceptual / Requirements Discovery
**Purpose:** Illustrate 3-level cascade exception handling model
**Example:** Hedgeye Portfolio Solutions Daily Trades (Keith's Commentary)

---

## The Problem

Every trading day, Hedgeye sends Portfolio Solutions daily update with:
- Current ETF rankings (26 positions)
- **Keith's Commentary**: Actual trades made that day
  - "Sold all URA. Sold 100bps LQD. Bought 50bps MAGS..."

**Characteristics:**
- **High frequency**: Daily (every trading day)
- **Structured format**: HTML email with tables
- **Free text component**: Keith's commentary (natural language, variable format)
- **Action required**: Decide which trades to follow
- **Exceptions likely**: Typos, new tickers, non-standard phrasing

This is **NOT** about AI summarization. This is about **exception handling escalation**.

---

## The SSS 3-Level Cascade Model

### Level 1: Automated Code Processing

**Role:** Handle the happy path
**Technology:** Python script (deterministic parsing)

```python
# parse_portfolio_solutions_daily.py
try:
    email = parse_eml(email_path)
    rankings = extract_rankings_table(email)
    commentary = extract_keith_commentary(email)
    trades = parse_trades_from_commentary(commentary)
    save_to_database(trades)
    output_obsidian_note(trades, rankings)
    # SUCCESS - job done, no escalation
except ParsingException as e:
    # FAILURE - escalate to O-Agent
    raise_to_agent(e, context={email, commentary})
```

**Success condition:** Standard format, known tickers, parseable text
**Failure condition:** Throws exception → escalates to Level 2

---

### Level 2: O-Agent (LLM-Powered Exception Handler)

**Role:** Handle exceptions that deterministic code cannot
**Technology:** AI Assistant (LLM + MCP tool-calling) - part of SSS team
**Framework:** O-Agent (currently OpenAI SDK, but framework-agnostic)

#### Runtime Agent
**Priority:** Get usable result RIGHT NOW

**Capabilities:**
- LLM-powered flexibility for non-standard formats
- Information enrichment (resolve ambiguous tickers)
- Alternative parsing strategies
- Best-effort interpretation of free text

**Actions on receiving exception:**
```
1. Analyze the parsing failure
2. Try alternative extraction methods
   - Use LLM to parse free text
   - Look up ticker variations
   - Check for spelling errors
3. Enrich with context:
   - "URA = Global X Uranium ETF"
   - "Last position was 200bps, selling 'all' means -200bps"
4. If successful: Return corrected data
5. If still failing: Escalate to Human with summary
```

**Success:** Produces usable output for human review
**Failure:** Escalates to Level 3

#### Senior Software Debugger Agent
**Priority:** Fix the system for NEXT TIME (offline process)

**Capabilities:**
- Analyzes failures that required O-Agent intervention
- Identifies patterns in exceptions
- Proposes code changes to handle automatically
- Files software issues with context

**Actions (runs asynchronously):**
```
1. Review today's exceptions
2. Identify: "3 times this week, 'Sold all XYZ' wasn't parsed"
3. Propose: "Add pattern: 'sold all <TICKER>' → lookup position size"
4. File issue: "parse_trades() should handle 'all' keyword"
5. Or: Update symbol mapping table if it's a ticker variant
```

**Output:** GitHub issues, code improvements, knowledge base updates

---

### Level 3: Human in the Loop (Me)

**Trigger:** O-Agent unable to resolve exception

**Scenarios requiring human:**
- **Incorrect ticker symbols**: "Keith wrote 'GLD' but meant 'GOLD'"
- **Non-existent ETFs**: New ticker not yet in database
- **Badly formatted emails**: Hedgeye changed HTML structure
- **Spelling errors**: "Bough" vs "Bought"
- **Ambiguous intent**: "Reduced exposure" - by how much?

**Human actions:**
```
1. Review O-Agent summary of the problem
2. Engage in clarification dialogue with O-Agent:
   - "Is this ticker valid?"
   - "Check if GLD and GOLD are different instruments"
   - "What was the last known position in URA?"
3. Provide correction:
   - "Use GOLD, not GLD"
   - "Set position to 0"
   - "Skip this trade, will handle manually"
4. Feed correction back to system:
   - Real-time: O-Agent uses correction to complete task
   - Offline: Debugger Agent logs for future code improvement
```

**Escalation complete:** Task finishes with human-provided correction

---

## Workflow Example: Exception Handling in Action

### Scenario: Typo in Keith's Commentary

**Input email (Nov 8, 2025):**
```
Keith's Commentary: "Sold all URAa. Bought 100bps UUP."
```

**Level 1 (Code):**
```python
trades = parse_trades("Sold all URAa. Bought 100bps UUP.")
# Exception: Unknown ticker 'URAa'
raise_to_agent(exception="Unknown ticker", ticker="URAa", context=commentary)
```

**Level 2 (Runtime O-Agent):**
```
RECEIVED: Unknown ticker 'URAa'
CONTEXT: "Sold all URAa. Bought 100bps UUP."

AGENT REASONING:
1. Check database: No ticker 'URAa' exists
2. Look for similar tickers: URA (Global X Uranium) - distance=1
3. Check recent portfolio: URA was held at 200bps
4. Pattern match: "Sold all [ticker]" + context → likely typo
5. HIGH CONFIDENCE: URAa → URA

AGENT ACTION:
- Correct ticker to URA
- Parse trade: SELL URA, 200bps (all)
- Flag for human review: "Auto-corrected URAa → URA (typo suspected)"
- Return corrected data

SUCCESS - No human escalation needed
```

**Level 2 (Debugger O-Agent, offline):**
```
ANALYSIS: Typo 'URAa' auto-corrected to 'URA' today
PATTERN: This is the 2nd typo this week (prev: 'URa')
RECOMMENDATION: Add fuzzy matching to Level 1 code
FILE ISSUE: "parse_trades() should use edit-distance matching for tickers"
```

### Scenario: New Ticker Not in Database

**Input email:**
```
Keith's Commentary: "Bought 100bps NEWF (new frontier markets ETF)."
```

**Level 1 (Code):**
```python
# Exception: Unknown ticker 'NEWF'
raise_to_agent(exception="Unknown ticker", ticker="NEWF")
```

**Level 2 (Runtime O-Agent):**
```
RECEIVED: Unknown ticker 'NEWF'

AGENT ACTIONS:
1. Search external sources (Yahoo Finance, FMP)
2. Found: No ticker 'NEWF' exists
3. Search with description: "new frontier markets ETF"
   → Found: FM (iShares MSCI Frontier Markets)
4. LOW CONFIDENCE: Cannot determine correct ticker

ESCALATE TO HUMAN:
"Keith mentioned 'NEWF (new frontier markets ETF)' but:
- No ticker 'NEWF' found
- Possible match: FM (iShares Frontier Markets)
- Or could be brand new ETF not yet listed
What should I do?"
```

**Level 3 (Human):**
```
ME: "Check when this email was sent. If recent, NEWF might not be listed yet."
AGENT: "Email is from today. Yahoo Finance updated hourly."
ME: "Skip this trade. I'll investigate manually and update tomorrow."
AGENT: "Understood. Logging NEWF for tomorrow's retry. Continuing with remaining trades."
```

**Level 2 (Debugger O-Agent, offline):**
```
LOGGED: NEWF - unknown ticker, human deferred
MONITOR: Check daily if NEWF appears in data sources
IF FOUND: Auto-add to database and notify human
```

---

## Key Insights from This Model

### Multiple O-Agent Roles Emerge

1. **Runtime Agent**: Focus on NOW - get usable result, prefer speed over perfection
2. **Debugger Agent**: Focus on FUTURE - learn from exceptions, improve system

These might be:
- Same agent with different modes
- Different specialized agents
- Different prompts/tool access

### Exception Types Reveal System Design

**Solvable by Code:**
- Known patterns → add to parser
- Symbol mappings → maintain lookup table
- Format variations → expand regex patterns

**Solvable by Runtime Agent:**
- Fuzzy matching (typos)
- Context inference (position sizes)
- External lookups (ticker validation)

**Requires Human:**
- Ambiguous intent
- Novel situations
- Business logic decisions
- Domain expertise

### The Feedback Loop

```
Human Correction
    ↓
Runtime Agent (immediate use)
    ↓
Debugger Agent (learns pattern)
    ↓
Code Improvement (handles automatically next time)
    ↓
Fewer exceptions over time
```

---

## Why This Belongs in Syndicate (Not Standalone hedgeye-kb)

This workflow requires:
- **Code** (parsers, database, pipeline)
- **O-Agents** (exception handling, debugging)
- **Human oversight** (decision-making, corrections)
- **Memory/Learning** (pattern recognition, improvement)
- **Team coordination** (multiple agents, roles)

This is not a "parse emails" project.
This is an **operational workflow** requiring the full SSS architecture.

Therefore: hedgeye-kb should be **integrated into syndicate** as a domain-specific module within the SSS framework.

---

## Current Status: Requirements Discovery

**What we have:**
- ✅ Proof-of-concept parser (`parse_etf_pro.py`)
- ✅ Understanding of exception scenarios
- ✅ Manual extraction examples

**What we're discovering:**
- Exception types and frequencies
- Agent role boundaries
- Human-in-loop interaction patterns
- Feedback loop requirements

**Next steps:**
- Run parser on historical emails → collect exceptions
- Categorize failures: code-solvable vs agent-solvable vs human-required
- Design O-Agent tool interfaces
- Prototype exception escalation flow

---

## Notes

**Barbell Strategy:**
- High-level vision (this document)
- Concrete throwaway artifacts (current parser script)
- Middle will emerge through iteration

**Framework Agnostic:**
- "O-Agent" is conceptual (LLM + tools)
- Currently OpenAI SDK, but could be Claude, custom, etc.
- Focus on architecture, not implementation

**This Document's Purpose:**
Guide design decisions by illustrating:
- The roles in the cascade
- The exception handling model
- The learning/improvement loop
- Why SSS integration is essential

---

**Last Updated:** 2025-11-09
**Author:** RK (via Claude Code)
**Status:** Living document - will evolve as we build
