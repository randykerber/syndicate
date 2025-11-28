#!/usr/bin/env python3
"""
Runs the YouTube Triage Agent on a given video ID.

This script orchestrates the process of reading a pre-fetched transcript,
invoking the YouTubeTriageAgent to generate a structured JSON summary,
and saving that summary to the 'prod' (Silver) data layer.
"""
import sys
import os
import json
from pathlib import Path

# Add the src directory to the Python path to allow importing sss and shared
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from sss.agents.youtube import YouTubeTriageAgent
from shared.config import load_config

def main():
    """Main function to run the triage agent."""
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/run_youtube_triage.py <youtube_video_id>", file=sys.stderr)
        sys.exit(1)

    video_id = sys.argv[1]
    
    # Load the SSS config
    config_path = Path(__file__).parent.parent / "config" / "sss" / "config.yaml"
    config = load_config(config_path)

    # --- Bronze Layer: Read Raw Data ---
    transcripts_dir = Path(config['youtube']['transcripts_dir'])
    transcript_path = transcripts_dir / f"{video_id}.txt"

    if not transcript_path.exists():
        print(f"Error: Transcript file not found at {transcript_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Reading transcript from: {transcript_path}")
    transcript_content = transcript_path.read_text()

    # --- Agent Processing ---
    print("Initializing YouTubeTriageAgent...")
    agent = YouTubeTriageAgent(session_id=f"triage_{video_id}")

    prompt = f"""
Please analyze the following YouTube video transcript and return a valid JSON object
as per your instructions.

Transcript:
---
{transcript_content}
---
"""

    print("Agent is processing the transcript...")
    agent_output_str = agent.chat_sync(prompt)

    # --- Silver Layer: Save Processed Data ---
    print("Parsing agent output...")
    try:
        # Clean the string in case the agent wraps it in markdown
        if agent_output_str.startswith("```json"):
            agent_output_str = agent_output_str[7:-4].strip()
        summary_data = json.loads(agent_output_str)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON from agent output.", file=sys.stderr)
        print(f"Raw output was:\n{agent_output_str}", file=sys.stderr)
        sys.exit(1)

    # Construct path to the output in the "Silver" layer
    triage_summaries_dir = Path(config['youtube']['triage_summaries_dir'])
    triage_summaries_dir.mkdir(parents=True, exist_ok=True) # Ensure dir exists
    output_path = triage_summaries_dir / f"{video_id}.json"

    print(f"Saving structured summary to: {output_path}")
    with open(output_path, 'w') as f:
        json.dump(summary_data, f, indent=2)

    print("\n--- Triage Complete ---")
    print(f"Summary for {video_id} saved successfully.")
    print("-----------------------\n")

if __name__ == "__main__":
    main()
