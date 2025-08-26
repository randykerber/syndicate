#!/usr/bin/env python3
"""
Wendy Enhanced Demo - GPT-5 with MCP server configurations
"""

import asyncio
import os
import sys
import httpx
sys.path.insert(0, '../src')
sys.path.insert(0, '../../config')

from agents import Agent, Runner, SQLiteSession
from agents.tool import function_tool

# Import our organized configs
try:
    from mcp_agent_configs import weather_agent_mcp_server_params
    from weather_config import weather_mcp_servers
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("⚠️  MCP config files not found - using simplified weather demo")

@function_tool
async def get_weather_alerts(state: str) -> str:
    """Get active weather alerts for a state from National Weather Service."""
    try:
        state_upper = state.upper()
        url = f"https://api.weather.gov/alerts/active/area/{state_upper}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        
        if not data.get("features"):
            return f"No active weather alerts for {state_upper} at this time."
        
        alerts = []
        for feature in data["features"][:3]:  # Limit to 3 alerts
            props = feature["properties"]
            severity = props.get("severity", "Unknown")
            event = props.get("event", "Unknown Event")
            headline = props.get("headline", "No headline")
            
            alert_text = f"🚨 {severity.upper()}: {event}\n   {headline}"
            alerts.append(alert_text)
        
        return f"Active weather alerts for {state_upper}:\n\n" + "\n\n".join(alerts)
        
    except Exception as e:
        return f"Could not get weather alerts for {state}: {str(e)}"

@function_tool
async def get_weather_forecast(latitude: float, longitude: float, location_name: str = "") -> str:
    """Get weather forecast for coordinates from National Weather Service."""
    try:
        # First get the grid point
        points_url = f"https://api.weather.gov/points/{latitude},{longitude}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            points_response = await client.get(points_url)
            points_response.raise_for_status()
            points_data = points_response.json()
            
            # Get the forecast URL
            forecast_url = points_data["properties"]["forecast"]
            
            # Get the actual forecast
            forecast_response = await client.get(forecast_url)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
        
        periods = forecast_data["properties"]["periods"][:4]  # Next 4 periods
        
        forecasts = []
        for period in periods:
            name = period["name"]
            temp = period["temperature"]
            temp_unit = period["temperatureUnit"]
            wind = period.get("windSpeed", "Unknown wind")
            detailed = period["detailedForecast"]
            
            forecast_text = f"📅 {name}: {temp}°{temp_unit}\n   Wind: {wind}\n   {detailed}"
            forecasts.append(forecast_text)
        
        location_text = f" for {location_name}" if location_name else ""
        return f"Weather forecast{location_text}:\n\n" + "\n\n".join(forecasts)
        
    except Exception as e:
        return f"Could not get weather forecast: {str(e)}"

@function_tool 
def show_available_mcp_tools() -> str:
    """Show what MCP servers and tools are configured for this agent."""
    if not CONFIG_AVAILABLE:
        return "❌ MCP configuration not available. Using basic weather tools only."
    
    try:
        weather_servers = weather_agent_mcp_server_params()
        
        info = "🔧 Available MCP Server Configurations:\n\n"
        
        for i, server in enumerate(weather_servers, 1):
            cmd = server.get('command', 'unknown')
            args = ' '.join(server.get('args', []))
            info += f"{i}. {cmd} {args}\n"
            
            if 'env' in server:
                for key in server['env'].keys():
                    info += f"   📋 Requires: {key}\n"
        
        info += "\n💡 This shows the MCP server ecosystem available for weather agents!"
        return info
        
    except Exception as e:
        return f"Error reading MCP config: {str(e)}"

@function_tool
def get_location_coordinates(location: str) -> str:
    """Get coordinates for common locations."""
    locations = {
        "denver": {"lat": 39.7392, "lon": -104.9903, "full_name": "Denver, Colorado"},
        "denver, colorado": {"lat": 39.7392, "lon": -104.9903, "full_name": "Denver, Colorado"},
        "san francisco": {"lat": 37.7749, "lon": -122.4194, "full_name": "San Francisco, California"},
        "new york": {"lat": 40.7128, "lon": -74.0060, "full_name": "New York, New York"},
        "chicago": {"lat": 41.8781, "lon": -87.6298, "full_name": "Chicago, Illinois"},
        "los angeles": {"lat": 34.0522, "lon": -118.2437, "full_name": "Los Angeles, California"},
        "miami": {"lat": 25.7617, "lon": -80.1918, "full_name": "Miami, Florida"},
        "seattle": {"lat": 47.6062, "lon": -122.3321, "full_name": "Seattle, Washington"},
        "austin": {"lat": 30.2672, "lon": -97.7431, "full_name": "Austin, Texas"},
        "boston": {"lat": 42.3601, "lon": -71.0589, "full_name": "Boston, Massachusetts"},
        "phoenix": {"lat": 33.4484, "lon": -112.0740, "full_name": "Phoenix, Arizona"},
        "portland": {"lat": 45.5152, "lon": -122.6784, "full_name": "Portland, Oregon"}
    }
    
    location_lower = location.lower().strip()
    
    if location_lower in locations:
        coords = locations[location_lower]
        return f"Found coordinates for {coords['full_name']}: {coords['lat']}, {coords['lon']}"
    
    return f"Coordinates not available for '{location}'. Try cities like Denver, San Francisco, New York, Chicago, Los Angeles, Miami, Seattle, Austin, Boston, Phoenix, or Portland."

