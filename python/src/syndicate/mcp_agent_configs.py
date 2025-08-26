import os
from dotenv import load_dotenv

load_dotenv(override=True)

brave_env = {"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY")}

# Base MCP server configurations for different agent types

def base_mcp_server_params():
    """Core MCP servers available to all agents."""
    return [
        {"command": "uv", "args": ["run", "python/servers/push_server.py"]},
        {"command": "uv", "args": ["run", "python/servers/human_input_server.py"]}
    ]

def weather_agent_mcp_server_params():
    """MCP servers for weather agents with human disambiguation."""
    return base_mcp_server_params() + [
        {"command": "npx", "args": ["-y", "@timlukahorstmann/mcp-weather"], "env": {"ACCUWEATHER_API_KEY": os.getenv("ACCUWEATHER_API_KEY")}}
    ]

def content_router_mcp_server_params():
    """MCP servers for content routing and SiloSlayer operations."""
    return base_mcp_server_params() + [
        {"command": "uv", "args": ["run", "python/servers/drafts_server.py"]},
        {"command": "uvx", "args": ["mcp-server-fetch"]},
        {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-brave-search"], "env": brave_env}
    ]

def trading_agent_mcp_server_params():
    """MCP servers for trading and investment agents."""
    return base_mcp_server_params() + [
        {"command": "uv", "args": ["run", "python/servers/accounts_server.py"]},
        {"command": "uv", "args": ["run", "python/servers/market_server.py"]}
    ]

def researcher_mcp_server_params(name: str):
    """MCP servers for research agents with memory."""
    return base_mcp_server_params() + [
        {"command": "uvx", "args": ["mcp-server-fetch"]},
        {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-brave-search"], "env": brave_env},
        {"command": "npx", "args": ["-y", "mcp-memory-libsql"], "env": {"LIBSQL_URL": f"file:./memory/{name}.db"}}
    ]

def siloslayer_mcp_server_params(name: str):
    """MCP servers for SiloSlayer agents with full toolkit."""
    return base_mcp_server_params() + [
        {"command": "uv", "args": ["run", "python/servers/drafts_server.py"]},
        {"command": "uvx", "args": ["mcp-server-fetch"]},
        {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-brave-search"], "env": brave_env},
        {"command": "npx", "args": ["-y", "mcp-memory-libsql"], "env": {"LIBSQL_URL": f"file:./memory/{name}.db"}}
    ]

# Tool inventory by category
PUBLISHED_MCP_SERVERS = [
    "mcp-server-fetch",  # Web content fetching
    "@modelcontextprotocol/server-brave-search",  # Search capabilities
    "mcp-memory-libsql",  # Memory/database storage
    "@timlukahorstmann/mcp-weather"  # Weather data
]

LOCAL_MCP_SERVERS = [
    "human_input_server.py",  # Human-in-the-loop disambiguation
    "push_server.py",  # Push notifications
    "drafts_server.py",  # Drafts processing (SiloSlayer)
    "accounts_server.py",  # Trading account management
    "market_server.py"  # Market data simulation
]