# Obsidian - Knowledge Management & PKM Hub

## Overview
Obsidian serves as the central knowledge repository and Personal Knowledge Management (PKM) system in SSS, containing 7,200+ notes across multiple vaults with sophisticated relationship mapping and content organization.

## Current Status
- **Content Volume**: 7,200+ notes across multiple vaults
- **Vault Structure**: Fin vault (financial), Tech vault
- **Raycast Integration**: ✅ Complete integration via community extensions
- **Primary Role**: "Data warehouse" for structured knowledge and long-term reference
- **Challenge**: Content discovery and cross-vault relationship management

## Vault Organization

### Fin Vault (Financial)
- **Purpose**: Investing, economics, financial analysis, market research, general knowledge
- **Content Types**: Company analysis, market trends, investment research, people, companies, concepts, decisions
- **Sources**: Financial reports, market analysis, investment newsletters, meeting notes, reference material
- **Analysis Focus**: Luke Gromen content, economic indicators, market patterns
- **Linking Strategy**: Heavy use of backlinks and graph relationships
- **Growth Pattern**: Steady accumulation of processed information from other sources

### Tech Vault  
- **Purpose**: Computing, software, technology, information science
- **Content Types**: Technical documentation, frameworks, tools, methodologies
- **Integration Points**: Development notes, tool evaluations, architecture decisions
- **Sources**: Tech articles, documentation, research papers, project notes


## Raycast Integration Details

### Available Operations (Community Extensions)
```typescript
// Content Search & Discovery
- Search Notes (by title/content across vaults)
- Search Media (images, video, audio, PDFs within vaults)
- Random Note (discovery mechanism for forgotten content)
- Bookmarked Notes (quick access to important content)

// Content Creation
- Create Note (with templates, paths, tags)
- Daily Note creation (journal/log functionality)
- Append to Daily Note (quick content addition)

// Navigation & Management
- Open Vault (switch between Fin/Tech)
- Open in new pane (multi-document workflows)
- Menu Bar integration (quick vault access)
```

### Voice Integration Workflow
```
Voice Input: "Find my notes about microservice architecture patterns"
↓
1. SuperWhisper → Text transcription
2. Raycast Obsidian Search → Tech vault search
3. Results displayed with relevance ranking
4. Selected note opens for reference/editing
```

## SSS Integration Strategy

### As Knowledge Destination
```typescript
// Content routing from other sources:
Drafts → AI Analysis → Obsidian (structured knowledge)
Web Research → Bear (temporary) → Obsidian (permanent reference)
Meeting Notes → Immediate capture → Obsidian (processed & linked)
```

### Graph-Based Relationships
- **People**: Connect meeting notes to person pages
- **Projects**: Link all project-related content across vaults
- **Concepts**: Build concept maps with cross-references
- **Timeline**: Connect events and decisions chronologically

## Content Processing Workflows

### Incoming Content Pipeline
```typescript
// Multi-source content aggregation:
1. Raw Input Sources:
   - Processed Drafts (meeting notes, thoughts)
   - Web articles (via Bear or direct capture)
   - Research findings (Tech/FIN focus areas)
   - AI analysis results (from SSS processing)

2. AI-Enhanced Processing:
   - Extract key concepts and relationships
   - Suggest vault placement (Fin/Tech)
   - Identify linking opportunities to existing notes
   - Generate appropriate tags and metadata

3. Human Review & Refinement:
   - Verify AI suggestions for accuracy
   - Add personal insights and connections
   - Establish manual cross-vault relationships
```

### Cross-Vault Content Discovery
```typescript
// Challenge: Finding related content across vault boundaries
Problems:
- Tech concepts that apply to financial analysis
- People who span multiple domains (tech + finance)
- Projects that have both technical and business components

AI Solutions:
- Semantic search across all vaults
- Relationship detection between concepts
- Automatic cross-vault linking suggestions
```

## Advanced Obsidian Capabilities

### Plugin Ecosystem Integration
- **Dataview**: Database-like queries across notes
- **Templater**: Dynamic content generation
- **Advanced Tables**: Structured data management
- **Graph Analysis**: Relationship visualization and analysis

### API & Automation Potential
- **Obsidian URI**: URL scheme for external automation
- **Plugin Development**: Custom SSS-specific functionality
- **File System Access**: Direct markdown manipulation
- **Vault Sync**: Cross-device content availability

## MCP Server Integration

### Obsidian MCP Server Integration (ACTIVE)

**Current Status**: Successfully configured with single MCP server managing both vaults.

#### Available Tools (11 total)
All tools require `vault` parameter to specify target vault ("fin" or "tech"):

