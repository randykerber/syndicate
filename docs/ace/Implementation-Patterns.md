# Context Engineering - Implementation Patterns

Concrete patterns from Google's Context Engineering whitepaper with code-level guidance.

---

## Pattern 1: Session State Management with Event Logs

**Problem**: Need to track conversation history across multiple turns

**Solution**: Store each interaction as a structured event

### Structure
```python
class SessionEvent:
    event_id: str
    event_type: str  # "user_message", "agent_response", "tool_call", "thinking"
    timestamp: datetime
    content: str | dict
    metadata: dict
```

### Implementation Notes
- Store events in append-only log (database or file)
- Each turn = multiple events (user → [thinking, tool calls, ...] → agent)
- Include tokens used per event for compaction decisions
- Tag events with importance scores for later pruning

### Syndicate Status
✅ **Partially implemented** via `SQLiteSession` - needs event typing and metadata

---

## Pattern 2: Rolling Summary Compaction

**Problem**: Session exceeds context window limit

**Solution**: Summarize old turns, keep recent verbatim

### Algorithm
```
1. Calculate current session token count
2. If > threshold (e.g., 80% of context window):
   a. Identify summarization boundary (e.g., keep last 10 turns verbatim)
   b. Extract turns before boundary
   c. Generate summary of extracted turns
   d. Replace extracted turns with summary
   e. Mark summary event with "compacted_from" metadata
3. Continue with reduced session
```

### Key Decisions
- **Boundary placement**: How many recent turns to keep?
- **Summary granularity**: Per-turn vs multi-turn blocks?
- **Preservation**: Always keep system instructions, critical tool results

### Syndicate Applicability
⚠️ **Needed** - SQLiteSession can grow unbounded, will overflow context

---

## Pattern 3: Memory Generation Pipeline

**Problem**: Extract long-term knowledge from conversations

**Solution**: Three-stage pipeline (Extract → Consolidate → Store)

### Stage 1: Extraction
```python
async def extract_memories(session: Session) -> List[Memory]:
    """
    Analyze session events for memorable information:
    - User preferences stated explicitly
    - Repeated patterns (user always does X)
    - Successful workflows (task completed successfully)
    - Corrections (user says "no, I meant Y")
    """
    prompt = f"""
    Analyze this conversation and extract:
    1. User preferences (what they like/dislike)
    2. Facts about the user (location, tools, workflows)
    3. Procedural patterns (how they accomplish tasks)

    Conversation:
    {session.to_text()}
    """
    return await llm.extract_memories(prompt)
```

### Stage 2: Consolidation
```python
async def consolidate_memories(new_memories: List[Memory],
                               existing_memories: List[Memory]) -> List[Memory]:
    """
    Merge new memories with existing:
    - Deduplicate (same preference stated twice)
    - Resolve conflicts (preference changed)
    - Update trust scores (confirmed vs inferred)
    """
    conflicts = find_conflicts(new_memories, existing_memories)
    for conflict in conflicts:
        # Prefer: recent > old, explicit > inferred
        resolved = resolve_conflict(conflict)
    return merge_and_dedupe(new_memories, existing_memories, resolved)
```

### Stage 3: Storage
```python
# Option A: Simple key-value
await db.set("user.preferred_vault", "Obsidian Main")

# Option B: Vector database for semantic search
embedding = await embed(memory.content)
await vector_db.insert(
    id=memory.id,
    vector=embedding,
    metadata={
        "type": memory.type,  # "preference", "workflow", "fact"
        "created_at": memory.timestamp,
        "source_session": memory.session_id,
        "trust_score": memory.trust
    }
)
```

### Syndicate Applicability
🎯 **High priority** - This is the core of making agents "remember" across conversations

---

## Pattern 4: Semantic Similarity Retrieval (Vector DB)

**Problem**: Find relevant memories without exact keyword matching

**Solution**: Embed memories and query, search by vector similarity

