"""
fin - Financial Instrument and Entity catalog.

Provides a canonical ticker catalog using TICKER.cc format (e.g., AAPL.us, ARX.ca)
as the primary entity identifier, with categorization metadata.

Key concepts:
- Entity: The underlying company/issuer (canonical, e.g., ARX.ca)
- Financial Instrument (FI): A tradable ticker that points to an entity (e.g., AETUF -> ARX.ca)
- cid: Canonical ID in TICKER.cc format
"""

__version__ = "0.1.0"


