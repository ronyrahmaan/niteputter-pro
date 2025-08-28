"""
Product Tests for NitePutter Pro
Tests product CRUD operations and search functionality
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app
from app.database import get_database
from bson import ObjectId
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
    await db.products.delete_many({"sku": {"$regex": "^TEST_"}})

@pytest.fixture
async def admin_token(client: AsyncClient, test_db):
    """Get admin authentication token"""
    # Create admin user
    admin_data = {
        "email": "test_admin@niteputter.com",
        "password": "AdminPass123!",
        "first_name": "Test",
        "last_name": "Admin",
        "role": "admin"
    }
    await test_db.users.insert_one({
        **admin_data,
        "password_hash": "$2b$12$hashed_password_here",
        "status": "active",
        "created_at": datetime.now(UTC)
    })
    
    # Login to get token
    response = await client.post("/api/auth/login", json={
        "email": admin_data["email"],
        "password": admin_data["password"]
    })
    return response.json()["access_token"]

@pytest.fixture
async def sample_product():
    """Sample product data"""
    return {
        "sku": "TEST_PRODUCT_001",
        "name": "Test NitePutter LED Light",
        "slug": "test-niteputter-led",
        "category": "basic",
        "status": "active",
        "short_description": "Test product for unit testing",
        "description": "Detailed test product description",
        "price": 149.99,
        "compare_at_price": 199.99,
        "images": [
            {
                "url": "https://example.com/test-image.jpg",
                "alt_text": "Test product image",
                "is_primary": True,
                "display_order": 1
            }
        ],
        "features": ["Test Feature 1", "Test Feature 2"],
        "specifications": {
            "battery_life": "10 hours",
            "weight": "150g",
            "warranty": "1 year"
        },
        "inventory": {
            "quantity": 100,
            "reserved_quantity": 0,
            "low_stock_threshold": 10,
            "track_inventory": True,
            "allow_backorder": False
        }
    }


class TestProductCRUD:
    """Test product CRUD operations"""
    
    async def test_create_product(self, client: AsyncClient, admin_token: str, sample_product: dict):
        """Test creating a new product"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await client.post(
            "/api/products",
            json=sample_product,
            headers=headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["sku"] == sample_product["sku"]
        assert data["name"] == sample_product["name"]
        assert data["price"] == sample_product["price"]
        assert "id" in data
    
    async def test_create_duplicate_sku(self, client: AsyncClient, admin_token: str, sample_product: dict):
        """Test creating product with duplicate SKU"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create first product
        await client.post("/api/products", json=sample_product, headers=headers)
        
        # Try to create duplicate
        response = await client.post("/api/products", json=sample_product, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()
    
    async def test_get_product(self, client: AsyncClient, admin_token: str, sample_product: dict):
        """Test retrieving a product"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product
        create_response = await client.post("/api/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Get product
        response = await client.get(f"/api/products/{product_id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == product_id
        assert data["sku"] == sample_product["sku"]
    
    async def test_get_product_by_slug(self, client: AsyncClient, admin_token: str, sample_product: dict):
        """Test retrieving product by slug"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product
        await client.post("/api/products", json=sample_product, headers=headers)
        
        # Get by slug
        response = await client.get(f"/api/products/slug/{sample_product['slug']}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["slug"] == sample_product["slug"]
    
    async def test_list_products(self, client: AsyncClient, admin_token: str):
        """Test listing products"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create multiple products
        for i in range(3):
            product = {
                "sku": f"TEST_LIST_{i}",
                "name": f"Test Product {i}",
                "slug": f"test-product-{i}",
                "category": "basic",
                "price": 100 + i * 10,
                "inventory": {"quantity": 50}
            }
            await client.post("/api/products", json=product, headers=headers)
        
        # List products
        response = await client.get("/api/products")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 3
    
    async def test_list_products_with_filters(self, client: AsyncClient):
        """Test listing products with filters"""
        # Filter by category
        response = await client.get("/api/products?category=basic")
        assert response.status_code == status.HTTP_200_OK
        
        # Filter by price range
        response = await client.get("/api/products?min_price=100&max_price=200")
        assert response.status_code == status.HTTP_200_OK
        
        # Filter by availability
        response = await client.get("/api/products?in_stock=true")
        assert response.status_code == status.HTTP_200_OK
    
    async def test_update_product(self, client: AsyncClient, admin_token: str, sample_product: dict):
        """Test updating a product"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product
        create_response = await client.post("/api/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Update product
        update_data = {
            "name": "Updated Test Product",
            "price": 199.99,
            "inventory": {"quantity": 150}
        }
        response = await client.put(
            f"/api/products/{product_id}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "Updated Test Product"
        assert data["price"] == 199.99
    
    async def test_delete_product(self, client: AsyncClient, admin_token: str, sample_product: dict):
        """Test deleting a product"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product
        create_response = await client.post("/api/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Delete product
        response = await client.delete(f"/api/products/{product_id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify product is deleted
        get_response = await client.get(f"/api/products/{product_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_product_authorization(self, client: AsyncClient, sample_product: dict):
        """Test product authorization"""
        # Try to create product without auth
        response = await client.post("/api/products", json=sample_product)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Customer shouldn't be able to create products
        customer_token = "customer_token_here"  # Would get from login
        headers = {"Authorization": f"Bearer {customer_token}"}
        response = await client.post("/api/products", json=sample_product, headers=headers)
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestProductSearch:
    """Test product search functionality"""
    
    async def test_search_products(self, client: AsyncClient, admin_token: str):
        """Test product search"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create products with searchable content
        products = [
            {
                "sku": "TEST_SEARCH_1",
                "name": "LED Light System",
                "description": "Bright LED light for night putting",
                "category": "basic",
                "price": 149.99,
                "inventory": {"quantity": 50}
            },
            {
                "sku": "TEST_SEARCH_2",
                "name": "Smart Putting Trainer",
                "description": "Advanced training system with app",
                "category": "pro",
                "price": 299.99,
                "inventory": {"quantity": 30}
            }
        ]
        
        for product in products:
            await client.post("/api/products", json=product, headers=headers)
        
        # Search for "LED"
        response = await client.get("/api/products/search?q=LED")
        assert response.status_code == status.HTTP_200_OK
        results = response.json()["items"]
        assert len(results) >= 1
        assert any("LED" in p["name"] or "LED" in p.get("description", "") for p in results)
        
        # Search for "training"
        response = await client.get("/api/products/search?q=training")
        assert response.status_code == status.HTTP_200_OK
        results = response.json()["items"]
        assert any("train" in p["name"].lower() or "train" in p.get("description", "").lower() for p in results)
    
    async def test_product_sorting(self, client: AsyncClient):
        """Test product sorting"""
        # Sort by price ascending
        response = await client.get("/api/products?sort=price_asc")
        assert response.status_code == status.HTTP_200_OK
        items = response.json()["items"]
        if len(items) > 1:
            prices = [item["price"] for item in items]
            assert prices == sorted(prices)
        
        # Sort by price descending
        response = await client.get("/api/products?sort=price_desc")
        assert response.status_code == status.HTTP_200_OK
        items = response.json()["items"]
        if len(items) > 1:
            prices = [item["price"] for item in items]
            assert prices == sorted(prices, reverse=True)
        
        # Sort by name
        response = await client.get("/api/products?sort=name")
        assert response.status_code == status.HTTP_200_OK
        items = response.json()["items"]
        if len(items) > 1:
            names = [item["name"] for item in items]
            assert names == sorted(names)
    
    async def test_product_pagination(self, client: AsyncClient):
        """Test product pagination"""
        # First page
        response = await client.get("/api/products?page=1&limit=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert data["page"] == 1
        assert data["limit"] == 10
        
        # Second page
        response = await client.get("/api/products?page=2&limit=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 2


class TestInventoryManagement:
    """Test inventory management"""
    
    async def test_update_inventory(self, client: AsyncClient, admin_token: str, sample_product: dict):
        """Test inventory update"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product
        create_response = await client.post("/api/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Update inventory
        inventory_update = {
            "quantity": 75,
            "reserved_quantity": 5,
            "low_stock_threshold": 15
        }
        response = await client.put(
            f"/api/products/{product_id}/inventory",
            json=inventory_update,
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["inventory"]["quantity"] == 75
        assert data["inventory"]["reserved_quantity"] == 5
        assert data["inventory"]["low_stock_threshold"] == 15
    
    async def test_low_stock_alert(self, client: AsyncClient, admin_token: str):
        """Test low stock alert"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product with low stock
        product = {
            "sku": "TEST_LOW_STOCK",
            "name": "Low Stock Product",
            "category": "basic",
            "price": 99.99,
            "inventory": {
                "quantity": 5,
                "low_stock_threshold": 10,
                "track_inventory": True
            }
        }
        await client.post("/api/products", json=product, headers=headers)
        
        # Get low stock products
        response = await client.get("/api/products/low-stock", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        
        items = response.json()["items"]
        assert any(p["sku"] == "TEST_LOW_STOCK" for p in items)
    
    async def test_reserve_inventory(self, client: AsyncClient, admin_token: str, sample_product: dict):
        """Test inventory reservation"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create product
        create_response = await client.post("/api/products", json=sample_product, headers=headers)
        product_id = create_response.json()["id"]
        
        # Reserve inventory
        reservation = {
            "product_id": product_id,
            "quantity": 10
        }
        response = await client.post(
            "/api/inventory/reserve",
            json=reservation,
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Check updated inventory
        product_response = await client.get(f"/api/products/{product_id}")
        inventory = product_response.json()["inventory"]
        assert inventory["reserved_quantity"] >= 10
        assert inventory["quantity"] >= inventory["reserved_quantity"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])