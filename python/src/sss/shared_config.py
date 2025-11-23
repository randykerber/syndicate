"""
Shared configuration utilities for accessing project-wide config files.

This module provides functions to load shared configuration files from the 
project root config/ directory, enabling consistent configuration across
Python and JavaScript components.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


def get_project_root() -> Path:
    """
    Find the project root directory by looking for syndicate-specific markers.
    
    Returns:
        Path to the project root directory
        
    Raises:
        FileNotFoundError: If project root cannot be found
    """
    current = Path(__file__).resolve()
    
    # Look for project markers going up the directory tree
    for parent in [current] + list(current.parents):
        if (parent / "config" / "mcp-config.json").exists():
            return parent
            
    raise FileNotFoundError("Cannot find project root (no config/mcp-config.json found)")


def load_shared_config(config_name: str) -> Dict[str, Any]:
    """
    Load a shared configuration file from the project root config/ directory.
    
    Args:
        config_name: Name of the config file (e.g., "mcp-config.json")
        
    Returns:
        Dictionary containing the configuration data
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    project_root = get_project_root()
    config_path = project_root / "config" / config_name
    
    if not config_path.exists():
        raise FileNotFoundError(f"Shared config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    # Substitute environment variables if needed
    return _substitute_env_vars(config_data)


def _substitute_env_vars(data: Any) -> Any:
    """
    Recursively substitute ${VAR_NAME:-default} patterns with environment variables.
    
    Args:
        data: Configuration data (dict, list, str, etc.)
        
    Returns:
        Configuration data with environment variables substituted
    """
    if isinstance(data, dict):
        return {key: _substitute_env_vars(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_substitute_env_vars(item) for item in data]
    elif isinstance(data, str):
        # Handle ${VAR_NAME:-default_value} patterns
        import re
        
        def replace_env_var(match):
            var_expr = match.group(1)
            if ':-' in var_expr:
                var_name, default_value = var_expr.split(':-', 1)
            else:
                var_name, default_value = var_expr, ''
            
            return os.environ.get(var_name, default_value)
        
        return re.sub(r'\$\{([^}]+)\}', replace_env_var, data)
    else:
        return data


def load_mcp_config() -> Dict[str, Any]:
    """
    Load the shared MCP configuration.
    
    Returns:
        Dictionary containing MCP server configurations
        
    Example:
        >>> config = load_mcp_config()
        >>> servers = config['mcpServers']
        >>> obsidian_config = servers['obsidian']
    """
    return load_shared_config("mcp-config.json")


def get_mcp_server_config(server_name: str) -> Optional[Dict[str, Any]]:
    """
    Get configuration for a specific MCP server.
    
    Args:
        server_name: Name of the MCP server (e.g., "obsidian", "filesystem")
        
    Returns:
        Server configuration dictionary, or None if not found
        
    Example:
        >>> obsidian_config = get_mcp_server_config("obsidian")
        >>> if obsidian_config:
        >>>     command = obsidian_config["command"]
        >>>     args = obsidian_config.get("args", [])
    """
    try:
        mcp_config = load_mcp_config()
        return mcp_config.get("mcpServers", {}).get(server_name)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def list_mcp_servers() -> list[str]:
    """
    List all available MCP servers from the shared configuration.
    
    Returns:
        List of MCP server names
        
    Example:
        >>> servers = list_mcp_servers()
        >>> print(f"Available MCP servers: {', '.join(servers)}")
    """
    try:
        mcp_config = load_mcp_config()
        return list(mcp_config.get("mcpServers", {}).keys())
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# Example usage and testing
if __name__ == "__main__":
    try:
        print("🔧 Testing shared configuration utilities...")
        
        # Test project root detection
        root = get_project_root()
        print(f"📁 Project root: {root}")
        
        # Test MCP config loading
        mcp_config = load_mcp_config()
        servers = list_mcp_servers()
        print(f"🔗 Available MCP servers: {', '.join(servers)}")
        
        # Test specific server config
        for server_name in servers[:3]:  # Show first 3 servers
            config = get_mcp_server_config(server_name)
            if config:
                command = config.get('command', 'N/A')
                print(f"   • {server_name}: {command}")
        
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

