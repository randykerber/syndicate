# Example: Vehicle Maintenance Tracking

**Category**: Maintenance Tracking
**Frequency**: Every 3-6 months (per vehicle)
**Pain Level**: 7/10
**Status**: Not implemented

---

## Current State (What Sucks)

### The Scenario
You just got an oil change on the 2011 Lexus GX460. You want to record this fact so you can:
1. Remember when it was done (months later when it matters)
2. Track odometer reading at time of change
3. Get reminded when next oil change is needed
4. Not lose this information in the chaos of daily life

### Current Painful Workflow

**Step 1: Capture the information**
- If on the road → Add to Drafts (quick capture, but wrong destination)
- If at home → Try to add directly to Bear (slower, requires finding right page)

**Step 2: Find the right place in Bear**
- Search for "Lexus GX460" note
- Hope the note exists (did I create it? what did I name it?)
- If it doesn't exist, create it now (more friction)
- Navigate to correct section (maintenance log? service history?)

**Step 3: Manually format the entry**
```
Oil Change - December 18, 2025
- Odometer: 127,543 miles
- Location: Jiffy Lube
- Cost: $75
- Notes: Used synthetic 5W-30
```

**Step 4: Create a reminder (the annoying part)**
- Open Apple Reminders
- Create new reminder: "Check Lexus oil change"
- **When to schedule it?** No idea. Guess 3 months? 3,000 miles? Both?
- Pick arbitrary date: March 18, 2026
- Hope you remember why this reminder exists when it fires

**Step 5 (3 months later): Deal with nagging reminder**
- Reminder fires: "Check Lexus oil change"
- Is it actually time? Can't remember
- Need to check odometer (requires going to car)
- If not time yet, snooze or reschedule (painful in Apple Reminders)
- If time, do oil change, repeat entire process

### Pain Points

- **Information loss**: Easy to forget to record entirely
- **Manual formatting**: Have to structure the data yourself
- **App switching**: Drafts → Bear → Reminders → multiple apps
- **Arbitrary scheduling**: No intelligent calculation of when next change needed
- **Nagging reminders**: Generic "check oil" doesn't tell you if it's actually time
- **Context loss**: 3 months later, "why did I set this reminder?"
- **Friction**: Multiple steps discourage recording information
- **No intelligence**: System doesn't know vehicle maintenance intervals
- **Retrieval failure**: Months later, "when was last oil change?" requires manual search

---

## Ideal Future State

### Conversation (Just After Oil Change)

**Human** (via voice): "Hey Claude, I changed the oil on the Lexus yesterday"

**Agent**: "Got it. What's the current odometer reading?"

**Human**: "127,543 miles"

**Agent**: "Recorded. Oil change on Lexus GX460 - December 18, 2025 at 127,543 miles. I'll check in when you're due for the next one."

