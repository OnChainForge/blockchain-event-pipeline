from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tx_hash: str
    block_number: int
    from_address: str
    to_address: Optional[str]
    value_eth: float
    gas_used: Optional[int]
    gas_price_gwei: Optional[float]
    status: Optional[int]
    is_contract_call: bool
    to_is_contract: bool
    forwarded_to_risk_engine: bool
    created_at: datetime


class BlockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    block_number: int
    timestamp: datetime
    tx_count: int
    processed_at: datetime
