from pathlib import Path

# Define base path
base_path = Path.home() / "gh" / "randykerber" / "hedgeye-kb" / "conf"

# File names and contents for configuration
files = {
    ".env": """\
# Environment variables used in the Hedgeye KB pipeline

INCOMING_EMAILS_DIR=/Users/rk/d/downloads/hedgeye/raw/eml
MARKDOWN_OUTPUT_DIR=/Users/rk/d/downloads/hedgeye/prod/daily/md
CSV_OUTPUT_DIR=/Users/rk/d/downloads/hedgeye/prod/daily/csv
""",
    "config.yaml": """\
# General configuration for Hedgeye Risk Range processing

paths:
  incoming_emails: /Users/rk/d/downloads/hedgeye/raw/eml
  output_md: /Users/rk/d/downloads/hedgeye/prod/daily/md
  output_csv: /Users/rk/d/downloads/hedgeye/prod/daily/csv

parsing:
  date_format_input: "%B %d, %Y"
  date_format_output: "%Y-%m-%d"
  filename_prefix: "RISK RANGE"

output:
  markdown_enabled: true
  csv_enabled: true
  include_change_events: true
""",
    "README.md": """\
# Configuration Files

This directory holds all configuration-related resources, including:

- `.env`: Local environment-specific variables (e.g., file paths, keys)
- `config.yaml`: Application settings for parsing and output control
- `README.md`: Description of this folder and contents
"""
}

# Create files
for filename, content in files.items():
    path = base_path / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
