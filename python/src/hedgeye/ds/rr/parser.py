import re
from decimal import Decimal
from typing import List, Tuple
from email import policy
from email.parser import BytesParser

from hedgeye.ds.rr.models import RiskRangeEntry, ChangeEvent, Trend, Bucket


def parse_eml(filepath: str) -> Tuple[str, List[RiskRangeEntry], List[ChangeEvent]]:
    with open(filepath, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    body = msg.get_body(preferencelist=('plain')).get_content()

    lines = body.splitlines()
    lines = [line.strip() for line in lines if line.strip()]

    date_line = next(line for line in lines if re.search(r'\w+ \d{1,2}, \d{4}', line))

    match = re.search(r'(\w+ \d{1,2}, \d{4})', date_line)
    report_date = match.group(1)

    change_events = extract_change_events(lines, report_date)

    print("Scanning lines for table start...")
    for i, line in enumerate(lines):
        print(f"{i:02}: {repr(line)}")

    risk_range_entries = extract_risk_range_entries(lines, report_date)

    return report_date, risk_range_entries, change_events


def parse_date_line(line: str) -> str:
    import datetime
    return str(datetime.datetime.strptime(line, "%B %d, %Y").date())


def extract_change_events(lines: List[str], date: str) -> List[ChangeEvent]:
    events = []
    in_block = False

    for line in lines:
        if line.startswith("TREND CHANGE:"):
            in_block = True
            continue
        if in_block and re.match(r'^[A-Z]+ ', line):
            if "changed from" in line:
                m = re.match(r'(\S+)\s+changed from\s+(\w+)\s+to\s+(\w+)', line)
                if m:
                    index, from_trend, to_trend = m.groups()
                    events.append(ChangeEvent(
                        date=date,
                        index=index,
                        trend_from=Trend(from_trend),
                        trend_to=Trend(to_trend)
                    ))
            elif "moved to the #OutBucket" in line:
                m = re.match(r'(\S+)\s+moved to the #OutBucket', line)
                if m:
                    index = m.group(1)
                    events.append(ChangeEvent(
                        date=date,
                        index=index,
                        bucket_from=Bucket.IN,
                        bucket_to=Bucket.OUT
                    ))
            elif "added back to Risk Ranges" in line:
                m = re.match(r'(\S+)\s+added back to Risk Ranges', line)
                if m:
                    index = m.group(1)
                    events.append(ChangeEvent(
                        date=date,
                        index=index,
                        bucket_from=Bucket.OUT,
                        bucket_to=Bucket.IN
                    ))
            elif "in the #OutBucket" in line:
                m = re.match(r'(\S+)\s+changed from\s+(\w+)\s+to\s+(\w+)\s+in the #OutBucket', line)
                if m:
                    index, from_trend, to_trend = m.groups()
                    events.append(ChangeEvent(
                        date=date,
                        index=index,
                        trend_from=Trend(from_trend),
                        trend_to=Trend(to_trend),
                        bucket_from=Bucket.OUT,
                        bucket_to=Bucket.OUT
                    ))
        elif in_block:
            break

    return events


def extract_risk_range_entries(lines: List[str], date: str) -> List[RiskRangeEntry]:
    entries = []
    header_found = False
    pattern = re.compile(r'^(.+?)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)$')

    for line in lines:
        if line.startswith("INDEX") and "PREV. CLOSE" in line:
            header_found = True
            continue
        if header_found:
            m = pattern.match(line)
            if m:
                index_line, buy, sell, close = m.groups()
                parts = index_line.split()
                index = parts[0]
                trend = Trend(parts[-1].strip("()"))
                entries.append(RiskRangeEntry(
                    date=date,
                    index=index,
                    trend=trend,
                    buy_trade=Decimal(buy.replace(",", "")),
                    sell_trade=Decimal(sell.replace(",", "")),
                    prev_close=Decimal(close.replace(",", "")),
                    bucket=Bucket.IN
                ))
            else:
                break  # reached the end of table

    return entries
