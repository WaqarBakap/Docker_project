# models.py
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class TransactionBase(BaseModel):
    amount: Decimal
    date: str
    category: str
    description: str

class TransactionCreate(TransactionBase):
    type: str  # "income" or "expense"

class Transaction(TransactionCreate):
    id: int
    
    class Config:
        from_attributes = True