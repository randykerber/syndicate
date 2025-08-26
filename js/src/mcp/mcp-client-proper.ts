import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { getServerConfig, listAvailableServers } from './mcp-client-config';

/**
 * Proper MCP client using configuration file instead of hardcoded values
 */
export class ConfiguredMCPClient {
  private clients: Map<string, Client> = new Map();
  
  /**
   * Connect to a specific MCP server using configuration
   */
  async connectToServer(serverName: string): Promise<Client> {
    // Check if already connected
    if (this.clients.has(serverName)) {
      return this.clients.get(serverName)!;
    }
    
    // Get server configuration
    const serverConfig = getServerConfig(serverName);
    console.log(`🔗 Connecting to MCP server: ${serverName}`);
    console.log(`   Command: ${serverConfig.command} ${serverConfig.args?.join(' ') || ''}`);
    
    // Create transport from configuration
    const envVars = { ...process.env };
    if (serverConfig.env) {
      Object.assign(envVars, serverConfig.env);
    }
    
    const transport = new StdioClientTransport({
      command: serverConfig.command,
      args: serverConfig.args || [],
      env: envVars as Record<string, string>
    });
    
    // Create and connect client
    const client = new Client({
      name: 'syndicate-js-client',
      version: '1.0.0'
    }, {
      capabilities: {}
    });
    
    await client.connect(transport);
    this.clients.set(serverName, client);
    
    console.log(`✅ Connected to ${serverName}`);
    return client;
  }
  
  /**
   * Get available tools from a specific server
   */
  async getServerTools(serverName: string): Promise<any[]> {
    const client = await this.connectToServer(serverName);
    const { tools } = await client.listTools();
    return tools;
  }
  
  /**
   * Call a tool on a specific server
   */
  async callTool(serverName: string, toolName: string, args: any): Promise<any> {
    const client = await this.connectToServer(serverName);
    return await client.callTool({ name: toolName, arguments: args });
  }
  
  /**
   * List all configured servers
   */
  listServers(): string[] {
    return listAvailableServers();
  }
  
  /**
   * Close all connections
   */
  async closeAll(): Promise<void> {
    const promises = Array.from(this.clients.values()).map(client => client.close());
    await Promise.all(promises);
    this.clients.clear();
  }
}

/**
 * Test the configuration-based MCP client
 */
async function testConfiguredMCPClient() {
  console.log('🧪 Testing Configuration-Based MCP Client\n');
  
  const client = new ConfiguredMCPClient();
  
  try {
    // List available servers
    const servers = client.listServers();
    console.log('📋 Available servers from config:', servers);
    
    // Test filesystem server
    console.log('\n🗂️  Testing filesystem server...');
    const fsTools = await client.getServerTools('filesystem');
    console.log(`   Available tools: ${fsTools.map(t => t.name).join(', ')}`);
    
    // Test file read
    await client.callTool('filesystem', 'read_file', {
      path: './package.json'
    });
    console.log('   ✅ Successfully read package.json');
    
    // Test sequential thinking server if available
    if (servers.includes('sequential-thinking')) {
      console.log('\n🧠 Testing sequential-thinking server...');
      const thinkingTools = await client.getServerTools('sequential-thinking');
      console.log(`   Available tools: ${thinkingTools.map(t => t.name).join(', ')}`);
    }
    
    console.log('\n✨ Configuration-based MCP client working perfectly!');
    
  } catch (error) {
    console.error('❌ Configuration-based MCP client failed:', error);
  } finally {
    await client.closeAll();
  }
}

// Run the test if this file is executed directly
if (require.main === module) {
  testConfiguredMCPClient().catch(console.error);
}