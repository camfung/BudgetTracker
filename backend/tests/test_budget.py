"""
Tests for budget management functionality.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.budget import PayPeriod, BudgetCategory, PayPeriodStatus
from ..models.user import User
from ..services.budget_service import BudgetService
from ..schemas.budget import PayPeriodCreate, BudgetCategoryCreate, BudgetAllocationRequest


@pytest.mark.asyncio
class TestBudgetService:
    """Test budget service methods."""
    
    async def test_create_pay_period(self, db_session: AsyncSession, test_user: User):
        """Test creating a pay period."""
        start_date = date.today()
        end_date = start_date + timedelta(days=14)
        
        pay_period_data = PayPeriodCreate(
            start_date=start_date,
            end_date=end_date,
            total_income=Decimal("2000.00")
        )
        
        pay_period = await BudgetService.create_pay_period(
            test_user, pay_period_data, db_session
        )
        
        assert pay_period.user_id == test_user.id
        assert pay_period.start_date == start_date
        assert pay_period.end_date == end_date
        assert pay_period.total_income == Decimal("2000.00")
        assert pay_period.status == PayPeriodStatus.ACTIVE
    
    async def test_create_pay_period_invalid_dates(self, db_session: AsyncSession, test_user: User):
        """Test creating pay period with invalid dates."""
        start_date = date.today()
        end_date = start_date - timedelta(days=1)  # End before start
        
        pay_period_data = PayPeriodCreate(
            start_date=start_date,
            end_date=end_date,
            total_income=Decimal("2000.00")
        )
        
        with pytest.raises(Exception):  # Should raise HTTPException
            await BudgetService.create_pay_period(
                test_user, pay_period_data, db_session
            )
    
    async def test_get_user_pay_periods(self, db_session: AsyncSession, test_user: User):
        """Test getting user's pay periods."""
        # Create two pay periods
        start_date1 = date.today()
        end_date1 = start_date1 + timedelta(days=14)
        
        start_date2 = end_date1 + timedelta(days=1)
        end_date2 = start_date2 + timedelta(days=14)
        
        pay_period_data1 = PayPeriodCreate(
            start_date=start_date1,
            end_date=end_date1,
            total_income=Decimal("2000.00")
        )
        
        pay_period_data2 = PayPeriodCreate(
            start_date=start_date2,
            end_date=end_date2,
            total_income=Decimal("2200.00")
        )
        
        await BudgetService.create_pay_period(test_user, pay_period_data1, db_session)
        await BudgetService.create_pay_period(test_user, pay_period_data2, db_session)
        
        # Get all pay periods
        pay_periods = await BudgetService.get_user_pay_periods(test_user, db_session)
        
        assert len(pay_periods) == 2
        # Should be ordered by start_date descending
        assert pay_periods[0].start_date == start_date2
        assert pay_periods[1].start_date == start_date1
    
    async def test_allocate_budget(self, db_session: AsyncSession, test_user: User):
        """Test budget allocation to categories."""
        # Create pay period
        start_date = date.today()
        end_date = start_date + timedelta(days=14)
        
        pay_period_data = PayPeriodCreate(
            start_date=start_date,
            end_date=end_date,
            total_income=Decimal("2000.00")
        )
        
        pay_period = await BudgetService.create_pay_period(
            test_user, pay_period_data, db_session
        )
        
        # Allocate budget
        allocation_request = BudgetAllocationRequest(
            pay_period_id=pay_period.id,
            allocations=[
                BudgetCategoryCreate(name="Groceries", allocated_amount=Decimal("500.00")),
                BudgetCategoryCreate(name="Rent", allocated_amount=Decimal("1200.00")),
                BudgetCategoryCreate(name="Entertainment", allocated_amount=Decimal("200.00"))
            ]
        )
        
        categories = await BudgetService.allocate_budget(
            test_user, allocation_request, db_session
        )
        
        assert len(categories) == 3
        assert categories[0].name == "Groceries"
        assert categories[0].allocated_amount == Decimal("500.00")
        assert categories[0].remaining_amount == Decimal("500.00")
    
    async def test_allocate_budget_over_income(self, db_session: AsyncSession, test_user: User):
        """Test budget allocation exceeding income."""
        # Create pay period
        start_date = date.today()
        end_date = start_date + timedelta(days=14)
        
        pay_period_data = PayPeriodCreate(
            start_date=start_date,
            end_date=end_date,
            total_income=Decimal("1000.00")
        )
        
        pay_period = await BudgetService.create_pay_period(
            test_user, pay_period_data, db_session
        )
        
        # Try to allocate more than income
        allocation_request = BudgetAllocationRequest(
            pay_period_id=pay_period.id,
            allocations=[
                BudgetCategoryCreate(name="Rent", allocated_amount=Decimal("1500.00"))
            ]
        )
        
        with pytest.raises(Exception):  # Should raise HTTPException
            await BudgetService.allocate_budget(
                test_user, allocation_request, db_session
            )
    
    async def test_get_period_summary(self, db_session: AsyncSession, test_user: User):
        """Test getting period summary."""
        # Create pay period with categories
        start_date = date.today()
        end_date = start_date + timedelta(days=14)
        
        pay_period_data = PayPeriodCreate(
            start_date=start_date,
            end_date=end_date,
            total_income=Decimal("2000.00"),
            budget_categories=[
                BudgetCategoryCreate(name="Groceries", allocated_amount=Decimal("500.00"))
            ]
        )
        
        pay_period = await BudgetService.create_pay_period(
            test_user, pay_period_data, db_session
        )
        
        summary = await BudgetService.get_period_summary(
            test_user, pay_period.id, db_session
        )
        
        assert summary is not None
        assert summary["total_allocated"] == Decimal("500.00")
        assert summary["total_spent"] == Decimal("0.00")
        assert len(summary["categories_summary"]) == 1