### Implementation
```python
async def search_memories(query: str, top_k: int = 5) -> List[Memory]:
    """
    1. Embed the query
    2. Search vector DB for similar embeddings
    3. Re-rank by recency and importance
    """
    query_embedding = await embed(query)

    # Vector similarity search
    candidates = await vector_db.similarity_search(
        vector=query_embedding,
        limit=top_k * 2  # Get more candidates for re-ranking
    )

    # Re-rank by recency + importance
    scored = []
    for candidate in candidates:
        score = (
            0.6 * candidate.similarity +  # Semantic match
            0.3 * recency_score(candidate.created_at) +  # Recent = better
            0.1 * candidate.trust_score  # Trust
        )
        scored.append((score, candidate))

    return sorted(scored, reverse=True)[:top_k]
```

### Vector DB Options
- **Chroma**: Embedded Python, good for prototyping
- **FAISS**: Facebook's library, very fast
- **Pinecone**: Managed service
- **Weaviate**: Open source, feature-rich

### Syndicate Applicability
📅 **Future** - Start with simple key-value, upgrade later

---

## Pattern 5: Memory-as-a-Tool (Reactive Retrieval)

**Problem**: Don't know which memories to load before conversation starts

**Solution**: Give agent a tool to search memory when needed

### MCP Server Implementation
```python
# memory_server.py
from mcp.server import Server

server = Server("memory")

@server.tool()
async def search_memories(query: str, collection: str = "all") -> str:
    """
    Search agent's memory for information related to query.

    Args:
        query: What to search for
        collection: Which memory collection ("preferences", "tasks", "domain", "all")

    Returns:
        JSON array of relevant memories with trust scores
    """
    memories = await vector_db.search(query, collection)
    return json.dumps([m.to_dict() for m in memories])

@server.tool()
async def remember(content: str, memory_type: str, importance: int = 5) -> str:
    """
    Store a new memory.

    Args:
        content: What to remember
        memory_type: "preference", "fact", "workflow"
        importance: 1-10 score for future retrieval
    """
    memory = Memory(content=content, type=memory_type, importance=importance)
    await memory_db.insert(memory)
    return f"Remembered: {content}"
```

### Agent Integration
```python
# In agent's system prompt
MEMORY_TOOL_GUIDANCE = """
You have access to a memory system via tools:
- search_memories(query, collection): Find relevant past information
- remember(content, type, importance): Store new information

When to search memory:
- User mentions "my usual X" or "where I normally Y"
- Task seems similar to something done before
- Missing context that might be stored

When to remember:
- User explicitly states preference: "I prefer X"
- Successful workflow completed: "Task: X → Result: Y"
- User corrects you: "No, I meant Z" (update existing memory)
"""
```

### Syndicate Applicability
🎯 **Perfect fit** - Aligns with existing MCP tool architecture

---

## Pattern 6: Proactive Memory Loading

**Problem**: Critical memories should always be in context

**Solution**: Auto-load memories before agent starts

### Implementation
```python
async def load_agent_with_memories(user_message: str, user_id: str):
    """
    1. Quick semantic search of user's initial message
    2. Always load user's preference profile
    3. Load recent task history if relevant
    4. Inject into agent's context before first turn
    """
    # Always load user profile
    profile = await memory_db.get_user_profile(user_id)

    # Semantic search for relevant memories
    relevant = await search_memories(user_message, top_k=5)

    # Combine into agent context
    context = f"""
    User Profile:
    {profile.to_text()}

    Relevant Past Context:
    {format_memories(relevant)}

    Current User Request:
    {user_message}
    """

    return context
```

### Tradeoff: Proactive vs Reactive
- **Proactive**: Lower latency (no mid-conversation search), but may load irrelevant memories
- **Reactive**: Only load what's needed, but adds latency and tool call costs
- **Hybrid**: Load critical profile + offer memory tool

### Syndicate Applicability
✅ **Use hybrid** - Auto-load user preferences, offer memory search tool

---

## Pattern 7: Multi-Agent Session Sharing

**Problem**: Multiple agents need access to conversation context

**Solution**: Shared session with agent-specific views

### Architecture Options

**Option A: Shared Session (Full Visibility)**
```python
class SharedSession:
    events: List[Event]  # All agents see all events

    def add_event(self, event: Event, agent_id: str):
        event.metadata["agent_id"] = agent_id
        self.events.append(event)

    def get_context(self) -> str:
        """All agents see full history"""
        return format_events(self.events)
```

