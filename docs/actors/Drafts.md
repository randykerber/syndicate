# Drafts - Text Capture & Processing Hub

**Official Docs**: https://docs.getdrafts.com/
**Scripting Reference**: https://scripting.getdrafts.com/

## Overview
Drafts is a quick-capture notes app for macOS, iOS, iPadOS, and Apple Watch. It serves as the primary text capture and initial processing point in the SSS ecosystem, with 1,200+ existing notes requiring intelligent triage and organization.

## Current Status
- **Content Volume**: 1,200+ notes accumulated
- **External Access**: ⚠️ **AppleScript CRU (no Delete) + JavaScript Delete (internal only)**
- **Raycast Integration**: ✅ Full integration via FlohGro extension
- **Primary Challenge**: Backlog triage and intelligent routing
- **Processing Goal**: Transform from "text dumping ground" to "intelligent capture system"
- **DELETE Capability**: Requires hybrid approach (AppleScript triggers Drafts Action with JavaScript)

## Raycast Integration Details

### Available Operations (FlohGro Extension)
```typescript
// Text Capture
- Create Draft in Background
- Create and Open Draft
- Create Blank Draft
- Create Draft from Clipboard
- Dictate Draft (voice input via SuperWhisper)

// Content Management  
- Find Draft (search existing)
- Append/Prepend to Draft
- Run Draft Action (execute automation)

// Workflow Integration
- Find Workspace, Find Action
- Create Drafts Quicklink
- Create Open Draft Quicklink
```

### Voice Integration Workflow
```
1. SuperWhisper activation → Voice input
2. Raycast "Dictate Draft" command
3. Automatic transcription and draft creation
4. Optional: Immediate routing via Draft Actions
```

---

## External Access Methods (CRUD Capabilities)

### 1. AppleScript (macOS) - ⚠️ CRU Only (No Direct Delete)

**Status**: Create, Read, Update supported. **DELETE requires Drafts Action + JavaScript**.

**Documentation**: https://docs.getdrafts.com/docs/automation/applescript

**CRITICAL LIMITATION**: AppleScript CANNOT delete drafts directly. Must use JavaScript API via Drafts Actions.

#### Create Draft
```applescript
tell application "Drafts"
    make new draft with properties {content:"My new draft", name:"Title", tags:{"tag1", "tag2"}}
end tell
```

#### Read Drafts
```applescript
-- Get all drafts
tell application "Drafts"
    get drafts
end tell

-- Get specific draft by UUID
tell application "Drafts"
    get draft id "DRAFT-UUID-HERE"
end tell

-- Get content of draft
tell application "Drafts"
    set firstDraft to first draft
    set draftContent to content of firstDraft
    set draftTags to tags of firstDraft
end tell
```

#### Update Draft
```applescript
tell application "Drafts"
    set content of draft id "DRAFT-UUID" to "Updated content"
end tell
```

#### Delete Draft - ❌ NOT AVAILABLE via AppleScript
**AppleScript CANNOT delete drafts directly.** The `delete` command does not work (returns no error but draft remains).

**Solution**: Use JavaScript API via Drafts Action (see JavaScript section below).

#### Search Drafts
```applescript
tell application "Drafts"
    search drafts for "search query"
end tell
```

#### Run Action on Draft
```applescript
tell application "Drafts"
    run action "Action Name" with draft id "DRAFT-UUID"
end tell
```

**SSS Implication**: This is the KEY to delete capability - run JavaScript-based Drafts Actions via AppleScript!

---

### 2. JavaScript API - ⚠️ Internal Only

**Status**: **Runs ONLY inside Drafts** - Cannot be called from terminal/external scripts

**Documentation**: https://scripting.getdrafts.com/

**Key Objects**:
- `Draft` - Current draft object (content, uuid, tags, etc.)
- `Drafts` - App-level methods (createDraft, findAllDrafts, executeAction)
- `Editor` - Editor state and manipulation
- `Action` - Action execution

**Example** (runs inside Drafts Action):
```javascript
// Get current draft
let content = draft.content;
draft.addTag("processed");

// Create new draft
Drafts.createDraft({
  content: "Processed: " + content,
  tags: ["new", "processed"]
});

// Delete draft (THIS IS THE ONLY WAY TO DELETE!)
Draft.delete(draft.uuid);

// Find drafts
let allDrafts = Draft.query("", "inbox", [], [], "created", true, false);
```

**Delete Capability**:
- `Draft.delete(uuid)` - ONLY available in JavaScript API
- Runs ONLY inside Drafts Action scripts
- Cannot be called from external terminal/scripts
- Must be triggered via AppleScript `run action` or URL scheme

**SSS Implication**: Can create Drafts Actions that process and delete, but must be triggered externally (via AppleScript or URL scheme)

