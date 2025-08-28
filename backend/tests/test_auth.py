"""
Authentication Tests for NitePutter Pro
Tests user registration, login, and token management
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app
from app.database import get_database
from app.core.security import Security
import asyncio

security = Security()

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
    await db.users.delete_many({"email": {"$regex": "^test_"}})

class TestAuthentication:
    """Test authentication endpoints"""
    
    async def test_user_registration(self, client: AsyncClient, test_db):
        """Test user registration"""
        payload = {
            "email": "test_user@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User",
            "phone": "1234567890"
        }
        
        response = await client.post("/api/auth/register", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["email"] == payload["email"]
        assert "access_token" in data
        assert "refresh_token" in data
        assert "password" not in data
        
        # Verify password is hashed in database
        user = await test_db.users.find_one({"email": payload["email"]})
        assert user["password_hash"] != payload["password"]
        assert security.verify_password(payload["password"], user["password_hash"])
    
    async def test_registration_duplicate_email(self, client: AsyncClient, test_db):
        """Test registration with duplicate email"""
        payload = {
            "email": "test_duplicate@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        # First registration
        response = await client.post("/api/auth/register", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Duplicate registration
        response = await client.post("/api/auth/register", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()
    
    async def test_registration_weak_password(self, client: AsyncClient):
        """Test registration with weak password"""
        payload = {
            "email": "test_weak@example.com",
            "password": "weak",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = await client.post("/api/auth/register", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_user_login(self, client: AsyncClient, test_db):
        """Test user login"""
        # Register user first
        register_payload = {
            "email": "test_login@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        await client.post("/api/auth/register", json=register_payload)
        
        # Login
        login_payload = {
            "email": "test_login@example.com",
            "password": "SecurePass123!"
        }
        response = await client.post("/api/auth/login", json=login_payload)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == login_payload["email"]
    
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials"""
        payload = {
            "email": "nonexistent@example.com",
            "password": "WrongPass123!"
        }
        
        response = await client.post("/api/auth/login", json=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid credentials" in response.json()["detail"]
    
    async def test_token_refresh(self, client: AsyncClient, test_db):
        """Test token refresh"""
        # Register and login
        register_payload = {
            "email": "test_refresh@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        reg_response = await client.post("/api/auth/register", json=register_payload)
        refresh_token = reg_response.json()["refresh_token"]
        
        # Refresh token
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    async def test_protected_route(self, client: AsyncClient, test_db):
        """Test accessing protected route"""
        # Register user
        register_payload = {
            "email": "test_protected@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        reg_response = await client.post("/api/auth/register", json=register_payload)
        access_token = reg_response.json()["access_token"]
        
        # Access protected route with token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/api/users/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == register_payload["email"]
        
        # Access without token
        response = await client.get("/api/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_token_expiration(self, client: AsyncClient, test_db):
        """Test token expiration"""
        # Create expired token
        user_data = {"sub": "test_expired@example.com", "role": "customer"}
        expired_token = security.create_token(user_data, expires_delta=-1)  # Expired
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await client.get("/api/users/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "expired" in response.json()["detail"].lower()
    
    async def test_password_reset_request(self, client: AsyncClient, test_db):
        """Test password reset request"""
        # Register user
        register_payload = {
            "email": "test_reset@example.com",
            "password": "OldPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        await client.post("/api/auth/register", json=register_payload)
        
        # Request password reset
        response = await client.post(
            "/api/auth/password-reset",
            json={"email": "test_reset@example.com"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert "Password reset email sent" in response.json()["message"]
    
    async def test_logout(self, client: AsyncClient, test_db):
        """Test user logout"""
        # Register and get tokens
        register_payload = {
            "email": "test_logout@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        reg_response = await client.post("/api/auth/register", json=register_payload)
        access_token = reg_response.json()["access_token"]
        
        # Logout
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/auth/logout", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert "Successfully logged out" in response.json()["message"]
        
        # Verify token is invalidated (would need Redis for full test)
        # In production, this would check Redis blacklist


class TestUserManagement:
    """Test user management endpoints"""
    
    async def test_update_profile(self, client: AsyncClient, test_db):
        """Test profile update"""
        # Register user
        register_payload = {
            "email": "test_update@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        reg_response = await client.post("/api/auth/register", json=register_payload)
        access_token = reg_response.json()["access_token"]
        
        # Update profile
        update_payload = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "9876543210"
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.put("/api/users/me", json=update_payload, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["phone"] == "9876543210"
    
    async def test_change_password(self, client: AsyncClient, test_db):
        """Test password change"""
        # Register user
        register_payload = {
            "email": "test_password@example.com",
            "password": "OldPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        reg_response = await client.post("/api/auth/register", json=register_payload)
        access_token = reg_response.json()["access_token"]
        
        # Change password
        change_payload = {
            "current_password": "OldPass123!",
            "new_password": "NewPass456!"
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post(
            "/api/users/change-password",
            json=change_payload,
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Login with new password
        login_payload = {
            "email": "test_password@example.com",
            "password": "NewPass456!"
        }
        response = await client.post("/api/auth/login", json=login_payload)
        assert response.status_code == status.HTTP_200_OK
    
    async def test_delete_account(self, client: AsyncClient, test_db):
        """Test account deletion"""
        # Register user
        register_payload = {
            "email": "test_delete@example.com",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        reg_response = await client.post("/api/auth/register", json=register_payload)
        access_token = reg_response.json()["access_token"]
        
        # Delete account
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.delete("/api/users/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify user is deleted
        user = await test_db.users.find_one({"email": "test_delete@example.com"})
        assert user is None or user["status"] == "deleted"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])