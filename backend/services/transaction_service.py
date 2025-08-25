"""
Transaction service for managing expenses and budget deductions.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, func, desc
from fastapi import HTTPException, status
from decimal import Decimal
from datetime import datetime

from models.user import User
from models.budget import BudgetCategory, PayPeriod
from models.transaction import Transaction, TransactionSource
from schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionResponse,
    TransactionBulkCreate, TransactionSummary, SpendingAnalytics
)


class TransactionService:
    """
    Service for transaction management operations.
    """
    
    @staticmethod
    async def create_transaction(
        user: User,
        transaction_data: TransactionCreate,
        db: AsyncSession
    ) -> Transaction:
        """
        Create a new transaction and update budget remaining amount.
        
        Args:
            user (User): Current user.
            transaction_data (TransactionCreate): Transaction data.
            db (AsyncSession): Database session.
            
        Returns:
            Transaction: Created transaction.
            
        Raises:
            HTTPException: If validation fails or insufficient budget.
        """
        # Get budget category and verify ownership
        result = await db.execute(
            select(BudgetCategory)
            .join(PayPeriod)
            .where(
                and_(
                    BudgetCategory.id == transaction_data.budget_category_id,
                    PayPeriod.user_id == user.id
                )
            )
        )
        budget_category = result.scalar_one_or_none()
        
        if not budget_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget category not found"
            )
        
        # Check if sufficient budget remaining
        if budget_category.remaining_amount < transaction_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient budget. Available: ${budget_category.remaining_amount}, Requested: ${transaction_data.amount}"
            )
        
        # Create transaction
        transaction_date = transaction_data.transaction_date or datetime.utcnow()
        
        db_transaction = Transaction(
            pay_period_id=budget_category.pay_period_id,
            budget_category_id=budget_category.id,
            amount=transaction_data.amount,
            description=transaction_data.description,
            transaction_date=transaction_date,
            source=transaction_data.source
        )
        
        # Update budget category remaining amount
        budget_category.remaining_amount -= transaction_data.amount
        
        db.add(db_transaction)
        await db.commit()
        await db.refresh(db_transaction)
        
        return db_transaction
    
    @staticmethod
    async def bulk_create_transactions(
        user: User,
        bulk_data: TransactionBulkCreate,
        db: AsyncSession
    ) -> List[Transaction]:
        """
        Create multiple transactions (for API integration).
        
        Args:
            user (User): Current user.
            bulk_data (TransactionBulkCreate): Bulk transaction data.
            db (AsyncSession): Database session.
            
        Returns:
            List[Transaction]: Created transactions.
            
        Raises:
            HTTPException: If any transaction fails validation.
        """
        created_transactions = []
        
        # Process each transaction
        for transaction_data in bulk_data.transactions:
            # Mark as API source
            transaction_data.source = TransactionSource.API
            
            try:
                transaction = await TransactionService.create_transaction(
                    user, transaction_data, db
                )
                created_transactions.append(transaction)
            except HTTPException as e:
                # Rollback all transactions if any fails
                await db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Bulk transaction failed: {e.detail}"
                )
        
        return created_transactions
    
    @staticmethod
    async def get_user_transactions(
        user: User,
        db: AsyncSession,
        pay_period_id: Optional[int] = None,
        category_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = 0
    ) -> List[Transaction]:
        """
        Get transactions for a user with optional filters.
        
        Args:
            user (User): Current user.
            db (AsyncSession): Database session.
            pay_period_id (Optional[int]): Filter by pay period.
            category_id (Optional[int]): Filter by category.
            limit (Optional[int]): Limit results.
            offset (Optional[int]): Offset for pagination.
            
        Returns:
            List[Transaction]: List of transactions.
        """
        query = (
            select(Transaction)
            .join(PayPeriod)
            .where(PayPeriod.user_id == user.id)
            .order_by(desc(Transaction.transaction_date))
        )
        
        if pay_period_id:
            query = query.where(Transaction.pay_period_id == pay_period_id)
        
        if category_id:
            query = query.where(Transaction.budget_category_id == category_id)
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_transaction_by_id(
        user: User,
        transaction_id: int,
        db: AsyncSession
    ) -> Optional[Transaction]:
        """
        Get a specific transaction by ID.
        
        Args:
            user (User): Current user.
            transaction_id (int): Transaction ID.
            db (AsyncSession): Database session.
            
        Returns:
            Optional[Transaction]: Transaction if found and belongs to user.
        """
        result = await db.execute(
            select(Transaction)
            .join(PayPeriod)
            .where(
                and_(
                    Transaction.id == transaction_id,
                    PayPeriod.user_id == user.id
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_transaction(
        user: User,
        transaction_id: int,
        update_data: TransactionUpdate,
        db: AsyncSession
    ) -> Optional[Transaction]:
        """
        Update a transaction.
        
        Args:
            user (User): Current user.
            transaction_id (int): Transaction ID.
            update_data (TransactionUpdate): Update data.
            db (AsyncSession): Database session.
            
        Returns:
            Optional[Transaction]: Updated transaction.
            
        Raises:
            HTTPException: If insufficient budget for amount change.
        """
        transaction = await TransactionService.get_transaction_by_id(
            user, transaction_id, db
        )
        if not transaction:
            return None
        
        # Handle amount change
        if update_data.amount is not None:
            # Get budget category
            result = await db.execute(
                select(BudgetCategory).where(
                    BudgetCategory.id == transaction.budget_category_id
                )
            )
            budget_category = result.scalar_one_or_none()
            
            if budget_category:
                # Calculate difference
                amount_diff = update_data.amount - transaction.amount
                
                # Check if sufficient budget for increase
                if amount_diff > 0 and budget_category.remaining_amount < amount_diff:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Insufficient budget for amount increase. Available: ${budget_category.remaining_amount}"
                    )
                
                # Update budget remaining amount
                budget_category.remaining_amount -= amount_diff
                transaction.amount = update_data.amount
        
        if update_data.description is not None:
            transaction.description = update_data.description
        
        await db.commit()
        await db.refresh(transaction)
        return transaction
    
    @staticmethod
    async def delete_transaction(
        user: User,
        transaction_id: int,
        db: AsyncSession
    ) -> bool:
        """
        Delete a transaction and restore budget amount.
        
        Args:
            user (User): Current user.
            transaction_id (int): Transaction ID.
            db (AsyncSession): Database session.
            
        Returns:
            bool: True if deleted, False if not found.
        """
        transaction = await TransactionService.get_transaction_by_id(
            user, transaction_id, db
        )
        if not transaction:
            return False
        
        # Restore budget amount
        result = await db.execute(
            select(BudgetCategory).where(
                BudgetCategory.id == transaction.budget_category_id
            )
        )
        budget_category = result.scalar_one_or_none()
        
        if budget_category:
            budget_category.remaining_amount += transaction.amount
        
        await db.delete(transaction)
        await db.commit()
        return True
    
    @staticmethod
    async def get_spending_summary(
        user: User,
        pay_period_id: int,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Get spending summary by category for a pay period.
        
        Args:
            user (User): Current user.
            pay_period_id (int): Pay period ID.
            db (AsyncSession): Database session.
            
        Returns:
            List[Dict[str, Any]]: Spending summary data.
        """
        # Verify pay period ownership
        result = await db.execute(
            select(PayPeriod).where(
                and_(PayPeriod.id == pay_period_id, PayPeriod.user_id == user.id)
            )
        )
        pay_period = result.scalar_one_or_none()
        
        if not pay_period:
            return []
        
        # Get spending by category
        result = await db.execute(
            select(
                BudgetCategory.id,
                BudgetCategory.name,
                BudgetCategory.allocated_amount,
                func.coalesce(func.sum(Transaction.amount), 0).label("total_spent"),
                func.count(Transaction.id).label("transaction_count")
            )
            .outerjoin(Transaction, BudgetCategory.id == Transaction.budget_category_id)
            .where(BudgetCategory.pay_period_id == pay_period_id)
            .group_by(BudgetCategory.id)
        )
        
        summary_data = []
        for row in result.fetchall():
            summary_data.append({
                "category_id": row.id,
                "category_name": row.name,
                "allocated_amount": row.allocated_amount,
                "total_spent": row.total_spent,
                "remaining_amount": row.allocated_amount - row.total_spent,
                "transaction_count": row.transaction_count
            })
        
        return summary_data
    
    @staticmethod
    async def get_spending_analytics(
        user: User,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get comprehensive spending analytics across all periods.
        
        Args:
            user (User): Current user.
            db (AsyncSession): Database session.
            
        Returns:
            Dict[str, Any]: Analytics data.
        """
        # Get total periods and income
        result = await db.execute(
            select(
                func.count(PayPeriod.id),
                func.coalesce(func.sum(PayPeriod.total_income), 0)
            )
            .where(PayPeriod.user_id == user.id)
        )
        period_count, total_income = result.fetchone()
        
        # Get total spent
        result = await db.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0))
            .join(PayPeriod)
            .where(PayPeriod.user_id == user.id)
        )
        total_spent = result.scalar()
        
        # Get top spending categories
        result = await db.execute(
            select(
                BudgetCategory.name,
                func.sum(Transaction.amount).label("total_spent")
            )
            .join(Transaction)
            .join(PayPeriod)
            .where(PayPeriod.user_id == user.id)
            .group_by(BudgetCategory.name)
            .order_by(desc(func.sum(Transaction.amount)))
            .limit(5)
        )
        
        top_categories = [
            {"category": row.name, "total_spent": row.total_spent}
            for row in result.fetchall()
        ]
        
        return {
            "total_periods": period_count,
            "total_income": total_income,
            "total_spent": total_spent,
            "average_spending_per_period": total_spent / period_count if period_count > 0 else 0,
            "top_categories": top_categories
        }