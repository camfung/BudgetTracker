"""
Transaction API endpoints for expense tracking and management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_session
from models.user import User
from schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionResponse,
    TransactionBulkCreate, TransactionSummary, SpendingAnalytics
)
from schemas.auth import MessageResponse
from services.auth_service import AuthService
from services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Create a new transaction.
    
    Args:
        transaction_data (TransactionCreate): Transaction data.
        current_user (User): Current authenticated user.
        db (AsyncSession): Database session.
        
    Returns:
        TransactionResponse: Created transaction data.
    """
    transaction = await TransactionService.create_transaction(
        current_user, transaction_data, db
    )
    return TransactionResponse.model_validate(transaction)


@router.post("/bulk", response_model=List[TransactionResponse])
async def bulk_create_transactions(
    bulk_data: TransactionBulkCreate,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Create multiple transactions (for API integration).
    
    Args:
        bulk_data (TransactionBulkCreate): Bulk transaction data.
        current_user (User): Current authenticated user.
        db (AsyncSession): Database session.
        
    Returns:
        List[TransactionResponse]: Created transactions.
    """
    transactions = await TransactionService.bulk_create_transactions(
        current_user, bulk_data, db
    )
    return [TransactionResponse.model_validate(t) for t in transactions]


@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    pay_period_id: Optional[int] = Query(None, description="Filter by pay period"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    limit: Optional[int] = Query(100, description="Limit results"),
    offset: Optional[int] = Query(0, description="Offset for pagination"),
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Get transactions for the current user with optional filters.
    
    Args:
        pay_period_id (Optional[int]): Filter by pay period.
        category_id (Optional[int]): Filter by category.
        limit (Optional[int]): Limit results.
        offset (Optional[int]): Offset for pagination.
        current_user (User): Current authenticated user.
        db (AsyncSession): Database session.
        
    Returns:
        List[TransactionResponse]: List of transactions.
    """
    transactions = await TransactionService.get_user_transactions(
        current_user, db, pay_period_id, category_id, limit, offset
    )
    return [TransactionResponse.model_validate(t) for t in transactions]


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Get a specific transaction by ID.
    
    Args:
        transaction_id (int): Transaction ID.
        current_user (User): Current authenticated user.
        db (AsyncSession): Database session.
        
    Returns:
        TransactionResponse: Transaction data.
        
    Raises:
        HTTPException: If transaction not found.
    """
    transaction = await TransactionService.get_transaction_by_id(
        current_user, transaction_id, db
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return TransactionResponse.model_validate(transaction)


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    update_data: TransactionUpdate,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Update a transaction.
    
    Args:
        transaction_id (int): Transaction ID.
        update_data (TransactionUpdate): Update data.
        current_user (User): Current authenticated user.
        db (AsyncSession): Database session.
        
    Returns:
        TransactionResponse: Updated transaction data.
        
    Raises:
        HTTPException: If transaction not found.
    """
    transaction = await TransactionService.update_transaction(
        current_user, transaction_id, update_data, db
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return TransactionResponse.model_validate(transaction)


@router.delete("/{transaction_id}", response_model=MessageResponse)
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Delete a transaction.
    
    Args:
        transaction_id (int): Transaction ID.
        current_user (User): Current authenticated user.
        db (AsyncSession): Database session.
        
    Returns:
        MessageResponse: Success message.
        
    Raises:
        HTTPException: If transaction not found.
    """
    deleted = await TransactionService.delete_transaction(
        current_user, transaction_id, db
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return MessageResponse(message="Transaction deleted successfully")


@router.get("/summary/{pay_period_id}")
async def get_spending_summary(
    pay_period_id: int,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Get spending summary by category for a pay period.
    
    Args:
        pay_period_id (int): Pay period ID.
        current_user (User): Current authenticated user.
        db (AsyncSession): Database session.
        
    Returns:
        List[dict]: Spending summary data.
    """
    summary = await TransactionService.get_spending_summary(
        current_user, pay_period_id, db
    )
    return summary


@router.get("/analytics/spending")
async def get_spending_analytics(
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Get comprehensive spending analytics across all periods.
    
    Args:
        current_user (User): Current authenticated user.
        db (AsyncSession): Database session.
        
    Returns:
        dict: Analytics data.
    """
    analytics = await TransactionService.get_spending_analytics(current_user, db)
    return analytics