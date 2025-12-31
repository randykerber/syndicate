"""
TickerCatalog - Main interface for looking up and managing entities.

Usage:
    from fin.catalog import TickerCatalog
    
    catalog = TickerCatalog()
    
    # Lookup by canonical ID
    entity = catalog.get("AAPL.us")
    
    # Lookup by any ticker (resolves aliases)
    entity = catalog.lookup("AETUF")  # -> ARX.ca entity
    
    # Search
    results = catalog.search("apple")
"""

import os
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from .country_codes import make_cid, parse_cid, exchange_to_country
from .models import Base, Entity, TickerAlias, get_engine, get_session, create_tables


# Default database location
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "fin_catalog.db"


class TickerCatalog:
    """
    Main interface for the financial entity catalog.
    
    Provides methods to:
    - Look up entities by cid or any alias
    - Search entities by name/description
    - Add/update entities
    - Manage ticker aliases
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the catalog.
        
        Args:
            db_path: Path to SQLite database. Defaults to data/fin_catalog.db
        """
        if db_path is None:
            db_path = str(DEFAULT_DB_PATH)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.engine = get_engine(db_path)
        create_tables(self.engine)
        self._session: Optional[Session] = None
    
    @property
    def session(self) -> Session:
        """Get or create session."""
        if self._session is None:
            self._session = get_session(self.engine)
        return self._session
    
    def close(self):
        """Close the session."""
        if self._session:
            self._session.close()
            self._session = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # -------------------------------------------------------------------------
    # Lookups
    # -------------------------------------------------------------------------
    
    def get(self, cid: str) -> Optional[Entity]:
        """
        Get entity by canonical ID.
        
        Args:
            cid: Canonical ID like "AAPL.us" or "AAPL" (assumes .us)
            
        Returns:
            Entity or None if not found
        """
        # Normalize cid
        ticker, country = parse_cid(cid)
        normalized_cid = make_cid(ticker, country)
        
        return self.session.query(Entity).filter(Entity.cid == normalized_cid).first()
    
    def lookup(self, ticker: str, exchange: Optional[str] = None) -> Optional[Entity]:
        """
        Look up entity by any ticker (resolves aliases).
        
        First checks if ticker is a direct cid, then checks aliases.
        
        Args:
            ticker: Any ticker symbol
            exchange: Optional exchange to narrow search
            
        Returns:
            Entity or None
        """
        ticker = ticker.upper().strip()
        
        # First, try as a direct cid
        if "." in ticker:
            entity = self.get(ticker)
            if entity:
                return entity
        
        # Try with assumed .us suffix
        entity = self.get(f"{ticker}.us")
        if entity:
            return entity
        
        # Look in aliases
        query = self.session.query(TickerAlias).filter(TickerAlias.ticker == ticker)
        if exchange:
            query = query.filter(TickerAlias.exchange == exchange.upper())
        
        alias = query.first()
        if alias:
            return alias.entity
        
        return None
    
    def resolve(self, ticker: str, exchange: Optional[str] = None) -> Optional[str]:
        """
        Resolve any ticker to its canonical ID.
        
        Args:
            ticker: Any ticker symbol
            exchange: Optional exchange hint
            
        Returns:
            Canonical ID string or None
        """
        entity = self.lookup(ticker, exchange)
        return entity.cid if entity else None
    
    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------
    
    def search(self, query: str, limit: int = 20) -> list[Entity]:
        """
        Search entities by name or ticker.
        
        Args:
            query: Search string
            limit: Max results to return
            
        Returns:
            List of matching entities
        """
        query = f"%{query}%"
        
        return (
            self.session.query(Entity)
            .filter(
                (Entity.name.ilike(query)) |
                (Entity.cid.ilike(query)) |
                (Entity.description.ilike(query))
            )
            .limit(limit)
            .all()
        )
    
    def by_sector(self, sector: str) -> list[Entity]:
        """Get all entities in a sector."""
        return self.session.query(Entity).filter(Entity.sector == sector).all()
    
    def by_industry(self, industry: str) -> list[Entity]:
        """Get all entities in an industry."""
        return self.session.query(Entity).filter(Entity.industry == industry).all()
    
    def by_asset_class(self, asset_class: str) -> list[Entity]:
        """Get all entities of an asset class (stock, etf, index, etc.)."""
        return self.session.query(Entity).filter(Entity.asset_class == asset_class).all()
    
    # -------------------------------------------------------------------------
    # Add/Update
    # -------------------------------------------------------------------------
    
    def add_entity(
        self,
        cid: str,
        name: str,
        asset_class: str = "stock",
        sector: Optional[str] = None,
        industry: Optional[str] = None,
        exchange: Optional[str] = None,
        **kwargs
    ) -> Entity:
        """
        Add or update an entity.
        
        Args:
            cid: Canonical ID (will be normalized)
            name: Entity name
            asset_class: stock, etf, index, commodity, currency
            sector: Sector name
            industry: Industry name
            exchange: Primary exchange
            **kwargs: Additional Entity fields
            
        Returns:
            Created or updated Entity
        """
        ticker, country = parse_cid(cid)
        normalized_cid = make_cid(ticker, country)
        
        entity = self.get(normalized_cid)
        
        if entity:
            # Update existing
            entity.name = name
            entity.asset_class = asset_class
            entity.country = country
            if sector:
                entity.sector = sector
            if industry:
                entity.industry = industry
            if exchange:
                entity.exchange = exchange
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
        else:
            # Create new
            entity = Entity(
                cid=normalized_cid,
                name=name,
                asset_class=asset_class,
                country=country,
                sector=sector,
                industry=industry,
                exchange=exchange,
                **kwargs
            )
            self.session.add(entity)
        
        self.session.commit()
        return entity
    
    def add_alias(
        self,
        ticker: str,
        entity_cid: str,
        exchange: Optional[str] = None,
        alias_type: Optional[str] = None,
        source: str = "manual",
        is_primary: bool = False
    ) -> TickerAlias:
        """
        Add a ticker alias for an entity.
        
        Args:
            ticker: The alias ticker
            entity_cid: The canonical ID this resolves to
            exchange: Optional exchange qualifier
            alias_type: "adr", "otc", "exchange_variant", etc.
            source: Where this mapping came from
            is_primary: Is this the primary ticker?
            
        Returns:
            Created TickerAlias
        """
        ticker = ticker.upper().strip()
        
        # Normalize entity_cid
        t, c = parse_cid(entity_cid)
        normalized_cid = make_cid(t, c)
        
        # Check entity exists
        entity = self.get(normalized_cid)
        if not entity:
            raise ValueError(f"Entity {normalized_cid} does not exist")
        
        # Check if alias already exists
        existing = (
            self.session.query(TickerAlias)
            .filter(TickerAlias.ticker == ticker, TickerAlias.entity_cid == normalized_cid)
            .first()
        )
        
        if existing:
            # Update
            existing.exchange = exchange
            existing.alias_type = alias_type
            existing.source = source
            existing.is_primary = is_primary
            alias = existing
        else:
            alias = TickerAlias(
                ticker=ticker,
                entity_cid=normalized_cid,
                exchange=exchange,
                alias_type=alias_type,
                source=source,
                is_primary=is_primary
            )
            self.session.add(alias)
        
        self.session.commit()
        return alias
    
    # -------------------------------------------------------------------------
    # Stats
    # -------------------------------------------------------------------------
    
    def stats(self) -> dict:
        """Get catalog statistics."""
        return {
            "entities": self.session.query(Entity).count(),
            "aliases": self.session.query(TickerAlias).count(),
            "stocks": self.session.query(Entity).filter(Entity.asset_class == "stock").count(),
            "etfs": self.session.query(Entity).filter(Entity.asset_class == "etf").count(),
            "indexes": self.session.query(Entity).filter(Entity.asset_class == "index").count(),
        }


