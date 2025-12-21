# Example: Subscription Tracking

**Category**: Finance | Information capture
**Frequency**: Monthly (renewals), Weekly (wondering "am I still paying for X?")
**Pain Level**: 6/10
**Status**: Not implemented

---

## Current State (What Sucks)

### The Scenario
You have 15+ subscriptions across streaming, software, services. Some annual, some monthly. Renewals happen automatically, charges appear on credit card, and you're never sure:
- What you're paying for
- When renewals happen
- What you're no longer using
- How much you're spending total

### Current Painful Workflow

**Discovery (when charge appears)**:

**Step 1**: See credit card charge
- "$19.99 - STREAMING-SERVICE-XYZ"
- "What is that? Am I still using that?"

**Step 2**: Try to remember
- "Did I cancel that?"
- "Is Kathy using it?"
- "What email is it under?"

**Step 3**: Log into service (if you can remember password)
- Find login email
- Reset password (because you forgot)
- Check subscription status
- "Oh right, we do use this"

**Step 4**: Forget again next month
- Repeat entire process

**Tracking Attempt**:

**Step 1**: Try to create a list
- Open Notes/Bear/Spreadsheet
- "I'll track all my subscriptions!"

**Step 2**: List what you remember
- Miss half of them
- Don't know renewal dates
- Don't update when things change

**Step 3**: List becomes stale
- Forgot to update when you canceled Hulu
- Still shows old price for Netflix (increased 6 months ago)
- List is now untrustworthy

### Pain Points

- **Discovery via surprise charges**: Only know about renewals when bill arrives
- **Memory failure**: Can't remember what subscriptions exist
- **Stale tracking**: Manual lists become outdated immediately
- **Usage unknown**: Paying for services nobody uses
- **No spending visibility**: How much total per month/year?
- **Difficult cancellation**: Don't know renewal dates to cancel before next charge
- **Shared confusion**: "Are you using Disney+?" "I thought you were?"

---

## Ideal Future State

### Conversation (Recording New Subscription)

**Human** (via voice): "Hey Claude, I just signed up for Cursor Pro, $20 a month"

**Agent**: "Got it. Cursor Pro subscription - $20/month starting today. Should I remind you before the next renewal?"

**Human**: "Yeah, maybe a few days before"

**Agent**: "I'll check in 3 days before each renewal to see if you're still using it."

---

### Conversation (Renewal Check-In)

**Agent** (via push notification - 3 days before renewal): "Cursor Pro renews in 3 days ($20). Still using it?"

**Human**: "Yes, definitely"

**Agent**: "Great, I'll check in again next month."

---

**Alternative - Unused Service**:

**Agent** (push notification): "Adobe Creative Cloud renews in 3 days ($54.99). You haven't mentioned using it in 6 months. Still need it?"

**Human**: "No, cancel it"

**Agent**: "I can't cancel directly, but here's the cancellation link: [URL]. Want me to remind you to do it today?"

---

### Conversation (Spending Overview)

**Human**: "How much am I spending on subscriptions?"

**Agent**: "Current subscriptions: 12 active
- Monthly: $147/month (Netflix, Spotify, Cursor Pro, Claude Pro, ...)
- Annual: $358/year (IntelliJ, Obsidian Sync, ...)
- Total: ~$2,122/year

Top 3: IntelliJ ($119/yr), Obsidian Sync ($96/yr), Claude Pro ($20/mo)"

---

### Conversation (Usage Check)

**Human**: "What subscriptions am I not using?"

**Agent**: "Based on our conversations:
- Adobe Creative Cloud ($55/mo) - last mentioned 8 months ago
- Hulu ($15/mo) - you said 'never watch it' 3 months ago but didn't cancel
- LinkedIn Premium ($30/mo) - signed up 1 year ago, never mentioned since

Combined waste: ~$100/month. Want to review?"

---

## What Agent Does (Behind the Scenes)

### On "Signed up for Cursor Pro, $20/month"

1. **Parse subscription details**:
   - Service: Cursor Pro
   - Cost: $20
   - Frequency: monthly
   - Start date: today (2025-12-20)

2. **Calculate next renewal**:
   - Next renewal: 2026-01-20

