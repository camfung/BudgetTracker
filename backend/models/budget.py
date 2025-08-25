"""
Budget-related models for pay periods and budget categories.
"""

from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .database import Base


class PayPeriodStatus(PyEnum):
    """
    Enum for pay period status.
    """
    ACTIVE = "active"
    COMPLETED = "completed"


class PayFrequency(PyEnum):
    """
    Enum for pay frequency types.
    """
    WEEKLY = "weekly"
    BI_WEEKLY = "bi_weekly"
    MONTHLY = "monthly"


class PayPeriod(Base):
    """
    Pay period model representing a budget cycle with configurable frequency.
    
    Args:
        id (int): Primary key, auto-incremented.
        user_id (int): Foreign key to users table.
        start_date (date): Start date of the pay period.
        end_date (date): End date of the pay period (auto-calculated).
        frequency (PayFrequency): Pay frequency (weekly, bi_weekly, monthly).
        total_income (Decimal): Total income for this pay period.
        status (PayPeriodStatus): Status of the pay period (active, completed).
        created_at (datetime): Timestamp when pay period was created.
        updated_at (datetime): Timestamp when pay period was last updated.
    """
    
    __tablename__ = "pay_periods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    frequency = Column(Enum(PayFrequency), default=PayFrequency.BI_WEEKLY, nullable=False)
    total_income = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(PayPeriodStatus), default=PayPeriodStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="pay_periods")
    budget_categories = relationship("BudgetCategory", back_populates="pay_period", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="pay_period", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<PayPeriod(id={self.id}, user_id={self.user_id}, period={self.start_date} to {self.end_date})>"


class BudgetCategory(Base):
    """
    Budget category model for allocating money within a pay period.
    
    Args:
        id (int): Primary key, auto-incremented.
        pay_period_id (int): Foreign key to pay_periods table.
        name (str): Name of the budget category.
        allocated_amount (Decimal): Amount allocated to this category.
        remaining_amount (Decimal): Amount remaining in this category.
        created_at (datetime): Timestamp when category was created.
        updated_at (datetime): Timestamp when category was last updated.
    """
    
    __tablename__ = "budget_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    pay_period_id = Column(Integer, ForeignKey("pay_periods.id"), nullable=False)
    name = Column(String(100), nullable=False)
    allocated_amount = Column(Numeric(10, 2), nullable=False)
    remaining_amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    pay_period = relationship("PayPeriod", back_populates="budget_categories")
    transactions = relationship("Transaction", back_populates="budget_category", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<BudgetCategory(id={self.id}, name='{self.name}', allocated=${self.allocated_amount})>"