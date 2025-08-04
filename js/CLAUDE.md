# CLAUDE.md - SiloSlayer Syndicate (JavaScript/TypeScript)

This file provides guidance to Claude Code when working with the JavaScript/TypeScript components of the SiloSlayer Syndicate (SSS) system.

## Project Overview

This is the **JavaScript/TypeScript integration layer** of the SiloSlayer Syndicate - a system designed to liberate information from app silos and create unified, intelligent content management. This project handles native tool integrations with superior API capabilities, while the Python project (`~/gh/randykerber/agentic-ai/`) handles agent orchestration and AI workflows.

## SiloSlayer Syndicate Mission

**Core Problem**: Information scattered across Drafts (1219+ items), Obsidian (7200+ notes), YouTube saves, Substack queues, podcast apps, reminder systems - creating "app prison" where users can't find their own information.

**Solution**: AI-powered information liberation using "English as programming language" approach where voice/text instructions trigger multi-agent workflows that intelligently route content to proper destinations.

## Architecture Position

### Hybrid Python/JavaScript Strategy
```
SiloSlayer Syndicate Architecture:
├── agentic-ai/ (Python)     - Agent orchestration, mature MCP servers, AI workflows  
├── syndicate-js/ (THIS)     - Native tool integrations, rich UI components
└── MCP Protocol             - Language-agnostic communication bridge
```

### JavaScript Advantages for SSS Tools
**Why JavaScript/TypeScript for core integrations:**
- **Raycast**: Native extension API with rich UI components, real-time search
- **Drafts**: Direct JavaScript runtime access, complete Draft API 
- **Obsidian**: Full Plugin API, vault manipulation, metadata cache
- **Apple Shortcuts**: URL schemes (same capability as Python)

**Result**: JavaScript provides **3 out of 4 key integrations** with significantly superior native capabilities.

## Development Environment

- **IDE**: WebStorm with Claude Code integration
- **Runtime**: Node.js with TypeScript
- **Package Management**: npm (transitioning from global to local packages)
- **Testing**: Basic npm scripts, no centralized framework yet
- **Global Context**: ~/.claude/CLAUDE.md (cross-conversation persistence)

## Project Structure

```
syndicate-js/
├── src/
│   ├── agents/           # OpenAI Agent SDK implementations
│   │   └── reminder-agent.ts     # Working O-Agent example
│   ├── tools/            # MCP and custom tool implementations  
│   │   ├── tool-registry.ts      # Central tool discovery (35 tools)
│   │   ├── working-reminders.ts  # Apple Reminders integration
│   │   └── simple-tools.ts       # File, system, and reminder tools
│   └── utils/            # Shared utilities
├── config/
│   └── mcp-config.json   # MCP server configurations
├── docs/
│   ├── Tool-Inventory.md # Comprehensive tool documentation
│   └── actors/           # Individual tool/integration docs
└── dist/                 # TypeScript compilation output
```

## Current Tool Inventory (35 Total)

### **Custom Tools (7):**
- `read_project_file`, `write_project_file` - File operations
- `run_command`, `get_env_var` - System operations  
- `create_working_reminder` - Apple Reminders integration (working)

### **MCP Tools (28):**
- **Filesystem**: File operations, multi-file reads, git-style diffs
- **Obsidian**: Note creation, editing, search, vault management (2 vaults: Fin, Tech)
- **Sequential-thinking**: AI reasoning workflows
- **Tavily**: Web search and research

### **OpenAI Built-in Tools**: Currently none integrated

## Key Integrations Status

### ✅ **Working Integrations:**
- **Tool Registry**: Central discovery system for all 35 tools
- **MCP Servers**: 4 servers operational (filesystem, obsidian, sequential-thinking, tavily)
- **Obsidian**: Both vaults accessible (Fin: financial, Tech: development)  
- **Apple Reminders**: Basic creation via AppleScript (working but has timeout issues)
- **OpenAI Agents SDK**: Basic O-Agent patterns functional

### 🎯 **Priority Development Areas:**
- **Raycast Extensions**: Leverage superior native API capabilities
- **Drafts Actions**: Direct JavaScript runtime integration
- **Obsidian Plugins**: Full vault API utilization
- **Human-in-Loop Patterns**: Agent asks for clarification when uncertain

### 🚫 **Abandoned/Removed:**
- Smart reminders system (over-engineered, unreliable)
- Notification system hacks (iOS API limitations)
- AppleScript bulk operations (timeout issues)

## Human-in-Loop Agent Pattern

**Core Workflow:**
1. **Receive request** - "File this article about productivity techniques"
2. **Fill in what agent can** - Extract title, determine category, identify concepts
3. **Assess completeness** - "I can create the note, think it goes in /Systems/Productivity, unsure about tags"
4. **Present draft tool call** - "I'm going to call create_note with [parameters]. Does this look right?"
5. **Wait for confirmation** - User confirms or provides corrections
6. **Execute with confidence** - Make the actual tool call

