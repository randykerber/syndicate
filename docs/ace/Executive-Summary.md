# Context Engineering: Sessions, Memory - Executive Summary

**Source**: Google Research Whitepaper (November 2025)
**Authors**: Kimberly Milam, Antonio Gulli
**Full Document**: `/Users/rk/local/obsidian/Tech/_para/Resources/Context-Engineering_Google_2025-11.pdf`

## What is Context Engineering?

Context engineering is the **dynamic assembly of information** into an LLM's context window to enable intelligent agent behavior. It's the practice of selecting, organizing, and managing what information an agent "sees" when processing a request.

### Three Core Components

1. **Conversation History** - Recent turns between user and agent
2. **Memories** - Long-term knowledge about the user, extracted and persisted
3. **External Knowledge** - Retrieved information (RAG, tool results, database queries)

## Sessions: Managing Conversations

### The Problem
- Context windows have finite size (8K-200K+ tokens)
- Conversations grow unbounded over time
- Agents need recent context + relevant history

### The Solution: Session Management

**Session** = Structured container for conversation state across multiple turns

**Key Concepts**:
- **Events**: Individual actions (user message, agent response, tool call, thinking)
- **Compaction**: Strategies to reduce session size when approaching limits
- **Multi-agent patterns**: How multiple agents share or split session state

### Compaction Strategies

1. **Rolling Summaries** - Summarize old turns, keep recent verbatim
2. **Sliding Window** - Keep last N turns, drop oldest
3. **Importance Scoring** - Retain critical turns, summarize/drop low-importance
4. **Hybrid** - Combine multiple strategies

## Memory: Long-Term Persistence

### Memory vs Sessions

| Aspect | Session | Memory |
|--------|---------|--------|
| Lifespan | Current conversation | Across conversations |
| Storage | Temporary (hours/days) | Persistent (weeks/months/years) |
| Purpose | Maintain coherence in current chat | Personalization, learning over time |
| Size | Limited by context window | Unbounded, stored externally |

### Memory Generation Pipeline

```
1. Extraction   - Identify important information from conversations
2. Consolidation - Merge, deduplicate, resolve conflicts
3. Storage      - Persist to vector DB or structured store
```

### Types of Memory

**Declarative Memory** ("knowing what"):
- User preferences: "Likes dark mode", "Prefers Python over JavaScript"
- Facts: "Lives in Colorado", "Works on Syndicate project"
- Relationships: "Uses Obsidian for notes", "Pushover for mobile alerts"

**Procedural Memory** ("knowing how"):
- Workflows: "When user says 'investment note', create in Obsidian Main/Investing/"
- Patterns: "User prefers concise responses, dislikes verbose explanations"
- Routines: "Daily market data fetch at 9:30 AM ET"

### Memory Organization

1. **Collections** - Group memories by type (preferences, tasks, domain knowledge)
2. **Structured Profiles** - Schema-based storage (user profile, task history)
3. **Graph-based** - Entities and relationships
4. **Temporal** - Time-ordered event logs

### Memory Retrieval

**Three Key Factors**:
1. **Semantic Similarity** - Vector search for relevant memories
2. **Recency** - Newer memories weighted higher
3. **Importance** - Explicit scoring or learned relevance

**Retrieval Patterns**:
- **Proactive** - Auto-load memories before agent runs
- **Reactive (Memory-as-a-Tool)** - Agent decides when to search memory
- **Hybrid** - Load critical memories, offer tool for additional searches

## Memory vs RAG

**RAG (Retrieval-Augmented Generation)**:
- Purpose: Make agents experts on *facts* (documents, knowledge bases)
- Example: "What's in the Q3 earnings report?"
- Data: External documents, databases, knowledge repositories

**Memory**:
- Purpose: Make agents experts on *users* (preferences, history, context)
- Example: "Where do I usually save investment notes?"
- Data: User interactions, preferences, past workflows

**Use Together**: RAG for factual knowledge + Memory for personalization

## Production Considerations

### Asynchronous Processing
- Memory extraction should not block agent responses
- Background jobs for consolidation and storage
- Eventual consistency acceptable for memory updates

### Privacy and Safety
- **PII Redaction** - Strip sensitive data before storing (SSNs, API keys, passwords)
- **Memory Poisoning** - Validate memories, prevent injection attacks
- **Provenance Tracking** - Record when/how/why memories were created
- **User Control** - Allow viewing, editing, deleting memories

### Trust and Reliability
- Score memory reliability (direct observation > inferred > user-reported)
- Handle contradictions (prefer recent, higher-reliability memories)
- Graceful degradation when memory unavailable

## Key Insights for Implementation

1. **Start Simple** - Key-value preferences before vector search
2. **Separation of Concerns** - Session management ≠ memory management
3. **User Transparency** - Show what's remembered, allow corrections
4. **Incremental Enhancement** - Add memory to working agents, don't rebuild from scratch
5. **Tools Over Auto-loading** - Let agents decide when to search memory (Memory-as-a-Tool)

## Relevance to Syndicate Project

### Current State
- ✅ Session persistence via SQLiteSession
- ✅ Multi-turn conversations
- ⚠️ No memory system (sessions not persisted across new conversations)
- ⚠️ No compaction (sessions could overflow context)

### Recommended Additions
1. **Short-term**: Add session compaction (rolling summaries)
2. **Medium-term**: Implement memory extraction for user preferences
3. **Long-term**: Vector DB for semantic memory search

### Immediate Win
Create `memory_server.py` MCP server with:
- `remember_preference(key, value)` - Store user preference
- `recall_preference(key)` - Retrieve preference
- `search_task_history(query)` - Find similar past workflows

This gives Syndicate agents Memory-as-a-Tool without complex vector search infrastructure.

---

**For Deeper Details**: See `Concept-Glossary.md` and `Implementation-Patterns.md`