3. **Store structured data**:
```json
{
  "service": "Cursor Pro",
  "cost": 20.00,
  "currency": "USD",
  "frequency": "monthly",
  "start_date": "2025-12-20",
  "next_renewal": "2026-01-20",
  "status": "active",
  "reminder_days": 3,
  "usage_mentioned": ["2025-12-20"]
}
```

4. **Set reminder**:
   - Check-in: 2026-01-17 (3 days before renewal)

### On Renewal Check-In

1. **Send notification** 3 days before renewal
2. **If user confirms still using**:
   - Update `usage_mentioned` array
   - Schedule next check-in
3. **If user wants to cancel**:
   - Provide cancellation link/instructions
   - Mark status as "pending_cancellation"
   - Remind day-of if not completed

### On "How much am I spending?"

1. **Query all active subscriptions**
2. **Calculate totals**:
   - Monthly: sum of monthly subscriptions
   - Annual: sum of annual, convert to monthly equivalent
   - Total: annual cost
3. **Rank by cost**
4. **Format response**

### On "What subscriptions am I not using?"

1. **Check `usage_mentioned` array** for each subscription
2. **Identify subscriptions** with no mentions in past 3-6 months
3. **Check conversation history** for negative mentions ("never use", "don't watch")
4. **Calculate waste**: sum of likely-unused subscription costs
5. **Suggest review**

---

## Technical Requirements

### Information Needed

**Per Subscription**:
- Service name
- Cost (amount + currency)
- Frequency (monthly, annual, one-time)
- Start date
- Next renewal date
- Payment method (optional)
- Login email (optional)
- Cancellation link (optional)
- Usage mentions (timestamps of when user mentioned using it)
- Status (active, cancelled, pending_cancellation)

### Context Triggers

Load subscription data when conversation involves:
- Spending, budget, money, subscriptions
- Specific service names (Netflix, Spotify, etc.)
- "What am I paying for?"

Don't load when:
- Cooking, car maintenance, general topics

### Tools/Integrations

**MCP Server**: `subscriptions_server.py` (new)

**Tools**:
- `add_subscription(service, cost, frequency, start_date)` - Record new subscription
- `list_subscriptions(status)` - Show all active/cancelled/all
- `calculate_spending()` - Total monthly/annual costs
- `find_unused(months)` - Identify subscriptions not mentioned in X months
- `update_subscription(service, field, value)` - Modify details
- `cancel_subscription(service)` - Mark as cancelled

**External Integrations** (future):
- Bank/credit card feed (auto-detect new subscriptions)
- Service APIs (fetch current price, renewal date)
- Calendar integration (add renewal dates)

**Storage**:
- Simple: JSON file `~/data/subscriptions.json`
- Better: SQLite with time-series tracking

---

## Success Criteria

✅ **Proactive renewal reminders**
- Check-in before each renewal, not reactive to charges

✅ **Usage tracking**
- Agent knows which services are actually used based on conversations

✅ **Spending visibility**
- "How much am I spending?" → instant answer with breakdown

✅ **Waste identification**
- "What am I not using?" → suggests services to cancel

✅ **Easy recording**
- Voice input: "Signed up for X, $Y/month" → tracked

✅ **No stale data**
- Renewal dates auto-calculated, prices updated when mentioned

---

## Implementation Priority

**Phase 1 - Manual Tracking**:
- Add/list subscriptions via voice
- Calculate total spending
- Manual renewal reminders

**Phase 2 - Usage Analysis**:
- Track usage mentions in conversations
- Identify unused subscriptions
- Suggest cancellations

**Phase 3 - Automated Detection**:
- Bank feed integration (detect new subscriptions)
- Service API integration (auto-update prices, renewal dates)
- One-click cancellation where possible

---

## Related Examples

- **Bill reminders** (utilities, insurance - similar renewal tracking)
- **Contract renewals** (leases, warranties - annual cycles)
- **Membership tracking** (gym, clubs - monthly/annual fees)

**Common Pattern**: Recurring charges that fade from awareness, agent provides visibility and proactive check-ins before renewals.

---

**Created**: 2025-12-20
**Status**: Not implemented
**Owner**: rk
