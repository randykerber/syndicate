# SSS Philosophy: Problem-Focused, Tool-Agnostic

**Last Updated**: 2025-12-20

---

## Core Principle: "Solved" Not "Solved by SSS"

**Goal**: Eliminate daily annoyances and information management friction

**Not the goal**: Build SSS for its own sake

### What This Means

If a problem can be solved by:
- ✅ Raycast hotkey (2-second setup)
- ✅ Apple Shortcut
- ✅ Quick Siri command
- ✅ ChatGPT/Claude Desktop query
- ✅ 1Password feature
- ✅ Obsidian plugin
- ✅ Browser extension

**That's a WIN.** Don't force it into SSS architecture if a simpler tool works.

### When SSS is the Right Answer

Use SSS when:
- Problem requires **memory across sessions** (not just in-conversation)
- Information is **personal/specific** (not general knowledge)
- Needs **context-aware loading** (cooking → food inventory, not everything)
- Requires **multi-tool coordination** (Drafts → Obsidian → Bear routing)
- Voice input → structured storage → intelligent retrieval
- **No existing tool solves it well**

### When SSS is Overkill

Don't use SSS when:
- Simple automation works (Raycast hotkey, Shortcut)
- One-time lookup (just Google it)
- General knowledge (ChatGPT/Claude already handle this)
- Existing app has the feature (use that app)

---

## Success Pattern: Raycast Hotkey Wins

### Example 1: Email Address Insert

**Problem**: Typing email address dozens of times daily
**Solution**: Raycast hotkey inserts "rk@example.com"
**Setup time**: 2 minutes
**Daily savings**: 30 seconds × 20 times = 10 minutes
**Complexity**: Zero
**SSS needed**: No

### Example 2: Apple Mail Sort Toggle

**Problem**: Sorting Apple Mail by sender requires 3-4 menu clicks
**Solution**: Raycast hotkey `ctrl-shift-opt-F` → sorted by sender, same chord → back to date
**Setup time**: 5 minutes
**Daily usage**: 5-10 times
**Complexity**: Zero
**SSS needed**: No

### The Pattern

**Best solutions are**:
- Triggered with **single action** (hotkey, voice command)
- **Zero thinking** required (muscle memory)
- **Instant execution** (no lag, no loading)
- **High frequency** payoff (used daily/hourly)
- **Low setup cost** (minutes to configure)

---

## Goal: 100x These Simple Wins

### Not:
- ❌ Build complex agent architecture first
- ❌ Over-engineer before validating need
- ❌ Create tools because they're technically interesting

### Instead:
- ✅ Identify **high-frequency pain points** (login method recall, subscription level lookup)
- ✅ Find **simplest solution** (might be Raycast, might be SSS)
- ✅ Implement **quick win** (minutes/hours, not weeks)
- ✅ Move to next pain point
- ✅ **Compound** small wins into massive productivity gains

---

## Pain Point → Solution Decision Tree

```
1. Is this a frequent pain point? (daily/weekly)
   NO → Defer, not worth solving
   YES → Continue

2. Does existing tool solve it?
   YES → Use that tool (Raycast, Shortcuts, 1Password, etc.)
   NO → Continue

3. Can I solve it with simple automation? (hotkey, script)
   YES → Do that, takes < 1 hour
   NO → Continue

4. Does it require memory/context/personalization?
   NO → Maybe wrong problem, reconsider
   YES → Continue

5. Does it need multi-session persistence?
   NO → ChatGPT/Claude Desktop might work
   YES → SSS candidate

6. Does it need context-aware loading?
   NO → Simple database might work
   YES → SSS architecture justified
```

### Examples Through This Filter

**Email address insert**:
- Frequent? Yes
- Existing tool? No
- Simple automation? Yes → **Raycast hotkey** ✅

