"""
Tools for interacting with YouTube.
"""
from youtube_transcript_api import YouTubeTranscriptApi
from agents.tool import function_tool

def fetch_youtube_transcript(video_url: str) -> str:
    """
    Fetches the transcript for a given YouTube video URL.
    This is a plain, reusable function.

    Args:
        video_url: The URL of the YouTube video.

    Returns:
        The transcript of the video as a single string, or an error message.
    """
    try:
        # Extract video ID from URL
        if "v=" in video_url:
            video_id = video_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in video_url:
            video_id = video_url.split("youtu.be/")[1].split("?")[0]
        else:
            return "Error: Could not parse YouTube video ID from URL."

        # Create API instance and fetch transcript
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id)
        # Extract text from FetchedTranscriptSnippet objects
        transcript = " ".join([item.text for item in transcript_list])
        return transcript
    except Exception as e:
        return f"Error fetching transcript: {e}"

@function_tool
def get_youtube_transcript(video_url: str) -> str:
    """
    An agent-facing tool that wraps the core transcript-fetching logic.
    The decorator makes it usable by the agent framework.
    """
    return fetch_youtube_transcript(video_url)
