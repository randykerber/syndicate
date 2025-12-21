# Case: Podcast Transcript Processing

**Category**: Information capture | Knowledge management
**Frequency**: Daily (multiple podcasts per week)
**Pain Level**: 7/10
**Status**: Not implemented
**Source**: Real draft from 2025-12-20 (Ian Harnett on Alpha Exchange)

---

## Current State (What Sucks)

### The Scenario
Listening to podcast on iPhone. Guest says something interesting. Want to capture it for later reference in Obsidian knowledge base.

### Current Painful Workflow

**Step 1**: Listen to podcast in app (Overcast, Apple Podcasts, etc.)
- Hear interesting quote or insight
- Want to save it

**Step 2**: Open Snipd app (or similar)
- Find the episode
- Copy transcript snippet
- Transcript might have errors

**Step 3**: Switch to Drafts app
- Create new draft
- Type guest name (often misspelled: "Ian Hartnett" instead of "Ian Harnett")
- Paste transcript from Snipd
- Add context manually (show name, date)

**Step 4**: Leave it in Drafts inbox
- Draft sits unprocessed
- Episode not finished yet, might add more later
- Will forget about it

**Step 5** (eventual manual processing):
- Open Obsidian Fin vault
- Search for guest's page (do they have one? what's the exact spelling?)
- Create person page if doesn't exist
- Figure out structure (how did I format last episode?)
- Copy-paste from Drafts
- Add metadata (episode title, URL, date)
- Update daily note with link
- Remember to delete from Drafts (usually forget)

### Pain Points

- **Spelling errors**: Hearing name → typing name → wrong spelling → propagates
- **App switching**: Podcast → Snipd → Drafts → Obsidian (4 apps)
- **Manual metadata**: Episode title, URL, date - have to look up
- **Inconsistent structure**: Forget how I formatted previous episodes
- **Drafts purgatory**: Notes sit unprocessed for weeks
- **Multi-file updates**: Person page + daily note + episode index (if exists)
- **Incomplete content**: Episode not done, but don't want to lose snippet
- **Context loss**: Weeks later, "What podcast was this from?"

---

## Ideal Future State

### Conversation (During Podcast)

**Human** (via Siri while listening): "Hey Claude, save this podcast snippet"

**Agent**: "Got it. I see you're listening to Alpha Exchange from Dec 18. Guest is Ian Harnett. I'll grab the transcript from Snipd. What timestamp?"

**Human**: "Last 30 seconds"

**Agent**: "Saved. Want me to add it to Ian Harnett's page now, or wait until you finish the episode?"

**Human**: "Wait till I'm done"

**Agent**: "OK, I'll hold it in your inbox. I'll check in after the episode ends."

---

### Conversation (After Episode Ends)

**Agent** (push notification): "You finished Alpha Exchange with Ian Harnett. Ready to process that snippet?"

**Human**: "Yes"

**Agent**: "I found Ian Harnett's page in your Fin vault. Adding this under Episodes section. Also linking from today's daily note. Done."

*[No Obsidian opening, no copy-paste, no formatting]*

---

### Alternative: Immediate Processing

**Human** (via voice): "Save this to Ian Harnett's page"

**Agent**: "Adding to Ian Harnett's Obsidian page now. I see you misspelled his name in your draft as 'Hartnett' - I've corrected it. Episode title is 'Systemic Risk and Private Credit Markets' from Alpha Exchange Dec 18. Added to his Episodes section and linked from today's note."

---

## What Agent Does (Behind the Scenes)

### On "Save this podcast snippet"

1. **Detect context**:
   - User listening to podcast (via Now Playing API or app detection)
   - Episode: Alpha Exchange, Dec 18, 2025
   - Guest: Ian Harnett (extracted from episode metadata)

2. **Get transcript**:
   - Query Snipd API for recent segment
   - Or use podcast transcript service
   - Extract last 30 seconds (or whatever user specified)

3. **Create draft** with metadata:
```markdown
Ian Harnett

on: Alpha Exchange
date: 2025-12-18
status: pending (episode not finished)

{transcript content}
```

4. **Wait for completion signal** (or user says "process now")

### On Processing

1. **Fix spelling errors**:
   - "Ian Hartnett" → check against known entities
   - Find existing `[[Ian Harnett]]` page in Fin vault
   - Correct spelling

2. **Extract/fetch metadata**:
   - Episode title: Query podcast API or Snipd
   - Episode URL: Get from podcast feed
   - Date: Extract from episode metadata
   - Show: "Alpha Exchange" (recognize as podcast show)

3. **Update person page** (`Fin/People/Ian Harnett.md`):
   - Find or create `## Episodes` section
   - Add new episode entry:
```markdown
### on Alpha Exchange 2025-12-18

on: [[Alpha Exchange]]
when: 2025-12-18
title: Systemic Risk and Private Credit Markets
url: https://podcasts.apple.com/...

Systemic risk is multiplicative. When a node goes to zero, the network stops working.

Lehman was not small enough to let die.

[...rest of transcript...]
```

4. **Update daily note** (`Fin/Daily/2025-12-20.md`):
   - Create file if doesn't exist
   - Append to end:
```markdown
### Ian Harnett on Alpha Exchange
- [[Ian Harnett#on Alpha Exchange 2025-12-18]]
```

5. **Archive draft** (remove from Drafts inbox)

---

## Technical Requirements

### Information Needed

**Episode Metadata**:
- Podcast show name
- Episode title
- Episode date
- Episode URL
- Guest name(s)
- Timestamp (if snippet)

**Entity Recognition**:
- Person names (guests, hosts)
- Podcast shows
- Common misspellings (Hartnett vs Harnett)

**Obsidian Structure**:
- Which vault (Fin for investing podcasts, Tech for tech podcasts)
- Person page location (`People/` or root?)
- Daily note location and format
- Episode section template

### Context Triggers

Load podcast processing when:
- Drafts content mentions podcast shows (Alpha Exchange, etc.)
- Content has transcript-like format (speaker + content)
- User says "save podcast snippet" or "process episode"

### Tools/Integrations

**MCP Server**: `podcast_server.py` (new) or extend `drafts_server.py`

**Tools**:
- `detect_podcast_content(text)` → identify if content is podcast transcript
- `extract_episode_metadata(show_name, date)` → get title, URL from API
- `fix_entity_spelling(text, entity_type)` → correct common misspellings
- `update_person_page(name, episode_data, vault)` → add to person's page
- `update_daily_note(date, link, vault)` → add to daily note
- `get_transcript_segment(episode, timestamp, duration)` → fetch from Snipd/podcast API

**External Integrations**:
- **Snipd API** (if available) - transcript extraction
- **Podcast APIs** (Apple Podcasts, Spotify, RSS feeds) - episode metadata
- **Now Playing API** (iOS/macOS) - detect what user is listening to
- **Obsidian MCP** (already exists) - file read/write in vaults
- **Entity database** - known people, shows, common misspellings

**Storage**:
- Obsidian vaults (Fin, Tech)
- Metadata cache (episode info, person info)
- Misspelling dictionary (Hartnett→Harnett, etc.)

---

## Success Criteria

✅ **Voice capture during listening**
- No app switching, speak to save snippet

✅ **Automatic metadata extraction**
- Episode title, URL, date fetched automatically

✅ **Spelling correction**
- "Hartnett" → "Harnett" corrected automatically

✅ **Multi-file orchestration**
- Person page + daily note updated atomically

✅ **Wait for completion**
- Can hold snippet until episode done

✅ **Zero manual formatting**
- Agent knows the template, applies consistently

✅ **Context preservation**
- Weeks later, snippet has full context (show, date, URL)

---

## Real-World Complexity

### From Actual Draft (2025-12-20)

**Input**:
```
Ian Hartnett

Systemic risk is multiplicative. When a node goes to zero, the network stops working.

Lehman was not small enough to let die.

Risk builds during low volatility, high liquidity.
[...]
```

**Issues detected**:
1. Misspelled name (Hartnett vs Harnett)
2. No episode metadata (show, date, URL)
3. Mixed input (manual + Snipd paste)
4. Incomplete (episode not finished)
5. No structure (just raw content)

**Processing needed**:
- Spell correction
- Metadata lookup (Alpha Exchange, Dec 18)
- Template application (Episodes section format)
- Multi-file update (person page + daily note)
- Status tracking (wait for episode completion)

---

## Implementation Priority

**Phase 1 - Manual Assist**:
- Detect podcast content in Drafts
- Suggest person page to update
- Offer to fix spelling
- Human confirms each step

**Phase 2 - Metadata Automation**:
- Fetch episode metadata from APIs
- Auto-populate template
- Still require human confirmation

**Phase 3 - Full Automation**:
- Voice capture during listening
- Automatic processing on episode completion
- No human intervention needed

---

## Related Cases

- **YouTube video notes** (similar: video → transcript → person page)
- **Meeting notes** (similar: transcript → action items → person pages)
- **Book highlights** (similar: Kindle → quotes → book page)

**Common Pattern**: Transcript/content from external source → entity recognition → structured storage in knowledge base with metadata and cross-linking.

---

**Created**: 2025-12-20
**Status**: Not implemented
**Owner**: rk
**Source**: Real draft analyzing Ian Harnett on Alpha Exchange