**Subscription level recall**:
- Frequent? Yes
- Existing tool? No (1Password doesn't track tier names well)
- Simple automation? No (requires database)
- Needs memory? Yes
- Multi-session? Yes
- **SSS candidate** ✅

**Login method recall**:
- Frequent? Yes
- Existing tool? Partially (1Password has it, but requires opening + checking)
- Simple automation? No
- Needs memory? Yes
- Multi-session? Yes
- Context-aware? Yes (auto-answer when on login page)
- **SSS candidate** ✅

**Oil change tracking**:
- Frequent? Monthly
- Existing tool? No (Reminders sucks for this)
- Simple automation? No
- Needs memory? Yes
- Multi-session? Yes (months apart)
- Intelligent intervals? Yes (time + mileage)
- **SSS candidate** ✅

---

## Measurement: Time Saved + Frustration Eliminated

### Track Wins

For each solution (SSS or otherwise):
- **Frequency**: How often used (daily, weekly, monthly)
- **Time saved per use**: Seconds/minutes
- **Annual savings**: Frequency × time saved
- **Frustration score**: 1-10 (10 = rage-inducing)
- **Setup time**: How long to implement

### Example Scoring

**Raycast email insert**:
- Frequency: 20x/day
- Time saved: 5 seconds/use
- Annual: 20 × 5 × 365 = 36,500 seconds = 10 hours/year
- Frustration: 3/10 (minor annoyance)
- Setup: 2 minutes
- **ROI: Massive**

**Login method recall**:
- Frequency: 3x/day
- Time saved: 90 seconds/use (avoid 1Password → guess → retry)
- Annual: 3 × 90 × 365 = 98,550 seconds = 27 hours/year
- Frustration: 10/10 (rage + fear of duplicate accounts)
- Setup: TBD (needs SSS implementation)
- **ROI: Huge (if implemented)**

**Meeting action items**:
- Frequency: 3 meetings/day with action items
- Time saved: 5 minutes/meeting (capture + retrieval)
- Annual: 3 × 5 × 260 work days = 3,900 minutes = 65 hours/year
- Frustration: 8/10 (dropped commitments = career damage)
- Setup: TBD
- **ROI: Huge (if implemented)**

---

## Philosophy in Practice

### Question to Ask

"Is building this into SSS the **simplest** way to solve this problem?"

If yes → build it
If no → use simpler tool
If unsure → prototype with simple tool first, upgrade to SSS if needed

### Example: Subscription Tracking

**Could solve with**:
1. Spreadsheet in Numbers/Excel
2. Apple Notes list
3. 1Password secure note
4. Obsidian table
5. SSS memory server

**Why SSS wins**:
- Voice input ("I signed up for Cursor Pro")
- Voice query ("What's my Drafts tier?")
- Renewal reminders (integrated with push notifications)
- Usage tracking (mentions in conversations)
- Context-aware (loads during subscription discussions)

**Simpler solutions fail**:
- Spreadsheet: Can't query via voice, manual updates
- Notes: No structure, hard to search
- 1Password: Requires opening app, no tier-specific tracking
- Obsidian: Better, but still manual, no voice interface

**Verdict**: SSS justified ✅

### Example: Quick Calculations

**Problem**: Need to calculate tips, unit conversions, quick math

**Could solve with**:
1. SSS math tool
2. Siri ("Hey Siri, 18% tip on $47")
3. Spotlight calculator
4. ChatGPT

**Why SSS is overkill**:
- Siri already does this instantly
- No memory needed
- No context required
- General knowledge, not personal

**Verdict**: Use Siri, not SSS ❌

---

## Summary

**SSS exists to solve problems that**:
1. Happen frequently (daily/weekly)
2. Require personal memory (preferences, history, context)
3. Need cross-session persistence
4. Benefit from context-aware loading
5. **Can't be solved more simply**

**Everything else**: use the simplest tool that works.

**Goal**: 100x the number of small wins (Raycast-style), not build the most impressive architecture.

**Measure success by**: Time saved + frustration eliminated, not lines of code written.

---

**References**:
- See `/docs/examples/` for specific pain points
- See `/docs/examples/_TEMPLATE.md` for documenting new examples
- See global `~/.claude/CLAUDE.md` for user context and tool subscriptions
