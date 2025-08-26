import { readFileSync } from 'fs';
import { join } from 'path';

/**
 * Proper MCP configuration management following industry best practices
 */

export interface MCPServerConfig {
  command: string;
  args?: string[];
  env?: Record<string, string>;
}

export interface MCPConfiguration {
  mcpServers: Record<string, MCPServerConfig>;
}

/**
 * Load MCP configuration from file with environment variable substitution
 */
export function loadMCPConfig(configPath?: string): MCPConfiguration {
  const defaultPath = join(process.cwd(), '..', 'config', 'mcp-config.json');
  const path = configPath || defaultPath;
  
  try {
    const configText = readFileSync(path, 'utf-8');
    const config = JSON.parse(configText) as MCPConfiguration;
    
    // Substitute environment variables in the config
    return substituteEnvironmentVariables(config);
  } catch (error) {
    console.error(`Failed to load MCP config from ${path}:`, error);
    throw new Error(`MCP configuration file not found or invalid: ${path}`);
  }
}

/**
 * Substitute ${VAR_NAME} patterns with environment variables
 */
function substituteEnvironmentVariables(config: MCPConfiguration): MCPConfiguration {
  const configStr = JSON.stringify(config);
  const substituted = configStr.replace(/\$\{([^}]+)\}/g, (match, varName) => {
    const [name, defaultValue] = varName.split(':-');
    return process.env[name] || defaultValue || match;
  });
  
  return JSON.parse(substituted);
}

/**
 * Get specific server configuration
 */
export function getServerConfig(serverName: string, config?: MCPConfiguration): MCPServerConfig {
  const mcpConfig = config || loadMCPConfig();
  const serverConfig = mcpConfig.mcpServers[serverName];
  
  if (!serverConfig) {
    throw new Error(`MCP server '${serverName}' not found in configuration`);
  }
  
  return serverConfig;
}

/**
 * List available MCP servers from configuration
 */
export function listAvailableServers(config?: MCPConfiguration): string[] {
  const mcpConfig = config || loadMCPConfig();
  return Object.keys(mcpConfig.mcpServers);
}