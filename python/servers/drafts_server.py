"""
Drafts MCP Server - SiloSlayer A-Team Integration

Provides tools and resources for interacting with Drafts notes,
enabling the A-Team to process the 1219+ note backlog and route
new information intelligently.

This server focuses on Mac-based integration via Drafts' URL schemes
and potential file system access for bulk operations.
"""

from mcp.server.fastmcp import FastMCP
import subprocess
import urllib.parse
import json
import os
from typing import List, Dict, Optional
from datetime import datetime

mcp = FastMCP("drafts_server")

@mcp.tool()
async def get_drafts_inbox_count() -> int:
    """Get the current count of unprocessed notes in Drafts inbox.
    
    Returns:
        Number of drafts in inbox
    """
    # This would integrate with Drafts URL scheme: drafts://get?uuid=count
    # For now, returning the known count from our documentation
    return 1219

@mcp.tool() 
async def get_recent_drafts(limit: int = 20) -> List[Dict]:
    """Get recent drafts from the inbox for AI-assisted triage.
    
    Args:
        limit: Maximum number of recent drafts to retrieve (default 20)
        
    Returns:
        List of draft objects with id, content, created_date, tags
    """
    # This would use Drafts URL scheme or scripting integration
    # For prototype, returning mock data structure
    recent_drafts = []
    for i in range(min(limit, 10)):
        recent_drafts.append({
            "id": f"draft-{i+1}",
            "content": f"Sample draft content {i+1} - needs categorization",
            "created_date": datetime.now().isoformat(),
            "tags": ["inbox"],
            "length": 50 + i * 10
        })
    return recent_drafts

@mcp.tool()
async def categorize_draft_content(content: str) -> Dict:
    """Analyze draft content and suggest categorization.
    
    Args:
        content: The text content of the draft
        
    Returns:
        Categorization suggestion with destination, confidence, and reasoning
    """
    # Basic keyword-based categorization logic
    content_lower = content.lower()
    
    # Financial/Investment keywords
    financial_keywords = ["stock", "invest", "portfolio", "dividend", "market", "trading", "crypto", "bitcoin", "401k", "ira"]
    
    # Technical/Development keywords  
    tech_keywords = ["code", "python", "javascript", "api", "server", "database", "deploy", "github", "programming", "debug"]
    
    # Personal keywords
    personal_keywords = ["family", "vacation", "grocery", "doctor", "appointment", "birthday", "phone number", "address"]
    
    # Ephemeral/Reference keywords
    ephemeral_keywords = ["password", "code", "pin", "confirmation", "verification", "temp", "quick note"]
    
    confidence = 0.0
    destination = "Drafts"  # Default safety net
    reasoning = "Default routing - content not clearly categorized"
    
    # Check for financial content
    financial_matches = sum(1 for keyword in financial_keywords if keyword in content_lower)
    if financial_matches >= 2:
        destination = "Obsidian Main"
        confidence = 0.8
        reasoning = f"Financial content detected ({financial_matches} keywords)"
    
    # Check for technical content  
    tech_matches = sum(1 for keyword in tech_keywords if keyword in content_lower)
    if tech_matches >= 2:
        destination = "Obsidian Tech" 
        confidence = 0.8
        reasoning = f"Technical content detected ({tech_matches} keywords)"
    
    # Check for personal content
    personal_matches = sum(1 for keyword in personal_keywords if keyword in content_lower)
    if personal_matches >= 1:
        destination = "Bear"
        confidence = 0.7
        reasoning = f"Personal content detected ({personal_matches} keywords)"
        
    # Check for ephemeral content
    ephemeral_matches = sum(1 for keyword in ephemeral_keywords if keyword in content_lower)
    if ephemeral_matches >= 1:
        destination = "1Password" if any(k in content_lower for k in ["password", "pin", "code"]) else "Digital Junk Drawer"
        confidence = 0.9
        reasoning = f"Ephemeral/reference content detected ({ephemeral_matches} keywords)"
    
    return {
        "destination": destination,
        "confidence": confidence,
        "reasoning": reasoning,
        "content_preview": content[:100] + "..." if len(content) > 100 else content
    }