@pytest.mark.asyncio
class TestBudgetEndpoints:
    """Test budget API endpoints."""
    
    async def test_create_pay_period_endpoint(self, client: AsyncClient, auth_headers: dict):
        """Test creating pay period via API."""
        start_date = date.today()
        end_date = start_date + timedelta(days=14)
        
        pay_period_data = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_income": "2000.00"
        }
        
        response = await client.post(
            "/api/budget/pay-periods",
            json=pay_period_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["total_income"] == "2000.00"
        assert data["status"] == "active"
    
    async def test_get_pay_periods_endpoint(self, client: AsyncClient, auth_headers: dict):
        """Test getting pay periods via API."""
        # Create a pay period first
        start_date = date.today()
        end_date = start_date + timedelta(days=14)
        
        pay_period_data = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_income": "2000.00"
        }
        
        await client.post(
            "/api/budget/pay-periods",
            json=pay_period_data,
            headers=auth_headers
        )
        
        # Get pay periods
        response = await client.get("/api/budget/pay-periods", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["total_income"] == "2000.00"
    
    async def test_allocate_budget_endpoint(self, client: AsyncClient, auth_headers: dict):
        """Test budget allocation via API."""
        # Create pay period
        start_date = date.today()
        end_date = start_date + timedelta(days=14)
        
        pay_period_data = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_income": "2000.00"
        }
        
        period_response = await client.post(
            "/api/budget/pay-periods",
            json=pay_period_data,
            headers=auth_headers
        )
        
        pay_period_id = period_response.json()["id"]
        
        # Allocate budget
        allocation_data = {
            "pay_period_id": pay_period_id,
            "allocations": [
                {"name": "Groceries", "allocated_amount": "500.00"},
                {"name": "Rent", "allocated_amount": "1200.00"}
            ]
        }
        
        response = await client.post(
            "/api/budget/allocate",
            json=allocation_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Groceries"
        assert data[0]["allocated_amount"] == "500.00"
    
    async def test_get_period_summary_endpoint(self, client: AsyncClient, auth_headers: dict):
        """Test getting period summary via API."""
        # Create pay period with categories
        start_date = date.today()
        end_date = start_date + timedelta(days=14)
        
        pay_period_data = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_income": "2000.00",
            "budget_categories": [
                {"name": "Groceries", "allocated_amount": "500.00"}
            ]
        }
        
        period_response = await client.post(
            "/api/budget/pay-periods",
            json=pay_period_data,
            headers=auth_headers
        )
        
        pay_period_id = period_response.json()["id"]
        
        # Get summary
        response = await client.get(
            f"/api/budget/pay-periods/{pay_period_id}/summary",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_allocated"] == "500.00"
        assert data["total_spent"] == "0.00"
    
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test unauthorized access to budget endpoints."""
        response = await client.get("/api/budget/pay-periods")
        assert response.status_code == 401
        
        response = await client.post("/api/budget/pay-periods", json={})
        assert response.status_code == 401


@pytest.mark.asyncio
class TestBudgetEdgeCases:
    """Test budget edge cases and error scenarios."""
    
    async def test_get_nonexistent_pay_period(self, client: AsyncClient, auth_headers: dict):
        """Test getting non-existent pay period."""
        response = await client.get("/api/budget/pay-periods/999", headers=auth_headers)
        assert response.status_code == 404
    
    async def test_allocate_to_nonexistent_period(self, client: AsyncClient, auth_headers: dict):
        """Test allocating budget to non-existent pay period."""
        allocation_data = {
            "pay_period_id": 999,
            "allocations": [
                {"name": "Test", "allocated_amount": "100.00"}
            ]
        }
        
        response = await client.post(
            "/api/budget/allocate",
            json=allocation_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_overlapping_pay_periods(self, client: AsyncClient, auth_headers: dict):
        """Test creating overlapping pay periods."""
        start_date = date.today()
        end_date = start_date + timedelta(days=14)
        
        pay_period_data = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_income": "2000.00"
        }
        
        # Create first pay period
        response1 = await client.post(
            "/api/budget/pay-periods",
            json=pay_period_data,
            headers=auth_headers
        )
        assert response1.status_code == 201
        
        # Try to create overlapping period
        overlapping_data = {
            "start_date": (start_date + timedelta(days=7)).isoformat(),
            "end_date": (end_date + timedelta(days=7)).isoformat(),
            "total_income": "2000.00"
        }
        
        response2 = await client.post(
            "/api/budget/pay-periods",
            json=overlapping_data,
            headers=auth_headers
        )
        
        assert response2.status_code == 400
        assert "overlaps" in response2.json()["message"]