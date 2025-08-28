"""
Authentication Service for NitePutter Pro
JWT-based authentication with refresh tokens
"""

import os
import jwt
import secrets
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta, UTC
from fastapi import HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import logging

from ..database import get_database
from ..models.user import User, UserCreate, UserLogin

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer for JWT
security = HTTPBearer()

class AuthService:
    """Authentication service handling user registration, login, and JWT tokens"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.refresh_secret_key = REFRESH_SECRET_KEY
        self.algorithm = ALGORITHM
        
    async def register(self, user_data: UserCreate) -> Tuple[User, str, str]:
        """
        Register a new user
        Returns: (user, access_token, refresh_token)
        """
        db = await get_database()
        
        # Check if email already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Create new user
        user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            preferences={"newsletter_subscribed": user_data.newsletter_subscribed}
        )
        
        # Hash password
        user.set_password(user_data.password)
        
        # Generate verification token
        user.generate_verification_token()
        
        # Insert into database
        user_dict = user.model_dump(by_alias=True, exclude_none=True)
        result = await db.users.insert_one(user_dict)
        user.id = str(result.inserted_id)
        
        # Generate tokens
        access_token = self.create_access_token(user.id, user.email)
        refresh_token = self.create_refresh_token(user.id)
        
        # Send verification email (would integrate with email service)
        # await email_service.send_verification_email(user.email, user.email_verification_token)
        
        logger.info(f"New user registered: {user.email}")
        return user, access_token, refresh_token
    
    async def login(self, credentials: UserLogin) -> Tuple[User, str, str]:
        """
        Authenticate user and return tokens
        Returns: (user, access_token, refresh_token)
        """
        db = await get_database()
        
        # Find user
        user_doc = await db.users.find_one({"email": credentials.email})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user = User(**user_doc)
        
        # Check if account is locked
        if user.is_locked():
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked due to multiple failed login attempts"
            )
        
        # Verify password
        if not user.verify_password(credentials.password):
            user.record_failed_login()
            await db.users.update_one(
                {"_id": user_doc["_id"]},
                {"$set": {
                    "failed_login_attempts": user.failed_login_attempts,
                    "locked_until": user.locked_until
                }}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Record successful login
        user.record_login()
        await db.users.update_one(
            {"_id": user_doc["_id"]},
            {"$set": {
                "last_login": user.last_login,
                "last_activity": user.last_activity,
                "login_count": user.login_count,
                "failed_login_attempts": 0,
                "locked_until": None
            }}
        )
        
        # Generate tokens
        access_token = self.create_access_token(str(user.id), user.email)
        refresh_token = self.create_refresh_token(str(user.id))
        
        logger.info(f"User logged in: {user.email}")
        return user, access_token, refresh_token
    
    def create_access_token(self, user_id: str, email: str) -> str:
        """Create JWT access token"""
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.now(UTC) + expires_delta
        
        payload = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "iat": datetime.now(UTC),
            "type": "access"
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        expire = datetime.now(UTC) + expires_delta
        
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.now(UTC),
            "type": "refresh",
            "jti": secrets.token_urlsafe(16)  # JWT ID for token revocation
        }
        
        token = jwt.encode(payload, self.refresh_secret_key, algorithm=self.algorithm)
        return token
    
    async def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            secret_key = self.secret_key if token_type == "access" else self.refresh_secret_key
            payload = jwt.decode(token, secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def refresh_tokens(self, refresh_token: str) -> Tuple[str, str]:
        """Generate new access and refresh tokens using refresh token"""
        payload = await self.verify_token(refresh_token, token_type="refresh")
        user_id = payload.get("sub")
        
        # Get user to ensure they still exist and are active
        db = await get_database()
        user_doc = await db.users.find_one({"_id": user_id})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = User(**user_doc)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Generate new tokens
        new_access_token = self.create_access_token(str(user.id), user.email)
        new_refresh_token = self.create_refresh_token(str(user.id))
        
        return new_access_token, new_refresh_token
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = None) -> User:
        """Get current user from JWT token"""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        token = credentials.credentials
        payload = await self.verify_token(token)
        user_id = payload.get("sub")
        
        db = await get_database()
        user_doc = await db.users.find_one({"_id": user_id})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = User(**user_doc)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Update last activity
        await db.users.update_one(
            {"_id": user_id},
            {"$set": {"last_activity": datetime.now(UTC)}}
        )
        
        return user
    
    async def verify_email(self, email: str, token: str) -> bool:
        """Verify user email with token"""
        db = await get_database()
        
        user_doc = await db.users.find_one({"email": email})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = User(**user_doc)
        if user.verify_email(token):
            await db.users.update_one(
                {"_id": user_doc["_id"]},
                {"$set": {
                    "is_verified": True,
                    "status": user.status.value,
                    "email_verification_token": None,
                    "email_verification_expires": None
                }}
            )
            logger.info(f"Email verified for user: {email}")
            return True
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    async def request_password_reset(self, email: str) -> str:
        """Request password reset token"""
        db = await get_database()
        
        user_doc = await db.users.find_one({"email": email})
        if not user_doc:
            # Don't reveal if email exists
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return ""
        
        user = User(**user_doc)
        reset_token = user.generate_reset_token()
        
        await db.users.update_one(
            {"_id": user_doc["_id"]},
            {"$set": {
                "password_reset_token": user.password_reset_token,
                "password_reset_expires": user.password_reset_expires
            }}
        )
        
        # Send reset email (would integrate with email service)
        # await email_service.send_password_reset_email(user.email, reset_token)
        
        logger.info(f"Password reset requested for user: {email}")
        return reset_token
    
    async def reset_password(self, email: str, token: str, new_password: str) -> bool:
        """Reset user password with token"""
        db = await get_database()
        
        user_doc = await db.users.find_one({"email": email})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = User(**user_doc)
        if user.reset_password(token, new_password):
            await db.users.update_one(
                {"_id": user_doc["_id"]},
                {"$set": {
                    "password_hash": user.password_hash,
                    "password_reset_token": None,
                    "password_reset_expires": None,
                    "failed_login_attempts": 0,
                    "locked_until": None
                }}
            )
            logger.info(f"Password reset for user: {email}")
            return True
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    async def logout(self, user: User, refresh_token: Optional[str] = None):
        """Logout user and optionally revoke refresh token"""
        # In production, you might want to:
        # 1. Add refresh token to a blacklist
        # 2. Clear server-side session if using sessions
        # 3. Log the logout event
        
        logger.info(f"User logged out: {user.email}")
        
        # For now, just return success
        # The client should delete the tokens
        return {"message": "Successfully logged out"}


# Create singleton instance
auth_service = AuthService()