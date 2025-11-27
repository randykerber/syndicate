#!/usr/bin/env python3
"""
Runs the YouTube Triage Agent on a given video ID.

This script orchestrates the process of reading a pre-fetched transcript,
invoking the YouTubeTriageAgent to generate a summary, and printing the result.
"""
import sys
import os
import yaml
from pathlib import Path

# Add the src directory to the Python path to allow importing sss
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from sss.agents.youtube import YouTubeTriageAgent

def load_config():
    """Loads the SSS configuration from the YAML file."""
    config_path = Path(__file__).parent.parent / "config" / "sss" / "config.yaml"
    with open(config_path, 'r') as f:
        # Replace environment variables
        content = os.path.expandvars(f.read())
        return yaml.safe_load(content)

def main():
    """Main function to run the triage agent."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_youtube_triage.py <youtube_video_id>", file=sys.stderr)
        sys.exit(1)

    video_id = sys.argv[1]
    config = load_config()

    # 1. Construct path to the transcript in the "Bronze" layer
    transcripts_dir = Path(config['youtube']['transcripts_dir'])
    transcript_path = transcripts_dir / f"{video_id}.txt"

    if not transcript_path.exists():
        print(f"Error: Transcript file not found at {transcript_path}", file=sys.stderr)
        print("Please run get_yt_transcript.py first.", file=sys.stderr)
        sys.exit(1)

    # 2. Read the transcript content
    print(f"Reading transcript from: {transcript_path}")
    transcript_content = transcript_path.read_text()

    # 3. Instantiate the YouTubeTriageAgent
    print("Initializing YouTubeTriageAgent...")
    agent = YouTubeTriageAgent(session_id=f"triage_{video_id}")

    # 4. Create the prompt for the agent
    prompt = f"""
Please analyze the following YouTube video transcript and provide a triage summary.
Focus on identifying the core argument or "bombshell" and assessing its novelty.

Transcript:
---
{transcript_content}
---
"""

    # 5. Run the agent and get the response
    print("Agent is processing the transcript...")
    # Using chat_sync for a simpler script, can be async if needed
    summary = agent.chat_sync(prompt)

    # 6. Print the result
    print("\n--- Agent Triage Summary ---")
    print(summary)
    print("--------------------------\n")

if __name__ == "__main__":
    main()