This pattern leverages human judgment for difficult decisions while automating mechanical work.

## Context Engineering

### Global Context Strategy
- **~/.claude/CLAUDE.md**: Cross-conversation persistent context (proven working)
- **Local CLAUDE.md**: Project-specific context and status
- **Session continuity**: `claude --ide --continue` maintains conversation across days

### Knowledge Staleness Alerts
- **AI/MCP tooling changes rapidly** - always verify current docs against training data
- **Raycast extensions, Obsidian APIs frequently updated** - check official sources
- **Ask about information currency** for fast-moving topics

## Common Constraints & Anti-Patterns

### User Preferences
- **Practical over theoretical** - working solutions beat elegant architectures
- **Avoid over-engineering** - simple working code beats complex "smart" systems
- **Quick wins vs rabbit holes** - prefer incremental progress over perfect solutions
- **Question "appearance of progress"** - challenge solutions that don't solve real problems

### Technical Constraints  
- **AppleScript timeout issues** - keep scripts simple, avoid bulk operations
- **MCP server reliability varies** - some timeout, some work perfectly
- **iOS notification system locked down** - accept limitations, don't fight the platform
- **Multi-language complexity** - MCP bridges the gap but adds debugging overhead

### Anti-Patterns to Avoid
- **Elimination reminders** - generic tasks without specific targets are useless
- **Bulk notification hacks** - iOS won't allow, don't waste time trying
- **Perfect mega-prompts** - iterative conversation beats elaborate prompt engineering
- **Architecture paralysis** - pick a direction and build, perfect later

## Integration Patterns

### MCP Server Integration
```typescript
// Tool Registry discovers and manages all tools
const registry = new ToolRegistry();
await registry.printToolInventory(); // Shows all 35 tools

// Execute tools through unified interface
const result = await registry.executeTool('create_note', {
  vault: 'fin',
  filename: 'example.md',
  content: 'Note content'
});
```

### OpenAI Agent Pattern
```typescript
import { Agent, run, tool } from '@openai/agents';

const agent = Agent.create({
  model: 'gpt-4o-mini', 
  name: 'Task Agent',
  instructions: 'Agent instructions here',
  tools: [toolDefinitions]
});

const response = await run(agent, "User request");
```

## Development Workflow

### Common Commands
```bash
# Build TypeScript
npm run build

# Tool inventory report
npm run tool-inventory

# Test specific functionality
node -e "const { testFunction } = require('./dist/path/file.js'); testFunction();"
```

### File Operations
- **Read project files**: Use tool registry or direct file operations
- **MCP server config**: `config/mcp-config.json` for server definitions
- **TypeScript compilation**: Always build before testing Node.js code

## SSS Integration Roadmap

### Phase 1: Native Tool Excellence
- [ ] **Raycast Extension Development** - Leverage superior native API
- [ ] **Drafts Action Creation** - Direct JavaScript runtime integration  
- [ ] **Obsidian Plugin Development** - Full vault API utilization
- [ ] **Unified Command Interface** - Single entry point for SSS operations

### Phase 2: MCP Bridge Development  
- [ ] **Publish JS tools via MCP** - Make native integrations available to Python side
- [ ] **Cross-language coordination** - Python agents orchestrate JS tool execution
- [ ] **Bidirectional communication** - JS can trigger Python AI workflows

### Phase 3: SiloSlayer Integration
- [ ] **Content liberation workflows** - Break information out of app silos
- [ ] **English instruction parsing** - Natural language becomes programming interface
- [ ] **Unified content dashboard** - All saved content across apps in prioritized view
- [ ] **Intelligent routing** - AI-powered categorization and destination selection

## Next Session Priorities

### High Priority
1. **Human-in-loop agent implementation** - Build the clarification request pattern
2. **Obsidian note destination expert** - MCP tool for intelligent note routing
3. **Raycast extension exploration** - Investigate native integration possibilities

### Medium Priority  
1. **Voice input integration** - SuperWhisper or Siri-based content capture
2. **Drafts processing automation** - Smart exits from universal inbox
3. **Cross-project coordination** - Define MCP integration points with Python side

### Context Maintenance
- **Update global ~/.claude/CLAUDE.md** with architectural decisions
- **Document tool integration patterns** that work vs those that don't
- **Track MCP ecosystem evolution** - JavaScript tooling is rapidly maturing

## Success Metrics

**Immediate (Next Session):**
- Human-in-loop agent working with real tools
- Clear MCP integration pattern with Python project
- One concrete SSS workflow end-to-end functional

**Short-term (Next Month):**
- Native Raycast/Drafts/Obsidian integrations superior to Python alternatives
- Reduced information capture friction (faster routing decisions)
- Cross-language agent coordination via MCP working

**Long-term (SSS Mission Success):**
- Information liberation: break out of app silos into unified system
- English as programming language: voice instructions → multi-agent execution
- "National debt" approach: reduce information backlog growth rate significantly