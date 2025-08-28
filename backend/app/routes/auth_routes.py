"""
Authentication Routes for NitePutter Pro
User registration, login, and account management
"""

from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
import logging
from datetime import datetime, UTC

from ..core.security import security, get_current_user, get_current_user_optional
from ..services.auth_service import auth_service
from ..models.user import UserCreate, UserLogin, PasswordReset, PasswordChange
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Request/Response Models
class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = Field(default=None, max_length=20)
    newsletter: bool = Field(default=True)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        if not security.is_strong_password(v):
            validation = security.validate_password(v)
            raise ValueError(f"Password is not strong enough: {', '.join(validation['errors'])}")
        return v

class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str
    remember_me: bool = Field(default=False)

class RefreshTokenRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    """Password reset request"""
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    """Password reset confirmation"""
    email: EmailStr
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class VerifyEmailRequest(BaseModel):
    """Email verification request"""
    email: EmailStr
    token: str

class AuthResponse(BaseModel):
    """Authentication response"""
    success: bool
    message: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    user: Optional[Dict[str, Any]] = None


@router.post("/register", response_model=AuthResponse)
async def register(
    request: RegisterRequest,
    background_tasks: BackgroundTasks
) -> AuthResponse:
    """
    Register a new user account
    
    - **email**: User email address (must be unique)
    - **password**: Strong password (min 8 chars, uppercase, lowercase, number, special char)
    - **confirm_password**: Must match password
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **phone**: Optional phone number
    - **newsletter**: Subscribe to newsletter
    """
    try:
        # Sanitize email
        email = security.sanitize_email(request.email)
        
        # Create user
        user_data = UserCreate(
            email=email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            newsletter_subscribed=request.newsletter
        )
        
        # Register user
        user, access_token, refresh_token = await auth_service.register(user_data)
        
        # TODO: Send verification email in background
        # background_tasks.add_task(send_verification_email, user.email, user.email_verification_token)
        
        logger.info(f"User registered: {user.email}")
        
        return AuthResponse(
            success=True,
            message="Registration successful. Please check your email to verify your account.",
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "verified": user.is_verified
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest) -> AuthResponse:
    """
    Login with email and password
    
    - **email**: Registered email address
    - **password**: Account password
    - **remember_me**: Keep user logged in longer
    """
    try:
        # Sanitize email
        email = security.sanitize_email(request.email)
        
        # Create login data
        login_data = UserLogin(
            email=email,
            password=request.password,
            remember_me=request.remember_me
        )
        
        # Authenticate user
        user, access_token, refresh_token = await auth_service.login(login_data)
        
        # Extend token expiry if remember_me
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        if request.remember_me:
            expires_in *= 7  # Extend to 7 times longer
        
        logger.info(f"User logged in: {user.email}")
        
        return AuthResponse(
            success=True,
            message="Login successful",
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            user={
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "verified": user.is_verified
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(request: RefreshTokenRequest) -> AuthResponse:
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    """
    try:
        # Refresh tokens
        new_access_token, new_refresh_token = await auth_service.refresh_tokens(request.refresh_token)
        
        return AuthResponse(
            success=True,
            message="Token refreshed successfully",
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Logout current user
    
    Requires authentication
    """
    try:
        # Get user
        from ..database import get_database
        db = await get_database()
        user_doc = await db.users.find_one({"_id": current_user["user_id"]})
        
        if user_doc:
            from ..models.user import User
            user = User(**user_doc)
            result = await auth_service.logout(user)
            
            logger.info(f"User logged out: {user.email}")
            return result
        
        return {"success": True, "message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"success": True, "message": "Logged out"}


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Request password reset token
    
    - **email**: Account email address
    """
    try:
        # Sanitize email
        email = security.sanitize_email(request.email)
        
        # Request reset token
        reset_token = await auth_service.request_password_reset(email)
        
        # TODO: Send password reset email in background
        # background_tasks.add_task(send_password_reset_email, email, reset_token)
        
        # Always return success to prevent email enumeration
        return {
            "success": True,
            "message": "If an account exists with this email, a password reset link has been sent."
        }
        
    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        # Still return success to prevent enumeration
        return {
            "success": True,
            "message": "If an account exists with this email, a password reset link has been sent."
        }


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest) -> Dict[str, Any]:
    """
    Reset password with token
    
    - **email**: Account email
    - **token**: Reset token from email
    - **new_password**: New password
    - **confirm_password**: Confirm new password
    """
    try:
        # Validate password strength
        if not security.is_strong_password(request.new_password):
            validation = security.validate_password(request.new_password)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password is not strong enough: {', '.join(validation['errors'])}"
            )
        
        # Sanitize email
        email = security.sanitize_email(request.email)
        
        # Reset password
        success = await auth_service.reset_password(
            email=email,
            token=request.token,
            new_password=request.new_password
        )
        
        if success:
            logger.info(f"Password reset for: {email}")
            return {
                "success": True,
                "message": "Password has been reset successfully. You can now login with your new password."
            }
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset failed"
        )


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Change password for authenticated user
    
    - **current_password**: Current password
    - **new_password**: New password
    - **confirm_password**: Confirm new password
    
    Requires authentication
    """
    try:
        # Validate password strength
        if not security.is_strong_password(request.new_password):
            validation = security.validate_password(request.new_password)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password is not strong enough: {', '.join(validation['errors'])}"
            )
        
        # Get user from database
        from ..database import get_database
        db = await get_database()
        user_doc = await db.users.find_one({"_id": current_user["user_id"]})
        
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        from ..models.user import User
        user = User(**user_doc)
        
        # Verify current password
        if not user.verify_password(request.current_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Set new password
        user.set_password(request.new_password)
        
        # Update in database
        await db.users.update_one(
            {"_id": user_doc["_id"]},
            {"$set": {"password_hash": user.password_hash}}
        )
        
        logger.info(f"Password changed for: {user.email}")
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.post("/verify-email")
async def verify_email(request: VerifyEmailRequest) -> Dict[str, Any]:
    """
    Verify email address with token
    
    - **email**: Email to verify
    - **token**: Verification token from email
    """
    try:
        # Sanitize email
        email = security.sanitize_email(request.email)
        
        # Verify email
        success = await auth_service.verify_email(email, request.token)
        
        if success:
            logger.info(f"Email verified: {email}")
            return {
                "success": True,
                "message": "Email verified successfully. Your account is now active."
            }
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email verification failed"
        )


@router.get("/me")
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current user profile
    
    Requires authentication
    """
    try:
        # Get full user profile
        from ..database import get_database
        db = await get_database()
        user_doc = await db.users.find_one(
            {"_id": current_user["user_id"]},
            {
                "password_hash": 0,
                "email_verification_token": 0,
                "password_reset_token": 0,
                "two_factor_secret": 0
            }
        )
        
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "success": True,
            "user": {
                "id": str(user_doc["_id"]),
                "email": user_doc["email"],
                "first_name": user_doc["first_name"],
                "last_name": user_doc["last_name"],
                "display_name": user_doc.get("display_name"),
                "phone": user_doc.get("phone"),
                "role": user_doc["role"],
                "status": user_doc["status"],
                "verified": user_doc["is_verified"],
                "profile": user_doc.get("profile", {}),
                "preferences": user_doc.get("preferences", {}),
                "created_at": user_doc["created_at"],
                "last_login": user_doc.get("last_login")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )


@router.post("/validate-token")
async def validate_token(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Validate current access token
    
    Returns token validity and user info if valid
    """
    if current_user:
        return {
            "valid": True,
            "user_id": current_user["user_id"],
            "email": current_user["email"],
            "role": current_user["role"]
        }
    
    return {
        "valid": False
    }


@router.post("/resend-verification")
async def resend_verification_email(
    email: EmailStr,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Resend email verification link
    
    - **email**: Email address to resend verification to
    """
    try:
        # Sanitize email
        email = security.sanitize_email(email)
        
        # Get user
        from ..database import get_database
        db = await get_database()
        user_doc = await db.users.find_one({"email": email})
        
        if user_doc and not user_doc.get("is_verified"):
            from ..models.user import User
            user = User(**user_doc)
            
            # Generate new verification token
            token = user.generate_verification_token()
            
            # Update in database
            await db.users.update_one(
                {"_id": user_doc["_id"]},
                {"$set": {
                    "email_verification_token": user.email_verification_token,
                    "email_verification_expires": user.email_verification_expires
                }}
            )
            
            # TODO: Send verification email in background
            # background_tasks.add_task(send_verification_email, email, token)
            
            logger.info(f"Verification email resent to: {email}")
        
        # Always return success to prevent enumeration
        return {
            "success": True,
            "message": "If an unverified account exists, a verification email has been sent."
        }
        
    except Exception as e:
        logger.error(f"Resend verification error: {e}")
        return {
            "success": True,
            "message": "If an unverified account exists, a verification email has been sent."
        }