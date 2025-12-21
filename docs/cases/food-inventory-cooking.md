# Example: Food Inventory for Cooking

**Category**: Information capture | Cooking
**Frequency**: 2-3 times daily
**Pain Level**: 8/10
**Status**: Not implemented

---

## Current State (What Sucks)

### The Scenario
Kathy wants to make dinner but doesn't know what ingredients are available across kitchen fridge, second fridge, chest freezer, pantry, and cabinets.

### Current Painful Workflow

**Step 1**: Think of meal idea
- "I could make chicken parmesan..."

**Step 2**: Try to remember what's in stock
- "Do we have chicken? I think so... maybe in the freezer?"
- "Breadcrumbs? Not sure"
- "Cheese? Probably?"

**Step 3**: Physical inventory check
- Walk to chest freezer (garage/basement)
- Dig through frozen items
- Walk back to kitchen
- Check fridge
- Walk to pantry
- Repeat because you forgot what you found earlier

**Step 4**: Discover missing ingredients
- "We're out of panko breadcrumbs"
- Now have to change meal plan OR make shopping trip

**Step 5**: Give up and order takeout
- Too much effort
- Information scattered across locations
- Mental overhead too high

### Pain Points

- **Physical search required**: Walking to multiple locations to check inventory
- **Memory failure**: Forget what you found by the time you check third location
- **No central index**: Information exists only by physically looking
- **Context switching**: Recipe in head → freezer → fridge → pantry → mental reassembly
- **Meal planning impossible**: Can't plan without knowing what's available
- **Food waste**: Items forgotten in second fridge/freezer until expired

---

## Ideal Future State

### Conversation

**Kathy** (voice): "Hey Claude, what can I make for dinner with what we have?"

**Agent**: "Checking your inventory... You have chicken breast in the chest freezer, eggs and cheddar cheese in the kitchen fridge, and pasta in the pantry. I can suggest: chicken alfredo, chicken stir-fry with rice, or chicken and vegetable bake. Which sounds good?"

**Kathy**: "How about chicken parmesan?"

**Agent**: "For chicken parmesan you'd need: chicken (✓ chest freezer B3), marinara sauce (✗ none in stock), mozzarella (you have cheddar, not mozzarella), panko breadcrumbs (✗ none in stock). You're missing 2-3 key ingredients. Want me to add them to your shopping list?"

**Kathy**: "Yes"

**Agent**: "Added marinara sauce, mozzarella, and panko breadcrumbs to your shopping list. Want a different recipe suggestion with current ingredients?"

---

### Alternative: Post-Shopping Update

**Kathy** (returning from store): "Hey Claude, I bought groceries"

**Agent**: "Want to update your inventory? You can show me the receipt or tell me what you got."

**Kathy**: "I got marinara, mozzarella, panko breadcrumbs, and ground beef"

**Agent**: "Updated inventory. Ground beef goes in which location?"

**Kathy**: "Chest freezer"

**Agent**: "Got it. Inventory updated. You now have everything for chicken parmesan, plus ground beef added to chest freezer."

---

## What Agent Does (Behind the Scenes)

### On "What can I make for dinner?"

1. **Load food inventory** (context-triggered by "dinner")
2. **Scan available ingredients** across all locations
3. **Match against recipe database** (or use LLM knowledge)
4. **Suggest feasible meals** based on what's in stock

### On "How about chicken parmesan?"

1. **Retrieve recipe** (chicken parmesan ingredients)
2. **Check inventory** for each ingredient
3. **Report matches and gaps** (✓ have, ✗ missing)
4. **Offer alternatives** (substitute cheddar? different recipe?)

### On "Add to shopping list"

1. **Extract missing items**: marinara, mozzarella, panko
2. **Add to shopping list** (separate knowledge base or tool)
3. **Optionally**: Suggest stores, prices, remind before next shopping trip

### On "I bought groceries"

1. **Parse natural language** or receipt image
2. **Extract items**: marinara, mozzarella, panko, ground beef
3. **Update inventory** (increment quantities or add new items)
4. **Disambiguate location** if needed (where does ground beef go?)

---

## Technical Requirements

### Information Needed

**Inventory Structure**:
```json
{
  "kitchen_fridge": [
    {"item": "eggs", "quantity": "8", "unit": "count", "expires": "2025-12-28"},
    {"item": "cheddar_cheese", "quantity": "1/2 block", "unit": "approx"}
  ],
  "chest_freezer": [
    {"item": "chicken_breast", "quantity": "2 lbs", "location": "B3"},
    {"item": "ground_beef", "quantity": "1.5 lbs", "location": "A2"}
  ],
  "pantry": [
    {"item": "pasta", "quantity": "2 boxes"},
    {"item": "rice", "quantity": "5 lbs"}
  ]
}
```

**Recipe Database** (optional):
- Ingredient lists for common meals
- Or use LLM knowledge + verification

### Context Triggers

Load food inventory when conversation involves:
- Cooking keywords (dinner, breakfast, lunch, recipe, meal)
- Ingredients (chicken, pasta, vegetables)
- Shopping (grocery, store, buy food)

Don't load when:
- Discussing car maintenance, travel, finance

### Tools/Integrations

**MCP Server**: `inventory_server.py` (new)

**Tools**:
- `search_ingredient(ingredient)` → locations and quantities
- `list_by_location(location)` → all items in that location
- `check_recipe_ingredients(recipe_name)` → ✓/✗ availability
- `update_inventory(item, quantity, location, action)` → add/remove/update
- `add_to_shopping_list(items)` → integrate with shopping list

**External Integrations** (future):
- Receipt scanning (OCR → extract items)
- Barcode scanning (add items via phone camera)
- Store APIs (prices, availability, online ordering)

**Storage**:
- Simple: JSON file `~/data/food-inventory.json`
- Better: SQLite with expiration tracking
- Best: Postgres with automated expiration warnings

---

## Success Criteria

✅ **Zero physical searching**
- "What can I make?" answered without walking to freezer/fridge/pantry

✅ **Ingredient gap detection**
- "Want chicken parmesan" → immediately know what's missing

✅ **Voice-based updates**
- "I bought groceries" → inventory updated through conversation

✅ **Multi-location awareness**
- Agent knows chicken is in chest freezer B3, not kitchen fridge

✅ **Context-aware loading**
- Inventory loaded during cooking discussions, not during car maintenance

✅ **Reduced food waste**
- Agent can remind: "Eggs expire in 2 days, want to use them?"

---

## Implementation Priority

**Phase 1 - Basic Inventory**:
- Manual entry: "We have chicken in the freezer"
- Simple search: "Do we have X?"
- JSON storage by location

**Phase 2 - Recipe Matching**:
- Check recipe ingredients against inventory
- Suggest meals based on available ingredients
- Shopping list integration

**Phase 3 - Automated Updates**:
- Receipt scanning after shopping
- Barcode scanning for new items
- Expiration warnings

---

## Related Examples

- **Recipe ingredient check** (before starting to cook, verify all ingredients)
- **Shopping list generation** (track what's needed across weeks)
- **Meal planning** (plan week's meals based on inventory + preferences)

**Common Pattern**: Information scattered across physical locations, mental burden to track, agent becomes central index for household state.

---

**Created**: 2025-12-20
**Status**: Not implemented
**Owner**: rk
