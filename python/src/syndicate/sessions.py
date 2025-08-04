"""
Sessions - SQLiteSession management and conversation persistence

Utilities for managing persistent conversation sessions in Syndicate agents.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional
from agents import SQLiteSession


class SessionManager:
    """Manages SQLite sessions for Syndicate agents."""
    
    def __init__(self, sessions_dir: str = "./syndicate_sessions"):
        """
        Initialize session manager.
        
        Args:
            sessions_dir: Directory to store session databases
        """
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def create_session(self, session_id: str) -> SQLiteSession:
        """
        Create a new SQLite session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            SQLiteSession instance
        """
        db_path = self.sessions_dir / f"{session_id}.db"
        session = SQLiteSession(session_id, db_path=str(db_path))
        print(f"🗄️  Session created: {session_id} → {db_path}")
        return session
    
    def get_session(self, session_id: str) -> SQLiteSession:
        """
        Get existing session or create new one.
        
        Args:
            session_id: Session identifier
            
        Returns:
            SQLiteSession instance
        """
        return self.create_session(session_id)
    
    def list_sessions(self) -> list[str]:
        """List all existing session IDs."""
        session_files = list(self.sessions_dir.glob("*.db"))
        return [f.stem for f in session_files]
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and its database file.
        
        Args:
            session_id: Session to delete
            
        Returns:
            True if deleted, False if not found
        """
        db_path = self.sessions_dir / f"{session_id}.db"
        if db_path.exists():
            db_path.unlink()
            print(f"🗑️  Session deleted: {session_id}")
            return True
        return False
    
    def get_session_info(self, session_id: str) -> dict:
        """
        Get information about a session.
        
        Args:
            session_id: Session to inspect
            
        Returns:
            Dictionary with session metadata
        """
        db_path = self.sessions_dir / f"{session_id}.db"
        
        if not db_path.exists():
            return {"exists": False}
        
        stat = db_path.stat()
        return {
            "exists": True,
            "session_id": session_id,
            "db_path": str(db_path),
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "size_bytes": stat.st_size
        }


def create_session(session_id: str, sessions_dir: str = "./syndicate_sessions") -> SQLiteSession:
    """
    Convenience function to create a SQLite session.
    
    Args:
        session_id: Unique session identifier
        sessions_dir: Directory to store session databases
        
    Returns:
        SQLiteSession instance
    """
    manager = SessionManager(sessions_dir)
    return manager.create_session(session_id)


def generate_session_id(prefix: str = "syndicate") -> str:
    """
    Generate a unique session ID.
    
    Args:
        prefix: Prefix for the session ID
        
    Returns:
        Unique session identifier
    """
    timestamp = int(datetime.now().timestamp())
    return f"{prefix}_{timestamp}"


# Utility functions for common session patterns
def create_user_session(user_id: str) -> SQLiteSession:
    """Create session for a specific user."""
    session_id = f"user_{user_id}_{int(datetime.now().timestamp())}"
    return create_session(session_id)


def create_agent_session(agent_name: str, user_id: Optional[str] = None) -> SQLiteSession:
    """Create session for a specific agent and optional user."""
    if user_id:
        session_id = f"{agent_name.lower()}_{user_id}_{int(datetime.now().timestamp())}"
    else:
        session_id = f"{agent_name.lower()}_{int(datetime.now().timestamp())}"
    return create_session(session_id)


if __name__ == "__main__":
    # Demo session management
    print("🗄️  Session Management Demo")
    print("=" * 30)
    
    manager = SessionManager()
    
    # Create a test session
    session = manager.create_session("demo_session")
    
    # List sessions
    sessions = manager.list_sessions()
    print(f"Sessions: {sessions}")
    
    # Get session info
    info = manager.get_session_info("demo_session")
    print(f"Session info: {info}")
    
    # Clean up
    manager.delete_session("demo_session")