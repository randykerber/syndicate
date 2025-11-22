# MCP Configuration Notes

## Types of Tools
1. **Built-in Tools**
   - Native to LLMs like ChatGPT or Claude
   - Integrated within the model itself

2. **Custom Functions**
   - Defined in your application
   - Must be specified in configuration

## Configuration Requirements
- Custom functions need to be listed in **mcp-config.json**
- Python implementation may use annotations
- Tools must be specified to both:
  - The LLM
  - The agent definition

## MCP Servers Types
1. **Local Servers**
   - Run on your machine
   - **Your responsibility** to launch them
   - Examples: servers launched via NPM, NPX, or UV
   - LLM will not trigger their launch

2. **Cloud Servers**
   - Located on the internet
   - Externally managed

## Important Note
- Agent definition may differ from MCP definition
- Ensure all local servers are running before attempting to use them

## Current Configuration
See `mcp-config.json` for the actual server definitions:
- **filesystem**: File operations server
- **sequential-thinking**: Problem-solving workflows
- **tavily-search**: Web search capabilities