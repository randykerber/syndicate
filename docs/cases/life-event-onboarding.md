# Case: Life Event Onboarding Tracking - "Vital Part Done, Cleanup Forgotten"

**Category**: Task management | Information capture | Checklist tracking
**Frequency**: Monthly (new devices, services, life events)
**Pain Level**: 8/10 (high stakes when forgotten)
**Status**: Not implemented

---

## The Core Problem

**"New life event creates cascading tasks. Vital parts get done (urgently), detail cleanup gets forgotten (not urgent)."**

**Pattern**:
1. **Urgent thing** happens (Medicare deadline, new device purchase)
2. **Critical tasks** completed (sign up, pay first bill, basic setup)
3. **Detail tasks** deferred (record info, file manual, understand coverage)
4. **Memory decays** (weeks later, can't remember what's done/pending)
5. **Triggered at wrong time** ("Do I have vision coverage?" at Costco appointment)

**Result**: Important information lost, decisions delayed, stress when needed urgently

---

## Real Example: Medicare Signup

### The Situation

**Life event**: Turned 65, Medicare enrollment required

**Timeline**:

**October**: Started research
- Medicare A, B, C, D - what are these?
- Supplement plans (Medigap)
- Dental and vision (optional add-ons)
- **Information overload**

**November**: Urgent deadline approaching
- **Priority 1**: Get basic coverage (A+B)
- **Priority 2**: Supplement plan (picked one, enrolled)
- **Priority 3**: Pay first premiums (done)
- **Status**: COVERED (vital goal achieved!)

