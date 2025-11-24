# Standard library imports
import os
import re
import csv
import email
from datetime import datetime
from email import policy
from pathlib import Path
from typing import List, Tuple

# Third-party imports
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Internal imports
from hedgeye.ds.rr.models import RiskRangeEntry, ChangeEvent, Trend, Bucket
from hedgeye.config_loader import load_config
from hedgeye.ds.rr.symbol_canonicalization import canonicalize_symbol


# --- Load configuration and secrets ---

# Load secrets from project root .env
load_dotenv()

# Load paths from YAML config
config = load_config()

RAW_EML_DIR = config["paths"]["raw_eml_dir"]
MARKDOWN_OUTPUT_DIR = config["paths"]["markdown_output_dir"]
CSV_OUTPUT_DIR = config["paths"]["csv_output_dir"]

# Secrets
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def standardize_date(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%B %d, %Y")
    return dt.strftime("%Y-%m-%d")


def parse_eml(filepath: str) -> Tuple[str, List[RiskRangeEntry], List[ChangeEvent]]:
    with open(filepath, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    html = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html += part.get_content()
    else:
        html = msg.get_content()

    html = re.sub(r'=\r?\n', '', html)
    html = re.sub(r'=3D', '=', html)
    html = re.sub(r'=E2=84=A2', '™', html)

    soup = BeautifulSoup(html, "html.parser")

    report_date = None
    headline_div = soup.find("div", class_="headline")
    if headline_div:
        date_match = re.search(r"(\w+ \d{1,2}, \d{4})", headline_div.get_text())
        if date_match:
            report_date = standardize_date(date_match.group(1))

    if not report_date:
        raise ValueError("Could not find date in headline section")

    text = soup.get_text()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    changes = []
    for line in lines:
        if "TREND CHANGE" in line.upper():
            continue
        if "moved to the #OutBucket" in line:
            m = re.match(r"(\w+) moved to the #OutBucket", line)
            if m:
                changes.append(ChangeEvent(
                    date=report_date,
                    index=canonicalize_symbol(m.group(1)),
                    trend_from=None,
                    trend_to=None,
                    bucket_from=Bucket.IN,
                    bucket_to=Bucket.OUT,
                    notes=None
                ))
        elif "added back to Risk Ranges" in line:
            m = re.match(r"(\w+) added back to Risk Ranges", line)
            if m:
                changes.append(ChangeEvent(
                    date=report_date,
                    index=canonicalize_symbol(m.group(1)),
                    trend_from=None,
                    trend_to=None,
                    bucket_from=Bucket.OUT,
                    bucket_to=Bucket.IN,
                    notes=None
                ))
        elif "changed from" in line:
            m = re.match(r"(\w+) changed from (\w+) to (\w+)", line)
            if m:
                changes.append(ChangeEvent(
                    date=report_date,
                    index=canonicalize_symbol(m.group(1)),
                    trend_from=Trend(m.group(2).upper()),
                    trend_to=Trend(m.group(3).upper()),
                    bucket_from=None,
                    bucket_to=None,
                    notes=None
                ))

    entries = []
    table_rows = soup.find_all("tr")
    for row in table_rows:
        cells = row.find_all("td")
        if len(cells) != 4:
            continue

        first_cell = cells[0].get_text(strip=True)
        ticker_match = re.match(r"([A-Z0-9./]+) \((\w+)\)", first_cell)
        if not ticker_match:
            continue

        ticker, trend_str = ticker_match.groups()

        try:
            buy_trade = float(cells[1].get_text(strip=True).replace(",", ""))
            sell_trade = float(cells[2].get_text(strip=True).replace(",", ""))
            prev_close = float(cells[3].get_text(strip=True).replace(",", ""))
            trend = Trend(trend_str.upper())
        except ValueError:
            continue

        bucket = Bucket.OUT if ticker in [c.index for c in changes if c.bucket_to == Bucket.OUT] else Bucket.IN

        entries.append(RiskRangeEntry(
            date=report_date,
            index=canonicalize_symbol(ticker),
            trend=trend,
            buy_trade=buy_trade,
            sell_trade=sell_trade,
            prev_close=prev_close,
            bucket=bucket
        ))

    return report_date, entries, changes


def save_outputs(report_date: str, entries: List[RiskRangeEntry], changes: List[ChangeEvent]):
    os.makedirs(MARKDOWN_OUTPUT_DIR, exist_ok=True)
    os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)

    md_path = os.path.join(MARKDOWN_OUTPUT_DIR, f"risk_range_{report_date}.md")
    with open(md_path, "w") as f:
        f.write(f"## Risk Range Entries — {report_date}\n\n")
        f.write("| Index | Trend | Buy | Sell | Prev Close | Bucket |\n")
        f.write("|-------|--------|------|------|-------------|--------|\n")
        for e in entries:
            f.write(f"| {e.index} | {e.trend.name} | {e.buy_trade} | {e.sell_trade} | {e.prev_close} | {e.bucket.name} |\n")

        f.write(f"\n## Change Events — {report_date}\n\n")
        f.write("| Index | Trend From | Trend To | Bucket From | Bucket To | Notes |\n")
        f.write("|--------|-------------|----------|--------------|-------------|--------|\n")
        for c in changes:
            f.write(f"| {c.index} | {c.trend_from.name if c.trend_from else ''} | {c.trend_to.name if c.trend_to else ''} | {c.bucket_from.name if c.bucket_from else ''} | {c.bucket_to.name if c.bucket_to else ''} | {c.notes or ''} |\n")

    csv_path = os.path.join(CSV_OUTPUT_DIR, f"risk_range_{report_date}.csv")
    with open(csv_path, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["date", "index", "trend", "buy_trade", "sell_trade", "prev_close", "bucket"])
        for e in entries:
            writer.writerow([e.date, e.index, e.trend.name, e.buy_trade, e.sell_trade, e.prev_close, e.bucket.name])

    changes_csv_path = os.path.join(CSV_OUTPUT_DIR, f"change_events_{report_date}.csv")
    with open(changes_csv_path, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["date", "index", "trend_from", "trend_to", "bucket_from", "bucket_to", "notes"])
        for c in changes:
            writer.writerow([
                c.date,
                c.index,
                c.trend_from.name if c.trend_from else '',
                c.trend_to.name if c.trend_to else '',
                c.bucket_from.name if c.bucket_from else '',
                c.bucket_to.name if c.bucket_to else '',
                c.notes or ''
            ])


def process_new_eml_files():
    eml_dir = Path(INCOMING_EMAILS_DIR)
    for eml_file in eml_dir.glob("RISK RANGE*.eml"):
        try:
            report_date, _, _ = parse_eml(str(eml_file))
            csv_outfile = Path(CSV_OUTPUT_DIR) / f"risk_range_{report_date}.csv"
            if not csv_outfile.exists():
                report_date, entries, changes = parse_eml(str(eml_file))
                save_outputs(report_date, entries, changes)
                print(f"Processed: {eml_file.name}")
            else:
                print(f"Skipped (already exists): {eml_file.name}")
        except Exception as e:
            print(f"Error processing {eml_file.name}: {e}")


if __name__ == "__main__":
    process_new_eml_files()
