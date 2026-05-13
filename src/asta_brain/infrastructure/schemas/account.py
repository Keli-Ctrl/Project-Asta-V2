from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class AccountType(str, Enum):
    DEMO = "demo"
    LIVE = "live"

class AccountSchema(BaseModel):
    id: str
    broker: str
    login: str
    account_type: AccountType
    balance: float
    equity: float
    currency: str = "USD"
    leverage: int = 1
    
class AccountConnection(BaseModel):
    id: str
    token: str
    account_id: str
    region: str = "vint-hill"
