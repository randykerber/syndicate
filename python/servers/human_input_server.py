"""
Human Input MCP Server for SiloSlayer Syndicate

Provides tools for human-in-the-loop decision making and disambiguation.
This server uses an async file-based queue system for non-blocking human input.
"""

from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Optional
from datetime import datetime
import json
from sss.human_interface import ask_human_choice, ask_human_approval, ask_human_text

mcp = FastMCP("human_input_server")

@mcp.tool()
async def disambiguate_location(query: str, possible_matches: List[str]) -> str:
    """Ask human to clarify ambiguous location for weather queries.
    
    Args:
        query: The original location query that was ambiguous
        possible_matches: List of possible location matches to choose from
        
    Returns:
        The clarified location string selected by human
    """
    
    # Add custom option
    options = possible_matches + ["Enter a different location"]
    
    question = f"Which '{query}' did you mean?"
    
    response = await ask_human_choice(
        agent_name="WeatherAgent",
        question=question,
        options=options,
        timeout=300
    )
    
    if response == "Enter a different location":
        # Ask for custom location
        custom_response = await ask_human_text(
            agent_name="WeatherAgent", 
            question=f"Please enter the correct location for '{query}':",
            timeout=300
        )
        return custom_response or query
    
    return response or query

@mcp.tool()
async def get_human_approval(action: str, details: str, risk_level: str = "medium") -> bool:
    """Request human approval for an action.
    
    Args:
        action: Description of the action to be performed
        details: Additional details about the action
        risk_level: Risk level (low, medium, high)
        
    Returns:
        True if human approves, False if rejected
    """
    
    return await ask_human_approval(
        agent_name="Agent",
        action=action,
        details=details,
        risk_level=risk_level,
        timeout=300
    )

@mcp.tool()
async def get_human_choice(question: str, options: List[str]) -> str:
    """Present multiple choice question to human.
    
    Args:
        question: The question to ask the human
        options: List of options to choose from
        
    Returns:
        The selected option
    """
    
    response = await ask_human_choice(
        agent_name="Agent",
        question=question,
        options=options,
        timeout=300
    )
    
    return response or (options[0] if options else "")

@mcp.tool()
async def log_human_interaction(interaction_type: str, details: Dict) -> str:
    """Log human interactions for analysis and learning.
    
    Args:
        interaction_type: Type of interaction (disambiguation, approval, choice)
        details: Details about the interaction
        
    Returns:
        Confirmation message
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": interaction_type,
        "details": details
    }
    
    # In a real system, this would write to a database or log file
    print(f"📝 Logged interaction: {interaction_type}")
    return f"Interaction logged: {interaction_type} at {log_entry['timestamp']}"

@mcp.resource("human-input://interaction-log")
async def read_interaction_log() -> str:
    """Provide access to human interaction history."""
    
    # Mock interaction log for now
    sample_log = {
        "recent_interactions": [
            {
                "timestamp": "2025-07-31T14:30:00",
                "type": "location_disambiguation",
                "query": "Springfield",
                "selected": "Springfield, Illinois"
            }
        ],
        "patterns": {
            "common_ambiguous_locations": ["Springfield", "Portland", "Paris"],
            "user_preferences": {
                "default_country": "United States",
                "preferred_Springfield": "Springfield, Illinois"
            }
        }
    }
    
    return json.dumps(sample_log, indent=2)

if __name__ == "__main__":
    mcp.run(transport='stdio')