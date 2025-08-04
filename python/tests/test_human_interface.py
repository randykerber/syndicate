"""
Test suite for human interface and async communication.
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from syndicate.human_interface import HumanQueue, HumanRequest, HumanResponse
from syndicate.human_interface import ask_human_choice, ask_human_approval, ask_human_text


def test_human_request_creation():
    """Test HumanRequest dataclass creation."""
    request = HumanRequest(
        request_id="test-123",
        agent_name="TestAgent", 
        request_type="choice",
        question="Test question?",
        options=["Option A", "Option B"]
    )
    
    assert request.request_id == "test-123"
    assert request.agent_name == "TestAgent"
    assert len(request.options) == 2
    assert request.created_at is not None


def test_human_response_creation():
    """Test HumanResponse dataclass creation."""
    response = HumanResponse(
        request_id="test-123",
        response="Option A",
        response_method="cli"
    )
    
    assert response.request_id == "test-123"
    assert response.response == "Option A"
    assert response.responded_at is not None


@pytest.mark.asyncio
async def test_human_queue_creation():
    """Test HumanQueue initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        queue = HumanQueue(temp_dir)
        
        assert queue.queue_dir.exists()
        assert queue.requests_dir.exists()
        assert queue.responses_dir.exists()
        assert queue.archive_dir.exists()


@pytest.mark.asyncio
async def test_request_creation():
    """Test creating a human request."""
    with tempfile.TemporaryDirectory() as temp_dir:
        queue = HumanQueue(temp_dir)
        
        request_id = await queue.create_request(
            agent_name="TestAgent",
            request_type="choice",
            question="Test question?",
            options=["A", "B", "C"],
            send_notification=False  # Skip notification in tests
        )
        
        assert request_id is not None
        assert "TestAgent-choice" in request_id
        
        # Check files were created
        request_file = queue.requests_dir / f"{request_id}.json"
        summary_file = queue.requests_dir / f"{request_id}-summary.txt"
        
        assert request_file.exists()
        assert summary_file.exists()
        
        # Check file contents
        with open(request_file) as f:
            data = json.load(f)
        
        assert data["agent_name"] == "TestAgent"
        assert data["question"] == "Test question?"
        assert len(data["options"]) == 3


@pytest.mark.asyncio
async def test_response_handling():
    """Test responding to a request."""
    with tempfile.TemporaryDirectory() as temp_dir:
        queue = HumanQueue(temp_dir)
        
        # Create request
        request_id = await queue.create_request(
            agent_name="TestAgent",
            request_type="choice", 
            question="Pick one:",
            options=["Alpha", "Beta"],
            send_notification=False
        )
        
        # Create response
        queue.respond(request_id, "Alpha", "test")
        
        # Check response file exists
        response_file = queue.responses_dir / f"{request_id}-response.json"
        assert response_file.exists()
        
        with open(response_file) as f:
            data = json.load(f)
        
        assert data["response"] == "Alpha"
        assert data["method"] == "test"


def test_request_id_generation():
    """Test request ID generation."""
    request_id = HumanQueue.generate_request_id("TestAgent", "choice")
    
    assert "TestAgent-choice" in request_id
    assert len(request_id.split("-")) >= 4  # agent-type-timestamp-uuid


@pytest.mark.asyncio
async def test_list_pending_requests():
    """Test listing pending requests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        queue = HumanQueue(temp_dir)
        
        # Create a request
        await queue.create_request(
            agent_name="TestAgent",
            request_type="choice",
            question="Test?",
            options=["Yes", "No"],
            timeout_seconds=3600,  # Long timeout so it doesn't expire
            send_notification=False
        )
        
        # List pending
        pending = queue.list_pending_requests()
        assert len(pending) == 1
        assert pending[0]["agent_name"] == "TestAgent"


if __name__ == "__main__":
    pytest.main([__file__])