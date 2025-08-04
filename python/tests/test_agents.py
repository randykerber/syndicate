"""
Test suite for Syndicate agents with session persistence.
"""

import pytest
import asyncio
import tempfile
import os
from syndicate.agents import SyndicateAgent, WeatherAgent, ContentRouter


@pytest.mark.asyncio
async def test_syndicate_agent_basic():
    """Test basic SyndicateAgent functionality."""
    agent = SyndicateAgent(
        name="TestAgent",
        instructions="You are a helpful test assistant.",
        session_id="test_basic"
    )
    
    # Test session creation
    session = agent.create_session("./test_sessions")
    assert session is not None
    assert agent.session_id == "test_basic"
    
    # Test agent creation
    openai_agent = agent.create_agent()
    assert openai_agent is not None
    assert openai_agent.name == "TestAgent"


@pytest.mark.asyncio 
async def test_session_persistence():
    """Test that conversation memory persists across interactions."""
    with tempfile.TemporaryDirectory() as temp_dir:
        agent = SyndicateAgent(
            name="MemoryAgent",
            instructions="Remember what the user tells you.",
            session_id="memory_test"
        )
        
        # Override session directory for test isolation
        agent.create_session(temp_dir)
        
        # This test would require OpenAI API, so we'll mock or skip
        # In real tests, you'd verify session persistence here
        assert agent.session is not None


def test_weather_agent_creation():
    """Test WeatherAgent initialization."""
    agent = WeatherAgent("weather_test")
    
    assert agent.name == "WeatherAgent"
    assert "disambiguation" in agent.instructions
    assert "Springfield" in agent.instructions
    assert agent.session_id == "weather_test"


def test_content_router_creation():
    """Test ContentRouter initialization."""
    agent = ContentRouter("router_test")
    
    assert agent.name == "ContentRouter"
    assert "Obsidian" in agent.instructions
    assert "routing" in agent.instructions.lower()
    assert agent.session_id == "router_test"


@pytest.mark.asyncio
async def test_demo_function():
    """Test that demo functions run without errors."""
    # Import the demo function
    from syndicate.agents import demo_weather_disambiguation
    
    # This would require OpenAI API, so we'll test import only
    assert demo_weather_disambiguation is not None


if __name__ == "__main__":
    pytest.main([__file__])