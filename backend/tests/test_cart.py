"""
Cart Management Tests for NitePutter Pro
Tests cart operations, persistence, and calculations
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app
from app.database import get_database
from datetime import datetime, UTC
import asyncio

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def test_db():
    """Get test database"""
    db = await get_database()
    yield db
    # Cleanup after tests
    await db.carts.delete_many({"session_id": {"$regex": "^test_"}})

@pytest.fixture
async def test_product(test_db):
    """Create test product"""
    product = {
        "sku": "TEST_CART_001",
        "name": "Test Product for Cart",
        "slug": "test-cart-product",
        "category": "basic",
        "price": 149.99,
        "inventory": {
            "quantity": 100,
            "reserved_quantity": 0,
            "track_inventory": True
        },
        "created_at": datetime.now(UTC)
    }
    result = await test_db.products.insert_one(product)
    product["id"] = str(result.inserted_id)
    return product

@pytest.fixture
async def auth_headers(client: AsyncClient, test_db):
    """Get authenticated user headers"""
    # Register user
    user_data = {
        "email": "test_cart_user@example.com",
        "password": "SecurePass123!",
        "first_name": "Cart",
        "last_name": "Test"
    }
    response = await client.post("/api/auth/register", json=user_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestCartOperations:
    """Test cart CRUD operations"""
    
    async def test_create_cart(self, client: AsyncClient, test_product: dict):
        """Test creating a new cart"""
        session_id = "test_session_001"
        headers = {"X-Session-Id": session_id}
        
        cart_item = {
            "product_id": test_product["id"],
            "quantity": 2
        }
        
        response = await client.post("/api/cart/items", json=cart_item, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["session_id"] == session_id
        assert len(data["items"]) == 1
        assert data["items"][0]["product_id"] == test_product["id"]
        assert data["items"][0]["quantity"] == 2
    
    async def test_add_to_existing_cart(self, client: AsyncClient, test_product: dict, test_db):
        """Test adding items to existing cart"""
        session_id = "test_session_002"
        headers = {"X-Session-Id": session_id}
        
        # Add first item
        cart_item = {
            "product_id": test_product["id"],
            "quantity": 1
        }
        await client.post("/api/cart/items", json=cart_item, headers=headers)
        
        # Add more of same item
        response = await client.post("/api/cart/items", json=cart_item, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2
    
    async def test_get_cart(self, client: AsyncClient, test_product: dict):
        """Test retrieving cart"""
        session_id = "test_session_003"
        headers = {"X-Session-Id": session_id}
        
        # Add item to cart
        cart_item = {
            "product_id": test_product["id"],
            "quantity": 3
        }
        await client.post("/api/cart/items", json=cart_item, headers=headers)
        
        # Get cart
        response = await client.get("/api/cart", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["session_id"] == session_id
        assert len(data["items"]) == 1
        assert "subtotal" in data
        assert "total_items" in data
    
    async def test_update_cart_item(self, client: AsyncClient, test_product: dict):
        """Test updating cart item quantity"""
        session_id = "test_session_004"
        headers = {"X-Session-Id": session_id}
        
        # Add item to cart
        cart_item = {
            "product_id": test_product["id"],
            "quantity": 2
        }
        await client.post("/api/cart/items", json=cart_item, headers=headers)
        
        # Update quantity
        update_data = {"quantity": 5}
        response = await client.put(
            f"/api/cart/items/{test_product['id']}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["items"][0]["quantity"] == 5
    
    async def test_remove_cart_item(self, client: AsyncClient, test_product: dict):
        """Test removing item from cart"""
        session_id = "test_session_005"
        headers = {"X-Session-Id": session_id}
        
        # Add item to cart
        cart_item = {
            "product_id": test_product["id"],
            "quantity": 2
        }
        await client.post("/api/cart/items", json=cart_item, headers=headers)
        
        # Remove item
        response = await client.delete(
            f"/api/cart/items/{test_product['id']}",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["items"]) == 0
    
    async def test_clear_cart(self, client: AsyncClient, test_product: dict):
        """Test clearing entire cart"""
        session_id = "test_session_006"
        headers = {"X-Session-Id": session_id}
        
        # Add multiple items
        for i in range(3):
            cart_item = {
                "product_id": test_product["id"],
                "quantity": i + 1
            }
            await client.post("/api/cart/items", json=cart_item, headers=headers)
        
        # Clear cart
        response = await client.delete("/api/cart", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify cart is empty
        get_response = await client.get("/api/cart", headers=headers)
        data = get_response.json()
        assert len(data["items"]) == 0


class TestCartCalculations:
    """Test cart price calculations"""
    
    async def test_cart_subtotal(self, client: AsyncClient, test_product: dict):
        """Test cart subtotal calculation"""
        session_id = "test_calc_001"
        headers = {"X-Session-Id": session_id}
        
        # Add items with known prices
        cart_item = {
            "product_id": test_product["id"],
            "quantity": 3
        }
        await client.post("/api/cart/items", json=cart_item, headers=headers)
        
        # Get cart with calculations
        response = await client.get("/api/cart", headers=headers)
        data = response.json()
        
        expected_subtotal = test_product["price"] * 3
        assert data["subtotal"] == pytest.approx(expected_subtotal, rel=0.01)
    
    async def test_cart_with_coupon(self, client: AsyncClient, test_product: dict, test_db):
        """Test cart with coupon applied"""
        session_id = "test_coupon_001"
        headers = {"X-Session-Id": session_id}
        
        # Create test coupon
        coupon = {
            "code": "TEST10",
            "type": "percentage",
            "value": 10,
            "is_active": True,
            "min_purchase": 100,
            "valid_from": datetime.now(UTC),
            "valid_until": datetime.now(UTC).replace(year=datetime.now(UTC).year + 1)
        }
        await test_db.coupons.insert_one(coupon)
        
        # Add items to cart
        cart_item = {
            "product_id": test_product["id"],
            "quantity": 2
        }
        await client.post("/api/cart/items", json=cart_item, headers=headers)
        
        # Apply coupon
        response = await client.post(
            "/api/cart/coupon",
            json={"code": "TEST10"},
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["coupon_code"] == "TEST10"
        assert "discount_amount" in data
        
        # Verify discount calculation
        subtotal = test_product["price"] * 2
        expected_discount = subtotal * 0.1
        assert data["discount_amount"] == pytest.approx(expected_discount, rel=0.01)
    
    async def test_cart_tax_calculation(self, client: AsyncClient, test_product: dict):
        """Test cart tax calculation"""
        session_id = "test_tax_001"
        headers = {"X-Session-Id": session_id}
        
        # Add items to cart
        cart_item = {
            "product_id": test_product["id"],
            "quantity": 1
        }
        await client.post("/api/cart/items", json=cart_item, headers=headers)
        
        # Set shipping address for tax calculation
        address = {
            "state": "CA",
            "zip_code": "90210"
        }
        response = await client.post(
            "/api/cart/shipping-address",
            json=address,
            headers=headers
        )
        
        # Get cart with tax
        response = await client.get("/api/cart", headers=headers)
        data = response.json()
        
        assert "tax" in data
        assert data["tax"] > 0  # CA has sales tax
        assert "total" in data
        assert data["total"] > data["subtotal"]


class TestCartPersistence:
    """Test cart persistence and session management"""
    
    async def test_cart_persistence(self, client: AsyncClient, test_product: dict, test_db):
        """Test cart persists across requests"""
        session_id = "test_persist_001"
        headers = {"X-Session-Id": session_id}
        
        # Add item to cart
        cart_item = {
            "product_id": test_product["id"],
            "quantity": 2
        }
        await client.post("/api/cart/items", json=cart_item, headers=headers)
        
        # Simulate new request with same session
        new_headers = {"X-Session-Id": session_id}
        response = await client.get("/api/cart", headers=new_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2
    
    async def test_cart_merge_on_login(self, client: AsyncClient, test_product: dict, auth_headers: dict):
        """Test cart merging when user logs in"""
        # Create anonymous cart
        session_id = "test_merge_001"
        anon_headers = {"X-Session-Id": session_id}
        
        cart_item = {
            "product_id": test_product["id"],
            "quantity": 1
        }
        await client.post("/api/cart/items", json=cart_item, headers=anon_headers)
        
        # Login and merge cart
        merge_headers = {**auth_headers, "X-Session-Id": session_id}
        response = await client.post("/api/cart/merge", headers=merge_headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Get user cart
        user_cart = await client.get("/api/cart", headers=auth_headers)
        data = user_cart.json()
        assert len(data["items"]) >= 1
    
    async def test_cart_expiration(self, client: AsyncClient, test_product: dict, test_db):
        """Test cart expiration"""
        session_id = "test_expire_001"
        headers = {"X-Session-Id": session_id}
        
        # Add item to cart
        cart_item = {
            "product_id": test_product["id"],
            "quantity": 1
        }
        await client.post("/api/cart/items", json=cart_item, headers=headers)
        
        # Simulate expiration by updating cart timestamp
        from datetime import timedelta
        expired_time = datetime.now(UTC) - timedelta(days=31)
        await test_db.carts.update_one(
            {"session_id": session_id},
            {"$set": {"updated_at": expired_time}}
        )
        
        # Try to get expired cart
        response = await client.get("/api/cart", headers=headers)
        data = response.json()
        assert len(data.get("items", [])) == 0  # Should return empty cart


class TestInventoryValidation:
    """Test inventory validation in cart"""
    
    async def test_insufficient_inventory(self, client: AsyncClient, test_product: dict, test_db):
        """Test adding more items than available inventory"""
        session_id = "test_inventory_001"
        headers = {"X-Session-Id": session_id}
        
        # Update product to have limited inventory
        await test_db.products.update_one(
            {"sku": test_product["sku"]},
            {"$set": {"inventory.quantity": 5}}
        )
        
        # Try to add more than available
        cart_item = {
            "product_id": test_product["id"],
            "quantity": 10
        }
        response = await client.post("/api/cart/items", json=cart_item, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "insufficient inventory" in response.json()["detail"].lower()
    
    async def test_out_of_stock_product(self, client: AsyncClient, test_product: dict, test_db):
        """Test adding out of stock product"""
        session_id = "test_oos_001"
        headers = {"X-Session-Id": session_id}
        
        # Set product as out of stock
        await test_db.products.update_one(
            {"sku": test_product["sku"]},
            {"$set": {"inventory.quantity": 0}}
        )
        
        # Try to add to cart
        cart_item = {
            "product_id": test_product["id"],
            "quantity": 1
        }
        response = await client.post("/api/cart/items", json=cart_item, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "out of stock" in response.json()["detail"].lower()
    
    async def test_validate_cart_before_checkout(self, client: AsyncClient, test_product: dict, test_db):
        """Test cart validation before checkout"""
        session_id = "test_validate_001"
        headers = {"X-Session-Id": session_id}
        
        # Add item to cart
        cart_item = {
            "product_id": test_product["id"],
            "quantity": 2
        }
        await client.post("/api/cart/items", json=cart_item, headers=headers)
        
        # Reduce inventory after adding to cart
        await test_db.products.update_one(
            {"sku": test_product["sku"]},
            {"$set": {"inventory.quantity": 1}}
        )
        
        # Validate cart
        response = await client.post("/api/cart/validate", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0
        assert any("inventory" in error.lower() for error in data["errors"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])