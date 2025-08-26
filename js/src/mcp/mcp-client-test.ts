import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

/**
 * Test MCP client that connects to filesystem server
 */
async function testMCPClient() {
  const transport = new StdioClientTransport({
    command: '/usr/local/bin/mcp-server-filesystem',
    args: ['/Users/rk/gh/randykerber']
  });

  const client = new Client({
    name: 'syndicate-js-client',
    version: '1.0.0'
  }, {
    capabilities: {}
  });

  try {
    await client.connect(transport);
    console.log('✅ Connected to filesystem MCP server');

    // List available tools
    const { tools } = await client.listTools();
    console.log('📋 Available tools:', tools.map(t => t.name));

    // Test a simple file read
    const result = await client.callTool({
      name: 'read_file',
      arguments: {
        path: './package.json'
      }
    });

    console.log('📄 File read result:', result.content ? JSON.stringify(result.content) : 'No content');
    
  } catch (error) {
    console.error('❌ MCP client error:', error);
  } finally {
    await client.close();
  }
}

// Run the test
testMCPClient().catch(console.error);