**December**: Cleanup tasks deferred
- Did I get dental coverage? (Don't remember)
- Did I get vision coverage? (**Don't know**)
- What are the account numbers?
- How do I access online accounts?
- What's the payment schedule?
- Where are the confirmation emails/documents?

**December 20 (today)**: At Costco optical
- Making eye exam appointment
- Clerk: "Do you have vision coverage?"
- You: "Uh... I don't know. Maybe? I enrolled in some stuff in November."
- **Can't answer simple question about own coverage**

---

## Current Painful Workflow

### During Event (Vital Tasks)

**Step 1**: Emergency mode (deadline-driven)
- Research Medicare options (10+ hours)
- Make decisions under time pressure
- Enroll in basic coverage (A+B)
- Enroll in supplement plan
- Pay first premiums

**Step 2**: Exhale
- Coverage secured (vital goal)
- "I'll deal with details later"
- Back to other urgent tasks

### After Event (Cleanup Never Happens)

**Step 3**: Deferred tasks forgotten
- Record account numbers → "later"
- Save confirmation emails → "later"
- File documents → "later"
- Understand coverage details → "later"

**Step 4**: Memory decays
- Weeks pass
- "Did I get vision? Dental? I can't remember"
- "Where are those documents?"
- "What email did I use for enrollment?"

**Step 5**: Information needed at wrong time
- At Costco: "Do you have vision coverage?"
- At dentist: "What's your dental plan?"
- At pharmacy: "What's your Part D plan number?"
- **Can't answer, have to research own coverage**

---

## Other Examples of This Pattern

### New Device Purchase

**Vital part done**:
- Device purchased
- Basic setup completed
- Device working

**Cleanup forgotten**:
- Save user manual (PDF lost in Downloads)
- Record model number (can't remember exact model)
- Save purchase date (needed for warranty claim)
- Record warranty period (when does it expire?)
- Schedule maintenance (HVAC filter change every 3 months - when?)

**Triggered at wrong time**:
- Device breaks, need warranty claim: "When did I buy this?"
- Maintenance due: "What filter size do I need?"

### New Service Signup

**Vital part done**:
- Service activated (Netflix, Cursor Pro, etc.)
- Payment method added
- First bill paid

**Cleanup forgotten**:
- Record subscription tier (Pro? Plus? Premium?)
- Save account credentials (which email? which login method?)
- Note renewal date (annual? monthly? when?)
- Understand features (what's included in my tier?)

**Triggered at wrong time**:
- Login page: "How do I login to this?" (see: login-method-recall case)
- Renewal: "Wait, this renews? When?" (see: subscription-tracking case)

---

## Ideal Future State

### Scenario: Medicare Question at Costco

**Costco clerk**: "Do you have vision coverage?"

**Human** (via AirPods): "Hey Siri, do I have vision coverage?"

**Agent**: "Yes, you have VSP vision coverage through your Medicare supplement plan. Member ID: VSP-12345678. Your plan covers:
- Annual eye exam (covered 100%)
- Frames ($150 allowance)
- Lenses (covered)

Want me to send this info to the Costco optical desk?"

**Human**: "Yes"

**Agent**: *[Sends coverage details to clerk]*

---

### Scenario: Agent Tracks Onboarding

**November (during enrollment)**:

**Agent** (proactively): "I see you're enrolling in Medicare. I'll track what you've completed. Current status:

✅ Medicare Part A & B enrolled
✅ Supplement plan enrolled (Plan G)
✅ First premiums paid
⏸️  Vision coverage - did you add this?
⏸️  Dental coverage - did you add this?
❓ Online account access - need to set this up?

Want me to help finish the pending items?"

**Human**: "I got vision through VSP. Didn't get dental. Don't remember online account setup."

**Agent**: "Recorded:
- Vision: VSP (I'll find your member ID and save it)
- Dental: None
- Online access: I'll guide you through setup when you're ready

Anything else from your enrollment?"

---

### Scenario: Proactive Completion Reminder

**December 10** (agent notices incomplete items):

**Agent** (push notification): "Medicare enrollment is 80% complete. Remaining items:
- Online account access (not set up)
- Save enrollment confirmation emails
- Record payment schedule

These are due by Dec 31 for current year enrollment. Want to finish them now or schedule time?"

**Human**: "Schedule for Saturday morning"

**Agent**: "Added to Saturday 9 AM: Complete Medicare onboarding (30 min estimate)"

---

## What Agent Does (Behind the Scenes)

### During Life Event

**1. Detect event**:
- User mentions "Medicare enrollment"
- Browsing Medicare.gov
- Email confirmations arriving
- Calendar events about enrollment

**2. Create onboarding checklist**:
```
Medicare Enrollment Checklist:
☐ Research options
☐ Enroll in Part A & B
☐ Choose supplement plan
☐ Enroll in supplement
☐ Pay first premium
☐ Add vision coverage (optional)
☐ Add dental coverage (optional)
☐ Set up online account access
☐ Record all account numbers
☐ Save confirmation emails
☐ File documents
☐ Understand coverage details
☐ Add to 1Password
☐ Note renewal dates
```

**3. Track completion**:
- User says "I enrolled in Part A & B" → check item
- Email arrives from Medicare → check related item
- User pays bill → check premium payment

**4. Remember details**:
- Account numbers from emails
- Coverage details from confirmation PDFs
- Payment schedules from bills
- Login methods from account setup

### After Event

**5. Identify incomplete items**:
- Checklist shows 7/13 completed
- Critical items done (coverage secured)
- Cleanup items pending (details, documentation)

**6. Proactive reminders**:
- "30 days since enrollment, 6 items still pending"
- "Enrollment deadline Dec 31 - finish remaining items?"

**7. Answer questions anytime**:
- "Do I have vision coverage?" → YES (VSP, member ID xxx)
- "When did I enroll?" → November 15, 2025
- "What's my account number?" → Medicare: xxx, Supplement: yyy

---

## Technical Requirements

### Information Needed

**Per life event**:
- Event type (Medicare, new device, new service, etc.)
- Start date (when did this begin?)
- Checklist template (standard items for this type of event)
- Completion status (what's done, what's pending)
- Details captured (account #s, model #s, dates, etc.)

**Example: Medicare Enrollment**
```json
{
  "event_type": "medicare_enrollment",
  "start_date": "2025-10-01",
  "status": "incomplete",
  "critical_complete": true,
  "details_complete": false,
  "checklist": {
    "enroll_part_a_b": {"status": "complete", "date": "2025-11-15"},
    "supplement_plan": {"status": "complete", "plan": "Plan G", "provider": "UnitedHealthcare"},
    "vision_coverage": {"status": "complete", "provider": "VSP", "member_id": "VSP-12345"},
    "dental_coverage": {"status": "not_selected"},
    "online_access": {"status": "incomplete"},
    "save_documents": {"status": "incomplete"}
  },
  "deadline": "2025-12-31"
}
```

### Context Triggers

Create onboarding checklist when:
- User mentions life event keywords (Medicare, new car, new phone, moving, etc.)
- Confirmation emails detected (enrollment, purchase, signup)
- Calendar events suggest onboarding (delivery date, activation date)

### Tools/Integrations

**MCP Server**: `onboarding_server.py` (new) or extend `action_items_server.py`

**Tools**:
- `create_onboarding_checklist(event_type)` → standard template
- `update_checklist_item(event_id, item, status, details)` → mark complete
- `get_onboarding_status(event_type)` → what's done/pending
- `answer_coverage_question(question)` → query stored details

**External Integrations**:
- Email scanning (detect confirmations, extract details)
- Calendar integration (deadlines, appointments)
- Document storage (save PDFs, emails)
- 1Password (save account credentials)

**Storage**:
- Onboarding events database (event type, status, checklist)
- Details database (account numbers, model numbers, dates)
- Document repository (confirmations, manuals, receipts)

---

## Success Criteria

✅ **Automatic checklist creation**
- Agent detects life event → creates checklist

✅ **Passive completion tracking**
- Email arrives → item checked automatically
- User mentions completion → item checked

✅ **Detail capture**
- Account numbers extracted from emails
- Model numbers saved from receipts
- Dates recorded from confirmations

✅ **Answer questions anytime**
- "Do I have vision?" → instant answer
- "What's my account number?" → retrieved immediately

✅ **Proactive completion nudges**
- "6 items pending, deadline approaching"
- Not nagging, just helpful reminders

✅ **Zero manual tracking**
- User doesn't maintain checklist
- Agent does it passively

---

## This Is an Exemplar

**Not about**: "Track Medicare enrollment specifically"

**About**: The PRINCIPLE that:
- Life events create cascading task lists
- Urgent tasks get done, detail cleanup gets forgotten
- Memory decays, information is lost
- Agent should track completion and remember details

**Other examples of this pattern**:
- **New home purchase**: Vital (close deal, move in), cleanup (utilities, address changes, warranties)
- **New job**: Vital (sign offer, start work), cleanup (benefits enrollment, 401k setup, direct deposit)
- **Car purchase**: Vital (buy car, register), cleanup (manual, maintenance schedule, warranty info)
- **Baby birth**: Vital (hospital, basic care), cleanup (insurance, documents, pediatrician)

**Common thread**: High-stakes life event → urgent completion → detail neglect → information loss

---

## Implementation Priority

**Phase 1 - Manual Checklist**:
- User tells agent about life event
- Agent creates checklist template
- User manually updates completion
- Agent stores details as told

**Phase 2 - Passive Tracking**:
- Agent detects event from emails/calendar
- Auto-creates checklist
- Marks items complete based on email confirmations
- Extracts details automatically (account #s, etc.)

**Phase 3 - Proactive Guidance**:
- Agent suggests next steps
- Reminds of pending items approaching deadline
- Answers questions from stored details

---

## Related Cases

- **Activity reconstruction** - "What did I complete?" (similar to onboarding status)
- **Cross-silo search** - "Where are my Medicare documents?" (onboarding should capture this)
- **Information loss prevention** - Onboarding tracking prevents loss

**Common Pattern**: Important information captured during urgent phase, lost during cleanup neglect, needed later at wrong time.

---

**Created**: 2025-12-20
**Status**: Not implemented
**Owner**: rk
**Real story**: At Costco optical, couldn't answer "Do I have vision coverage?" about own Medicare plan
