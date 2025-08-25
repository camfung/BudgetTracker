"""
Budget schemas for pay periods and budget categories.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

from models.budget import PayPeriodStatus, PayFrequency


class BudgetCategoryBase(BaseModel):
    """
    Base budget category schema.
    """
    name: str = Field(..., min_length=1, max_length=100)
    allocated_amount: Decimal = Field(..., ge=0)


class BudgetCategoryCreate(BudgetCategoryBase):
    """
    Schema for creating a budget category.
    """
    pass


class BudgetCategoryUpdate(BaseModel):
    """
    Schema for updating a budget category.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    allocated_amount: Optional[Decimal] = Field(None, ge=0)


class BudgetCategoryResponse(BudgetCategoryBase):
    """
    Schema for budget category responses.
    """
    id: int
    pay_period_id: int
    remaining_amount: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True


class PayPeriodBase(BaseModel):
    """
    Base pay period schema.
    """
    start_date: date
    frequency: PayFrequency = PayFrequency.BI_WEEKLY
    total_income: Decimal = Field(..., gt=0)


class PayPeriodCreate(PayPeriodBase):
    """
    Schema for creating a pay period.
    """
    budget_categories: Optional[List[BudgetCategoryCreate]] = []


class PayPeriodUpdate(BaseModel):
    """
    Schema for updating a pay period.
    """
    status: Optional[PayPeriodStatus] = None
    total_income: Optional[Decimal] = Field(None, gt=0)


class PayPeriodResponse(BaseModel):
    """
    Schema for pay period responses.
    """
    id: int
    user_id: int
    start_date: date
    end_date: date
    frequency: PayFrequency
    total_income: Decimal
    status: PayPeriodStatus
    created_at: datetime
    budget_categories: List[BudgetCategoryResponse] = []
    
    class Config:
        from_attributes = True


class BudgetAllocationRequest(BaseModel):
    """
    Schema for allocating budget to categories.
    """
    pay_period_id: int
    allocations: List[BudgetCategoryCreate]


class PeriodSummaryResponse(BaseModel):
    """
    Schema for pay period summary.
    """
    pay_period: PayPeriodResponse
    total_allocated: Decimal
    total_spent: Decimal
    total_remaining: Decimal
    categories_summary: List[dict]