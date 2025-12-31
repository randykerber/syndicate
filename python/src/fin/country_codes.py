"""
ISO 3166-1 alpha-2 country codes for financial markets.

Convention: lowercase 2-letter codes
- .us = United States (often implicit/omitted)
- .ca = Canada
- .uk = United Kingdom (alias for .gb)
- .de = Germany
- etc.
"""

# Exchange to country code mapping
# Maps exchange identifiers to ISO 3166-1 alpha-2 codes (lowercase)
EXCHANGE_TO_COUNTRY = {
    # United States
    "NYSE": "us",
    "NASDAQ": "us",
    "AMEX": "us",
    "NYSEARCA": "us",
    "NYSEAMERICAN": "us",
    "BATS": "us",
    "OTC": "us",
    "PINK": "us",
    
    # Canada
    "TSX": "ca",
    "TSXV": "ca",
    "TSE": "ca",  # Toronto Stock Exchange (alternate)
    "CVE": "ca",  # Canadian Venture Exchange
    "NEO": "ca",
    
    # United Kingdom
    "LSE": "uk",  # Using .uk as preferred alias for .gb
    "LON": "uk",
    "LONDON": "uk",
    
    # Germany
    "XETRA": "de",
    "FRA": "de",
    "ETR": "de",
    
    # France
    "EPA": "fr",
    "EURONEXT": "fr",  # Simplified - actually multi-country
    
    # Japan
    "TSE": "jp",  # Note: conflicts with Toronto - context needed
    "TYO": "jp",
    "JPX": "jp",
    
    # China
    "SSE": "cn",  # Shanghai
    "SZSE": "cn",  # Shenzhen
    "SHA": "cn",
    "SHE": "cn",
    
    # Hong Kong
    "HKEX": "hk",
    "HKG": "hk",
    
    # Australia
    "ASX": "au",
    
    # Switzerland
    "SIX": "ch",
    "SWX": "ch",
    
    # Others
    "BMV": "mx",  # Mexico
    "B3": "br",   # Brazil
    "NSE": "in",  # India (National Stock Exchange)
    "BSE": "in",  # India (Bombay)
    "KRX": "kr",  # South Korea
    "TWSE": "tw", # Taiwan
    "SGX": "sg",  # Singapore
    "JSE": "za",  # South Africa
    "TASE": "il", # Israel
}

# Country code to full name (for display)
COUNTRY_NAMES = {
    "us": "United States",
    "ca": "Canada",
    "uk": "United Kingdom",
    "gb": "United Kingdom",  # ISO standard
    "de": "Germany",
    "fr": "France",
    "jp": "Japan",
    "cn": "China",
    "hk": "Hong Kong",
    "au": "Australia",
    "ch": "Switzerland",
    "mx": "Mexico",
    "br": "Brazil",
    "in": "India",
    "kr": "South Korea",
    "tw": "Taiwan",
    "sg": "Singapore",
    "za": "South Africa",
    "il": "Israel",
    "ae": "UAE",
    "sa": "Saudi Arabia",
    "nl": "Netherlands",
    "es": "Spain",
    "it": "Italy",
    "se": "Sweden",
    "no": "Norway",
    "dk": "Denmark",
    "fi": "Finland",
    "be": "Belgium",
    "at": "Austria",
    "ie": "Ireland",
    "pt": "Portugal",
    "pl": "Poland",
    "ru": "Russia",
    "nz": "New Zealand",
}

# Alias mappings (user preferences)
COUNTRY_ALIASES = {
    "uk": "gb",  # .uk is preferred but .gb is ISO standard
}

