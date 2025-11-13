from dataclasses import dataclass
from enum import Enum
from typing import Optional
from decimal import Decimal


class Trend(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class Bucket(str, Enum):
    IN = "in"
    OUT = "out"


@dataclass
class RiskRangeEntry:
    date: str  # ISO format date string: YYYY-MM-DD
    index: str
    trend: Trend
    buy_trade: Decimal
    sell_trade: Decimal
    prev_close: Decimal
    bucket: Bucket = Bucket.IN


@dataclass
class ChangeEvent:
    date: str  # ISO format date string
    index: str
    trend_from: Optional[Trend] = None
    trend_to: Optional[Trend] = None
    bucket_from: Optional[Bucket] = None
    bucket_to: Optional[Bucket] = None
    notes: Optional[str] = None
