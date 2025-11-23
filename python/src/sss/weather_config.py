#!/usr/bin/env python3
"""
Weather MCP Server Configuration for Syndicate

Clean MCP server configuration for AccuWeather integration.
"""

import os


def weather_mcp_servers():
    """Configure MCP servers for weather functionality."""
    return [
        {
            "command": "npx",
            "args": ["-y", "@timlukahorstmann/mcp-weather"],
            "env": {
                "ACCUWEATHER_API_KEY": os.getenv("ACCUWEATHER_API_KEY")
            }
        }
        # Human input server would go here if we had it set up
        # {
        #     "command": "uv",
        #     "args": ["run", "human_input_server.py"]
        # }
    ]


def weather_agent_mcp_server_params():
    """Legacy function name for compatibility."""
    return weather_mcp_servers()


if __name__ == "__main__":
    """Test MCP server configuration."""
    print("🔧 Weather MCP Server Configuration")
    print("=" * 40)
    
    config = weather_mcp_servers()
    
    for i, server in enumerate(config, 1):
        print(f"Server {i}:")
        print(f"  Command: {server['command']}")
        print(f"  Args: {' '.join(server['args'])}")
        if 'env' in server:
            for key, value in server['env'].items():
                masked_value = f"{value[:8]}..." if value and len(value) > 8 else "Not set"
                print(f"  Env {key}: {masked_value}")
        print()
    
    # Check API key
    api_key = os.getenv("ACCUWEATHER_API_KEY")
    if api_key:
        print(f"✅ AccuWeather API Key: {api_key[:8]}...")
    else:
        print("❌ AccuWeather API Key: Not found")
        print("   Add ACCUWEATHER_API_KEY to config/shared/.env")
    
    print()
    print("🚀 Ready for weather queries!")

