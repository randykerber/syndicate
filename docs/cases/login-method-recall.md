# Example: Login Method Recall

**Category**: Information capture | Authentication
**Frequency**: Daily (multiple times)
**Pain Level**: 10/10
**Status**: Not implemented

---

## Current State (What Sucks)

### The Scenario
You need to login to a service. The site asks: "How do you want to sign in?"

Options presented:
- Email address
- Phone number
- Username
- Continue with Google
- Continue with Apple
- Continue with GitHub
- Continue with Microsoft
- Continue with Facebook

**You have no idea which one you used when you created the account.**

### Current Painful Workflow

**Step 1**: See login page with multiple options
- "How do I login to this site?"
- "Did I use email or Google?"
- "Or was it Apple Sign In?"

**Step 2**: Fear paralysis
- "If I pick the wrong method, will it create a SECOND account?"
- "Will I end up with duplicate accounts that are impossible to merge?"
- "Will I have to contact customer service?" (kiss of death)
- "I'm not guessing, this could go very wrong"

**Step 3**: Give up on guessing, open 1Password
- Search for service name
- Open entry
- Look at details
- "Okay, username is my email... but does that mean I login with email or Google?"
- Check notes field (if you remembered to document it)

**Step 4**: Still not sure from 1Password
- Try to remember when you created account
- "Was this before or after I started using Google login everywhere?"
- "Did this site even support Apple Sign In back then?"

**Step 5**: Eventually try one method
- Success: "Phew, got lucky"
- Failure: "Wrong method, trying next one"
- Repeat until success or give up

**Step 6**: Workaround for next time
- Edit 1Password entry name: "ServiceName (Google login)"
- Or add note: "LOGIN METHOD: Apple Sign In"
- Next time: still have to open 1Password to check

### Pain Points

- **No memory**: Can't remember which login method for 100+ services
- **High stakes**: Fear of creating duplicate accounts
- **Customer service hell**: Merging accounts requires support ticket nightmare
- **No standard**: Every site offers different combinations of options
- **1Password doesn't track this**: Have to manually add notes
- **Frequency**: Happens daily across different services
- **Friction**: Have to open 1Password, read notes, then login
- **Manual workaround**: Rename entries to include login method clue

### Common Culprits

Services with multiple login options:
- Medium (email, Google, Apple, Twitter, Facebook)
- Notion (email, Google, Apple)
- Figma (email, Google)
- Linear (email, Google, GitHub)
- Discord (email, phone, QR code)
- Slack (email, Google, Apple, SSO)
- Hundreds more...

---

## Ideal Future State

### Conversation (At Login Screen)

**Human** (via phone): "Hey Siri, how do I login to Medium?"

**Agent**: "Medium - use Apple Sign In"

**Human**: *taps Apple button* → Logged in

---

**Human**: "Which login method for Notion?"

**Agent**: "Notion - Continue with Google (rk@example.com)"

---

**Human**: "How do I sign into Discord?"

**Agent**: "Discord - email address (you tried phone number once, but primary method is email)"

---

### Alternative: Visual Recognition (Future)

**On login screen**:
- Phone camera sees multiple login buttons
- Agent: "Use the Apple Sign In button for this site"
- Visual highlight of correct button

---

## What Agent Does (Behind the Scenes)

### On "How do I login to X?"

1. **Query login methods database**:
   - Service: Medium
   - Primary method: Apple Sign In
   - Email used: rk@example.com (Apple ID email)
   - Backup method: Email (if Apple Sign In unavailable)

2. **Return answer**:
   - Immediate, confident response
   - No 1Password lookup needed
   - No guessing

### Initial Population

**Option A - Manual Recording**:
```
Human (after successful login): "I just logged into Medium with Apple Sign In"
Agent: "Recorded: Medium → Apple Sign In"
```

**Option B - 1Password Import**:
- Agent reads 1Password entries
- Extracts login method from:
  - Entry names (if you renamed them)
  - Notes field (if documented)
  - Username field analysis (email vs username pattern)

**Option C - Browser Extension** (future):
- Watches successful logins
- Records which button was clicked
- Auto-updates database

### Handling Multiple Methods

If service allows multiple methods:
```
Human: "How do I login to Slack?"
Agent: "Slack has 2 methods for you:
  Primary: Google (rk@example.com)
  Backup: Email + password (same address)
Use Google unless it's unavailable"
```

---

## Technical Requirements

### Information Needed

**Per Service**:
- Service name
- Primary login method (email, phone, username, Google, Apple, GitHub, etc.)
- Account identifier (which email, which phone number)
- Backup methods (if any)
- Notes (e.g., "SSO for work Slack, personal login for other Slack")
- Last successful login date
- Created date (helps determine likely method for old accounts)

### Context Triggers

Load login methods database when:
- On a login page (browser extension detects)
- Asking "how do I login to X?"
- Asking "which method for X?"

### Tools/Integrations

**MCP Server**: `auth_server.py` (new)

**Tools**:
- `lookup_login_method(service)` → primary method + backups
- `record_login_method(service, method, identifier)` → save after login
- `list_services_by_method(method)` → "which sites use Google login?"

**External Integrations** (future):
- 1Password API (import existing entries)
- Browser extension (watch successful logins)
- Passkey integration (track passkey-enabled sites)

**Storage**:
- Simple: JSON file with login method mappings
- Better: SQLite with login history
- Best: Integrated with password manager

---

## Success Criteria

✅ **Instant recall**
- "How do I login to X?" → immediate answer

✅ **Voice accessible**
- Ask Siri/Claude while looking at login screen on phone

✅ **Zero fear**
- Confident answer eliminates duplicate account risk

✅ **No 1Password lookup**
- Don't have to open 1Password to check notes

✅ **Works across all devices**
- Database synced, available on phone, Mac, iPad

✅ **Passive recording**
- Agent learns from successful logins without manual entry

---

## Implementation Priority

**Phase 1 - Manual Database**:
- After login: "I used Google login for Notion"
- Query: "How do I login to Notion?" → "Google"
- JSON storage

**Phase 2 - 1Password Import**:
- Extract login methods from existing entries
- Parse entry names/notes for clues
- One-time population of database

**Phase 3 - Browser Extension**:
- Detect login button clicks
- Record successful logins automatically
- Update database in background

**Phase 4 - Visual Assist**:
- Camera sees login screen
- Highlights correct button
- "Tap this one"

---

## Related Examples

- **Subscription level recall** (What tier of X do I have?)
- **Password lookup** (What's my password for X?)
- **Account email recall** (Which email did I use for X?)

**Common Pattern**: Authentication information you can't remember, requiring multi-step lookup or guessing with high error cost.

---

## Real-World Impact

**Frequency**: 3-5 times per day (different services, re-logins)
**Time saved**: 1-2 minutes per lookup × 5/day = 5-10 min/day = 30-60 hours/year
**Error prevention**: Eliminates duplicate account creation risk
**Frustration reduction**: Massive (no more login method guessing game)

**Current workarounds**:
- Rename 1Password entries: "Medium (Apple login)"
- Add notes to entries: "LOGIN: Google"
- Keep trying methods until one works (risky)
- Just use "Forgot password" every time (creates more problems)

**Why this is so painful**:
- High frequency (daily logins)
- High stakes (duplicate account = hell)
- No good solution exists (password managers don't track this well)
- Manual workarounds are tedious and incomplete

---

**Created**: 2025-12-20
**Status**: Not implemented
**Owner**: rk
**Inspiration**: "HOW THE HELL CAN I REMEMBER... if I go thru the wrong door, I have the potential of accidentally creating... super-duper, super-sized hell"
