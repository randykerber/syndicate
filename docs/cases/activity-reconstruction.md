# Case: Activity Reconstruction - "What Was I Working On?"

**Category**: Information retrieval | Context reconstruction
**Frequency**: Weekly
**Pain Level**: 9/10
**Status**: Not implemented
**Mission**: Reconstruct past work sessions when memory has faded

---

## The Core Problem

**"What was I working on about X a couple weeks ago?"**

Not just "where is the file?" - but reconstruct the ENTIRE activity:
- What articles did I read?
- What code did I write?
- What notes did I take?
- What conversations did I have?
- What browser tabs were open?
- What was the outcome (finished? abandoned? paused?)

**Memory fades. Context is lost. Work is wasted.**

---

## Real Example (From Today)

### The Question
"A week or two ago I was investigating Context Engineering and memories management for Google Gemini. Where was I doing that? **What artifacts did I create?**"

### The Hidden Questions
- When exactly was this? (Dec 7? Dec 12? Don't remember)
- What prompted it? (Some article? A problem to solve?)
- What did I learn?
- Did I finish or abandon halfway?
- Are there browser tabs still open about it?
- Should I continue this work or was it a dead end?

### Current Painful Workflow

**Step 1**: Try to remember the timeline
- "Was this last week or the week before?"
- "Before or after I worked on Hedgeye pipelines?"
- "Was this a weekend project or weekday?"

**Step 2**: Check various activity logs
- Git commits (if code was written)
- File modification dates (`ls -lt`)
- Browser history (terrible for reconstruction)
- Obsidian daily notes (if you wrote any)

**Step 3**: Try to piece together fragments
- Found a file from Dec 13
- Found some browser history from Dec 7
- Found a Drafts note (undated)
- **Can't tell if these are related or separate activities**

**Step 4**: Missing context
- "Why was I doing this? What problem was I solving?"
- "Did I solve it or give up?"
- "Should I restart this or is it finished?"

**Step 5**: Usually give up
- Too hard to reconstruct
- Start from scratch
- Waste previous work

---

## Ideal Future State

### Conversation

**Human**: "What was I working on about Gemini context a couple weeks ago?"

**Agent**: "Found a work session on Gemini context engineering:

**When**: Dec 7-13, 2025 (6-day span)

**What you did**:

**Dec 7** (Saturday morning):
- Researched Gemini context and memories APIs
- Read 5 articles:
  - Google AI docs on context caching
  - Article about Gemini's memory system
  - Comparison of Claude vs Gemini context handling
- Created GEMINI-specific.md (296 bytes)
- Started browser workspace 'AI Context' in Arc (12 tabs)

**Dec 8** (Sunday):
- Wrote Python builder: gemini_builder.py
- Experimented with context assembly
- Took notes in Obsidian Tech: 'AI Context Systems'

**Dec 13** (Friday):
- Built final GEMINI.md (17KB)
- Tested with Gemini CLI
- Last modification to gemini_builder.py

**Outcome**:
- ✅ Completed: Working GEMINI.md context file
- ✅ Tested: Gemini CLI successfully loads context
- ⏸️  Paused: Didn't document how to update it or use memories API

**Artifacts created**:
- gemini_builder.py
- GEMINI.md (3 versions in ACE system)
- Obsidian note (partial)

**Browser tabs**: Closed (no longer in Arc), but I can restore the URLs if needed.

**Next step**: You stopped here. Want to continue with the memories API integration, or was this sufficient?"

---

### Alternative: Abandoned Work

**Human**: "What happened to my work on X from last month?"

**Agent**: "Found incomplete work on X from Nov 15-18:

**Activity**:
- Started research Nov 15 (5 articles read)
- Created draft design doc Nov 16
- Started coding Nov 17
- **Stopped abruptly Nov 18** (no activity since)

**What interrupted it**:
- Hedgeye pipeline emergency started Nov 18
- You never returned to X

**Status**:
- ❌ Incomplete: Design doc is draft, code is 30% done
- ⚠️  Risk: Dependencies may have updated since Nov
- 🗑️  Suggest: Archive or restart?

Want me to show you what you had, or should we archive it?"

---

## What Agent Does (Behind the Scenes)

### On "What was I working on about X?"

**1. Identify time range**:
- User said "a couple weeks ago"
- Search Dec 1-20 (generous range)
- Look for X-related activities

**2. Gather activities from all sources**:

**File system**:
- Files created/modified with "gemini" or "context" in name
- `ls -lt` sorted by modification date
- Git commits mentioning relevant keywords

**Browser history**:
- Sites visited about topic
- When tabs were opened/closed
- Arc workspaces created

**Code/documents**:
- Python files created/edited
- Markdown notes in Obsidian
- Drafts entries

**Conversations**:
- Claude Code sessions discussing topic
- Search chat logs for relevant keywords

**3. Construct timeline**:
```
Timeline: Gemini Context Work (Dec 7-13)

Dec 7 09:30 - Read Google AI docs (browser)
Dec 7 10:15 - Created GEMINI-specific.md (file)
Dec 8 14:20 - Wrote gemini_builder.py (git commit)
Dec 8 15:45 - Chat with Claude about context assembly (session log)
Dec 13 11:00 - Built GEMINI.md final version (file modified)
Dec 13 11:30 - Tested with Gemini CLI (terminal history?)
```

**4. Determine outcome**:
- Completed? (artifacts exist, no TODOs left)
- In progress? (recent activity, no conclusion)
- Abandoned? (stopped abruptly, no recent activity)

**5. Present reconstruction**:
- Timeline of activities
- Artifacts created
- Outcome/status
- Next steps (if known)

---

## Technical Requirements

### Activity Sources

**File system**:
- File creation/modification times
- Git commit history
- File content changes (git diff)

**Browser**:
- History (sites visited, timestamps)
- Tab sessions (Arc workspaces, Chrome sessions)
- Bookmarks created

**Applications**:
- Obsidian daily notes
- Drafts timestamps
- Bear note creation dates
- Email sent/received

**Terminal**:
- Bash/zsh history
- Commands run (with timestamps if available)

**Conversations**:
- Claude Code session logs
- Claude Desktop chat history
- Gemini CLI history

**Calendar/Tasks** (optional):
- Calendar events during timeframe
- Tasks completed in Things
- Reminders checked off

### Context Triggers

Load activity reconstruction when:
- User asks "what was I working on...?"
- User mentions past timeframe ("last week", "a couple weeks ago")
- User mentions they lost context on something

### Tools/Integrations

**MCP Server**: `activity_server.py` (new) or extend `search_server.py`

**Tools**:
- `reconstruct_activity(topic, date_range)` → timeline
- `find_artifacts(topic, date_range)` → created files/notes
- `get_work_session(date)` → what happened on specific day
- `identify_outcome(activity)` → completed/in-progress/abandoned

**External Integrations**:
- File system (mdfind, ls, git log)
- Browser history APIs (Arc, Chrome)
- Obsidian MCP
- Claude Code session logs
- Terminal history

---

## Success Criteria

✅ **Reconstruct timeline**
- "When did I work on this?" → date range + key events

✅ **Identify all artifacts**
- Files created, notes taken, commits made

✅ **Show outcome**
- Completed? In progress? Abandoned?

✅ **Provide context**
- "Why did I stop?" (interruption? finished? gave up?)

✅ **Enable continuation**
- "Here's where you left off, want to resume?"

✅ **Voice accessible**
- "Hey Siri, what was I doing with Gemini context last week?"

---

## This Is an Exemplar

**Not about**: "Reconstruct Gemini context work specifically"

**About**: The PRINCIPLE that:
- Past work shouldn't be lost when memory fades
- Agent should be able to reconstruct activity from scattered artifacts
- Timeline + artifacts + outcome = recoverable context

**Other examples of this pattern**:
- "What happened to my Hedgeye pipeline refactor?" (started, interrupted, forgot)
- "Did I finish that Obsidian plugin research?" (don't remember outcome)
- "Where did I leave off with the recipe database?" (paused weeks ago, can't recall why)

**Same principle, different topics.**

---

## Relationship to Cross-Silo Search

**Cross-Silo Search** = "Find X" (locate artifacts)
**Activity Reconstruction** = "What was I doing with X?" (understand context)

**Combined power**:
- Search finds artifacts across silos
- Reconstruction builds timeline from those artifacts
- Together: complete picture of past work

---

## Implementation Priority

**Phase 1 - File-based Reconstruction**:
- File modification timeline
- Git commit history
- Simple timeline display

**Phase 2 - Browser Integration**:
- Browser history correlation
- Tab session reconstruction
- Bookmark/workspace tracking

**Phase 3 - Conversation Logs**:
- Claude Code session history
- Search chat logs for topic
- Correlate with file activity

**Phase 4 - AI-Powered Analysis**:
- Detect work patterns (when do you usually work on what?)
- Identify interruptions (what caused you to stop?)
- Suggest continuation points (where to resume)

---

## Related Cases

- **Cross-Silo Search** - Find artifacts across apps
- **Information Loss Prevention** - Prevent losing work in first place
- **Project Status Tracking** - Know what's done/pending/abandoned

**Common Pattern**: Memory fades, context is lost, need to reconstruct past activities to avoid wasting previous work.

---

**Created**: 2025-12-20
**Status**: Not implemented
**Owner**: rk
**Mission**: Context shouldn't be lost when memory fades - agent remembers so you don't have to
