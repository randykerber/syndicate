# Drafts - Text Capture & Processing Hub

## Overview
Drafts serves as the primary text capture and initial processing point in the SSS ecosystem, with 1,200+ existing notes requiring intelligent triage and organization.

## Current Status
- **Content Volume**: 1,200+ notes accumulated
- **Raycast Integration**: ✅ Full integration via FlohGro extension
- **Primary Challenge**: Backlog triage and intelligent routing
- **Processing Goal**: Transform from "text dumping ground" to "intelligent capture system"

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