# SiloSlayer Syndicate Agent Tool Inventory

## Tool Registry: Single Source of Truth 🎯

**Key Principle:** **If it's not in the tool registry, it doesn't exist.**

The tool registry (`src/tools/tool-registry.ts`) provides **automatic discovery** of all available tools from three distinct sources. Run `npm run build && node dist/tools/tool-registry.js` to see the complete, current inventory.

## Three Primary Tool Categories

### 1. **OpenAI Built-in Tools** 
- **Source**: Provided directly by OpenAI's SDK
- **Discovery**: Automatic at runtime
- **Examples**: Currently none active, but includes future OpenAI-hosted tools
- **Configuration**: None required

### 2. **MCP Server Tools** ⭐ **Primary Integration Method**
- **Source**: External MCP (Model Context Protocol) servers
- **Discovery**: Automatic from `config/mcp-config.json`
- **Examples**: Filesystem operations, Obsidian vaults, web search, sequential thinking
- **Configuration**: Add server entry to config file
- **Current Servers**:
  - `filesystem` - File system operations (12 tools)
  - `sequential-thinking` - Structured problem solving (1 tool)  
  - `tavily-search` - Web search and content extraction (4 tools)
  - `obsidian-fin` - Fin Obsidian vault operations (11 tools)
  - `obsidian-tech` - Tech Obsidian vault operations (11 tools)

### 3. **Custom/Local Tools**
- **Source**: Our own JavaScript implementations 
- **Discovery**: Exported from `src/tools/simple-tools.ts`
- **Examples**: Project file operations, shell commands, Apple Reminders
- **Configuration**: Add to `createBasicToolkit()` export function
- **Current Tools**:
  - `read_project_file` - Read syndicate-js project files
  - `write_project_file` - Write syndicate-js project files  
  - `run_command` - Execute shell commands
  - `get_env_var` - Access environment variables
  - `create_reminder` - Apple Reminders (hello-world status)

## Tool Registry Architecture

The registry provides **one-stop tool discovery** for agent construction:

```typescript
// Get all available tools for an agent
const registry = new ToolRegistry();
const allTools = await registry.getAllTools();

// Create agent with complete tool set
const agent = new Agent({
  name: 'MyAgent',
  tools: allTools // Everything discovered automatically
});
```

## Current Tool Count: **43 Total Tools**
- **Custom Tools**: 5
- **MCP Tools**: 38  
- **OpenAI Built-ins**: 0

## Key Architectural Insights ✅

1. **Function Calling Works**: OpenAI correctly identifies tool needs and formats calls
2. **MCP Integration is Primary**: External servers provide most functionality
3. **Agent SDK is Extensible**: Agents can be converted to tools using `agent.asTool()`
4. **Registry Enables Discovery**: Single source eliminates tool hunting

## Adding New Tools

### To Add MCP Server Tools:
1. Add server configuration to `config/mcp-config.json`
2. Tools appear automatically in registry

### To Add Custom Tools:
1. Implement tool in `src/tools/simple-tools.ts`
2. Export from `createBasicToolkit()` function
3. Tools appear automatically in registry

## Proven Agent Construction Pattern

```typescript
import { ToolRegistry } from './tools/tool-registry.js';
import { Agent } from '@openai/agents';

// Get all available tools
const registry = new ToolRegistry();
const allTools = await registry.getAllTools();

// Create agent with complete toolset
const agent = new Agent({
  name: 'SpecializedAgent',
  model: 'gpt-4o-mini',
  instructions: 'Your specialized instructions...',
  tools: allTools
});
```

---

## Historical Research: Tool Source Analysis

*Note: The following sections document research into tool integration strategies and remain for reference, but current implementation focuses on the three primary categories above.*

### Extended Tool Source Categories
1. **Native Tools** (OS-Level) - System commands, file operations
2. **Third-Party Applications** - Direct app APIs, AppleScript, URL schemes  
3. **Web Applications** - REST APIs, browser-based services
4. **API Services** - Cloud/remote specialized services
5. **Automation Platforms** - Raycast, Apple Shortcuts, Zapier

### Integration Strategy Research
- **Raycast Hub Strategy**: Single interface for multiple apps
- **Apple Shortcuts Bridge**: Voice control and mobile workflows  
- **Warp Terminal**: System-level AI agent capabilities
- **MCP Ecosystem**: Community-driven tool servers

*See full historical analysis in git history for detailed research findings.*