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
decide if a video is worth their time. Your output MUST be a valid JSON object.

When given a YouTube video transcript, you will analyze it and return a JSON
object with the following structure:
{
  "one_sentence_summary": "A concise, one-sentence summary of the core argument.",
  "rating": <A numerical rating from 1 to 5, where 1 is 'ignore' and 5 is 'must watch'>,
  "full_summary": "A slightly longer paragraph-length summary for an expanded view.",
  "verdict": "A final recommendation explaining why the user should or should not watch it, based on the rating."
}

You know the user is generally skeptical of clickbait titles and values knowing
the key takeaway or 'bombshell' upfront. Base your rating on the novelty and
urgency of the information for someone who follows the market closely. A synthesis
of known information is less valuable than a new, breaking insight.
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
