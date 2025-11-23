"""
Human Interface - Async human-AI communication system

Provides file-based request/response queue for human-in-the-loop AI agents.
Supports push notifications and multiple response channels (mobile, desktop, voice).
"""

import json
import asyncio
import time
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import uuid


@dataclass
class HumanRequest:
    """Represents a request for human input."""
    request_id: str
    agent_name: str
    request_type: str  # "disambiguation", "approval", "choice", "text_input"
    question: str
    options: List[str] = None
    details: Dict[str, Any] = None
    created_at: str = None
    timeout_seconds: int = 300  # 5 minutes default
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.options is None:
            self.options = []
        if self.details is None:
            self.details = {}


@dataclass 
class HumanResponse:
    """Represents a human response to a request."""
    request_id: str
    response: str
    response_method: str  # "file", "mobile", "voice", "desktop"
    responded_at: str = None
    
    def __post_init__(self):
        if self.responded_at is None:
            self.responded_at = datetime.now().isoformat()


class HumanQueue:
    """Manages async human input requests and responses."""
    
    def __init__(self, queue_dir: str = "./data/human_queue"):
        """Initialize with custom queue directory."""
        self.queue_dir = Path(queue_dir)
        self.requests_dir = self.queue_dir / "requests"
        self.responses_dir = self.queue_dir / "responses"
        self.archive_dir = self.queue_dir / "archive"
        
        # Ensure directories exist
        for dir_path in [self.requests_dir, self.responses_dir, self.archive_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def generate_request_id(agent_name: str, request_type: str) -> str:
        """Generate unique request ID."""
        timestamp = int(time.time())
        short_uuid = str(uuid.uuid4())[:8]
        return f"{agent_name}-{request_type}-{timestamp}-{short_uuid}"
    
    async def create_request(
        self,
        agent_name: str,
        request_type: str,
        question: str,
        options: List[str] = None,
        details: Dict[str, Any] = None,
        timeout_seconds: int = 300,
        send_notification: bool = True
    ) -> str:
        """Create a new human input request."""
        
        request_id = self.generate_request_id(agent_name, request_type)
        
        request = HumanRequest(
            request_id=request_id,
            agent_name=agent_name,
            request_type=request_type,
            question=question,
            options=options or [],
            details=details or {},
            timeout_seconds=timeout_seconds
        )
        
        # Write request file
        request_file = self.requests_dir / f"{request_id}.json"
        with open(request_file, 'w') as f:
            json.dump(asdict(request), f, indent=2)
        
        # Create human-readable summary
        summary_file = self.requests_dir / f"{request_id}-summary.txt"
        summary = self._create_request_summary(request)
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        print(f"📝 Created human request: {request_id}")
        
        # Send push notification if enabled
        if send_notification:
            await self._send_notification(request)
        
        return request_id
    
    def _create_request_summary(self, request: HumanRequest) -> str:
        """Create human-readable request summary."""
        summary = f"""🤖 SYNDICATE AGENT REQUEST #{request.request_id}
{'='*60}
Agent: {request.agent_name}
Type: {request.request_type}
Created: {request.created_at}
Timeout: {request.timeout_seconds} seconds

QUESTION:
{request.question}
"""
        
        if request.options:
            summary += f"\nOPTIONS:\n"
            for i, option in enumerate(request.options, 1):
                summary += f"  {i}. {option}\n"
        
        if request.details:
            summary += f"\nDETAILS:\n"
            for key, value in request.details.items():
                summary += f"  {key}: {value}\n"
        
        summary += f"""
{'='*60}
TO RESPOND:
1. Create file: responses/{request.request_id}-response.txt
2. Content: Your answer (option number or text)
3. Or use: python -c "from sss import HumanQueue; HumanQueue().respond('{request.request_id}', 'your answer')"

EXAMPLES:
- Option selection: "1" or "Paris, France"  
- Approval: "yes" or "no"
- Text input: "Any text response"
"""
        return summary
    
    async def _send_notification(self, request: HumanRequest):
        """Send push notification about the request."""
        try:
            import requests
            
            # Load push credentials
            pushover_user = os.getenv("PUSHOVER_USER")
            pushover_token = os.getenv("PUSHOVER_TOKEN")
            pushover_url = "https://api.pushover.net/1/messages.json"
            
            if not pushover_user or not pushover_token:
                print(f"⚠️  Pushover credentials not configured, skipping notification")
                return
            
            # Create notification message
            title = f"🤖 {request.agent_name} Needs Input"
            message = f"{request.question[:100]}..."
            if request.options:
                message += f"\n\n{len(request.options)} options available"
            message += f"\n\nRequest ID: {request.request_id}"
            
            payload = {
                "user": pushover_user,
                "token": pushover_token,
                "title": title,
                "message": message,
                "priority": 1  # High priority
            }
            
            response = requests.post(pushover_url, data=payload)
            if response.status_code == 200:
                print(f"📱 Push notification sent for {request.request_id}")
            else:
                print(f"⚠️  Push notification failed: {response.status_code}")
            
        except Exception as e:
            print(f"⚠️  Failed to send notification: {e}")
    
    async def wait_for_response(
        self,
        request_id: str, 
        poll_interval: float = 2.0,
        timeout_override: Optional[int] = None
    ) -> Optional[str]:
        """Wait for human response to a request."""
        
        # Load request to get timeout
        request_file = self.requests_dir / f"{request_id}.json"
        if not request_file.exists():
            raise ValueError(f"Request {request_id} not found")
        
        with open(request_file) as f:
            request_data = json.load(f)
        
        timeout = timeout_override or request_data.get('timeout_seconds', 300)
        start_time = time.time()
        
        print(f"⏳ Waiting for human response to {request_id} (timeout: {timeout}s)")
        
        while time.time() - start_time < timeout:
            # Check for response file
            response_file = self.responses_dir / f"{request_id}-response.txt"
            json_response_file = self.responses_dir / f"{request_id}-response.json"
            
            if response_file.exists():
                response_text = response_file.read_text().strip()
                print(f"✅ Got human response: {response_text}")
                
                # Create response record and archive
                response = HumanResponse(
                    request_id=request_id,
                    response=response_text,
                    response_method="file"
                )
                await self._archive_interaction(request_data, response)
                return response_text
                
            elif json_response_file.exists():
                with open(json_response_file) as f:
                    response_data = json.load(f)
                
                response_text = response_data.get('response', '')
                print(f"✅ Got human response: {response_text}")
                
                response = HumanResponse(
                    request_id=request_id,
                    response=response_text,
                    response_method=response_data.get('method', 'file')
                )
                await self._archive_interaction(request_data, response)
                return response_text
            
            await asyncio.sleep(poll_interval)
        
        print(f"⏰ Timeout waiting for response to {request_id}")
        return None
    
    async def _archive_interaction(self, request_data: dict, response: HumanResponse):
        """Archive completed interaction."""
        request_id = request_data['request_id']
        
        # Create archive record
        archive_record = {
            'request': request_data,
            'response': asdict(response),
            'archived_at': datetime.now().isoformat()
        }
        
        archive_file = self.archive_dir / f"{request_id}.json"
        with open(archive_file, 'w') as f:
            json.dump(archive_record, f, indent=2)
        
        # Clean up active files
        for file_pattern in [f"{request_id}*"]:
            for active_dir in [self.requests_dir, self.responses_dir]:
                for file_path in active_dir.glob(file_pattern):
                    file_path.unlink(missing_ok=True)
        
        print(f"📦 Archived interaction: {request_id}")
    
    def respond(self, request_id: str, response: str, method: str = "cli"):
        """Programmatic way to respond to a request."""
        response_file = self.responses_dir / f"{request_id}-response.json"
        
        response_data = {
            'response': response,
            'method': method,
            'responded_at': datetime.now().isoformat()
        }
        
        with open(response_file, 'w') as f:
            json.dump(response_data, f, indent=2)
        
        print(f"✅ Response recorded for {request_id}: {response}")
    
    def list_pending_requests(self) -> List[Dict]:
        """List all pending requests."""
        pending = []
        
        for request_file in self.requests_dir.glob("*-summary.txt"):
            request_id = request_file.stem.replace("-summary", "")
            json_file = self.requests_dir / f"{request_id}.json"
            
            if json_file.exists():
                with open(json_file) as f:
                    request_data = json.load(f)
                
                # Check if not expired
                created_at = datetime.fromisoformat(request_data['created_at'])
                timeout = timedelta(seconds=request_data.get('timeout_seconds', 300))
                
                if datetime.now() < created_at + timeout:
                    pending.append(request_data)
        
        return pending


# Convenience functions for common request types
async def ask_human_choice(
    agent_name: str,
    question: str, 
    options: List[str],
    timeout: int = 300,
    queue_dir: str = "./data/human_queue"
) -> Optional[str]:
    """Ask human to choose from options."""
    queue = HumanQueue(queue_dir)
    request_id = await queue.create_request(
        agent_name=agent_name,
        request_type="choice",
        question=question,
        options=options,
        timeout_seconds=timeout
    )
    
    response = await queue.wait_for_response(request_id)
    
    # Try to parse numeric response
    if response and response.isdigit():
        choice_num = int(response)
        if 1 <= choice_num <= len(options):
            return options[choice_num - 1]
    
    return response


async def ask_human_approval(
    agent_name: str,
    action: str,
    details: str = "",
    risk_level: str = "medium",
    timeout: int = 300,
    queue_dir: str = "./data/human_queue"
) -> bool:
    """Ask human for approval."""
    queue = HumanQueue(queue_dir)
    question = f"Approve this action: {action}"
    if details:
        question += f"\nDetails: {details}"
    
    request_id = await queue.create_request(
        agent_name=agent_name,
        request_type="approval", 
        question=question,
        options=["Yes", "No"],
        details={"risk_level": risk_level},
        timeout_seconds=timeout
    )
    
    response = await queue.wait_for_response(request_id)
    
    if response:
        return response.lower() in ['yes', 'y', '1', 'approve', 'ok']
    
    return False


async def ask_human_text(
    agent_name: str,
    question: str,
    timeout: int = 300,
    queue_dir: str = "./data/human_queue"
) -> Optional[str]:
    """Ask human for text input."""
    queue = HumanQueue(queue_dir)
    request_id = await queue.create_request(
        agent_name=agent_name,
        request_type="text_input",
        question=question,
        timeout_seconds=timeout
    )
    
    return await queue.wait_for_response(request_id)

