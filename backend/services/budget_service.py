"""
Budget service for managing pay periods and budget categories.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, func, desc
from fastapi import HTTPException, status
from decimal import Decimal
from datetime import date, timedelta

from models.user import User
from models.budget import PayPeriod, BudgetCategory, PayPeriodStatus, PayFrequency
from models.transaction import Transaction
from schemas.budget import (
    PayPeriodCreate, PayPeriodUpdate, PayPeriodResponse,
    BudgetCategoryCreate, BudgetCategoryUpdate, BudgetCategoryResponse,
    BudgetAllocationRequest, PeriodSummaryResponse
)


class BudgetService:
    """
    Service for budget management operations.
    """
    
    @staticmethod
    def calculate_end_date(start_date: date, frequency: PayFrequency) -> date:
        """
        Calculate end date based on start date and pay frequency.
        
        Args:
            start_date (date): Start date of the pay period.
            frequency (PayFrequency): Pay frequency.
            
        Returns:
            date: Calculated end date.
        """
        if frequency == PayFrequency.WEEKLY:
            return start_date + timedelta(days=6)  # 7-day period
        elif frequency == PayFrequency.BI_WEEKLY:
            return start_date + timedelta(days=13)  # 14-day period
        elif frequency == PayFrequency.MONTHLY:
            # Calculate last day of the month starting from start_date
            if start_date.month == 12:
                next_month = start_date.replace(year=start_date.year + 1, month=1, day=1)
            else:
                next_month = start_date.replace(month=start_date.month + 1, day=1)
            return next_month - timedelta(days=1)
        else:
            # Default to bi-weekly
            return start_date + timedelta(days=13)
    
    @staticmethod
    async def create_pay_period(
        user: User, 
        pay_period_data: PayPeriodCreate, 
        db: AsyncSession
    ) -> PayPeriod:
        """
        Create a new pay period for a user with auto-calculated end date.
        
        Args:
            user (User): Current user.
            pay_period_data (PayPeriodCreate): Pay period data.
            db (AsyncSession): Database session.
            
        Returns:
            PayPeriod: Created pay period.
            
        Raises:
            HTTPException: If validation fails.
        """
        # Calculate end date based on frequency
        end_date = BudgetService.calculate_end_date(
            pay_period_data.start_date, 
            pay_period_data.frequency
        )
        
        # Check for overlapping pay periods
        result = await db.execute(
            select(PayPeriod).where(
                and_(
                    PayPeriod.user_id == user.id,
                    PayPeriod.status == PayPeriodStatus.ACTIVE,
                    PayPeriod.start_date <= end_date,
                    PayPeriod.end_date >= pay_period_data.start_date
                )
            )
        )
        overlapping_period = result.scalar_one_or_none()
        
        if overlapping_period:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pay period overlaps with existing active period"
            )
        
        # Create pay period
        db_pay_period = PayPeriod(
            user_id=user.id,
            start_date=pay_period_data.start_date,
            end_date=end_date,
            frequency=pay_period_data.frequency,
            total_income=pay_period_data.total_income,
            status=PayPeriodStatus.ACTIVE
        )
        
        db.add(db_pay_period)
        await db.commit()
        await db.refresh(db_pay_period)
        
        # Create initial budget categories if provided
        if pay_period_data.budget_categories:
            for category_data in pay_period_data.budget_categories:
                await BudgetService._create_budget_category(
                    db_pay_period, category_data, db
                )
        
        return db_pay_period
    
    @staticmethod
    async def get_user_pay_periods(
        user: User, 
        db: AsyncSession, 
        status_filter: Optional[PayPeriodStatus] = None
    ) -> List[PayPeriod]:
        """
        Get all pay periods for a user.
        
        Args:
            user (User): Current user.
            db (AsyncSession): Database session.
            status_filter (Optional[PayPeriodStatus]): Filter by status.
            
        Returns:
            List[PayPeriod]: List of pay periods.
        """
        query = select(PayPeriod).where(PayPeriod.user_id == user.id)
        
        if status_filter:
            query = query.where(PayPeriod.status == status_filter)
        
        query = query.options(selectinload(PayPeriod.budget_categories))
        query = query.order_by(desc(PayPeriod.start_date))
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_pay_period_by_id(
        user: User, 
        pay_period_id: int, 
        db: AsyncSession
    ) -> Optional[PayPeriod]:
        """
        Get a specific pay period by ID.
        
        Args:
            user (User): Current user.
            pay_period_id (int): Pay period ID.
            db (AsyncSession): Database session.
            
        Returns:
            Optional[PayPeriod]: Pay period if found and belongs to user.
        """
        result = await db.execute(
            select(PayPeriod)
            .where(and_(PayPeriod.id == pay_period_id, PayPeriod.user_id == user.id))
            .options(selectinload(PayPeriod.budget_categories))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_pay_period(
        user: User,
        pay_period_id: int,
        update_data: PayPeriodUpdate,
        db: AsyncSession
    ) -> Optional[PayPeriod]:
        """
        Update a pay period.
        
        Args:
            user (User): Current user.
            pay_period_id (int): Pay period ID.
            update_data (PayPeriodUpdate): Update data.
            db (AsyncSession): Database session.
            
        Returns:
            Optional[PayPeriod]: Updated pay period.
        """
        pay_period = await BudgetService.get_pay_period_by_id(user, pay_period_id, db)
        if not pay_period:
            return None
        
        if update_data.status is not None:
            pay_period.status = update_data.status
        
        if update_data.total_income is not None:
            pay_period.total_income = update_data.total_income
        
        await db.commit()
        await db.refresh(pay_period)
        return pay_period
    
    @staticmethod
    async def allocate_budget(
        user: User,
        allocation_request: BudgetAllocationRequest,
        db: AsyncSession
    ) -> List[BudgetCategory]:
        """
        Allocate budget to categories for a pay period.
        
        Args:
            user (User): Current user.
            allocation_request (BudgetAllocationRequest): Allocation data.
            db (AsyncSession): Database session.
            
        Returns:
            List[BudgetCategory]: Created budget categories.
            
        Raises:
            HTTPException: If validation fails.
        """
        # Get pay period
        pay_period = await BudgetService.get_pay_period_by_id(
            user, allocation_request.pay_period_id, db
        )
        
        if not pay_period:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pay period not found"
            )
        
        # Calculate total allocation
        total_allocation = sum(
            allocation.allocated_amount 
            for allocation in allocation_request.allocations
        )
        
        if total_allocation > pay_period.total_income:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Total allocation (${total_allocation}) exceeds income (${pay_period.total_income})"
            )
        
        # Clear existing categories
        await db.execute(
            select(BudgetCategory).where(BudgetCategory.pay_period_id == pay_period.id)
        )
        
        # Create new categories
        created_categories = []
        for allocation in allocation_request.allocations:
            category = await BudgetService._create_budget_category(
                pay_period, allocation, db
            )
            created_categories.append(category)
        
        return created_categories
    
    @staticmethod
    async def get_period_summary(
        user: User, 
        pay_period_id: int, 
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """
        Get summary of spending for a pay period.
        
        Args:
            user (User): Current user.
            pay_period_id (int): Pay period ID.
            db (AsyncSession): Database session.
            
        Returns:
            Optional[Dict[str, Any]]: Period summary data.
        """
        pay_period = await BudgetService.get_pay_period_by_id(user, pay_period_id, db)
        if not pay_period:
            return None
        
        # Get transaction totals by category
        result = await db.execute(
            select(
                BudgetCategory,
                func.coalesce(func.sum(Transaction.amount), 0).label("total_spent")
            )
            .outerjoin(Transaction, BudgetCategory.id == Transaction.budget_category_id)
            .where(BudgetCategory.pay_period_id == pay_period_id)
            .group_by(BudgetCategory.id)
        )
        
        category_summaries = []
        total_allocated = Decimal('0')
        total_spent = Decimal('0')
        
        for category, spent in result.fetchall():
            total_allocated += category.allocated_amount
            total_spent += spent
            
            category_summaries.append({
                "category": category,
                "allocated": category.allocated_amount,
                "spent": spent,
                "remaining": category.allocated_amount - spent
            })
        
        return {
            "pay_period": pay_period,
            "total_allocated": total_allocated,
            "total_spent": total_spent,
            "total_remaining": total_allocated - total_spent,
            "categories_summary": category_summaries
        }
    
    @staticmethod
    async def _create_budget_category(
        pay_period: PayPeriod, 
        category_data: BudgetCategoryCreate, 
        db: AsyncSession
    ) -> BudgetCategory:
        """
        Create a budget category.
        
        Args:
            pay_period (PayPeriod): Pay period to create category for.
            category_data (BudgetCategoryCreate): Category data.
            db (AsyncSession): Database session.
            
        Returns:
            BudgetCategory: Created budget category.
        """
        db_category = BudgetCategory(
            pay_period_id=pay_period.id,
            name=category_data.name,
            allocated_amount=category_data.allocated_amount,
            remaining_amount=category_data.allocated_amount
        )
        
        db.add(db_category)
        await db.commit()
        await db.refresh(db_category)
        return db_category