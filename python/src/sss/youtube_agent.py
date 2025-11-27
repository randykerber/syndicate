"""
YouTube Agent for summarizing video transcripts.
"""
from typing import Optional
from sss.agents import SSSAgent
from sss.youtube_tools import get_youtube_transcript

class YouTubeAgent(SSSAgent):
    """
    An agent that summarizes YouTube video transcripts.
    """
    def __init__(self, session_id: Optional[str] = None):
        instructions = """
You are a helpful assistant that summarizes YouTube videos.
When given a YouTube URL, you will fetch the transcript and provide a concise summary.
Your summary should capture the main points and key takeaways of the video.
"""
        super().__init__(
            name="YouTubeAgent",
            instructions=instructions,
            session_id=session_id,
            tools=[get_youtube_transcript]
        )
