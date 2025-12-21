# Example: Subscription Level Recall

**Category**: Information capture | Subscriptions
**Frequency**: Multiple times per week
**Pain Level**: 9/10
**Status**: Not implemented

---

## Current State (What Sucks)

### The Scenario
You need to know your subscription level for a service. You KNOW you're paying for it, but can't remember if it's called "Pro", "Plus", "Premium", "Advanced", "Professional", or something else. Service wants you to know this before you can proceed.

### Current Painful Workflow

**Step 1**: Try to remember
- "I have Drafts... Pro? Or is it Plus?"
- "Is it called Premium? Advanced?"
- "I'm definitely paying for it, but what's it called?"

**Step 2**: Check the app (if possible)
- Open Drafts Mac app
- Look for subscription info
- Can't find it anywhere obvious
- "Where the hell does it show my subscription level?"

**Step 3**: Give up on app, try website
- Open 1Password
- Search for Drafts login
- Navigate to Drafts website
- Login (if you can remember the password)
- Hunt for account settings
- Find subscription page
- "Oh right, it's Drafts Pro"

**Step 4**: Repeat this same process in 2 weeks
- Completely forget again
- "Was it Pro or Plus?"
- Burn another 2-5 minutes

**Common Victims**:
- OpenAI (Free, Plus, Team, Enterprise)
- Claude (Free, Pro, Team, Enterprise)
- Gemini (Free, Advanced, Business)
- JetBrains (Individual, Classroom, Organization, All Products Pack)
- Cursor (Free, Pro, Business)
- Drafts (Free, Pro)
- Obsidian (Free, Catalyst, Commercial)
- ChatGPT (same as OpenAI)
- Dozens more...

### Pain Points

- **Memory failure**: Know you're paid, can't remember specific name
- **No standard naming**: Every service uses different terms (Pro vs Plus vs Premium)
- **App doesn't show it**: Many apps hide subscription level
- **Multi-step lookup**: 1Password → website → login → account → subscription
- **Frequency**: Happens multiple times per week across different services
- **Frustration**: "I'm PAYING YOU and you make me guess my tier?"
- **Time waste**: 2-5 minutes per lookup, adds up fast

---

## Ideal Future State

### Conversation

**Human** (via Siri/Claude): "What's my subscription level for Drafts?"

**Agent**: "Drafts Pro - $19.99/year, renewed Oct 15, 2025"

---

**Human**: "What tier of Claude do I have?"

**Agent**: "Claude Pro - $20/month, started Nov 2024"

---

**Human**: "Am I paying for Cursor?"

**Agent**: "Yes, Cursor Pro - $20/month, renewed Dec 1, 2025"

---

**Human**: "Do I have free or paid Obsidian?"

**Agent**: "Obsidian Sync subscription - $8/month (not Catalyst tier, just standard with Sync add-on)"

---

## What Agent Does (Behind the Scenes)

### On "What's my subscription level for X?"

1. **Query subscription database**:
   - Service: Drafts
   - Tier: Pro
   - Cost: $19.99/year
   - Last renewal: Oct 15, 2025

2. **Return immediate answer**:
   - No app opening
   - No website navigation
   - No 1Password lookup
   - Instant recall

### Initial Population (One-Time Setup)

**Option A - Manual Entry**:
```
Human: "I have Drafts Pro, $20/year"
Agent: "Recorded: Drafts Pro subscription"
```

**Option B - 1Password Import** (future):
- Agent reads subscription entries from 1Password
- Extracts service name + tier from entry names
- Builds subscription database

**Option C - Receipt Scanning** (future):
- Agent monitors email for subscription receipts
- Extracts: service, tier, cost, renewal date
- Auto-updates database

---

## Technical Requirements

### Information Needed

**Per Subscription**:
- Service name (Drafts, Claude, Cursor, etc.)
- Tier name (Pro, Plus, Premium, Free, etc.)
- Cost (amount + frequency)
- Payment method (credit card, PayPal)
- Renewal date
- Login method (email, username, Google, Apple, GitHub)
- Account email (which email address)
- Status (active, cancelled)

### Context Triggers

Load subscription database when:
- Asking about "subscription", "tier", "level", "plan"
- Asking "do I have X?" (any service name)
- Asking "what am I paying for?"

### Tools/Integrations

**MCP Server**: `subscriptions_server.py` (extends subscription-tracking example)

**New Tools**:
- `lookup_subscription_tier(service_name)` → tier + cost + renewal
- `add_subscription_tier(service, tier, cost, frequency)` → record
- `list_all_subscriptions()` → show all paid services with tiers

**External Integrations** (future):
- 1Password API (read subscription entries)
- Email receipt parsing (auto-detect renewals)
- Service APIs (fetch current tier directly)

**Storage**:
- Simple: JSON file with subscription details
- Better: Same database as subscription-tracking example

---

## Success Criteria

✅ **Instant recall**
- "What's my Drafts tier?" → immediate answer, zero friction

✅ **No app/website navigation**
- Don't have to open app, visit website, or check 1Password

✅ **Works for all services**
- One database, all subscriptions tracked

✅ **Voice accessible**
- Via Siri, Claude, or any agent

✅ **Login method included**
- Also tracks HOW you login (see related example: login-method-recall)

---

## Implementation Priority

**Phase 1 - Manual Database**:
- Voice input: "I have Cursor Pro"
- Simple lookup: "What's my Cursor tier?"
- JSON storage

**Phase 2 - 1Password Integration**:
- Import existing subscription info from 1Password
- Sync when 1Password entries updated

**Phase 3 - Auto-detection**:
- Email receipt monitoring
- Service API integration
- Automatic tier updates when changed

---

## Related Examples

- **Login method recall** (HOW do I login to X?)
- **Subscription tracking** (WHEN does X renew?)
- **Password lookup** (WHAT is my password for X?)

**Common Pattern**: Information you need frequently but can never remember, requiring multi-step lookup that wastes time and creates frustration.

---

## Real-World Impact

**Frequency**: 5-10 times per week (different services)
**Time saved**: 3 minutes per lookup × 10/week = 30 min/week = 26 hours/year
**Frustration reduction**: Immense (eliminates "I'm paying you and you make me guess my tier" rage)

**Current workarounds**:
- Keep forgetting and re-looking up (most common)
- Write it down somewhere (becomes stale when tier changes)
- Just guess "Pro" for everything (wrong 40% of the time)

---

**Created**: 2025-12-20
**Status**: Not implemented
**Owner**: rk
**Inspiration**: "I had to burn a minute or two to determine I was Drafts Pro... I can *never* remember that"