```typescript
// ✅ WORKING TOOLS WITH PROPER SCHEMAS:
obsidian.create-note      // { vault, filename, content, folder? }
obsidian.search-vault     // { vault, query, path?, caseSensitive?, searchType? }
obsidian.move-note        // { vault, source, destination }
obsidian.create-directory // { vault, path, recursive? }
obsidian.delete-note      // { vault, path, permanent? }
obsidian.add-tags         // { vault, files[], tags[], location?, normalize?, position? }
obsidian.remove-tags      // { vault, files[], tags[], options? }
obsidian.rename-tag       // { vault, oldTag, newTag, createBackup?, normalize? }
obsidian.read-note        // { vault, filename, folder? }

// ✅ NO PARAMETERS (WORKS AS EXPECTED):
obsidian.list-available-vaults  // Returns: ["fin", "tech"]

// ❌ BROKEN SCHEMA (BUT LIKELY WORKS):
obsidian.edit-note        // Schema empty, but description shows vault examples
```

#### Configuration
```json
{
  "obsidian": {
    "command": "npx",
    "args": ["-y", "obsidian-mcp", "/path/to/Fin", "/path/to/Tech"]
  }
}
```

#### Usage Examples
```typescript
// Create note in Fin vault
{ "vault": "fin", "filename": "meeting-notes.md", "content": "# Meeting Notes..." }

// Search across Tech vault
{ "vault": "tech", "query": "microservices", "searchType": "both" }

// Cross-vault workflow using vault parameter
agent.call("obsidian.search-vault", { "vault": "fin", "query": "company analysis" })
agent.call("obsidian.search-vault", { "vault": "tech", "query": "architecture" })
```

### Integration with Warp AI
```bash
# Example Warp AI operations via MCP:
warp-ai "Find all Tech vault notes related to microservices and create a summary in Fin vault"
warp-ai "Analyze the relationship between Luke Gromen's inflation analysis and current tech stock trends"
warp-ai "Create a project note linking relevant content from both vaults"
```

## Content Curation Challenges

### Information Overload
- **Scale**: 7,200+ notes create discovery problems
- **Stale Content**: Outdated information mixed with current insights
- **Relationship Gaps**: Missing connections between related concepts
- **Quality Variance**: Imported content vs. refined analysis

### AI-Assisted Solutions
```typescript
// Proposed AI curation workflows:
1. Content Freshness Analysis:
   - Identify outdated technical information
   - Flag deprecated tools/frameworks
   - Suggest content updates or archival

2. Relationship Enhancement:
   - Detect implicit connections between notes
   - Suggest new backlinks and cross-references
   - Identify concept clusters for MOC (Map of Content) creation

3. Quality Assessment:
   - Rank notes by usefulness and reference frequency
   - Identify high-value content for promotion
   - Flag low-quality imports for review/deletion
```

## Cross-Vault Integration Strategies

### Unified Search & Discovery
```typescript
// Voice-driven cross-vault operations:
"Find everything about distributed systems architecture"
→ Search Tech vault for technical details
→ Search Fin vault for project applications
→ Search Fin vault for company implementations
→ Synthesize results into unified overview
```

### Concept Bridging
- **Tech ↔ Finance**: Technology companies, market analysis, investment decisions
- **Fin ↔ Tech**: Project decisions, tool selections, architecture choices, business strategy, economic impacts, market positioning

## Success Metrics & Goals

### Content Utilization
- **Discovery**: Reduce time to find relevant existing content
- **Linking**: Increase cross-referencing between related concepts
- **Quality**: Improve signal-to-noise ratio in search results
- **Freshness**: Maintain currency of technical and financial information

### Knowledge Synthesis
- **Cross-Domain Insights**: Connect concepts across vaults for novel insights
- **Decision Support**: Rapid access to relevant background for decisions
- **Research Efficiency**: Avoid duplicate research on previously explored topics

## Implementation Phases

### Phase 1: Current State Assessment
- [ ] Analyze content distribution across vaults
- [ ] Test Raycast cross-vault search capabilities
- [ ] Identify most frequently accessed content patterns

### Phase 2: AI-Enhanced Discovery
- [ ] Build Obsidian MCP server for external access
- [ ] Implement semantic search across all vaults
- [ ] Create relationship detection and suggestion system

### Phase 3: Content Curation
- [ ] AI-assisted content quality assessment
- [ ] Automated relationship enhancement
- [ ] Stale content identification and archival

### Phase 4: Advanced Integration
- [ ] Voice-driven cross-vault analysis
- [ ] Automated content synthesis and summary generation
- [ ] Predictive content suggestions based on current research patterns

## Integration Points with Other SSS Actors

### Content Flow Architecture
```
Drafts → AI Processing → Obsidian (permanent knowledge)
Web Research → Bear (staging) → Obsidian (refined reference)
Warp AI Analysis → Obsidian (technical documentation)
Meeting Notes → Obsidian (decision records + people connections)
```

### Knowledge Export & Sharing
- **Bear**: Quick mobile access to selected Obsidian content
- **Drafts**: Template generation from Obsidian structures
- **External**: Report generation and knowledge sharing workflows