---

### 3. URL Schemes - ⚠️ One-Way Only

**Status**: **Can send commands, cannot receive data**

**Documentation**: https://docs.getdrafts.com/docs/automation/urlschemes

**Capabilities**:
```
drafts://x-callback-url/create?text=...
drafts://x-callback-url/append?uuid=...&text=...
drafts://x-callback-url/prepend?uuid=...&text=...
drafts://x-callback-url/runAction?action=...&uuid=...
drafts://x-callback-url/search?query=...
```

**Limitation**: Can trigger actions, cannot retrieve results to terminal

---

### 4. Raycast Extension (FlohGro) - ✅ UI-Level Control

**Status**: **Full UI control** through Raycast commands

**Capabilities**: See "Raycast Integration Details" section above

**Limitation**: UI-driven, not scriptable for batch operations

---

## Recommended SSS Approach: Hybrid AppleScript + JavaScript

**Strategy**: Use AppleScript for external control, JavaScript for delete operations

**Workflow for Delete**:
1. **Create Drafts Action** (one-time setup):
   - Name: "Delete Draft by UUID"
   - Type: Script action
   - JavaScript: `Draft.delete(draft.uuid);`

2. **Trigger via AppleScript**:
   ```applescript
   tell application "Drafts"
       run action "Delete Draft by UUID" with draft id "DRAFT-UUID"
   end tell
   ```

**Full Processing Workflow**:
1. **AppleScript**: Query drafts, get UUIDs and content
2. **AI Analysis**: Process content externally (Claude, Gemini, etc.)
3. **Routing Decision**: Determine destination (Obsidian, Bear, Reminders, Delete)
4. **AppleScript**: Execute routing:
   - For routing to other apps: Use AppleScript/CLI tools directly
   - For delete: Run "Delete Draft by UUID" Drafts Action via AppleScript

**Example Flow**:
```applescript
-- Get all drafts
tell application "Drafts"
    set allDrafts to drafts
    repeat with aDraft in allDrafts
        set draftContent to content of aDraft
        set draftID to id of aDraft

        -- Process externally (call Python/Node script with content)
        -- Script returns: "delete" or "route:obsidian" or "route:bear"

        -- Route based on decision
        -- For delete: run Drafts Action with JavaScript
        run action "Delete Draft by UUID" with draft id draftID

        -- For Obsidian/Bear routing: use direct AppleScript/CLI commands
    end repeat
end tell
```

**Note**: The "Delete Draft by UUID" action must be created in Drafts first (see Workflow for Delete above).

## SSS Integration Strategy

### Current State: Information Accumulation
- **Input Sources**: Voice notes, quick thoughts, meeting notes, web clips
- **Storage Pattern**: Rapid capture with minimal organization
- **Pain Point**: 1,200+ unprocessed notes creating cognitive burden

### Target State: Intelligent Processing
- **AI Triage**: Automatic categorization and routing decisions
- **Smart Routing**: Content flows to appropriate destinations (Obsidian, Bear, Reminders)
- **Human-in-Loop**: AI requests clarification for ambiguous content
- **Bulk Processing**: Systematic reduction of backlog

## Processing Workflows

### Voice → Drafts → AI Analysis
```typescript
// Proposed workflow:
1. Voice input via SuperWhisper
2. Raycast creates draft
3. AI agent analyzes content
4. Routing decision: 
   - Obsidian (knowledge/reference)
   - Bear (personal/quick access)
   - Reminders (actionable items)
   - Archive (completed/irrelevant)
```

### Batch Processing Pipeline
```typescript
// For existing 1,200+ notes:
1. AI agent processes notes in batches (10-20 at a time)
2. Categorizes by type: reference, action, personal, project
3. Suggests routing destinations
4. Requests human clarification for ambiguous items
5. Executes approved routing decisions
6. Archives or deletes processed items
```

## Draft Actions & Automation

### Existing Capabilities
- **JavaScript API**: Full automation capabilities within Drafts
- **URL Schemes**: External app integration and triggering
- **Template System**: Structured content creation
- **Workspace Organization**: Context-based grouping

### SSS Enhancement Opportunities
```typescript
// Custom Draft Actions for SSS:
- "Route to Obsidian" (with vault selection)
- "Create Reminder" (extract actionable items)
- "Archive to Bear" (personal reference)
- "AI Analyze" (request intelligent processing)
- "Clarify" (mark for human review)
```

## MCP Server Integration

### Drafts MCP Server Concept
```typescript
// Proposed MCP server capabilities:
{
  "name": "drafts_server",
  "tools": [
    "list_drafts",           // Get drafts by workspace/tag/date
    "get_draft",             // Retrieve specific draft content
    "create_draft",          // Create new draft
    "update_draft",          // Modify existing draft
    "run_action",            // Execute Draft Action
    "search_drafts",         // Content-based search
    "route_draft",           // Move to other apps
    "drafts_agent"           // Natural language interface
  ]
}
```