# FMP symbol suffixes to country codes
# FMP uses exchange suffixes like .TO, .L, .AX - map to country
SUFFIX_TO_COUNTRY = {
    # North America
    "to": "ca",   # Toronto Stock Exchange
    "v": "ca",    # TSX Venture
    "cn": "ca",   # Canadian Securities Exchange
    "ne": "ca",   # NEO Exchange
    
    # UK / Europe
    "l": "uk",    # London Stock Exchange
    "ln": "uk",   # London (alternate)
    "as": "nl",   # Amsterdam
    "pa": "fr",   # Paris
    "de": "de",   # XETRA Germany
    "f": "de",    # Frankfurt
    "sw": "ch",   # Swiss Exchange
    "mi": "it",   # Milan
    "mc": "es",   # Madrid
    "ls": "pt",   # Lisbon
    "br": "be",   # Brussels
    "vi": "at",   # Vienna
    "ir": "ie",   # Ireland
    "he": "fi",   # Helsinki
    "st": "se",   # Stockholm
    "ol": "no",   # Oslo
    "co": "dk",   # Copenhagen
    
    # Asia Pacific
    "t": "jp",    # Tokyo
    "hk": "hk",   # Hong Kong
    "ss": "cn",   # Shanghai
    "sz": "cn",   # Shenzhen
    "ks": "kr",   # Korea
    "tw": "tw",   # Taiwan
    "si": "sg",   # Singapore
    "ax": "au",   # Australian Securities Exchange
    "nz": "nz",   # New Zealand
    "bk": "th",   # Bangkok (Thailand)
    "jk": "id",   # Jakarta (Indonesia)
    "kl": "my",   # Kuala Lumpur (Malaysia)
    "bo": "in",   # Bombay
    "ns": "in",   # National Stock Exchange India
    
    # Americas (non-US)
    "mx": "mx",   # Mexico
    "sa": "br",   # Sao Paulo (Brazil) - note: conflicts with Saudi
    
    # Middle East / Africa
    "ta": "il",   # Tel Aviv
    "me": "ru",   # Moscow (Russia)
    "jse": "za",  # Johannesburg
}


def normalize_country_code(code: str) -> str:
    """
    Normalize a country code to lowercase ISO 3166-1 alpha-2.
    
    Handles aliases (e.g., uk -> gb for ISO compliance if needed).
    """
    if not code:
        return "us"  # Default to US if no code
    
    code = code.lower().strip()
    
    # For now, keep .uk as-is (user preference)
    # If strict ISO needed: return COUNTRY_ALIASES.get(code, code)
    return code


def exchange_to_country(exchange: str) -> str:
    """
    Map an exchange identifier to its country code.
    
    Args:
        exchange: Exchange identifier (e.g., "NYSE", "TSX", "LSE")
        
    Returns:
        Two-letter country code (e.g., "us", "ca", "uk")
    """
    if not exchange:
        return "us"
    
    exchange = exchange.upper().strip()
    return EXCHANGE_TO_COUNTRY.get(exchange, "us")


def parse_cid(cid: str) -> tuple[str, str]:
    """
    Parse a canonical ID into ticker and country code.
    
    Args:
        cid: Canonical ID like "AAPL.us" or "ARX.ca" or "AAPL" (no suffix)
        
    Returns:
        Tuple of (ticker, country_code)
        
    Examples:
        >>> parse_cid("AAPL.us")
        ("AAPL", "us")
        >>> parse_cid("ARX.ca")
        ("ARX", "ca")
        >>> parse_cid("AAPL")
        ("AAPL", "us")  # Default to US
    """
    if not cid:
        raise ValueError("Empty cid")
    
    cid = cid.strip()
    
    if "." in cid:
        parts = cid.rsplit(".", 1)
        ticker = parts[0].upper()
        country = parts[1].lower()
    else:
        ticker = cid.upper()
        country = "us"  # Default
    
    return ticker, country


def make_cid(ticker: str, country: str = "us") -> str:
    """
    Create a canonical ID from ticker and country code.
    
    Args:
        ticker: Stock ticker symbol
        country: Two-letter country code (default: "us")
        
    Returns:
        Canonical ID like "AAPL.us"
    """
    ticker = ticker.upper().strip()
    country = normalize_country_code(country)
    return f"{ticker}.{country}"

