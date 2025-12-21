# SSS Problem Examples

**Purpose**: Concrete examples of daily annoyances that SSS (or other tools) should solve.

Each example documents:
- **Current painful workflow** (what sucks now)
- **Ideal future state** (how it should work)
- **Technical requirements** (what's needed to build it)
- **Success criteria** (how to know it works)
- **Implementation priority** (MVP → full feature)

---

## Index by Pain Level (10 = most painful)

| Example | Pain | Frequency | Annual Hours Saved | Status |
|---------|------|-----------|-------------------|--------|
| [Login Method Recall](login-method-recall.md) | 10/10 | Daily (3-5x) | 27-45 hours | Not implemented |
| [Subscription Level Recall](subscription-level-recall.md) | 9/10 | Weekly (5-10x) | 26 hours | Not implemented |
| [Meeting Action Items](meeting-action-items.md) | 8/10 | Daily (3-5x) | 30-60 hours | Not implemented |
| [Food Inventory Cooking](food-inventory-cooking.md) | 8/10 | Daily (2-3x) | 40+ hours | Not implemented |
| [Vehicle Maintenance](vehicle-maintenance-tracking.md) | 7/10 | Monthly | 10-15 hours | Not implemented |
| [Recipe Ingredient Check](recipe-ingredient-check.md) | 7/10 | Weekly (3-5x) | 15-20 hours | Not implemented |
| [Subscription Tracking](subscription-tracking.md) | 6/10 | Monthly | 5-10 hours | Not implemented |

**Total potential time savings**: 150+ hours/year if all implemented

---

## Index by Category

### Authentication & Account Management
- [Login Method Recall](login-method-recall.md) - Which method to login to each service
- [Subscription Level Recall](subscription-level-recall.md) - What tier/plan for each service

### Information Capture & Retrieval
- [Meeting Action Items](meeting-action-items.md) - Track commitments from meetings
- [Vehicle Maintenance](vehicle-maintenance-tracking.md) - Oil changes, service intervals

### Cooking & Household
- [Food Inventory Cooking](food-inventory-cooking.md) - What's in fridge/freezer/pantry
- [Recipe Ingredient Check](recipe-ingredient-check.md) - Do we have all ingredients?

### Finance & Subscriptions
- [Subscription Tracking](subscription-tracking.md) - Track renewals, find unused services

---

## Index by Implementation Priority

### High Priority (Solve First)
1. **Login Method Recall** - Daily pain, high error cost
2. **Subscription Level Recall** - Frequent frustration
3. **Food Inventory Cooking** - Daily use, Kathy's primary use case

### Medium Priority
4. **Recipe Ingredient Check** - Extends food inventory
5. **Meeting Action Items** - Professional impact
6. **Vehicle Maintenance** - Lower frequency but high value

### Lower Priority
7. **Subscription Tracking** - Useful but less urgent

---

## Index by Solution Type

### SSS Architecture Justified
- Login Method Recall (needs context-aware loading)
- Subscription Level Recall (needs voice query + memory)
- Food Inventory Cooking (needs context triggering)
- Meeting Action Items (needs multi-turn capture)
- Vehicle Maintenance (needs intelligent interval calculation)

### Could Use Simpler Tool
- Recipe Ingredient Check (extends food inventory, share architecture)
- Subscription Tracking (could use spreadsheet, but voice interface adds value)

---

## Common Patterns Across Examples

### Pattern 1: Information You Can't Remember
- Login method for 100+ services
- Subscription tier names across dozen+ services
- When last oil change was done

**Solution**: Voice-accessible memory database

### Pattern 2: Multi-Step Lookup Hell
- Current: 1Password → website → login → account → check subscription
- Future: "What's my Drafts tier?" → instant answer

**Solution**: Flatten multi-step lookups to single voice query

### Pattern 3: Arbitrary Reminders That Nag
- Current: "Check oil in 3 months" (guessed date) → nagging reminder
- Future: Agent calculates actual interval (time + mileage) → proactive check-in

**Solution**: Intelligent calculation instead of arbitrary dates

### Pattern 4: Information Scattered Across Physical Locations
- Current: Walk to freezer → fridge → pantry to check ingredients
- Future: "What can I make for dinner?" → instant inventory check

**Solution**: Central index of distributed information

### Pattern 5: High-Stakes Guessing
- Current: Guess login method → risk duplicate account → customer service hell
- Future: "How do I login?" → confident answer

**Solution**: Eliminate guessing where error cost is high

---

## How to Add New Examples

1. **Capture quick note** in Drafts:
   ```
   SSS: [Short name]
   Pain: [Current sucks]
   Ideal: [Future should work]
   Frequency: [How often]
   ```

2. **Copy template**: Use `_TEMPLATE.md` in this directory

3. **Fill in sections**:
   - Current painful workflow (be specific, include steps)
   - Ideal future conversation (show voice interaction)
   - What agent does behind scenes
   - Technical requirements
   - Success criteria

4. **Add to this index**: Update tables above

5. **Tag with pain level**: 1-10 (how frustrating is current state?)

6. **Estimate time savings**: Frequency × time per use = annual hours

---

## Related Documents

- **[Philosophy](../philosophy.md)**: "Solved" not "solved by SSS" - when to use SSS vs simpler tools
- **[Template](_TEMPLATE.md)**: Copy this to create new examples
- **[Context Engineering Summaries](../ace/)**: Technical implementation patterns

---

**Last Updated**: 2025-12-20
**Examples Count**: 7
**Total Potential Annual Savings**: 150+ hours
