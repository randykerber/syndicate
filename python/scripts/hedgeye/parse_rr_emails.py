#!/usr/bin/env python3
"""
Parse Hedgeye .eml files into CSV and Markdown outputs.
Usage:
    python scripts/parse_emails.py                    # Process all unprocessed files
    python scripts/parse_emails.py path/to/file.eml   # Process single file
"""
import sys
from hedgeye.rr_pipeline import run_rr_parsing_step
from hedgeye.run_rr_parser import process_single_file

def main():
    if len(sys.argv) > 1:
        try:
            process_single_file(sys.argv[1])
        except ValueError as e:
            if "Could not find date in headline section" in str(e):
                # Fallback for June 26 text format - TODO: remove when proper email restored
                print(f"Trying text parser fallback for: {sys.argv[1]}")
                from hedgeye.parse_rr_text_email import parse_text_email
                date, entries, changes = parse_text_email(sys.argv[1])
                print(f"Successfully parsed {len(entries)} entries for {date}")
            else:
                raise
    else:
        run_rr_parsing_step()

if __name__ == "__main__":
    main()