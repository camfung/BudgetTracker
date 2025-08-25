"""
Transaction schemas for expense tracking.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from models.transaction import TransactionSource


class TransactionBase(BaseModel):
    """
    Base transaction schema.
    """
    budget_category_id: int
    amount: Decimal = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=255)
    transaction_date: Optional[datetime] = None


class TransactionCreate(TransactionBase):
    """
    Schema for creating a transaction.
    """
    source: TransactionSource = TransactionSource.MANUAL


class TransactionUpdate(BaseModel):
    """
    Schema for updating a transaction.
    """
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[Decimal] = Field(None, gt=0)


class TransactionResponse(TransactionBase):
    """
    Schema for transaction responses.
    """
    id: int
    pay_period_id: int
    source: TransactionSource
    created_at: datetime
    
    class Config:
        from_attributes = True


class TransactionBulkCreate(BaseModel):
    """
    Schema for bulk transaction creation (API integration).
    """
    transactions: List[TransactionCreate]


class TransactionSummary(BaseModel):
    """
    Schema for transaction summary by category.
    """
    budget_category_id: int
    category_name: str
    allocated_amount: Decimal
    total_spent: Decimal
    remaining_amount: Decimal
    transaction_count: int


class SpendingAnalytics(BaseModel):
    """
    Schema for spending analytics across periods.
    """
    total_periods: int
    total_income: Decimal
    total_spent: Decimal
    average_spending_per_period: Decimal
    top_categories: List[dict]
    spending_trend: List[dict]