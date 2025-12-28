"""
Drafts MCP Server - Full CRUD Operations for Drafts App

Provides MCP tools for complete CRUD operations on Drafts notes via AppleScript.

SETUP REQUIRED (One-time):
    1. Open Drafts app
    2. Create new Action: "Delete Draft by UUID"
    3. Add Script step with JavaScript: Draft.delete(draft.uuid);
    4. Save action

After setup, all CRUD operations work via MCP tools.
"""

from mcp.server.fastmcp import FastMCP
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from syndicate.drafts_crud_operations import DraftsConnection, DraftsConfig, DraftsError
from typing import List, Dict, Optional
import json

# Initialize MCP server
mcp = FastMCP("drafts")

# Initialize Drafts connection (shared across all tool calls)
_drafts_config = DraftsConfig(verbose=False)
_drafts = DraftsConnection(_drafts_config)


# ========== CREATE ==========

@mcp.tool()
async def create_draft(content: str, tags: Optional[List[str]] = None) -> str:
    """
    Create a new draft in Drafts app.

    Args:
        content: Text content for the draft
        tags: Optional list of tags (e.g., ["work", "important"])

    Returns:
        UUID of the created draft

    Example:
        create_draft("Meeting notes from today", tags=["work", "2025"])
    """
    try:
        uuid = _drafts.create_draft(content, tags)
        return json.dumps({
            "status": "success",
            "uuid": uuid,
            "message": f"Draft created with UUID: {uuid}"
        })
    except DraftsError as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        })


# ========== READ ==========

@mcp.tool()
async def get_draft(uuid: str) -> str:
    """
    Get content and metadata of a specific draft.

    Args:
        uuid: Draft UUID

    Returns:
        JSON with draft content and tags

    Example:
        get_draft("ABC-123-DEF-456")
    """
    try:
        content = _drafts.get_draft_content(uuid)
        tags = _drafts.get_draft_tags(uuid)
        title = content.split('\n')[0] if content else ''

        return json.dumps({
            "status": "success",
            "uuid": uuid,
            "content": content,
            "title": title,
            "tags": tags
        }, indent=2)
    except DraftsError as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        })


@mcp.tool()
async def list_drafts(limit: int = 20) -> str:
    """
    List recent drafts.

    Args:
        limit: Maximum number of drafts to return (default 20)

    Returns:
        JSON array of drafts with uuid, title, content preview

    Example:
        list_drafts(10)  # Get 10 most recent drafts
    """
    try:
        drafts = _drafts.list_drafts(limit=limit)

        # Add content preview to each draft
        for draft in drafts:
            preview_length = 100
            draft['preview'] = (
                draft['content'][:preview_length] + "..."
                if len(draft['content']) > preview_length
                else draft['content']
            )

        return json.dumps({
            "status": "success",
            "count": len(drafts),
            "drafts": drafts
        }, indent=2)
    except DraftsError as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        })


@mcp.tool()
async def search_drafts(query: str) -> str:
    """
    Search drafts by content.

    Args:
        query: Search query string

    Returns:
        JSON array of matching drafts

    Example:
        search_drafts("project update")
    """
    try:
        results = _drafts.search_drafts(query)

        return json.dumps({
            "status": "success",
            "query": query,
            "count": len(results),
            "results": results
        }, indent=2)
    except DraftsError as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        })


@mcp.tool()
async def count_drafts() -> str:
    """
    Get total count of drafts in Drafts app.

    Returns:
        JSON with draft count

    Example:
        count_drafts()
    """
    try:
        count = _drafts.count_drafts()
        return json.dumps({
            "status": "success",
            "total_drafts": count
        })
    except DraftsError as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        })


# ========== UPDATE ==========

@mcp.tool()
async def update_draft(uuid: str, content: str) -> str:
    """
    Update the content of an existing draft.

    Args:
        uuid: Draft UUID
        content: New content to replace existing content

    Returns:
        JSON status message

    Example:
        update_draft("ABC-123", "Updated content here")
    """
    try:
        _drafts.update_draft_content(uuid, content)
        return json.dumps({
            "status": "success",
            "uuid": uuid,
            "message": "Draft updated successfully"
        })
    except DraftsError as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        })


