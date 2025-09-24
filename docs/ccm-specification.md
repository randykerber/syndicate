# Content Consumption Management (CCM) System Specification

**Goal**: Maximize knowledge output while minimizing time input through intelligent content triage.

## The Problem

Daily content flood of 300+ potential items across multiple sources with unclear value/time ratios. Current approach wastes significant time consuming low-value content while potentially missing high-value insights.

**Critical Gap**: No episode-level quality assessment exists. Even excellent podcasts have many worthless episodes or episodes where only segments are valuable. Current discovery relies on show-level subscriptions rather than episode-level curation.

## Core Principle

**Maximum Output / Minimum Input** where:
- **First Brain**: Understanding → Meat-ware brain (consumed, internalized, not catalogued)
- **Second Brain**: Actionable knowledge → Obsidian (catalogued, linked, searchable)
- **Input Optimization**: AI-powered pre-filtering to eliminate noise, surface value

## Content Sources (8 Primary Types)

1. **Podcasts** - 300+ subscriptions across Snipd (188 investing/tech) + Apple Podcasts (115 general)
2. **YouTube** - Video content, often overlaps with podcast versions
3. **Substack Articles** - Newsletter/long-form content, often with RSS feeds
4. **Individual Articles** - Blog posts, news articles, one-off URLs
5. **Twitter/X** - Saved threads and posts
6. **Email Newsletters** - Delivered content requiring processing
7. **PDFs** - Downloaded research, reports, papers
8. **Books** - Physical/digital books requiring highlight extraction

## Processing Architecture

### Stage 1: Universal Ingestion
- **RSS Feeds**: Podcasts, YouTube channels, blogs, Substack
- **Direct URLs**: Individual articles, PDFs
- **Manual Input**: Books, email forwards, Twitter saves

### Stage 2: Content Normalization
- **Text Extraction**: Transcripts (Whisper API), article parsing, PDF text
- **Metadata Capture**: Title, author, length, source, publication date
- **Topic Identification**: AI-powered tagging and categorization

### Stage 3: AI Triage
- **Summarization**: Key insights, main arguments, actionable points
- **Relevance Scoring**: Match against personal interests/goals
- **Time Investment Analysis**: Value vs. consumption time
- **Recommendation**: Consume fully / Extract highlights / Skip entirely

### Stage 4: Output Routing
- **High-Value Content**: Full consumption → First Brain + notes → Second Brain
- **Medium-Value Content**: AI summary + highlights → Second Brain
- **Low-Value Content**: Archive with summary for future reference
- **No-Value Content**: Discard entirely

## Technical Implementation

**Separated Workflow Design**:
- **Filtering System**: RSS processing + AI analysis + triage decisions
- **Consumption System**: Route to preferred apps (podcast players, browsers, readers)
- **Bridge Technology**: Universal identifiers (RSS URLs + GUIDs) enable cross-platform content tracking

**Key Technologies**:
- RSS/OPML for subscription management
- Whisper API for audio transcription
- AI summarization for all text content
- Universal content schema for processing pipeline

## Success Metrics

1. **Time Reduction**: 80% reduction in content consumption time
2. **Value Retention**: Maintain or increase insights to First Brain + Second Brain
3. **Workflow Efficiency**: Single triage interface for all content types
4. **Knowledge Integration**: Seamless addition to Second Brain (Obsidian)

## Current Status

- **Architecture Designed**: Separated filtering/consumption workflow
- **Data Available**: 300+ podcast subscriptions exported via OPML
- **Standards Research**: RSS, OPML, cross-platform compatibility confirmed
- **Next Steps**: Prototype development, AI integration, workflow testing

**Decision Point**: Snipd renewal ($84/year) vs. migration to Fountain/Pocket Casts by September 27, 2025.

---

*This system aligns with Syndicate's "information liberation" mission - breaking free from app silos while leveraging AI for intelligent content curation.*