*[That's it. No app switching, no manual formatting, no arbitrary reminder dates]*

---

### Conversation (3 Months Later)

**Human** (via voice): "Hey Claude, any maintenance needed on the Lexus?"

**Agent**: "Last oil change was December 18 at 127,543 miles. What's your current mileage?"

**Human**: "130,200"

**Agent**: "You've driven 2,657 miles. Typically oil changes are every 5,000 miles or 6 months. You're at 3.5 months and 53% of mileage interval. You're good for now - I'll remind you around late February or 132,000 miles, whichever comes first."

*[Agent calculated actual need based on both time and mileage]*

---

### Alternative: Proactive Check-In

**Agent** (via push notification - late February): "Your Lexus might be due for oil change soon (last changed Dec 18). Want me to check?"

**Human**: "Yes"

**Agent**: "What's your current odometer?"

**Human**: "132,400"

**Agent**: "You've hit the mileage interval (5,000 miles since last change). Time to schedule an oil change."

---

## What Agent Does (Behind the Scenes)

### On Initial Recording ("changed oil yesterday")

1. **Parse natural language**:
   - Vehicle: Lexus (assumes GX460, could disambiguate if multiple Lexus)
   - Action: Oil change
   - Date: "yesterday" → December 17, 2025

2. **Ask for missing data**:
   - Odometer reading (required for mileage tracking)

3. **Store structured data** (in vehicle maintenance DB):
```json
{
  "vehicle": "2011_Lexus_GX460",
  "event_type": "oil_change",
  "date": "2025-12-18",
  "odometer": 127543,
  "source": "user_voice_input",
  "confidence": "high"
}
```

4. **Update vehicle knowledge base**:
   - Last oil change: 2025-12-18
   - Last odometer reading: 127,543

5. **Calculate next service**:
   - Interval: 5,000 miles OR 6 months (whichever first)
   - Target date: ~June 18, 2026
   - Target mileage: ~132,543

6. **Create intelligent reminder** (not shown to user):
   - Check-in date: Late February (50% of time interval)
   - Don't nag - wait for user to ask OR proactively offer check when time is close

### On Retrieval ("any maintenance needed?")

1. **Load vehicle knowledge base** (context-triggered by "Lexus")
2. **Retrieve last oil change record**
3. **Ask for current odometer** (needed to calculate actual interval)
4. **Calculate status**:
   - Time elapsed: 3.5 months / 6 months = 58%
   - Miles driven: 2,657 / 5,000 = 53%
   - Status: Not due yet
5. **Provide informative answer** with calculations shown

---

## Technical Requirements

### Information Needed

**Vehicle Profile**:
- Make/Model/Year: 2011 Lexus GX460
- VIN (optional): JTJBM7FX8B5[xxxxx]
- Maintenance intervals:
  - Oil change: 5,000 miles or 6 months
  - Tire rotation: 5,000 miles
  - Air filter: 30,000 miles
  - [Could be looked up by VIN or user-provided]

**Maintenance Events** (time-series):
- Event type (oil change, tire rotation, brake service, etc.)
- Date
- Odometer reading
- Location (optional)
- Cost (optional)
- Notes (optional)

### Context Triggers

Load vehicle knowledge base when conversation involves:
- Car maintenance keywords (oil, tire, brake, filter, fluid)
- Vehicle name ("Lexus", "the car")
- Maintenance verbs (changed, replaced, serviced, checked)

Don't load when:
- Conversation about other topics (cooking, travel, investing)

### Tools/Integrations

**MCP Server**: `vehicle_server.py` (new)

**Tools**:
- `record_maintenance(vehicle, event_type, date, odometer, notes)` - Store event
- `get_last_service(vehicle, event_type)` - Retrieve last occurrence
- `calculate_service_status(vehicle, event_type, current_odometer)` - Check if due
- `get_maintenance_history(vehicle)` - Full service log

**External Integrations** (future):
- Vehicle maintenance API (look up intervals by VIN)
- Calendar integration (block time for service)
- Service center API (check availability, book appointment)

**Storage**:
- Simple: JSON file (`~/data/vehicles.json`)
- Better: SQLite database (time-series queries)
- Best: Postgres with proper schema

### Natural Language Processing

**Extract from**: "I changed the oil on the Lexus yesterday"
- Vehicle: "Lexus" → resolve to "2011_Lexus_GX460"
- Event: "changed the oil" → event_type: "oil_change"
- Date: "yesterday" → calculate actual date

**Missing data handling**:
- Odometer reading → ask user
- Service location → optional, don't ask unless user provides
- Cost → optional, don't ask

---

## Success Criteria

✅ **Information capture is frictionless**
- Voice input only, no app switching
- Natural language parsing (not "create oil change record at odometer 127543")

✅ **No arbitrary reminder dates**
- Agent calculates actual intervals based on time + mileage
- No guessing "3 months from now" - system knows when to check in

✅ **Intelligent retrieval**
- Months later, "when was last oil change?" returns immediate answer
- "Any maintenance needed?" calculates actual status, not just reminder date

✅ **Context-aware loading**
- Vehicle data only loaded during car-related conversations
- Not cluttering context during cooking/travel discussions

✅ **Proactive but not nagging**
- Agent checks in when approaching due date
- Asks for current odometer to make real calculation
- Single notification, not daily nagging

✅ **Human-in-the-loop for accuracy**
- Agent asks for odometer (can't guess)
- Confirms understanding ("Oil change on Lexus GX460 - Dec 18")
- User can correct if wrong

✅ **Zero information loss**
- All maintenance history preserved
- Searchable months/years later
- No "where did I write that down?" moments

---

## Implementation Priority

**Phase 1 - Basic Recording** (MVP):
- `vehicle_server.py` with record_maintenance and get_last_service tools
- Simple JSON storage
- Manual interval configuration (user tells agent "oil every 5k miles")

**Phase 2 - Intelligent Reminders**:
- Calculate service intervals based on time + mileage
- Proactive check-ins via push notifications
- Status calculation ("53% of interval")

**Phase 3 - Full Integration**:
- VIN lookup for manufacturer maintenance schedules
- Calendar integration for booking appointments
- Service center recommendations
- Cost tracking and budgeting

---

## Related Examples

- **Home appliance maintenance**: HVAC filter changes, smoke detector batteries
- **Subscription tracking**: "Renewed Netflix subscription" → track renewal dates
- **Medical**: "Had physical yesterday" → schedule next annual physical
- **Pet care**: "Gave dog heartworm pill" → track monthly medication

**Common Pattern**: Infrequent events that need tracking across months/years, with intelligent interval-based reminders, where current tools force manual scheduling and create nagging reminders.

---

**Created**: 2025-12-20
**Status**: Example only - not implemented
**Owner**: rk