@mcp.tool()
async def add_tag_to_draft(uuid: str, tag: str) -> str:
    """
    Add a tag to an existing draft.

    Args:
        uuid: Draft UUID
        tag: Tag to add

    Returns:
        JSON status message

    Example:
        add_tag_to_draft("ABC-123", "processed")
    """
    try:
        _drafts.add_tag(uuid, tag)
        return json.dumps({
            "status": "success",
            "uuid": uuid,
            "tag": tag,
            "message": f"Tag '{tag}' added to draft"
        })
    except DraftsError as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        })


# ========== DELETE ==========

@mcp.tool()
async def delete_draft(uuid: str) -> str:
    """
    Delete a draft by UUID.

    REQUIRES one-time Drafts Action setup:
        1. Open Drafts app
        2. Create Action: "Delete Draft by UUID"
        3. Add Script step: Draft.delete(draft.uuid);
        4. Save

    Args:
        uuid: Draft UUID to delete

    Returns:
        JSON status message

    Example:
        delete_draft("ABC-123-DEF")
    """
    try:
        _drafts.delete_draft(uuid)
        return json.dumps({
            "status": "success",
            "uuid": uuid,
            "message": "Draft deleted successfully"
        })
    except DraftsError as e:
        return json.dumps({
            "status": "error",
            "error": str(e),
            "help": "If error mentions missing action, create 'Delete Draft by UUID' action in Drafts app first"
        })


# ========== HELPER UTILITIES ==========

@mcp.tool()
async def get_first_draft() -> str:
    """
    Get the first (most recent) draft.

    Returns:
        JSON with draft UUID, content, and tags

    Example:
        get_first_draft()  # Get most recent draft for quick testing
    """
    try:
        uuid = _drafts.get_first_uuid()
        if not uuid:
            return json.dumps({
                "status": "success",
                "message": "No drafts found",
                "uuid": None
            })

        content = _drafts.get_draft_content(uuid)
        tags = _drafts.get_draft_tags(uuid)

        return json.dumps({
            "status": "success",
            "uuid": uuid,
            "content": content,
            "title": content.split('\n')[0] if content else '',
            "tags": tags
        }, indent=2)
    except DraftsError as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        })


@mcp.tool()
async def find_draft_by_title(title: str) -> str:
    """
    Find draft UUID by title (first line of content).

    Args:
        title: Title to search for (case-sensitive)

    Returns:
        JSON with UUID if found, or null if not found

    Example:
        find_draft_by_title("Meeting Notes")
    """
    try:
        uuid = _drafts.get_uuid_by_title(title)
        if uuid:
            return json.dumps({
                "status": "success",
                "title": title,
                "uuid": uuid
            })
        else:
            return json.dumps({
                "status": "success",
                "title": title,
                "uuid": None,
                "message": "No draft found with that title"
            })
    except DraftsError as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        })


# ========== RESOURCES ==========

@mcp.resource("drafts://connection/info")
async def connection_info() -> str:
    """Provide information about Drafts connection and setup status."""
    try:
        count = _drafts.count_drafts()
        first_uuid = _drafts.get_first_uuid()

        info = {
            "status": "connected",
            "total_drafts": count,
            "connection_working": True,
            "delete_action_name": _drafts.config.delete_action_name,
            "delete_setup_required": "Create 'Delete Draft by UUID' action in Drafts app",
            "first_draft_uuid": first_uuid,
            "verbose_logging": _drafts.config.verbose
        }
        return json.dumps(info, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e),
            "message": "Cannot connect to Drafts app"
        }, indent=2)


@mcp.resource("drafts://setup/instructions")
async def setup_instructions() -> str:
    """Provide setup instructions for delete capability."""
    instructions = {
        "title": "Drafts Delete Action Setup (One-Time)",
        "steps": [
            "1. Open Drafts app on your Mac",
            "2. Click '+' to create new Action",
            "3. Name it: 'Delete Draft by UUID'",
            "4. Add Action Step → Script",
            "5. Enter JavaScript: Draft.delete(draft.uuid);",
            "6. Save the action",
            "7. Test with: delete_draft(some_uuid)"
        ],
        "why_needed": "AppleScript cannot delete drafts directly - requires JavaScript API via Drafts Action",
        "test_command": "delete_draft('test-uuid-here')",
        "verification": "After setup, delete_draft() will work from Python/MCP"
    }
    return json.dumps(instructions, indent=2)


if __name__ == "__main__":
    mcp.run(transport='stdio')
