"""
Security Module for NitePutter Pro
JWT authentication and password management
"""

from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import re
import logging

from ..config import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS
)

# HTTP Bearer for JWT
security_scheme = HTTPBearer()

class Security:
    """Complete security implementation for authentication"""
    
    # Token settings
    SECRET_KEY = settings.JWT_SECRET_KEY
    REFRESH_SECRET_KEY = settings.JWT_REFRESH_SECRET_KEY
    ALGORITHM = settings.JWT_ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        
        # Check minimum length
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long")
        
        # Check for uppercase letter
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")
        
        # Check for lowercase letter
        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")
        
        # Check for digit
        if not re.search(r"\d", password):
            errors.append("Password must contain at least one number")
        
        # Check for special character
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Password must contain at least one special character")
        
        # Calculate password strength score
        score = 0
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if re.search(r"[A-Z]", password):
            score += 1
        if re.search(r"[a-z]", password):
            score += 1
        if re.search(r"\d", password):
            score += 1
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            score += 1
        
        strength = "weak"
        if score >= 5:
            strength = "strong"
        elif score >= 4:
            strength = "medium"
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "strength": strength,
            "score": score
        }
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token
        
        Args:
            data: Data to encode in the token
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=Security.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(UTC),
            "type": "access",
            "jti": secrets.token_urlsafe(16)  # JWT ID for token tracking
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            Security.SECRET_KEY,
            algorithm=Security.ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT refresh token
        
        Args:
            data: Data to encode in the token
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT refresh token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(days=Security.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(UTC),
            "type": "refresh",
            "jti": secrets.token_urlsafe(16)  # JWT ID for token revocation
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            Security.REFRESH_SECRET_KEY,
            algorithm=Security.ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        Decode and verify JWT token
        
        Args:
            token: JWT token to decode
            token_type: Type of token (access or refresh)
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Select appropriate secret key
            secret_key = Security.SECRET_KEY if token_type == "access" else Security.REFRESH_SECRET_KEY
            
            # Decode token
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=[Security.ALGORITHM]
            )
            
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
        except jwt.JWTError as e:
            logger.error(f"JWT decode error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    @staticmethod
    def verify_token(credentials: HTTPAuthorizationCredentials) -> Dict[str, Any]:
        """
        Verify bearer token from request
        
        Args:
            credentials: HTTP authorization credentials
            
        Returns:
            Decoded token payload
        """
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization required"
            )
        
        token = credentials.credentials
        return Security.decode_token(token, token_type="access")
    
    @staticmethod
    def generate_reset_token() -> str:
        """
        Generate a secure password reset token
        
        Returns:
            Secure random token string
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_verification_token() -> str:
        """
        Generate a secure email verification token
        
        Returns:
            Secure random token string
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a secure API key
        
        Returns:
            Secure API key string
        """
        return f"npp_{secrets.token_urlsafe(32)}"
    
    @staticmethod
    def generate_session_id() -> str:
        """
        Generate a secure session ID
        
        Returns:
            Secure session ID string
        """
        return secrets.token_urlsafe(24)
    
    @staticmethod
    def create_token_pair(user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Create both access and refresh tokens
        
        Args:
            user_data: User data to encode in tokens
            
        Returns:
            Dictionary with access_token and refresh_token
        """
        # Create access token
        access_token = Security.create_access_token(user_data)
        
        # Create refresh token with minimal data
        refresh_data = {
            "sub": user_data.get("sub"),  # User ID
            "email": user_data.get("email")
        }
        refresh_token = Security.create_refresh_token(refresh_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": Security.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # In seconds
        }
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Dict[str, str]:
        """
        Generate new access token from refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token and optionally new refresh token
        """
        try:
            # Decode refresh token
            payload = Security.decode_token(refresh_token, token_type="refresh")
            
            # Create new access token
            user_data = {
                "sub": payload.get("sub"),
                "email": payload.get("email")
            }
            
            # Generate new token pair
            return Security.create_token_pair(user_data)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    @staticmethod
    def get_password_hash_info(hashed_password: str) -> Dict[str, Any]:
        """
        Get information about a password hash
        
        Args:
            hashed_password: Bcrypt hashed password
            
        Returns:
            Dictionary with hash information
        """
        try:
            # Bcrypt format: $2b$[rounds]$[salt][hash]
            parts = hashed_password.split("$")
            if len(parts) >= 4:
                return {
                    "algorithm": parts[1],
                    "rounds": int(parts[2]),
                    "needs_rehash": pwd_context.needs_update(hashed_password)
                }
        except Exception as e:
            logger.error(f"Hash info error: {e}")
        
        return {"algorithm": "unknown", "rounds": 0, "needs_rehash": True}
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """
        Sanitize and normalize email address
        
        Args:
            email: Email address to sanitize
            
        Returns:
            Sanitized email address
        """
        # Convert to lowercase and strip whitespace
        email = email.lower().strip()
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        
        return email
    
    @staticmethod
    def is_strong_password(password: str) -> bool:
        """
        Quick check if password is strong
        
        Args:
            password: Password to check
            
        Returns:
            True if password is strong
        """
        result = Security.validate_password(password)
        return result["valid"] and result["strength"] in ["medium", "strong"]


# Create singleton instance
security = Security()

# Dependency for protected routes
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> Dict[str, Any]:
    """
    Dependency to get current user from JWT token
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        Current user data from token
    """
    payload = security.verify_token(credentials)
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("role", "customer")
    }

# Dependency for optional authentication
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> Optional[Dict[str, Any]]:
    """
    Dependency to optionally get current user
    
    Args:
        credentials: Optional HTTP authorization credentials
        
    Returns:
        Current user data or None
    """
    if not credentials:
        return None
    
    try:
        payload = security.verify_token(credentials)
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role", "customer")
        }
    except HTTPException:
        return None

# Dependency for admin-only routes
async def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dependency to require admin role
    
    Args:
        current_user: Current user from token
        
    Returns:
        Current user if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Dependency for staff or admin routes
async def require_staff(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dependency to require staff or admin role
    
    Args:
        current_user: Current user from token
        
    Returns:
        Current user if staff or admin
        
    Raises:
        HTTPException: If user is not staff or admin
    """
    if current_user.get("role") not in ["staff", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff access required"
        )
    return current_user