@mcp.tool()
async def route_draft_to_destination(draft_id: str, destination: str, content: str, rationale: str) -> Dict:
    """Route a draft to its destination tool and remove from Drafts inbox.
    
    Args:
        draft_id: The ID of the draft to route
        destination: Target destination (Obsidian Main, Obsidian Tech, Bear, 1Password, etc.)
        content: The content to route
        rationale: AI reasoning for the routing decision
        
    Returns:
        Result of the routing operation
    """
    # This would integrate with destination APIs/URL schemes
    # Actions for Obsidian, Bear API, 1Password CLI, etc.
    
    result = {
        "draft_id": draft_id,
        "destination": destination,
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "rationale": rationale
    }
    
    # Mock implementation - in real version would call appropriate APIs
    if destination == "Obsidian Main":
        result["action"] = "Added to Obsidian Main vault via Actions for Obsidian"
    elif destination == "Obsidian Tech":
        result["action"] = "Added to Obsidian Tech vault via Actions for Obsidian"
    elif destination == "Bear":
        result["action"] = "Created new Bear note via Bear API"
    elif destination == "1Password":
        result["action"] = "Added to 1Password as secure note"
    elif destination == "Digital Junk Drawer":
        result["action"] = "Added to searchable reference storage"
    else:
        result["status"] = "kept_in_drafts"
        result["action"] = "Remained in Drafts for manual review"
    
    return result

@mcp.tool()
async def bulk_categorize_drafts(limit: int = 50) -> List[Dict]:
    """Perform bulk categorization of multiple drafts for batch processing.
    
    Args:
        limit: Maximum number of drafts to process in this batch
        
    Returns:
        List of categorization results for batch review
    """
    drafts = await get_recent_drafts(limit)
    results = []
    
    for draft in drafts:
        categorization = await categorize_draft_content(draft["content"])
        results.append({
            "draft_id": draft["id"],
            "content_preview": draft["content"][:50] + "...",
            "suggested_destination": categorization["destination"],
            "confidence": categorization["confidence"],
            "reasoning": categorization["reasoning"]
        })
    
    return results

@mcp.tool()
async def create_quick_note(content: str, destination: str = "auto") -> Dict:
    """Create a new note and route it directly, bypassing Drafts inbox.
    
    Args:
        content: The note content
        destination: Target destination or 'auto' for AI routing
        
    Returns:
        Result of the note creation and routing
    """
    if destination == "auto":
        categorization = await categorize_draft_content(content)
        destination = categorization["destination"]
        rationale = f"Auto-routed: {categorization['reasoning']}"
    else:
        rationale = f"Manual destination: {destination}"
    
    # Create temporary draft ID for routing
    temp_id = f"quick-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    result = await route_draft_to_destination(temp_id, destination, content, rationale)
    result["quick_note"] = True
    
    return result

@mcp.resource("drafts://inbox/stats")
async def read_inbox_stats() -> str:
    """Provide current Drafts inbox statistics and processing metrics."""
    total_count = await get_drafts_inbox_count()
    
    stats = {
        "total_inbox_count": total_count,
        "target_monthly_processing": 100,
        "target_daily_processing": 3,
        "success_metric": "Reduce growth rate from 50+/month to 5-10/month",
        "processing_priority": "Recent 20-50 items with AI assistance",
        "last_updated": datetime.now().isoformat()
    }
    
    return json.dumps(stats, indent=2)

@mcp.resource("drafts://categorization/rules")
async def read_categorization_rules() -> str:
    """Provide the current categorization rules and keyword mappings."""
    rules = {
        "high_confidence_routes": {
            "Obsidian Main": ["financial", "investment", "portfolio", "stock", "trading", "crypto", "dividend"],
            "Obsidian Tech": ["code", "programming", "python", "javascript", "api", "server", "deploy", "github"],
            "Bear": ["personal", "family", "phone", "address", "appointment", "grocery"],
            "1Password": ["password", "pin", "verification", "confirmation code"],
            "Digital Junk Drawer": ["reference", "url", "link", "bathroom code", "temp info"]
        },
        "medium_confidence_processing": "Present 2-3 options with reasoning",
        "low_confidence_fallback": "Default to Drafts safety net",
        "confidence_thresholds": {
            "auto_route": 0.8,
            "suggest_options": 0.5,
            "safety_net": 0.0
        }
    }
    
    return json.dumps(rules, indent=2)

if __name__ == "__main__":
    mcp.run(transport='stdio')