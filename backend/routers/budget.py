"""
Budget API endpoints for pay periods and budget categories.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_session
from models.user import User
from models.budget import PayPeriodStatus
from schemas.budget import (
    PayPeriodCreate, PayPeriodUpdate, PayPeriodResponse,
    BudgetAllocationRequest, BudgetCategoryResponse, PeriodSummaryResponse
)
from schemas.auth import MessageResponse
from services.auth_service import AuthService
from services.budget_service import BudgetService

router = APIRouter(prefix="/budget", tags=["budget"])


@router.post("/pay-periods", response_model=PayPeriodResponse, status_code=status.HTTP_201_CREATED)
async def create_pay_period(
    pay_period_data: PayPeriodCreate,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Create a new pay period.
    
    Args:
        pay_period_data (PayPeriodCreate): Pay period data.
        current_user (User): Current authenticated user.
        db (AsyncSession): Database session.
        
    Returns:
        PayPeriodResponse: Created pay period data.
    """
    pay_period = await BudgetService.create_pay_period(
        current_user, pay_period_data, db
    )
    return PayPeriodResponse.model_validate(pay_period)


@router.get("/pay-periods", response_model=List[PayPeriodResponse])
async def get_pay_periods(
    status_filter: Optional[PayPeriodStatus] = Query(None, description="Filter by status"),
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Get all pay periods for the current user.
    
    Args:
        status_filter (Optional[PayPeriodStatus]): Filter by pay period status.
        current_user (User): Current authenticated user.
        db (AsyncSession): Database session.
        
    Returns:
        List[PayPeriodResponse]: List of pay periods.
    """
    pay_periods = await BudgetService.get_user_pay_periods(
        current_user, db, status_filter
    )
    return [PayPeriodResponse.model_validate(pp) for pp in pay_periods]


@router.get("/pay-periods/{pay_period_id}", response_model=PayPeriodResponse)
async def get_pay_period(
    pay_period_id: int,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Get a specific pay period by ID.
    
    Args:
        pay_period_id (int): Pay period ID.
        current_user (User): Current authenticated user.
        db (AsyncSession): Database session.
        
    Returns:
        PayPeriodResponse: Pay period data.
        
    Raises:
        HTTPException: If pay period not found.
    """
    pay_period = await BudgetService.get_pay_period_by_id(
        current_user, pay_period_id, db
    )
    
    if not pay_period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pay period not found"
        )
    
    return PayPeriodResponse.model_validate(pay_period)


@router.put("/pay-periods/{pay_period_id}", response_model=PayPeriodResponse)
async def update_pay_period(
    pay_period_id: int,
    update_data: PayPeriodUpdate,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Update a pay period.
    
    Args:
        pay_period_id (int): Pay period ID.
        update_data (PayPeriodUpdate): Update data.
        current_user (User): Current authenticated user.
        db (AsyncSession): Database session.
        
    Returns:
        PayPeriodResponse: Updated pay period data.
        
    Raises:
        HTTPException: If pay period not found.
    """
    pay_period = await BudgetService.update_pay_period(
        current_user, pay_period_id, update_data, db
    )
    
    if not pay_period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pay period not found"
        )
    
    return PayPeriodResponse.model_validate(pay_period)


@router.post("/allocate", response_model=List[BudgetCategoryResponse])
async def allocate_budget(
    allocation_request: BudgetAllocationRequest,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Allocate budget to categories for a pay period.
    
    Args:
        allocation_request (BudgetAllocationRequest): Budget allocation data.
        current_user (User): Current authenticated user.
        db (AsyncSession): Database session.
        
    Returns:
        List[BudgetCategoryResponse]: Created budget categories.
    """
    categories = await BudgetService.allocate_budget(
        current_user, allocation_request, db
    )
    return [BudgetCategoryResponse.model_validate(cat) for cat in categories]


@router.get("/pay-periods/{pay_period_id}/summary")
async def get_period_summary(
    pay_period_id: int,
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Get spending summary for a pay period.
    
    Args:
        pay_period_id (int): Pay period ID.
        current_user (User): Current authenticated user.
        db (AsyncSession): Database session.
        
    Returns:
        dict: Period summary data.
        
    Raises:
        HTTPException: If pay period not found.
    """
    summary = await BudgetService.get_period_summary(
        current_user, pay_period_id, db
    )
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pay period not found"
        )
    
    return summary


@router.get("/pay-periods/active/current", response_model=PayPeriodResponse)
async def get_current_active_period(
    current_user: User = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Get the current active pay period.
    
    Args:
        current_user (User): Current authenticated user.
        db (AsyncSession): Database session.
        
    Returns:
        PayPeriodResponse: Current active pay period.
        
    Raises:
        HTTPException: If no active period found.
    """
    pay_periods = await BudgetService.get_user_pay_periods(
        current_user, db, PayPeriodStatus.ACTIVE
    )
    
    if not pay_periods:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active pay period found"
        )
    
    # Return the most recent active period
    current_period = pay_periods[0]
    return PayPeriodResponse.model_validate(current_period)