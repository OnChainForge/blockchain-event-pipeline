from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON

from app.database import Base


class Block(Base):
    """A processed Ethereum block, tracked so the listener knows where it left off."""
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    block_number = Column(Integer, unique=True, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False)
    tx_count = Column(Integer, nullable=False)
    processed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Transaction(Base):
    """A normalized transaction extracted from a processed block."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    tx_hash = Column(String(80), unique=True, nullable=False, index=True)
    block_number = Column(Integer, nullable=False, index=True)
    from_address = Column(String(80), nullable=False)
    to_address = Column(String(80), nullable=True)
    value_eth = Column(Float, nullable=False)
    gas_used = Column(Integer, nullable=True)
    gas_price_gwei = Column(Float, nullable=True)
    status = Column(Integer, nullable=True)
    is_contract_call = Column(Boolean, default=False)
    to_is_contract = Column(Boolean, default=False)
    forwarded_to_risk_engine = Column(Boolean, default=False)
    raw_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
