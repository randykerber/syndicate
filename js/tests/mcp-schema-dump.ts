/**
 * Dump raw MCP tool schemas to see actual parameter definitions
 */
import { ToolRegistry } from '../src/tools/tool-registry.js';

async function dumpMCPSchemas() {
  console.log('🔍 RAW MCP TOOL SCHEMAS');
  console.log('======================\n');
  
  try {
    const registry = new ToolRegistry();
    await registry.discoverMCPTools();
    
    // Access the private mcpTools array
    const mcpTools = registry['mcpTools'] || [];
    
    // Filter for Obsidian tools
    const obsidianTools = mcpTools.filter(tool => tool.name.startsWith('obsidian.'));
    
    console.log(`Found ${obsidianTools.length} Obsidian tools:\n`);
    
    obsidianTools.forEach(tool => {
      console.log(`🔧 ${tool.name}`);
      console.log(`   Description: ${(tool.description || '').substring(0, 80)}...`);
      console.log(`   Parameters:`, JSON.stringify(tool.parameters, null, 2));
      console.log('');
    });
    
  } catch (error) {
    console.error('❌ Failed to dump schemas:', error);
  }
}

// Run if executed directly
if (require.main === module) {
  dumpMCPSchemas().then(() => {
    console.log('✅ Schema dump complete');
  });
}