class WendyEnhancedDemo:
    """GPT-5 Wendy with organized MCP configuration system."""
    
    def __init__(self):
        self.session = None
        self.agent = None
        
    def create_session(self):
        """Create SQLite session for conversation persistence."""
        os.makedirs("../data/sessions", exist_ok=True)
        db_path = f"../data/sessions/wendy_enhanced.db"
        self.session = SQLiteSession("wendy_enhanced", db_path=db_path)
        
    def create_agent(self):
        """Create GPT-5 Wendy agent with enhanced MCP awareness."""
        self.agent = Agent(
            name="Wendy",
            model="gpt-5",
            instructions=f"""
You are Wendy, an enhanced weather assistant powered by GPT-5 with MCP server integration! 🌤️

**Your Mission:**
- Provide real weather data from National Weather Service
- Demonstrate the organized MCP configuration system
- Show how configs support the broader Syndicate toolset vision

**Available Tools:**
1. `get_weather_forecast(lat, lon, location_name)` - Real NWS forecasts
2. `get_weather_alerts(state)` - Real NWS alerts  
3. `get_location_coordinates(location)` - Convert cities to coordinates
4. `show_available_mcp_tools()` - Show MCP server configurations

**Enhanced Features:**
- MCP Config Available: {CONFIG_AVAILABLE}
- Organized config system in /config/ directory
- Modular agent configurations for different purposes
- Foundation for rich Syndicate toolset

**Examples:**
- "Denver weather" → coordinates → forecast
- "Show me the MCP setup" → display available server configs
- "California alerts" → real weather alerts

Be conversational and showcase both weather data AND the underlying MCP infrastructure!
""",
            tools=[get_weather_forecast, get_weather_alerts, get_location_coordinates, show_available_mcp_tools]
        )
        
    async def chat(self, message: str):
        """Send message to Wendy and get response."""
        if not self.session:
            self.create_session()
        if not self.agent:
            self.create_agent()
            
        result = await Runner.run(
            self.agent,
            message,
            session=self.session,
            max_turns=6
        )
        
        response = str(result.final_output) if hasattr(result, 'final_output') else str(result)
        return response
    
    async def interactive_chat(self):
        """Run interactive chat session with enhanced features."""
        print("🌤️  WENDY ENHANCED DEMO")
        print("=" * 60)
        print("🚀 GPT-5 • Organized MCP configs • Real NWS data • Syndicate foundation")
        print("💡 Try: 'Denver weather', 'Show MCP tools', 'California alerts'")
        print("🛑 Type 'bye', 'quit', or 'exit' to end")
        print("=" * 60)
        
        if CONFIG_AVAILABLE:
            print("✅ MCP configuration system loaded")
        else:
            print("⚠️  Using simplified mode - MCP configs not found")
        print()
        
        # Initial greeting
        print("🌤️ Wendy: Hello! I'm Wendy Enhanced - your weather assistant with organized MCP server integration. I can provide real weather data AND show you the underlying Syndicate toolset architecture. What would you like to explore?")
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['bye', 'goodbye', 'quit', 'exit']:
                    print("🌤️ Wendy: Goodbye! Keep building the Syndicate! 🚀")
                    break
                    
                if user_input:
                    print("🌤️ Wendy: ", end="", flush=True)
                    response = await self.chat(user_input)
                    print(response)
                    
            except KeyboardInterrupt:
                print(f"\n\n👋 Enhanced chat ended. The MCP foundation is ready!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main entry point for enhanced Wendy demo."""
    wendy = WendyEnhancedDemo()
    await wendy.interactive_chat()

if __name__ == "__main__":
    asyncio.run(main())