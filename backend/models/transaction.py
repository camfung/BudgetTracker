"""
Transaction model for tracking expenses against budget categories.
"""

from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .database import Base


class TransactionSource(PyEnum):
    """
    Enum for transaction source types.
    """
    MANUAL = "manual"
    API = "api"


class Transaction(Base):
    """
    Transaction model for recording expenses against budget categories.
    
    Args:
        id (int): Primary key, auto-incremented.
        pay_period_id (int): Foreign key to pay_periods table.
        budget_category_id (int): Foreign key to budget_categories table.
        amount (Decimal): Transaction amount (positive for expenses).
        description (str): Description of the transaction.
        transaction_date (datetime): When the transaction occurred.
        source (TransactionSource): How the transaction was created (manual, api).
        created_at (datetime): Timestamp when transaction was recorded.
        updated_at (datetime): Timestamp when transaction was last updated.
    """
    
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    pay_period_id = Column(Integer, ForeignKey("pay_periods.id"), nullable=False)
    budget_category_id = Column(Integer, ForeignKey("budget_categories.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String(255), nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False, default=func.now())
    source = Column(Enum(TransactionSource), default=TransactionSource.MANUAL)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    pay_period = relationship("PayPeriod", back_populates="transactions")
    budget_category = relationship("BudgetCategory", back_populates="transactions")
    
    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, amount=${self.amount}, description='{self.description}')>"