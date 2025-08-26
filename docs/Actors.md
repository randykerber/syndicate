# Actors

> Apps, Services, and other Parties and Participants potentially interacting in and with The Syndicate ecosystem.

## Core System Actors

### Human Actor (You)
- **Role**: Primary decision maker, voice input provider, task delegator
- **Capabilities**: Voice via SuperWhisper, manual intervention when AI needs clarification
- **Interface**: Terminal, Raycast UI, voice commands

### AI Agents
- **OpenAI Agent**: Reasoning and orchestration (our syndicate-js implementation)
- **Warp AI**: System-level command execution and autonomous workflows
- **Raycast AI**: Cross-app automation and natural language processing

## Automation Platforms ⭐

### Warp Terminal
- **Status**: Pro subscription active
- **Capabilities**: System-level control, MCP integration, autonomous agent mode
- **Integration**: Native MCP support, voice commands, multi-agent workflows
- **Documentation**: [Warp Integration Details](actors/Warp.md)

### Raycast
- **Status**: Installed with multiple extensions
- **Capabilities**: Cross-app automation, 90% of target app functionality available
- **Integration**: MCP support, voice integration, extensive ecosystem
- **Documentation**: [Raycast Integration Details](actors/Raycast.md)

### Apple Shortcuts
- **Capabilities**: Voice control via Siri, iOS/macOS automation, mobile workflows
- **Integration**: URL schemes, app delegation, voice processing

## Information Management Apps

### Drafts App
- **Status**: 1,200+ notes requiring triage
- **Raycast Integration**: ✅ Full (create, search, edit, voice dictation, actions)
- **Capabilities**: Text capture, automation, JavaScript API
- **Documentation**: [Drafts Integration](actors/Drafts.md)

### Obsidian
- **Status**: 7,200+ notes across Main/Tech vaults
- **Raycast Integration**: ✅ Complete (search, create, navigate, bookmarks)
- **Capabilities**: PKM, graph relationships, plugin ecosystem
- **Documentation**: [Obsidian Integration](actors/Obsidian.md)

### Bear App
- **Status**: Personal/mobile notes storage
- **Raycast Integration**: ✅ Good (search, create, web capture, tags)
- **Capabilities**: Cross-device sync, simplified interface

## Task Management Apps

### Apple Reminders
- **Raycast Integration**: ✅ Advanced (AI parsing, location-based, natural language)
- **Capabilities**: Cross-device sync, location triggers, Siri integration

### Things
- **Raycast Integration**: ✅ AI-enhanced (natural language processing, workflow automation)
- **Capabilities**: GTD methodology, project management, scheduling

## Voice & Input Systems

### SuperWhisper
- **Status**: Universal voice-to-text input
- **Raycast Integration**: ✅ Official extension available
- **Capabilities**: Offline transcription, works across all apps

### Siri
- **Integration**: Through Apple Shortcuts, voice command delegation
- **Capabilities**: System-wide voice control, app launching

## External Services

### AI Model Providers
- **OpenAI**: GPT models, function calling, Agent SDK
- **Anthropic**: Claude models (via API keys configured)
- **Google**: Gemini models
- **Groq**: High-speed inference

### Search & Data APIs
- **Tavily**: Advanced web search (MCP server installed)
- **Brave Search**: Web search API
- **Exa**: Semantic search capabilities

### Notification Systems
- **Pushover**: Cross-platform push notifications (configured)
- **Apple Notifications**: System-level alerts and badges

## Development & Integration Tools

### MCP Servers (Installed)
- **@modelcontextprotocol/server-filesystem**: File operations
- **@modelcontextprotocol/server-sequential-thinking**: Problem solving workflows
- **tavily-mcp**: Web search integration

### Version Control
- **Git/GitHub**: Code management, issue tracking potential
- **This Repository**: syndicate-js project coordination

## Information Source Actors

### Content Platforms
- **Substack**: Newsletter subscriptions, long-form analysis content
- **YouTube**: Video content, tutorials, talks, research presentations
- **X.com (Twitter)**: Real-time news, quick updates, market sentiment
- **Podcasts**: Audio content, interviews, deep-dive discussions
- **Blog Sites**: Individual websites with periodic articles/episodes

### Additional Task Management
- **Reminders App**: System-level task tracking (covered above)
- **Things App**: Advanced GTD task management (covered above)
- **Paprida App**: [Specialized functionality - needs investigation]

### Security & Access Management
- **1Password**: Credential management, secure note storage, API access keys

### Version Control
- **Git/GitHub**: Code management, issue tracking potential
- **This Repository**: syndicate-js project coordination

## Markdown Linking Options

### Relative Path Links (Recommended)
```markdown
[Link Text](./actors/FileName.md)
[Warp Details](actors/Warp.md)
```

### Wiki-Style Links (Obsidian-compatible)
```markdown
[[FileName]]
[[Warp]]
```

### Absolute File URLs (Local only)
```markdown
[Link Text](file:///Users/rk/gh/randykerber/syndicate-js/docs/actors/Drafts.md)
```

## Status Legend
- ✅ **Fully Integrated**: Working through Raycast or direct API
- ⚠️ **Partial**: Some functionality available, gaps exist  
- 🔧 **Development Needed**: Custom integration required
- 📋 **Planned**: Identified for future integration

