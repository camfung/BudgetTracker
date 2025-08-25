"""
Tests for transaction management functionality.
"""

import pytest
from datetime import date, timedelta, datetime
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from ..models.budget import PayPeriod, BudgetCategory
from ..models.transaction import Transaction, TransactionSource
from ..services.transaction_service import TransactionService
from ..services.budget_service import BudgetService
from ..schemas.budget import PayPeriodCreate, BudgetCategoryCreate
from ..schemas.transaction import TransactionCreate, TransactionUpdate, TransactionBulkCreate


@pytest.mark.asyncio
class TestTransactionService:
    """Test transaction service methods."""
    
    async def test_create_transaction(self, db_session: AsyncSession, test_user: User):
        """Test creating a transaction."""
        # Create pay period with budget category
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
        
        category = pay_period.budget_categories[0]
        
        # Create transaction
        transaction_data = TransactionCreate(
            budget_category_id=category.id,
            amount=Decimal("50.00"),
            description="Grocery shopping",
            source=TransactionSource.MANUAL
        )
        
        transaction = await TransactionService.create_transaction(
            test_user, transaction_data, db_session
        )
        
        assert transaction.amount == Decimal("50.00")
        assert transaction.description == "Grocery shopping"
        assert transaction.source == TransactionSource.MANUAL
        
        # Check that budget category remaining amount was updated
        await db_session.refresh(category)
        assert category.remaining_amount == Decimal("450.00")
    
    async def test_create_transaction_insufficient_budget(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test creating transaction with insufficient budget."""
        # Create pay period with small budget category
        start_date = date.today()
        end_date = start_date + timedelta(days=14)
        
        pay_period_data = PayPeriodCreate(
            start_date=start_date,
            end_date=end_date,
            total_income=Decimal("100.00"),
            budget_categories=[
                BudgetCategoryCreate(name="Entertainment", allocated_amount=Decimal("50.00"))
            ]
        )
        
        pay_period = await BudgetService.create_pay_period(
            test_user, pay_period_data, db_session
        )
        
        category = pay_period.budget_categories[0]
        
        # Try to create transaction exceeding budget
        transaction_data = TransactionCreate(
            budget_category_id=category.id,
            amount=Decimal("100.00"),  # More than allocated
            description="Expensive entertainment"
        )
        
        with pytest.raises(Exception):  # Should raise HTTPException
            await TransactionService.create_transaction(
                test_user, transaction_data, db_session
            )
    
    async def test_bulk_create_transactions(self, db_session: AsyncSession, test_user: User):
        """Test bulk transaction creation."""
        # Create pay period with budget categories
        start_date = date.today()
        end_date = start_date + timedelta(days=14)
        
        pay_period_data = PayPeriodCreate(
            start_date=start_date,
            end_date=end_date,
            total_income=Decimal("2000.00"),
            budget_categories=[
                BudgetCategoryCreate(name="Groceries", allocated_amount=Decimal("500.00")),
                BudgetCategoryCreate(name="Gas", allocated_amount=Decimal("200.00"))
            ]
        )
        
        pay_period = await BudgetService.create_pay_period(
            test_user, pay_period_data, db_session
        )
        
        categories = pay_period.budget_categories
        
        # Create bulk transactions
        bulk_data = TransactionBulkCreate(
            transactions=[
                TransactionCreate(
                    budget_category_id=categories[0].id,
                    amount=Decimal("75.00"),
                    description="Walmart"
                ),
                TransactionCreate(
                    budget_category_id=categories[1].id,
                    amount=Decimal("45.00"),
                    description="Shell Gas"
                )
            ]
        )
        
        transactions = await TransactionService.bulk_create_transactions(
            test_user, bulk_data, db_session
        )
        
        assert len(transactions) == 2
        assert all(t.source == TransactionSource.API for t in transactions)
    
    async def test_get_user_transactions(self, db_session: AsyncSession, test_user: User):
        """Test getting user transactions."""
        # Create pay period with transactions
        start_date = date.today()
        end_date = start_date + timedelta(days=14)
        
        pay_period_data = PayPeriodCreate(
            start_date=start_date,
            end_date=end_date,
            total_income=Decimal("1000.00"),
            budget_categories=[
                BudgetCategoryCreate(name="Food", allocated_amount=Decimal("300.00"))
            ]
        )
        
        pay_period = await BudgetService.create_pay_period(
            test_user, pay_period_data, db_session
        )
        
        category = pay_period.budget_categories[0]
        
        # Create multiple transactions
        for i in range(3):
            transaction_data = TransactionCreate(
                budget_category_id=category.id,
                amount=Decimal("25.00"),
                description=f"Transaction {i+1}"
            )
            await TransactionService.create_transaction(
                test_user, transaction_data, db_session
            )
        
        # Get all transactions
        transactions = await TransactionService.get_user_transactions(
            test_user, db_session
        )
        
        assert len(transactions) == 3
        # Should be ordered by transaction_date descending
        assert transactions[0].description == "Transaction 3"
    
    async def test_update_transaction(self, db_session: AsyncSession, test_user: User):
        """Test updating a transaction."""
        # Create pay period with transaction
        start_date = date.today()
        end_date = start_date + timedelta(days=14)
        
        pay_period_data = PayPeriodCreate(
            start_date=start_date,
            end_date=end_date,
            total_income=Decimal("1000.00"),
            budget_categories=[
                BudgetCategoryCreate(name="Food", allocated_amount=Decimal("300.00"))
            ]
        )
        
        pay_period = await BudgetService.create_pay_period(
            test_user, pay_period_data, db_session
        )
        
        category = pay_period.budget_categories[0]
        
        transaction_data = TransactionCreate(
            budget_category_id=category.id,
            amount=Decimal("50.00"),
            description="Original description"
        )
        
        transaction = await TransactionService.create_transaction(
            test_user, transaction_data, db_session
        )
        
        # Update transaction
        update_data = TransactionUpdate(
            description="Updated description",
            amount=Decimal("75.00")
        )
        
        updated_transaction = await TransactionService.update_transaction(
            test_user, transaction.id, update_data, db_session
        )
        
        assert updated_transaction.description == "Updated description"
        assert updated_transaction.amount == Decimal("75.00")
    
    async def test_delete_transaction(self, db_session: AsyncSession, test_user: User):
        """Test deleting a transaction."""
        # Create pay period with transaction
        start_date = date.today()
        end_date = start_date + timedelta(days=14)
        
        pay_period_data = PayPeriodCreate(
            start_date=start_date,
            end_date=end_date,
            total_income=Decimal("1000.00"),
            budget_categories=[
                BudgetCategoryCreate(name="Food", allocated_amount=Decimal("300.00"))
            ]
        )
        
        pay_period = await BudgetService.create_pay_period(
            test_user, pay_period_data, db_session
        )
        
        category = pay_period.budget_categories[0]
        original_remaining = category.remaining_amount
        
        transaction_data = TransactionCreate(
            budget_category_id=category.id,
            amount=Decimal("50.00"),
            description="To be deleted"
        )
        
        transaction = await TransactionService.create_transaction(
            test_user, transaction_data, db_session
        )
        
        # Delete transaction
        deleted = await TransactionService.delete_transaction(
            test_user, transaction.id, db_session
        )
        
        assert deleted is True
        
        # Check that budget was restored
        await db_session.refresh(category)
        assert category.remaining_amount == original_remaining
    
    async def test_get_spending_analytics(self, db_session: AsyncSession, test_user: User):
        """Test getting spending analytics."""
        # Create pay period with transactions
        start_date = date.today()
        end_date = start_date + timedelta(days=14)
        
        pay_period_data = PayPeriodCreate(
            start_date=start_date,
            end_date=end_date,
            total_income=Decimal("1000.00"),
            budget_categories=[
                BudgetCategoryCreate(name="Food", allocated_amount=Decimal("300.00")),
                BudgetCategoryCreate(name="Gas", allocated_amount=Decimal("200.00"))
            ]
        )
        
        pay_period = await BudgetService.create_pay_period(
            test_user, pay_period_data, db_session
        )
        
        # Create transactions
        for category in pay_period.budget_categories:
            transaction_data = TransactionCreate(
                budget_category_id=category.id,
                amount=Decimal("50.00"),
                description=f"Spending on {category.name}"
            )
            await TransactionService.create_transaction(
                test_user, transaction_data, db_session
            )
        
        # Get analytics
        analytics = await TransactionService.get_spending_analytics(test_user, db_session)
        
        assert analytics["total_periods"] == 1
        assert analytics["total_income"] == Decimal("1000.00")
        assert analytics["total_spent"] == Decimal("100.00")
        assert len(analytics["top_categories"]) <= 5


@pytest.mark.asyncio
class TestTransactionEndpoints:
    """Test transaction API endpoints."""
    
    async def create_test_budget_category(
        self, client: AsyncClient, auth_headers: dict
    ) -> dict:
        """Helper to create a budget category for testing."""
        # Create pay period
        start_date = date.today()
        end_date = start_date + timedelta(days=14)
        
        pay_period_data = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_income": "1000.00",
            "budget_categories": [
                {"name": "Test Category", "allocated_amount": "300.00"}
            ]
        }
        
        response = await client.post(
            "/api/budget/pay-periods",
            json=pay_period_data,
            headers=auth_headers
        )
        
        pay_period = response.json()
        return pay_period["budget_categories"][0]
    
    async def test_create_transaction_endpoint(self, client: AsyncClient, auth_headers: dict):
        """Test creating transaction via API."""
        category = await self.create_test_budget_category(client, auth_headers)
        
        transaction_data = {
            "budget_category_id": category["id"],
            "amount": "50.00",
            "description": "Test transaction",
            "source": "manual"
        }
        
        response = await client.post(
            "/api/transactions/",
            json=transaction_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == "50.00"
        assert data["description"] == "Test transaction"
    
    async def test_get_transactions_endpoint(self, client: AsyncClient, auth_headers: dict):
        """Test getting transactions via API."""
        category = await self.create_test_budget_category(client, auth_headers)
        
        # Create a transaction
        transaction_data = {
            "budget_category_id": category["id"],
            "amount": "25.00",
            "description": "Test transaction"
        }
        
        await client.post(
            "/api/transactions/",
            json=transaction_data,
            headers=auth_headers
        )
        
        # Get transactions
        response = await client.get("/api/transactions/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["amount"] == "25.00"
    
    async def test_bulk_create_transactions_endpoint(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test bulk transaction creation via API."""
        category = await self.create_test_budget_category(client, auth_headers)
        
        bulk_data = {
            "transactions": [
                {
                    "budget_category_id": category["id"],
                    "amount": "30.00",
                    "description": "Bulk transaction 1"
                },
                {
                    "budget_category_id": category["id"],
                    "amount": "40.00",
                    "description": "Bulk transaction 2"
                }
            ]
        }
        
        response = await client.post(
            "/api/transactions/bulk",
            json=bulk_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(t["source"] == "api" for t in data)
    
    async def test_update_transaction_endpoint(self, client: AsyncClient, auth_headers: dict):
        """Test updating transaction via API."""
        category = await self.create_test_budget_category(client, auth_headers)
        
        # Create transaction
        transaction_data = {
            "budget_category_id": category["id"],
            "amount": "50.00",
            "description": "Original description"
        }
        
        create_response = await client.post(
            "/api/transactions/",
            json=transaction_data,
            headers=auth_headers
        )
        
        transaction_id = create_response.json()["id"]
        
        # Update transaction
        update_data = {
            "description": "Updated description",
            "amount": "75.00"
        }
        
        response = await client.put(
            f"/api/transactions/{transaction_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["amount"] == "75.00"
    
    async def test_delete_transaction_endpoint(self, client: AsyncClient, auth_headers: dict):
        """Test deleting transaction via API."""
        category = await self.create_test_budget_category(client, auth_headers)
        
        # Create transaction
        transaction_data = {
            "budget_category_id": category["id"],
            "amount": "50.00",
            "description": "To be deleted"
        }
        
        create_response = await client.post(
            "/api/transactions/",
            json=transaction_data,
            headers=auth_headers
        )
        
        transaction_id = create_response.json()["id"]
        
        # Delete transaction
        response = await client.delete(
            f"/api/transactions/{transaction_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Transaction deleted successfully"
    
    async def test_get_spending_analytics_endpoint(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting spending analytics via API."""
        category = await self.create_test_budget_category(client, auth_headers)
        
        # Create some transactions
        for i in range(2):
            transaction_data = {
                "budget_category_id": category["id"],
                "amount": "25.00",
                "description": f"Analytics test {i+1}"
            }
            
            await client.post(
                "/api/transactions/",
                json=transaction_data,
                headers=auth_headers
            )
        
        # Get analytics
        response = await client.get("/api/transactions/analytics/spending", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_periods"] == 1
        assert data["total_spent"] == "50.00"
    
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test unauthorized access to transaction endpoints."""
        response = await client.get("/api/transactions/")
        assert response.status_code == 401
        
        response = await client.post("/api/transactions/", json={})
        assert response.status_code == 401


@pytest.mark.asyncio
class TestTransactionEdgeCases:
    """Test transaction edge cases and error scenarios."""
    
    async def test_create_transaction_invalid_category(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating transaction with invalid category ID."""
        transaction_data = {
            "budget_category_id": 999,
            "amount": "50.00",
            "description": "Invalid category"
        }
        
        response = await client.post(
            "/api/transactions/",
            json=transaction_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_get_nonexistent_transaction(self, client: AsyncClient, auth_headers: dict):
        """Test getting non-existent transaction."""
        response = await client.get("/api/transactions/999", headers=auth_headers)
        assert response.status_code == 404
    
    async def test_update_nonexistent_transaction(self, client: AsyncClient, auth_headers: dict):
        """Test updating non-existent transaction."""
        update_data = {
            "description": "Updated"
        }
        
        response = await client.put(
            "/api/transactions/999",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_delete_nonexistent_transaction(self, client: AsyncClient, auth_headers: dict):
        """Test deleting non-existent transaction."""
        response = await client.delete("/api/transactions/999", headers=auth_headers)
        assert response.status_code == 404