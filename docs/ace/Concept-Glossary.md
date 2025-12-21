# Context Engineering - Concept Glossary

Quick reference for terminology from Google's Context Engineering whitepaper.

---

## Core Concepts

**Context Engineering**
The practice of dynamically assembling information (conversation history, memories, external knowledge) into an LLM's context window to enable intelligent agent behavior.

**Context Window**
The finite amount of text (measured in tokens) an LLM can process in a single request. Ranges from 8K to 200K+ tokens depending on model.

**Agent**
An AI system that uses an LLM to make decisions, use tools, and accomplish multi-step tasks through autonomous or semi-autonomous operation.

---

## Sessions

**Session**
A structured container for conversation state that persists across multiple turns between user and agent. Tracks the complete interaction history.

**Event**
An individual action within a session. Types include:
- User messages
- Agent responses
- Tool calls and results
- Thinking/reasoning steps
- System messages

**Turn**
A complete user-agent exchange: user message → agent processing → agent response. May include multiple events (tool calls, thinking steps).

**Session Compaction**
Techniques to reduce session size when approaching context window limits. Strategies include rolling summaries, sliding windows, and importance-based pruning.

**Rolling Summary**
Compaction strategy that summarizes older turns while keeping recent turns verbatim. Creates a concise history that grows more slowly than raw turns.

**Sliding Window**
Compaction strategy that keeps only the last N turns, dropping the oldest when new turns arrive. Simple but loses historical context.

**Multi-Agent Session**
Patterns for multiple agents sharing or splitting session state:
- **Shared Session**: All agents see full conversation history
- **Agent Handoff**: One agent's session passed to another
- **Parallel Sessions**: Multiple agents work independently, results merged

---

## Memory

**Memory (in context engineering)**
Long-term knowledge about users, their preferences, and past interactions that persists *across* conversation sessions. Distinct from session history (which is temporary).

**Memory Generation Pipeline**
Three-stage process for creating persistent memories:
1. **Extraction** - Identify important information from conversations
2. **Consolidation** - Merge, deduplicate, resolve conflicts
3. **Storage** - Persist to database or structured store

**Declarative Memory**
"Knowing what" - Facts, preferences, relationships
Examples: "User prefers Python", "Lives in Colorado", "Uses Obsidian for notes"

**Procedural Memory**
"Knowing how" - Workflows, patterns, learned behaviors
Examples: "When user says X, do Y", "User prefers concise responses"

**Memory Collection**
A grouped set of related memories (e.g., "user_preferences", "task_history", "domain_knowledge"). Enables targeted retrieval.

**Memory Provenance**
Metadata tracking when, how, and why a memory was created. Includes:
- Source (which conversation, which agent)
- Timestamp
- Trust score
- Extraction method (automatic vs manual)

**Memory Consolidation**
The process of merging redundant or conflicting memories to maintain a coherent knowledge base. Handles updates and contradictions.

---

## Retrieval

**Memory Retrieval**
The process of finding and loading relevant memories from storage into an agent's context.

**Semantic Similarity**
Retrieval method using vector embeddings to find memories conceptually related to current query. Powered by vector databases like Chroma, Pinecone, or FAISS.

**Recency Bias**
Retrieval strategy that weights newer memories higher than older ones. Useful when preferences change over time.

**Importance Scoring**
Assigning relevance scores to memories to prioritize which ones to retrieve. Can be manual (user-marked) or learned (model-based).

**Proactive Retrieval**
Loading relevant memories automatically *before* the agent runs, based on initial user message. Front-loads context assembly.

**Reactive Retrieval (Memory-as-a-Tool)**
Giving the agent a tool to search memory *on-demand* when it determines additional context is needed. Agent controls when to retrieve.

**Hybrid Retrieval**
Combination of proactive and reactive: auto-load critical memories, offer memory search tool for additional context.

---

## Memory vs RAG

**RAG (Retrieval-Augmented Generation)**
Fetching external documents or knowledge to answer factual questions. Makes agents experts on *facts*.

**Memory (User-Specific)**
Recalling user preferences, history, and context from past interactions. Makes agents experts on *users*.

**Key Distinction**
- RAG: "What's in the earnings report?" (external facts)
- Memory: "Where do I save my notes?" (user preferences)

---

## Production Considerations

**Asynchronous Memory Processing**
Running memory extraction and consolidation in background jobs rather than blocking agent responses. Improves latency.

**PII Redaction**
Removing personally identifiable information (SSNs, API keys, passwords) before storing memories. Critical for privacy.

**Memory Poisoning**
Attack where malicious users inject false memories to manipulate agent behavior. Requires validation and provenance tracking.

**Memory Drift**
Gradual degradation of memory accuracy over time through consolidation errors or evolving user preferences. Requires periodic review.

**Trust Scoring**
Assigning reliability scores to memories based on source and extraction method:
- High trust: Direct user statements, observed actions
- Medium trust: Inferred preferences
- Low trust: Third-party reports, unverified claims

---

## Multi-Agent Concepts

**Agent Handoff**
Transferring conversation control from one agent to another, along with session state. Example: triage agent → specialist agent.

**Swarm Pattern**
Multiple agents working in parallel on independent subtasks, then aggregating results.

**Hierarchical Delegation**
Manager agent coordinates multiple specialist agents, maintains overall session context.

---

## Vector Database Terms

**Embedding**
Numerical vector representation of text that captures semantic meaning. Similar texts have similar embeddings.

**Vector Database**
Specialized database optimized for storing and searching embeddings by similarity (e.g., Chroma, Pinecone, FAISS, Weaviate).

**Semantic Search**
Finding documents/memories by meaning rather than exact keyword matching. Uses embedding similarity.

**Cosine Similarity**
Mathematical measure of similarity between two vectors. Common metric for semantic search (range: -1 to 1, higher = more similar).

---

## Syndicate-Specific Mappings

| Whitepaper Term | Syndicate Implementation |
|----------------|-------------------------|
| Session | `SQLiteSession` class |
| Event | Database rows in session table |
| Turn | User message + agent response pair |
| Memory | *To be implemented* (`memory_server.py`) |
| Memory Collection | Collections in vector DB or table names |
| Proactive Retrieval | Pre-loading user preferences before agent runs |
| Reactive Retrieval | `search_memory()` tool in MCP server |
| Compaction | *To be implemented* |

---

**Last Updated**: 2025-12-20
**Source**: Google Context Engineering whitepaper (November 2025)
