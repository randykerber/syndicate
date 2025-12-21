# Example: Recipe Ingredient Check

**Category**: Cooking | Information capture
**Frequency**: 3-5 times per week
**Pain Level**: 7/10
**Status**: Not implemented

---

## Current State (What Sucks)

### The Scenario
Kathy finds a recipe she wants to make (online, cookbook, remembered from past). Before starting, needs to verify all ingredients are available. Recipe lists 12 ingredients.

### Current Painful Workflow

**Step 1**: Read recipe ingredient list
- Try to remember all 12 items while walking to kitchen

**Step 2**: Physical inventory check
- Check pantry for dry goods (items 1-4)
- Walk to fridge for dairy/produce (items 5-8)
- Forget what's left to check
- Walk back to recipe
- Re-read remaining ingredients
- Walk to freezer (items 9-10)
- Realize you forgot to check for one item in pantry
- Walk back to pantry

**Step 3**: Discover missing items mid-check
- "We're out of cumin"
- Continue checking other ingredients
- Forget what was missing by the time you finish checking

**Step 4**: Try to remember what's missing
- "Was it cumin and... something else? Or just cumin?"
- Walk back to recipe
- Re-read entire list
- Cross-reference with mental inventory

**Step 5**: Decision point
- Make shopping trip for 2 items? (High friction)
- Substitute ingredients? (Changes recipe, might not work)
- Pick different recipe entirely? (Wasted 15 minutes checking)

### Pain Points

- **Walking loops**: Recipe → pantry → fridge → freezer → recipe (multiple times)
- **Memory overload**: Can't hold 12 ingredients + current status in head
- **Interruption cost**: 15 minutes of checking before cooking even starts
- **Missing item discovery**: Found halfway through check, forgot by end
- **Decision paralysis**: Shop, substitute, or abandon recipe?
- **Cooking delay**: Want to start cooking now, not take shopping trip
- **Frustration**: Simple task takes 10-15 minutes of walking around

---

## Ideal Future State

### Conversation (Before Starting to Cook)

**Kathy** (voice): "Hey Claude, I want to make chicken tikka masala. Do we have all the ingredients?"

**Agent**: "Let me check your inventory against the recipe...

You have:
✓ Chicken (chest freezer)
✓ Yogurt (kitchen fridge)
✓ Onions, garlic, ginger (pantry)
✓ Tomato sauce (pantry)
✓ Rice (pantry)

Missing:
✗ Garam masala
✗ Ground cumin
✗ Heavy cream

You have 9 out of 12 ingredients. Want to add the missing items to your shopping list, or should I suggest substitutions?"

**Kathy**: "What substitutions?"

**Agent**: "For garam masala: you could use curry powder (you have that in pantry). For heavy cream: you have milk and butter, can make a substitute. For cumin: you're out of luck, that's essential. Add cumin to shopping list?"

**Kathy**: "Yeah, and just get the cream too"

**Agent**: "Added cumin and heavy cream to shopping list. Use curry powder instead of garam masala?"

**Kathy**: "Yes, that works"

**Agent**: "All set. You have everything to make chicken tikka masala with curry powder substitution."

---

### Alternative: Complete Match

**Kathy**: "Do we have ingredients for carbonara?"

**Agent**: "Checking... ✓ Yes, you have everything: pasta, eggs, bacon, parmesan, black pepper. All in stock."

**Kathy**: "Great, starting it now"

---

### Alternative: Suggest Alternative Recipe

**Kathy**: "Do we have ingredients for beef stroganoff?"

**Agent**: "Missing beef, sour cream, and mushrooms - 3 key ingredients. You have chicken, cream, and pasta though. Want to make chicken alfredo instead? You have all those ingredients."

**Kathy**: "Perfect, let's do that"

---

## What Agent Does (Behind the Scenes)

### On "Do we have ingredients for [recipe]?"

1. **Retrieve recipe**:
   - From LLM knowledge (common recipes)
   - From user's saved recipes (future)
   - From URL if provided

