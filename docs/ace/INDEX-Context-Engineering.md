# Context Engineering Document Index

**Full Document**: `/Users/rk/local/obsidian/Tech/_para/Resources/Context-Engineering_Google_2025-11.pdf`
**Source**: Google Research (November 2025)
**Authors**: Kimberly Milam, Antonio Gulli
**Pages**: 72
**Obsidian Link**: `[[Context Engineering]]` (Tech vault)

## When Agents Should Load This Document

### ✅ LOAD FULL DOCUMENT IF:
- Designing/implementing agent session management systems
- Building memory persistence for multi-turn conversations
- Implementing conversation compaction strategies
- Architecting multi-agent collaboration patterns
- Designing memory extraction → consolidation → storage pipelines
- Planning vector database schema for agent memory
- Implementing proactive vs reactive memory retrieval
- Building memory provenance and trust scoring systems
- Debugging context window overflow issues
- Evaluating RAG vs Memory tradeoffs

### ✋ USE SUMMARIES INSTEAD IF:
- Quick reference to terminology (→ use Concept-Glossary.md)
- Understanding high-level architecture (→ use Executive-Summary.md)
- Looking for specific implementation pattern (→ use Implementation-Patterns.md)
- General questions about context engineering concepts
- User asks "what is session compaction?" or similar concept questions

### 🚫 DON'T LOAD IF:
- Task unrelated to agent architecture or memory systems
- Simple tool integration questions
- MCP server configuration
- General coding tasks without agent session concerns

## Document Coverage

### Primary Topics
- **Sessions**: Event management, compaction, multi-agent patterns
- **Memory**: Long-term persistence, generation pipeline, retrieval strategies
- **Context Assembly**: Dynamic context construction for LLMs
- **Production Patterns**: Async processing, PII handling, memory poisoning prevention

### Key Technical Concepts
- Session events (turns, tool calls, thinking)
- Compaction strategies (rolling summaries, sliding windows)
- Memory types (declarative vs procedural)
- Memory organization (collections, profiles)
- Retrieval methods (semantic, recency, importance)
- Memory vs RAG distinction
- Memory-as-a-Tool pattern (reactive retrieval)
- Memory provenance tracking

### Implementation Patterns (Count: 8)
1. Session state management with event logs
2. Rolling summary compaction
3. Memory generation pipeline (extract → consolidate → store)
4. Semantic similarity retrieval (vector DB)
5. Memory-as-a-Tool (reactive on-demand access)
6. Proactive memory loading (pre-fetch relevant context)
7. Multi-agent session sharing
8. Memory consolidation (merging redundant entries)

## Related Syndicate Components

### Current Implementation
- `sessions.py` - Session persistence (partial implementation)
- `SQLiteSession` - Turn-by-turn conversation storage
- `human_interface.py` - Not memory, but related to multi-turn interaction

### Potential Enhancements
- Add memory compaction to SQLiteSession
- Implement memory extraction from completed conversations
- Create memory_server.py MCP server for semantic retrieval
- Add memory collections for user preferences, task history

## Quick Reference

**Memory vs RAG**: "RAG makes agents experts on facts; Memory makes them experts on users"

**Session vs Memory**:
- Session = Short-term, current conversation, temporary
- Memory = Long-term, across conversations, persistent

**Proactive vs Reactive Retrieval**:
- Proactive = Auto-load relevant memories before agent starts
- Reactive = Agent calls memory tool when needed (Memory-as-a-Tool)

## Document Lineage
- **Created**: 2025-12-20
- **Purpose**: Index for deciding when to load full 72-page whitepaper
- **Maintenance**: Update when Syndicate memory implementation evolves
