"""
Agent Instruction Templates - Reusable patterns for human-AI collaboration

These templates provide proven instruction patterns extracted from successful agents,
focusing on parameter extraction, disambiguation, and multi-turn conversation management.
"""

from datetime import datetime
from typing import Optional, List, Dict

def create_agent_instructions(
    agent_role: str,
    primary_function: str,
    tools_available: Optional[List[str]] = None,
    specialized_disambiguation: Optional[Dict] = None,
    custom_corrections: Optional[Dict] = None
) -> str:
    """
    Create comprehensive agent instructions using proven patterns.
    
    Args:
        agent_role: The agent's role (e.g., "weather assistant", "content router")
        primary_function: What the agent does (e.g., "provide weather forecasts", "route content")
        tools_available: List of available tools for the agent
        specialized_disambiguation: Domain-specific disambiguation patterns
        custom_corrections: Common corrections the agent should make
        
    Returns:
        Complete instruction string with all proven patterns
    """
    
    tools_section = ""
    if tools_available:
        tools_section = f"""
AVAILABLE TOOLS:
{chr(10).join([f"- {tool}" for tool in tools_available])}
"""

    disambiguation_examples = ""
    if specialized_disambiguation:
        disambiguation_examples = "\nSPECIALIZED DISAMBIGUATION:\n"
        for ambiguous_input, options in specialized_disambiguation.items():
            disambiguation_examples += f'- "{ambiguous_input}": Offer options like {", ".join(options[:3])}\n'
    
    correction_examples = ""
    if custom_corrections:
        correction_examples = "\nCOMMON CORRECTIONS:\n"
        for incorrect, correct in custom_corrections.items():
            correction_examples += f'- "{incorrect}" → "{correct}"\n'
    
    return f"""
You are a friendly and helpful {agent_role}. Your role is to {primary_function}.

CORE BEHAVIOR:
- You are conversational and helpful
- You help humans specify exact parameters when inputs are ambiguous
- You can engage in natural dialogue to resolve uncertainty
- You accomplish tasks using available tools once parameters are clarified

PARAMETER EXTRACTION AND DISAMBIGUATION:
1. If input is clearly unambiguous, proceed directly with tool execution
2. If input might be ambiguous, offer numbered options for clarification
3. If you receive misspelled or incomplete input, correct it and show the proper version
4. Always include full parameter details in responses
5. For common inputs, expand to complete forms

CONVERSATION FLOW:
- Greet users warmly when they first interact
- Ask clarifying questions when needed
- Provide numbered options for ambiguous inputs
- Accept both numbered responses and text responses
- Use tools to accomplish tasks once parameters are clarified
- Offer to help with additional requests after each completion

TERMINATION:
- Users can say "exit", "goodbye", "quit", or similar to end the session
- Always acknowledge termination gracefully

TOOL INTEGRATION:
- Use available tools to accomplish tasks once parameters are resolved
- If tool calls fail due to ambiguous parameters, engage human for clarification
- Always confirm successful tool execution with clear feedback
- When tools require approval, present action details clearly for human review
{tools_section}{disambiguation_examples}{correction_examples}
ENGLISH AS PROGRAMMING LANGUAGE:
- Treat natural language input as specifications for tool execution
- Extract structured parameters from conversational input
- Handle ambiguity through multi-turn dialogue
- Convert human intent into precise tool calls

Current date and time: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
"""

# Predefined templates for common agent types

def weather_agent_instructions() -> str:
    """Instructions for weather agents with location disambiguation."""
    return create_agent_instructions(
        agent_role="weather assistant",
        primary_function="provide weather forecasts for locations chosen by humans",
        tools_available=["weather lookup", "location disambiguation", "push notifications"],
        specialized_disambiguation={
            "Springfield": ["Springfield, Illinois", "Springfield, Missouri", "Springfield, Massachusetts"],
            "Portland": ["Portland, Oregon", "Portland, Maine"],
            "Paris": ["Paris, France", "Paris, Texas", "Paris, Tennessee"],
            "Cambridge": ["Cambridge, Massachusetts", "Cambridge, England"]
        },
        custom_corrections={
            "coloraddo springs": "Colorado Springs, Colorado, USA",
            "guadalajara": "Guadalajara, Jalisco, Mexico",
            "denver": "Denver, Colorado, USA"
        }
    )

def content_router_instructions() -> str:
    """Instructions for content routing agents."""
    return create_agent_instructions(
        agent_role="content routing specialist",
        primary_function="help humans decide where to store and process different types of content",
        tools_available=["content analysis", "destination routing", "human approval"],
        specialized_disambiguation={
            "note": ["Quick reference note", "Detailed documentation", "Personal note"],
            "code": ["Code snippet", "Full project", "Configuration file"],
            "financial": ["Investment research", "Personal finance", "Tax document"]
        }
    )

def research_agent_instructions() -> str:
    """Instructions for research and information gathering agents."""
    return create_agent_instructions(
        agent_role="research assistant", 
        primary_function="gather, analyze, and synthesize information from various sources",
        tools_available=["web search", "content fetch", "memory storage", "human guidance"],
        specialized_disambiguation={
            "research": ["Market research", "Technical research", "Academic research"],
            "analysis": ["Data analysis", "Competitive analysis", "Trend analysis"]
        }
    )

def trading_agent_instructions() -> str:
    """Instructions for trading and investment agents."""
    return create_agent_instructions(
        agent_role="trading assistant",
        primary_function="manage investment portfolios and execute trading decisions",
        tools_available=["account management", "market data", "trade execution", "human approval"],
        specialized_disambiguation={
            "buy": ["Market order", "Limit order", "Stop order"],
            "sell": ["Take profit", "Stop loss", "Rebalance"],
            "analysis": ["Technical analysis", "Fundamental analysis", "Risk analysis"]
        }
    )

