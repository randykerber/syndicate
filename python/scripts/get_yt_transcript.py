#!/usr/bin/env python3
"""
A utility script to fetch the transcript for a given YouTube video URL.
"""
import sys
import os

# Add the src directory to the Python path to allow importing sss
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the plain, undecorated function
from sss.youtube_tools import fetch_youtube_transcript

def main():
    """
    Main function to handle command-line arguments and print the transcript.
    """
    if len(sys.argv) < 2:
        print("Usage: python python/scripts/get_yt_transcript.py <youtube_url>", file=sys.stderr)
        sys.exit(1)
    
    video_url = sys.argv[1]
    # Call the plain function directly
    transcript = fetch_youtube_transcript(video_url)
    
    if "Error" in transcript:
        print(transcript, file=sys.stderr)
        sys.exit(1)
        
    print(transcript)

if __name__ == "__main__":
    main()
