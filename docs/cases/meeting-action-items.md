# Example: Meeting Action Items

**Category**: Productivity | Information capture
**Frequency**: Daily (for people with many meetings)
**Pain Level**: 8/10
**Status**: Not implemented

---

## Current State (What Sucks)

### The Scenario
You have a Zoom/Teams meeting with action items assigned. You need to remember what you committed to, follow through, and not let things fall through cracks.

### Current Painful Workflow

**During Meeting**:

**Step 1**: Try to take notes while listening
- Someone says: "Randy, can you send me that report by Friday?"
- You type/write: "Send report to John - Friday"
- Miss part of conversation while typing

**Step 2**: More action items pile up
- "Also follow up with Sarah about the API changes"
- "Review the proposal and send feedback"
- "Schedule next meeting for January"
- Notes becoming messy, incomplete

**After Meeting**:

**Step 3**: Try to process notes
- "What report did John want? Which report?"
- "Follow up with Sarah about... what specifically?"
- "When in January for next meeting?"

**Step 4**: Create reminders (maybe)
- Open Apple Reminders
- Create reminder: "Send report to John"
- Due date: Friday (which Friday? This one? Next one? Didn't write down the date)
- Create more reminders for other items
- Forget to create reminders for half the action items

**Step 5**: Reminders fail
- Friday reminder fires: "Send report to John"
- "Which report? What was this about?"
- Have to find meeting notes
- Or ask John (embarrassing: "What report did you need?")

**Week Later**:

**Step 6**: Discover dropped tasks
- Sarah: "Did you follow up on those API changes?"
- You: "Oh no, I completely forgot"
- Context is lost, have to reconstruct from memory or meeting recording

### Pain Points

- **Split attention**: Can't fully listen while taking notes
- **Incomplete capture**: Action items scattered in messy notes
- **Context loss**: "Send report" → which report? to whom? why?
- **Manual reminder creation**: Tedious, error-prone, often skipped
- **Arbitrary due dates**: "Friday" → which Friday? Guessing
- **Nagging without context**: Reminder fires, but you don't remember what it's about
- **Dropped commitments**: Items not captured fall through cracks
- **No follow-up tracking**: Did I do it? Did they respond?

---

## Ideal Future State

### Conversation (During or Right After Meeting)

**Human** (voice, while walking to next meeting): "Hey Claude, had a meeting with John and Sarah. I need to send John the Q4 revenue report by this Friday, follow up with Sarah about API changes to the webhook system, and schedule our next meeting for mid-January."

**Agent**: "Got it. Three action items from your meeting:

1. Send Q4 revenue report to John - due Friday Dec 22
2. Follow up with Sarah re: API changes to webhook system - no deadline mentioned, want one?
3. Schedule next meeting mid-January - who should I include?

Should I create these as action items?"

**Human**: "Yes. For the Sarah follow-up, sometime early next week. For the meeting, same group - John, Sarah, and me."

**Agent**: "Done. Action items created:

1. Q4 revenue report to John - I'll remind you Thursday morning
2. Sarah webhook API follow-up - I'll remind you Monday
3. Schedule meeting with John, Sarah, you for mid-Jan - I'll suggest times next week

Anything else from the meeting?"

**Human**: "No, that's it"

---

### Conversation (Reminder Firing - Context Included)

**Agent** (Thursday morning, push notification): "Reminder: Send Q4 revenue report to John by tomorrow (Friday). This is from your Tuesday meeting. The report is in your Obsidian vault at Business/Reports/Q4-2025-Revenue.md. Want me to draft the email?"

**Human**: "Yes"

**Agent**: "Draft email created in your Drafts app:

To: John <john@example.com>
Subject: Q4 Revenue Report

Hi John,

Attached is the Q4 revenue report we discussed in Tuesday's meeting.

[Report content here]

Let me know if you have questions.

Randy

Ready to send?"

---

### Conversation (Follow-up Tracking)

**Human** (Monday): "Did I send that report to John?"

**Agent**: "Yes, you sent the Q4 revenue report to John on Friday Dec 22 at 10:15 AM. He replied 'Thanks, looks good' at 11:30 AM. Action item completed."

**Human**: "Great. What other action items do I have?"

**Agent**: "You have 2 remaining from that meeting:
1. Follow up with Sarah about webhook API changes - due today, not started
2. Schedule meeting with John and Sarah for mid-January - not started

Want to tackle these now?"

---

## What Agent Does (Behind the Scenes)

### On Action Item Capture

1. **Parse natural language**:
   - "send John the Q4 revenue report by Friday"
   - Extract: action=send, recipient=John, item=Q4 revenue report, deadline=Friday

2. **Disambiguate**:
   - "Friday" → this Friday (Dec 22) or next Friday?
   - "Q4 revenue report" → specific document or need to create?

3. **Store structured data**:
```json
{
  "id": "action_001",
  "source": "meeting_2025-12-18_john_sarah",
  "action": "send_document",
  "what": "Q4 revenue report",
  "who": "John",
  "deadline": "2025-12-22",
  "status": "pending",
  "context": "From Tuesday meeting about quarterly review",
  "related_files": ["Business/Reports/Q4-2025-Revenue.md"]
}
```

4. **Create smart reminder**:
   - Remind 1 day before deadline (not on deadline)
   - Include full context in reminder
   - Link to related files/emails

### On Reminder Firing

1. **Load action item** with full context
2. **Locate relevant files** (Q4 revenue report in Obsidian)
3. **Present reminder** with context + resources
4. **Offer assistance** (draft email, find document, etc.)

### On Completion

1. **Mark action item** as completed
2. **Record completion time**
3. **Track follow-up** (did John respond? when?)
4. **Archive** but keep searchable

---

## Technical Requirements

### Information Needed

**Per Action Item**:
- Action description ("send report", "review proposal")
- Who's involved (recipient, collaborator)
- What's involved (document, deliverable)
- Deadline (date + time if applicable)
- Source meeting (when, with whom, why)
- Context (what was discussed, why this matters)
- Related files/emails/links
- Status (pending, in-progress, completed, blocked)
- Completion timestamp (when done)
- Follow-up tracking (responses, next steps)

### Context Triggers

Load action items when:
- Discussing tasks, todos, action items
- Asking "what do I need to do?"
- Mentioning specific people ("what did I promise John?")
- End of day review

Don't load when:
- Cooking, car maintenance, unrelated topics

### Tools/Integrations

**MCP Server**: `action_items_server.py` (new)

**Tools**:
- `create_action_item(description, who, what, deadline, context)` - Record new item
- `list_action_items(status, person, date_range)` - Show pending/completed
- `complete_action_item(id, notes)` - Mark as done
- `search_action_items(query)` - Find by person, topic, keyword

**External Integrations** (future):
- Calendar integration (show deadlines in calendar)
- Email integration (draft emails for "send X to Y" actions)
- Meeting transcription (auto-extract action items from Zoom/Teams)
- Things/OmniFocus integration (sync with existing task managers)

**Storage**:
- Simple: JSON file `~/data/action-items.json`
- Better: SQLite with time-series queries
- Best: Integrate with existing task manager (Things API)

---

## Success Criteria

✅ **Voice capture during/after meetings**
- No typing while in meeting, capture immediately after via voice

✅ **Context preservation**
- Reminders include full context: what, why, who, from which meeting

✅ **Smart reminder timing**
- Remind before deadline with time to act, not on due date

✅ **Related resource linking**
- "Send report" reminder includes link to the actual report

✅ **Completion tracking**
- "Did I do X?" → instant answer with timestamp and outcome

✅ **No dropped commitments**
- All action items captured, none fall through cracks

✅ **Follow-up awareness**
- Track whether recipient responded, next steps needed

---

## Implementation Priority

**Phase 1 - Basic Capture**:
- Voice input for action items
- Store with deadline and context
- Simple reminders before due date

**Phase 2 - Smart Context**:
- Link to related files/emails
- Include source meeting info in reminders
- Completion tracking with timestamps

**Phase 3 - Automation**:
- Meeting transcription → auto-extract action items
- Draft emails for "send X to Y" actions
- Sync with calendar/task managers

---

## Related Examples

- **Email follow-ups** (track whether you replied to important emails)
- **Project milestones** (larger tasks broken into action items)
- **Delegation tracking** (items you assigned to others)

**Common Pattern**: Commitments made verbally that need to be captured, contextualized, reminded with full information, and tracked through completion.

---

**Created**: 2025-12-20
**Status**: Not implemented
**Owner**: rk