**Option B: Agent Handoff (Sequential)**
```python
class HandoffSession:
    events: List[Event]
    current_agent: str

    def handoff_to(self, new_agent: str, handoff_context: str):
        """Transfer control, add handoff note"""
        self.events.append(Event(
            type="agent_handoff",
            content=f"{self.current_agent} → {new_agent}: {handoff_context}"
        ))
        self.current_agent = new_agent
```

**Option C: Parallel (Swarm)**
```python
class SwarmSession:
    main_session: Session
    agent_sessions: Dict[str, Session]  # Per-agent sub-sessions

    def aggregate_results(self):
        """Merge all agent results into main session"""
        for agent_id, sub_session in self.agent_sessions.items():
            self.main_session.add_event(Event(
                type="agent_result",
                content=sub_session.result,
                metadata={"agent": agent_id}
            ))
```

### Syndicate Applicability
🤔 **Future consideration** - Currently single-agent focus

---

## Pattern 8: Memory Consolidation (Merging Redundant Entries)

**Problem**: Same preference stored multiple times, slight variations

**Solution**: Periodic consolidation job

### Algorithm
```python
async def consolidate_memory_collection(collection: str):
    """
    1. Group similar memories (vector similarity > 0.9)
    2. For each group:
       a. Identify most reliable source (highest trust score)
       b. Merge metadata (all source sessions, timestamps)
       c. Replace group with single consolidated memory
    3. Update vector DB
    """
    memories = await memory_db.get_collection(collection)

    # Find similar clusters
    clusters = cluster_by_similarity(memories, threshold=0.9)

    for cluster in clusters:
        # Pick best representative
        primary = max(cluster, key=lambda m: m.trust_score)

        # Merge provenance
        primary.metadata["consolidated_from"] = [m.id for m in cluster]
        primary.metadata["source_sessions"] = list(set(
            m.session_id for m in cluster
        ))

        # Delete duplicates, keep primary
        await memory_db.delete_many([m.id for m in cluster if m != primary])
        await memory_db.update(primary)
```

### When to Run
- Scheduled job (nightly)
- After large conversation batches
- When memory count exceeds threshold

### Syndicate Applicability
📅 **Later** - Only needed once memory accumulates

---

## Pattern Selection Guide for Syndicate

### Implement Now
1. ✅ **Memory-as-a-Tool** - Fits MCP architecture perfectly
2. ✅ **Simple key-value storage** - User preferences, vault locations
3. ✅ **Proactive profile loading** - Auto-load known preferences

### Implement Soon
4. ⚠️ **Rolling summary compaction** - Prevent session overflow
5. ⚠️ **Memory extraction** - Learn from conversations

### Implement Later
6. 📅 **Vector DB semantic search** - When simple lookup insufficient
7. 📅 **Memory consolidation** - When duplicates become problem
8. 📅 **Multi-agent patterns** - When coordinating multiple agents

---

## Sample Memory Server for Syndicate

```python
# ~/gh/randykerber/syndicate/python/servers/memory_server.py
from mcp.server import Server
import json
from pathlib import Path

server = Server("memory")

# Simple file-based storage (upgrade to DB later)
MEMORY_FILE = Path.home() / ".syndicate" / "memory.json"

@server.tool()
async def remember_preference(key: str, value: str) -> str:
    """Store a user preference"""
    memories = load_memories()
    memories["preferences"][key] = {
        "value": value,
        "updated_at": datetime.now().isoformat()
    }
    save_memories(memories)
    return f"Remembered: {key} = {value}"

@server.tool()
async def recall_preference(key: str) -> str:
    """Retrieve a user preference"""
    memories = load_memories()
    pref = memories["preferences"].get(key)
    if pref:
        return pref["value"]
    return f"No preference stored for: {key}"

@server.tool()
async def search_task_history(query: str) -> str:
    """Find similar past tasks (simple keyword match for now)"""
    memories = load_memories()
    tasks = memories.get("task_history", [])
    matches = [t for t in tasks if query.lower() in t["description"].lower()]
    return json.dumps(matches[:5])

if __name__ == "__main__":
    server.run()
```

Start simple, evolve as needed.

---

**Last Updated**: 2025-12-20
**Source**: Google Context Engineering whitepaper (November 2025)
