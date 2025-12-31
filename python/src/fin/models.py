"""
SQLAlchemy models for the financial entity catalog.

Two primary objects:
- Entity: The canonical company/issuer (e.g., ARX.ca for ARC Resources)
- TickerAlias: Tradable tickers that map to entities (e.g., AETUF -> ARX.ca)
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class Entity(Base):
    """
    Canonical entity (company, ETF, index, commodity, currency).
    
    The cid (canonical ID) is the primary key in TICKER.cc format.
    All information about an entity is attached here.
    """
    __tablename__ = "entities"
    
    # Primary key: canonical ID like "AAPL.us", "ARX.ca"
    cid = Column(String(32), primary_key=True)
    
    # Basic info
    name = Column(String(255), nullable=False)  # "Apple Inc.", "ARC Resources Ltd"
    description = Column(Text, nullable=True)   # Company description
    
    # Classification
    asset_class = Column(String(32), nullable=True)   # stock, etf, index, commodity, currency, bond
    sector = Column(String(64), nullable=True)        # Technology, Energy, etc.
    industry = Column(String(128), nullable=True)     # Software, Oil & Gas E&P, etc.
    
    # Geography
    country = Column(String(2), nullable=False)       # us, ca, uk, etc.
    exchange = Column(String(32), nullable=True)      # Primary exchange: NYSE, TSX, LSE
    
    # Size/type indicators
    market_cap = Column(Float, nullable=True)         # Market cap in USD
    market_cap_category = Column(String(16), nullable=True)  # mega, large, mid, small, micro
    is_adr = Column(Boolean, default=False)           # American Depositary Receipt
    is_otc = Column(Boolean, default=False)           # Over-the-counter
    
    # For ETFs
    is_etf = Column(Boolean, default=False)
    etf_issuer = Column(String(64), nullable=True)    # "iShares", "Vanguard", etc.
    
    # For indexes
    is_index = Column(Boolean, default=False)
    
    # Metadata
    fmp_symbol = Column(String(32), nullable=True)    # Symbol as FMP knows it
    yahoo_symbol = Column(String(32), nullable=True)  # Symbol as Yahoo knows it
    figi = Column(String(12), nullable=True)          # OpenFIGI identifier
    isin = Column(String(12), nullable=True)          # International Securities ID
    cusip = Column(String(9), nullable=True)          # CUSIP (North America)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    aliases = relationship("TickerAlias", back_populates="entity")
    
    def __repr__(self) -> str:
        return f"<Entity(cid={self.cid!r}, name={self.name!r})>"


class TickerAlias(Base):
    """
    Alternative ticker symbols that map to a canonical entity.
    
    Examples:
    - AETUF (US OTC) -> ARX.ca (canonical for ARC Resources)
    - AAPL (standalone) -> AAPL.us
    - Different exchanges for same company
    """
    __tablename__ = "ticker_aliases"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # The alias ticker (what you might see in data)
    ticker = Column(String(32), nullable=False, index=True)
    
    # Optional exchange qualifier
    exchange = Column(String(32), nullable=True)
    
    # What this resolves to
    entity_cid = Column(String(32), ForeignKey("entities.cid"), nullable=False, index=True)
    
    # Why this alias exists
    alias_type = Column(String(32), nullable=True)  # "adr", "otc", "exchange_variant", "historical"
    
    # Source of this mapping
    source = Column(String(32), nullable=True)  # "fmp", "manual", "openfigi"
    
    # Is this the primary ticker for the entity?
    is_primary = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    entity = relationship("Entity", back_populates="aliases")
    
    def __repr__(self) -> str:
        return f"<TickerAlias(ticker={self.ticker!r}, entity_cid={self.entity_cid!r})>"


def get_engine(db_path: str = "fin_catalog.db"):
    """Create SQLite engine."""
    return create_engine(f"sqlite:///{db_path}", echo=False)


def create_tables(engine):
    """Create all tables."""
    Base.metadata.create_all(engine)


def get_session(engine):
    """Create a session factory."""
    Session = sessionmaker(bind=engine)
    return Session()


