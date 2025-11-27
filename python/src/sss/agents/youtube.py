"""
Specialized SSS agents for handling YouTube content.

This module contains agents for the two primary YouTube use cases:
1.  Triage: Quickly assessing a video's content to decide if it's worth watching.
2.  Extraction: Pulling out valuable "nuggets" of information for persistence.
"""

from typing import Optional
from .base import SSSAgent
from ..tools.youtube_tools import get_youtube_transcript


class YouTubeTriageAgent(SSSAgent):
    """
    An agent designed to provide a quick, high-level summary of a YouTube video
    to help the user decide whether to watch it.
    """
    def __init__(self, session_id: Optional[str] = None, **kwargs):
        instructions = """
You are a YouTube Triage Specialist. Your goal is to help the user quickly
decide if a video is worth their time.

When given a YouTube URL, you will:
1.  Fetch the transcript.
2.  Identify the core argument or "bombshell" the video is teasing.
3.  Provide a concise, one-sentence summary.
4.  Provide a 1-5 star rating of its likely importance to the user.
5.  Provide a slightly longer summary verdict for an expanded view.

You know the user is generally skeptical of clickbait titles and values knowing
the key takeaway upfront.
"""
        super().__init__(
            name="YouTubeTriageAgent",
            instructions=instructions,
            session_id=session_id,
            tools=[get_youtube_transcript],
            **kwargs
        )


class YouTubeExtractionAgent(SSSAgent):
    """
    An agent designed to extract detailed, valuable "nuggets" of information
    from a YouTube video transcript for storage in a knowledge base like Obsidian.
    """
    def __init__(self, session_id: Optional[str] = None, **kwargs):
        instructions = """
You are a Knowledge Extraction Specialist. Your goal is to pull out the most
valuable, insightful, and actionable "nuggets" from a YouTube transcript.

When given a YouTube URL, you will:
1.  Fetch the transcript.
2.  Analyze the content for key investment theses, surprising statistics,
    powerful quotes, or novel concepts.
3.  Format these nuggets clearly in Markdown, ready for copy-pasting into
    Obsidian.
4.  Include relevant metadata like source links and tags.
"""
        super().__init__(
            name="YouTubeExtractionAgent",
            instructions=instructions,
            session_id=session_id,
            tools=[get_youtube_transcript],
            **kwargs
        )
