# SSS (Silo-Slayer Syndicate) - High-Level Overview

**Last Updated:** 2025-01-10

---

## The Problem

**Information is trapped in isolated tools, creating friction at both ends:**

**INPUT:** "I don't want to decide which app to put this in - just capture it."
- New idea, reminder, note, article highlight → deciding where to store it creates friction
- Friction → capture failure → information lost

**OUTPUT:** "I don't want to remember where I put it - just find it."
- Information scattered across 15+ silos: Drafts (1200+ notes), Obsidian vaults, Bear, email, browser tabs, podcasts, AI chats, project repos
- Finding something = manually searching each silo one-by-one
- "I remember something about Springfield economics... where did I put it?"

**The Vicious Cycle:**
> Can't find things → Must carefully decide where to put them → Input friction → Capture failure → Information lost

**Result:** Information backlog grows ~50+ items/month

---

## The Vision

**Break the input/output friction. Stop information loss.**

SSS is a system of AI agents that:
- **Capture:** Accept information via any method (text, voice, multiple entry points) without deciding destination upfront
- **Route:** Use AI to understand intent and route to appropriate destination
- **Retrieve:** Universal search across all silos - don't need to remember location

**Not a Single Monolithic Solution:**
- Simple problems → simple solutions (Raycast shortcuts, better tool usage)
- Complex routing/disambiguation → AI agents
- Whatever removes friction

---

## Key Principles

### 1. AI-First, Flexible Pipelines
- Natural language understanding enables what wasn't possible 2-3 years ago
- No brittle API-driven workflows
- Handles fuzzy matches, understands intent

### 2. Graceful Degradation, Not Brittleness
- **Human-in-the-loop** for disambiguation when needed
- "Ask user for clarification" > "throw exception and crash"
- AI agents collaborate with humans, don't replace them

### 3. "English as Programming Language"
- Natural input → AI extracts parameters → routes/executes
- Example: "Remind me Thursday about Springfield report" → AI creates reminder, files note, tags appropriately

### 4. Tool Agnostic
- No lock-in to specific capture point (Drafts, voice notes, quick capture)
- No lock-in to specific storage (Obsidian, Bear, project docs)
- Use best tool for each job; let AI bridge the gaps

### 5. Optimize Later
- Get it working with AI agents first
- Replace with optimized code only when patterns are proven and stable

---

## Architecture (High-Level)

```
┌─────────────────────┐
│   CAPTURE POINTS    │
│  (text, voice,      │
│   multiple tools)   │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│    AI AGENTS        │
│  - Analyze intent   │
│  - Extract params   │
│  - Route decision   │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  HUMAN IN THE LOOP  │
│  (disambiguation,   │
│   confirmation)     │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│   DESTINATIONS      │
│ - Obsidian (2nd     │
│   brain)            │
│ - Reminders         │
│ - Calendar          │
│ - Email             │
│ - Project repos     │
└─────────────────────┘
```

**Media Content Flow:**
- Consume (podcasts, YouTube, newsletters)
- Extract highlights → into capture system
- Same AI routing applies

---

## Success Metric

**Reduce information backlog growth from 50+/month to 5-10/month**

---

## Current Status

SSS is in **early exploration phase**:
- Base infrastructure exists (MCP servers, session persistence, human-in-the-loop patterns)
- Individual tool integrations being explored (Drafts, Obsidian, others)
- Full routing pipeline not yet implemented
- This is the **overriding quest** behind technical work in this project

---

## For AI Assistants

When the user asks about:
- Drafts, Obsidian, or other tool integrations → this is likely SSS-related
- Content routing, tagging, or organization → SSS context
- "Universal capture" or "second brain" → SSS goals

**Design principles to follow:**
- Prefer flexible AI solutions over rigid code
- Build for graceful failure (ask user, don't crash)
- Don't lock into single tools
- Natural language interfaces where possible