### Integration with Warp AI
```bash
# Example Warp AI commands via MCP:
warp-ai "Process the last 10 drafts and route them appropriately"
warp-ai "Find all drafts about the Johnson project and create an Obsidian summary"
warp-ai "Clear drafts older than 30 days that don't contain action items"
```

## Content Analysis Patterns

### Typical Content Types in Current Backlog
1. **Meeting Notes**: Names, decisions, action items mixed together
2. **Quick Thoughts**: Random ideas, reminders, observations  
3. **Project Updates**: Status reports, progress notes
4. **Reference Material**: Links, quotes, research snippets
5. **Action Items**: TODOs disguised as notes

### AI Processing Rules
```typescript
// Content classification rules:
- Contains names + dates + decisions → Meeting notes → Obsidian
- Contains "TODO", "remind", action verbs → Reminders creation
- Contains URLs, quotes, references → Bear for quick access
- Contains project names + status → Project workspace in Obsidian
- Short, personal observations → Archive or Bear
```

## Human-in-Loop Processing

### Clarification Scenarios
```typescript
// When AI should ask for human input:
- Ambiguous pronoun references ("the project", "that meeting")
- Multiple possible routing destinations
- Incomplete action items missing context
- Personal vs. work content boundary unclear
- Time-sensitive items requiring priority assessment
```

### Voice-Enabled Clarification
```
AI: "This draft mentions 'the project deadline' - which project?"
Human (via SuperWhisper): "The Johnson website redesign project"
AI: "Routing to Obsidian Johnson project workspace"
```

## Success Metrics

### Backlog Reduction
- **Goal**: Reduce 1,200+ notes to <100 active items
- **Timeline**: Process 50-100 notes per week with AI assistance
- **Quality**: 95% routing accuracy with minimal human intervention

### New Content Flow
- **Capture**: Voice → Drafts (unchanged)
- **Processing**: Automatic routing within 24 hours
- **Review**: Weekly review of routing decisions
- **Adjustment**: Refinement of AI routing rules based on patterns

## Implementation Phases

### Phase 1: Current State Assessment
- [ ] Audit existing 1,200+ drafts for content patterns
- [ ] Test Raycast voice → Drafts workflow
- [ ] Identify most common content types requiring routing

### Phase 2: AI Processing Pipeline
- [ ] Build Drafts MCP server for external access
- [ ] Create content analysis AI agent
- [ ] Implement human-in-loop clarification system

### Phase 3: Batch Processing
- [ ] Process historical backlog with AI assistance
- [ ] Establish new content routing workflows
- [ ] Monitor and refine routing accuracy

### Phase 4: Advanced Automation
- [ ] Voice-driven immediate routing decisions
- [ ] Cross-app content relationship detection
- [ ] Predictive routing based on content patterns

---

## Added by Randy Kerber 2025-12-21

Ran command in Warp Terminal CLI:
```shell
osascript -e 'tell application "Drafts" to make new draft with properties {content:"Test draft to delete"}'

execution error: Drafts got an error: AppleEvent timed out. (-1712)
```

Popup says:
“Warp.app” wants access to control “Drafts.app”. Allowing control will provide access to documents and data in “Drafts.app”, and to perform actions within that app.

I clicked "Allow" button.

Despite error messages, there is now a note in Drafts called with contents = "Test draft to delete" in Drafts.

---

## Delete Investigation Findings - 2025-12-21

**Problem**: AppleScript `delete draft id "uuid"` command does not work
- Command executes without error
- BUT draft remains in Drafts app (confirmed by user)
- Tested multiple syntax variations - none worked

**Root Cause**: AppleScript does NOT support delete operations
- Current Drafts documentation (Context7) shows NO delete examples in AppleScript
- Only JavaScript API has `Draft.delete(uuid)` capability
- JavaScript API runs ONLY inside Drafts Actions (not externally callable)

**Solution**: Hybrid AppleScript + JavaScript approach
1. Create Drafts Action with JavaScript: `Draft.delete(draft.uuid);`
2. Trigger Action via AppleScript: `run action "Delete Draft by UUID" with draft id "uuid"`

**Test Drafts Created**:
- UUID: FD858B20-D8DE-4C4E-A2F3-EDEAA0A93509 (content: "Test draft to delete 1")
- UUID: EC8C8534-394C-4C14-8C91-67A68C3E7F09 (content: "Test draft to delete 2")

**Status**: Solution documented above in "Recommended SSS Approach" section. Needs testing.

**SSS Implication**: DELETE wall can be breached, but requires one-time Drafts Action setup.