2. **Extract ingredient list**:
   - Chicken tikka masala → [chicken, yogurt, onions, garlic, ginger, garam masala, cumin, tomato sauce, cream, rice, ...]

3. **Query inventory** for each ingredient:
   - `search_ingredient("chicken")` → found in chest freezer
   - `search_ingredient("garam masala")` → not found
   - Continue for all ingredients

4. **Categorize results**:
   - **Available** (✓): List with locations
   - **Missing** (✗): List what needs to be acquired
   - **Substitutable** (⚠️): Items that could be substituted

5. **Calculate completeness**:
   - "9 out of 12 ingredients" (75%)

6. **Present results** with options:
   - Add missing to shopping list
   - Suggest substitutions
   - Recommend alternative recipes

### On Substitution Request

1. **Check substitution database** (LLM knowledge + rules):
   - Garam masala → curry powder (acceptable)
   - Heavy cream → milk + butter (acceptable)
   - Cumin → no good substitute (essential spice)

2. **Cross-reference inventory**:
   - Do we have curry powder? → Yes (pantry)
   - Do we have milk + butter? → Yes (fridge)

3. **Present options**

### On Shopping List Addition

1. **Add items** to shopping list knowledge base
2. **Optionally**: Suggest stores, group by aisle, estimate cost

---

## Technical Requirements

### Information Needed

**Recipe Database**:
- Recipe name → ingredient list
- Sources: LLM knowledge, saved recipes, URL parsing

**Ingredient Inventory**:
- Current stock (from food inventory system)
- Locations (which fridge/freezer/pantry)

**Substitution Rules**:
- Ingredient → acceptable substitutes
- Quality rating (perfect, acceptable, poor)

### Context Triggers

Load food inventory + recipe database when:
- Asking about specific recipes ("do we have ingredients for X?")
- Cooking-related conversation
- "What can I make?" questions

### Tools/Integrations

**MCP Server**: `inventory_server.py` (extends food inventory example)

**New Tools**:
- `check_recipe_ingredients(recipe_name)` → ✓/✗/⚠️ status report
- `suggest_substitutes(ingredient)` → alternatives with ratings
- `find_similar_recipes(missing_ingredients, available_ingredients)` → alternatives

**External Integrations** (future):
- Recipe APIs (Spoonacular, Edamam)
- URL parsing (extract ingredients from recipe websites)
- Nutrition info (dietary restrictions, allergies)

**Storage**:
- Leverage food inventory system
- Add recipe cache (recently checked recipes)
- Substitution rules (JSON or LLM knowledge)

---

## Success Criteria

✅ **Zero walking around**
- "Do we have ingredients?" → instant answer, no physical checking

✅ **Complete ingredient status**
- Shows ✓ available, ✗ missing, ⚠️ substitutable

✅ **Location awareness**
- "Chicken in chest freezer" (know where to get it when cooking)

✅ **Substitution suggestions**
- Don't just say "missing X", suggest alternatives if available

✅ **Quick decision making**
- Missing 3 items? Add to shopping list or suggest different recipe

✅ **Cooking time saved**
- No 15-minute ingredient hunt, start cooking immediately

---

## Implementation Priority

**Phase 1 - Basic Check**:
- Manual recipe input: "Ingredients: chicken, rice, tomatoes"
- Check inventory for each
- Report ✓/✗ status

**Phase 2 - Recipe Database**:
- LLM knowledge for common recipes
- URL parsing for online recipes
- User's saved recipes

**Phase 3 - Smart Suggestions**:
- Substitution recommendations
- Alternative recipe suggestions
- Shopping list integration

---

## Related Examples

- **Food inventory for cooking** (maintains the ingredient database)
- **Shopping list generation** (adds missing ingredients)
- **Meal planning** (uses ingredient check to plan week's meals)

**Common Pattern**: Pre-flight check before starting task, agent verifies all requirements met, suggests alternatives if gaps exist.

---

**Created**: 2025-12-20
**Status**: Not implemented
**Owner**: rk
