import { createBasicToolkit } from './simple-tools';
import { ConfiguredMCPClient } from '../mcp-client-proper';

/**
 * CENTRAL TOOL REGISTRY - Single Source of Truth for All Available Tools
 * 
 * This is THE PLACE to find all tools available to SSS agents.
 * If it's not listed here, it doesn't exist.
 */

export interface ToolDefinition {
  name: string;
  description: string;
  source: 'custom' | 'mcp' | 'openai_builtin';
  parameters?: any;
  function?: Function;
  mcpServer?: string;
}

export class ToolRegistry {
  private mcpClient: ConfiguredMCPClient;
  private customTools: ToolDefinition[] = [];
  private mcpTools: ToolDefinition[] = [];
  private openaiTools: ToolDefinition[] = [];

  constructor() {
    this.mcpClient = new ConfiguredMCPClient();
    this.initializeCustomTools();
  }

  /**
   * Initialize custom JavaScript tools
   */
  private initializeCustomTools() {
    const basicToolkit = createBasicToolkit();
    
    this.customTools = basicToolkit.map(tool => ({
      name: tool.name,
      description: tool.description || 'Custom tool',
      source: 'custom' as const,
      parameters: tool.parameters,
      function: tool.function
    }));
  }

  /**
   * Discover and load MCP tools from all configured servers
   */
  async discoverMCPTools(): Promise<void> {
    this.mcpTools = [];
    const servers = this.mcpClient.listServers();
    
    for (const serverName of servers) {
      try {
        const serverTools = await this.mcpClient.getServerTools(serverName);
        
        for (const tool of serverTools) {
          this.mcpTools.push({
            name: `${serverName}.${tool.name}`,
            description: tool.description || `Tool from ${serverName} server`,
            source: 'mcp' as const,
            parameters: tool.inputSchema,
            mcpServer: serverName
          });
        }
      } catch (error) {
        console.warn(`Failed to discover tools from ${serverName}:`, error);
      }
    }
  }

  /**
   * Define OpenAI built-in tools
   */
  private initializeOpenAITools() {
    this.openaiTools = [
      {
        name: 'web_search',
        description: 'Search the web for current information',
        source: 'openai_builtin' as const
      },
      {
        name: 'code_interpreter',
        description: 'Execute code in a sandboxed environment',
        source: 'openai_builtin' as const
      },
      {
        name: 'file_search',
        description: 'Search through uploaded files and documents',
        source: 'openai_builtin' as const
      }
    ];
  }

  /**
   * Get ALL available tools from all sources
   */
  async getAllTools(): Promise<ToolDefinition[]> {
    await this.discoverMCPTools();
    this.initializeOpenAITools();
    
    return [
      ...this.customTools,
      ...this.mcpTools,
      ...this.openaiTools
    ];
  }

  /**
   * Get tools by source type
   */
  getCustomTools(): ToolDefinition[] {
    return [...this.customTools];
  }

  getMCPTools(): ToolDefinition[] {
    return [...this.mcpTools];
  }

  getOpenAITools(): ToolDefinition[] {
    return [...this.openaiTools];
  }

  /**
   * Find a specific tool by name
   */
  async findTool(toolName: string): Promise<ToolDefinition | null> {
    const allTools = await this.getAllTools();
    return allTools.find(tool => tool.name === toolName) || null;
  }

  /**
   * Check if a tool exists
   */
  async toolExists(toolName: string): Promise<boolean> {
    const tool = await this.findTool(toolName);
    return tool !== null;
  }

  /**
   * Execute a tool (handles routing to appropriate execution method)
   */
  async executeTool(toolName: string, args: any): Promise<any> {
    const tool = await this.findTool(toolName);
    
    if (!tool) {
      throw new Error(`Tool '${toolName}' not found in registry`);
    }

    switch (tool.source) {
      case 'custom':
        if (!tool.function) {
          throw new Error(`Custom tool '${toolName}' has no function defined`);
        }
        return await tool.function(args);

      case 'mcp':
        if (!tool.mcpServer) {
          throw new Error(`MCP tool '${toolName}' has no server defined`);
        }
        const actualToolName = toolName.split('.')[1]; // Remove server prefix
        return await this.mcpClient.callTool(tool.mcpServer, actualToolName, args);

      case 'openai_builtin':
        throw new Error(`OpenAI built-in tools must be handled by the OpenAI Agent SDK`);

      default:
        throw new Error(`Unknown tool source: ${tool.source}`);
    }
  }

  /**
   * Print comprehensive tool inventory
   */
  async printToolInventory(): Promise<void> {
    console.log('\n🧰 COMPREHENSIVE TOOL INVENTORY');
    console.log('=====================================\n');

    const customTools = this.getCustomTools();
    const mcpTools = this.getMCPTools();
    const openaiTools = this.getOpenAITools();

    // Make sure MCP tools are discovered
    if (mcpTools.length === 0) {
      await this.discoverMCPTools();
    }

    console.log(`📋 CUSTOM TOOLS (${customTools.length}):`);
    customTools.forEach(tool => {
      console.log(`   • ${tool.name}: ${tool.description}`);
    });

    console.log(`\n🔗 MCP TOOLS (${this.mcpTools.length}):`);
    this.mcpTools.forEach(tool => {
      console.log(`   • ${tool.name}: ${tool.description}`);
    });

    console.log(`\n🤖 OPENAI BUILT-IN TOOLS (${openaiTools.length}):`);
    openaiTools.forEach(tool => {
      console.log(`   • ${tool.name}: ${tool.description}`);
    });

    const totalTools = customTools.length + this.mcpTools.length + openaiTools.length;
    console.log(`\n✨ TOTAL AVAILABLE TOOLS: ${totalTools}`);
  }

  /**
   * Cleanup MCP connections
   */
  async cleanup(): Promise<void> {
    await this.mcpClient.closeAll();
  }
}

/**
 * Global tool registry instance (singleton pattern)
 */
let globalToolRegistry: ToolRegistry | null = null;

export function getToolRegistry(): ToolRegistry {
  if (!globalToolRegistry) {
    globalToolRegistry = new ToolRegistry();
  }
  return globalToolRegistry;
}

/**
 * Test the tool registry
 */
async function testToolRegistry() {
  console.log('🧪 Testing Tool Registry\n');
  
  const registry = getToolRegistry();
  
  try {
    // Print complete inventory
    await registry.printToolInventory();
    
    // Test tool existence
    console.log('\n🔍 Testing tool existence:');
    const testTools = ['read_project_file', 'filesystem.read_file', 'web_search', 'nonexistent_tool'];
    
    for (const toolName of testTools) {
      const exists = await registry.toolExists(toolName);
      console.log(`   ${exists ? '✅' : '❌'} ${toolName}`);
    }
    
    // Test tool execution
    console.log('\n⚙️  Testing tool execution:');
    try {
      const result = await registry.executeTool('read_project_file', { filepath: 'package.json' });
      console.log('   ✅ Successfully executed read_project_file');
      console.log(`   📄 File size: ${result.size} characters`);
    } catch (error) {
      console.log('   ❌ Failed to execute read_project_file:', error);
    }

  } catch (error) {
    console.error('❌ Tool registry test failed:', error);
  } finally {
    await registry.cleanup();
  }
}

// Run test if this file is executed directly
if (require.main === module) {
  testToolRegistry().catch(console.error);
}