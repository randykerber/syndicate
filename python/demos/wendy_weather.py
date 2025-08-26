#!/usr/bin/env python3
"""
Wendy Real Weather Demo - GPT-5 with actual National Weather Service data
"""

import asyncio
import os
import sys
import httpx
sys.path.insert(0, '../src')

from agents import Agent, Runner, SQLiteSession
from agents.tool import function_tool

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

@function_tool
def get_state_code(location: str) -> str:
    """Get state code for weather alerts."""
    state_mapping = {
        "california": "CA", "ca": "CA", "san francisco": "CA", "los angeles": "CA",
        "colorado": "CO", "co": "CO", "denver": "CO",
        "new york": "NY", "ny": "NY",
        "florida": "FL", "fl": "FL", "miami": "FL",
        "texas": "TX", "tx": "TX", "austin": "TX",
        "illinois": "IL", "il": "IL", "chicago": "IL",
        "washington": "WA", "wa": "WA", "seattle": "WA",
        "massachusetts": "MA", "ma": "MA", "boston": "MA",
        "arizona": "AZ", "az": "AZ", "phoenix": "AZ",
        "oregon": "OR", "or": "OR", "portland": "OR"
    }
    
    location_lower = location.lower().strip()
    
    for key, code in state_mapping.items():
        if key in location_lower or location_lower in key:
            return f"State code for {location}: {code}"
    
    return f"State code not available for '{location}'"

class WendyRealWeatherDemo:
    """GPT-5 Wendy with real National Weather Service data."""
    
    def __init__(self):
        self.session = None
        self.agent = None
        
    def create_session(self):
        """Create SQLite session for conversation persistence."""
        os.makedirs("../data/sessions", exist_ok=True)
        db_path = f"../data/sessions/wendy_real_weather.db"
        self.session = SQLiteSession("wendy_real_weather", db_path=db_path)
        
    def create_agent(self):
        """Create GPT-5 Wendy agent with real weather tools."""
        self.agent = Agent(
            name="Wendy",
            model="gpt-5",
            instructions="""
You are Wendy, a weather assistant powered by GPT-5 with REAL National Weather Service data! 🌤️

**Your Real Weather Tools:**
1. `get_weather_alerts(state)` - Active weather alerts from NWS
2. `get_weather_forecast(lat, lon, location_name)` - Detailed forecasts from NWS
3. `get_location_coordinates(location)` - Convert city names to coordinates
4. `get_state_code(location)` - Get state codes for alerts

**Smart Workflow:**
- For forecasts: get_location_coordinates() → get_weather_forecast()
- For alerts: get_state_code() → get_weather_alerts()
- Be conversational and explain you're using real NWS data

**Examples:**
- "Denver weather" → coordinates → forecast with real NWS data
- "California alerts" → get_weather_alerts("CA") 
- "Any storms in Florida?" → get_weather_alerts("FL")

Showcase GPT-5's improved tool chaining and natural conversation!
""",
            tools=[get_weather_alerts, get_weather_forecast, get_location_coordinates, get_state_code]
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
        """Run interactive chat session with real weather data."""
        print("🌤️  WENDY REAL WEATHER DEMO")
        print("=" * 55)
        print("🚀 GPT-5 • Real National Weather Service data • Live API calls")
        print("💡 Try: 'Denver forecast', 'California alerts', 'Miami weather'")
        print("🛑 Type 'bye', 'quit', or 'exit' to end")
        print("=" * 55)
        
        # Initial greeting
        print("\n🌤️ Wendy: Hello! I'm Wendy, powered by GPT-5 with direct access to the National Weather Service. I can get you real weather forecasts and alerts. What would you like to know?")
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['bye', 'goodbye', 'quit', 'exit']:
                    print("🌤️ Wendy: Goodbye! Stay weather-aware! 🌈")
                    break
                    
                if user_input:
                    print("🌤️ Wendy: ", end="", flush=True)
                    response = await self.chat(user_input)
                    print(response)
                    
            except KeyboardInterrupt:
                print(f"\n\n👋 Weather chat ended. Stay safe!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main entry point for real weather demo."""
    wendy = WendyRealWeatherDemo()
    await wendy.interactive_chat()

if __name__ == "__main__":
    asyncio.run(main())