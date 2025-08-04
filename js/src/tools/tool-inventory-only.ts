/**
 * Clean tool inventory report without server startup noise
 */
import { ToolRegistry } from './tool-registry.js';

async function printCleanInventory() {
  console.log('📊 CLEAN TOOL INVENTORY REPORT');
  console.log('==============================\n');
  
  try {
    const registry = new ToolRegistry();
    
    // Suppress MCP server startup logs by redirecting them
    const originalLog = console.log;
    const originalError = console.error;
    
    // Temporarily silence console during discovery
    console.log = () => {};
    console.error = () => {};
    
    const allTools = await registry.getAllTools();
    
    // Restore console
    console.log = originalLog;
    console.error = originalError;
    
    // Now print clean summary
    const customTools = registry['customTools'] || [];
    const mcpTools = registry['mcpTools'] || [];
    const openaiTools = registry['openaiTools'] || [];
    
    console.log(`📋 CUSTOM TOOLS (${customTools.length}):`);
    customTools.forEach(tool => {
      console.log(`   • ${tool.name}: ${tool.description || 'No description'}`);
    });
    
    console.log(`\n🔗 MCP TOOLS (${mcpTools.length}):`);
    mcpTools.forEach(tool => {
      console.log(`   • ${tool.name}: ${tool.description || 'No description'}`);
    });
    
    console.log(`\n🤖 OPENAI BUILT-IN TOOLS (${openaiTools.length}):`);
    
    console.log(`\n✨ TOTAL AVAILABLE TOOLS: ${allTools.length}`);
    
  } catch (error) {
    console.error('❌ Failed to generate inventory:', error);
  }
}

// Run if executed directly
if (require.main === module) {
  printCleanInventory();
}