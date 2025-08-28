"""
User Model for NitePutter Pro
Complete user authentication and profile system
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from enum import Enum
from .product import PyObjectId
import bcrypt
import secrets

class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    STAFF = "staff"
    GUEST = "guest"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"

class AuthProvider(str, Enum):
    LOCAL = "local"
    GOOGLE = "google"
    FACEBOOK = "facebook"
    APPLE = "apple"

class Address(BaseModel):
    """User address information"""
    label: str = "default"  # home, work, etc
    first_name: str
    last_name: str
    company: Optional[str] = None
    street_line1: str
    street_line2: Optional[str] = None
    city: str
    state_province: str
    postal_code: str
    country: str = "US"
    phone: str
    is_default: bool = False
    is_billing: bool = False
    is_shipping: bool = False

class PaymentMethod(BaseModel):
    """Saved payment method"""
    id: str = Field(default_factory=lambda: secrets.token_urlsafe(16))
    stripe_payment_method_id: Optional[str] = None
    type: str  # card, paypal, etc
    last4: Optional[str] = None
    brand: Optional[str] = None  # visa, mastercard, etc
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    is_default: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationPreferences(BaseModel):
    """User notification settings"""
    email_marketing: bool = True
    email_orders: bool = True
    email_shipping: bool = True
    email_promotions: bool = True
    sms_enabled: bool = False
    sms_orders: bool = False
    sms_shipping: bool = False
    push_enabled: bool = False

class UserPreferences(BaseModel):
    """User preferences and settings"""
    currency: str = "USD"
    language: str = "en"
    timezone: str = "America/New_York"
    newsletter_subscribed: bool = True
    notifications: NotificationPreferences = Field(default_factory=NotificationPreferences)

class UserProfile(BaseModel):
    """Extended user profile information"""
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    golf_handicap: Optional[float] = None
    favorite_course: Optional[str] = None
    years_playing: Optional[int] = None
    preferred_tee_time: Optional[str] = None  # morning, afternoon, evening, night
    skill_level: Optional[str] = None  # beginner, intermediate, advanced, pro

class User(BaseModel):
    """Complete user model for NitePutter Pro"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    # Authentication
    email: EmailStr = Field(..., description="User email (unique)")
    username: Optional[str] = Field(None, description="Optional username")
    password_hash: Optional[str] = Field(None, description="Hashed password for local auth")
    
    # OAuth
    auth_provider: AuthProvider = AuthProvider.LOCAL
    oauth_id: Optional[str] = None
    oauth_data: Dict[str, Any] = {}
    
    # Basic Information
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    
    # Role & Status
    role: UserRole = UserRole.CUSTOMER
    status: UserStatus = UserStatus.PENDING_VERIFICATION
    is_active: bool = True
    is_verified: bool = False
    
    # Profile
    profile: UserProfile = Field(default_factory=UserProfile)
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    
    # Addresses
    addresses: List[Address] = []
    
    # Payment Methods
    payment_methods: List[PaymentMethod] = []
    stripe_customer_id: Optional[str] = None
    
    # Security
    email_verification_token: Optional[str] = None
    email_verification_expires: Optional[datetime] = None
    password_reset_token: Optional[str] = None
    password_reset_expires: Optional[datetime] = None
    two_factor_enabled: bool = False
    two_factor_secret: Optional[str] = None
    
    # Activity
    last_login: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    login_count: int = 0
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    
    # Marketing
    referral_code: Optional[str] = None
    referred_by: Optional[str] = None
    loyalty_points: int = 0
    vip_tier: Optional[str] = None  # bronze, silver, gold, platinum
    
    # Metadata
    tags: List[str] = []
    notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            str: str,  # PyObjectId handled by annotation
            datetime: lambda v: v.isoformat()
        }
    )
    
    @field_validator('display_name', mode='before')
    @classmethod
    def generate_display_name(cls, v, info):
        if not v and info.data.get('first_name') and info.data.get('last_name'):
            return f"{info.data['first_name']} {info.data['last_name']}"
        return v
    
    @field_validator('referral_code', mode='before')
    @classmethod
    def generate_referral_code(cls, v, info):
        if not v and info.data.get('first_name'):
            # Generate unique referral code
            import random
            import string
            base = info.data['first_name'][:3].upper()
            suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            return f"{base}{suffix}"
        return v
    
    def set_password(self, password: str):
        """Hash and set user password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def generate_verification_token(self) -> str:
        """Generate email verification token"""
        token = secrets.token_urlsafe(32)
        self.email_verification_token = token
        self.email_verification_expires = datetime.utcnow() + timedelta(hours=24)
        return token
    
    def generate_reset_token(self) -> str:
        """Generate password reset token"""
        token = secrets.token_urlsafe(32)
        self.password_reset_token = token
        self.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        return token
    
    def verify_email(self, token: str) -> bool:
        """Verify email with token"""
        if not self.email_verification_token or self.email_verification_token != token:
            return False
        if self.email_verification_expires and self.email_verification_expires < datetime.utcnow():
            return False
        
        self.is_verified = True
        self.status = UserStatus.ACTIVE
        self.email_verification_token = None
        self.email_verification_expires = None
        return True
    
    def can_reset_password(self, token: str) -> bool:
        """Check if password can be reset with token"""
        if not self.password_reset_token or self.password_reset_token != token:
            return False
        if self.password_reset_expires and self.password_reset_expires < datetime.utcnow():
            return False
        return True
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password with token"""
        if not self.can_reset_password(token):
            return False
        
        self.set_password(new_password)
        self.password_reset_token = None
        self.password_reset_expires = None
        self.failed_login_attempts = 0
        self.locked_until = None
        return True
    
    def record_login(self):
        """Record successful login"""
        self.last_login = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.login_count += 1
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def record_failed_login(self):
        """Record failed login attempt"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            # Lock account for 30 minutes after 5 failed attempts
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def is_locked(self) -> bool:
        """Check if account is locked"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        permissions = {
            UserRole.ADMIN: ["all"],
            UserRole.STAFF: ["manage_orders", "manage_products", "view_analytics"],
            UserRole.CUSTOMER: ["place_orders", "view_own_orders"],
            UserRole.GUEST: ["view_products"]
        }
        
        role_permissions = permissions.get(self.role, [])
        return permission in role_permissions or "all" in role_permissions
    
    def add_loyalty_points(self, points: int):
        """Add loyalty points and update VIP tier"""
        self.loyalty_points += points
        
        # Update VIP tier based on points
        if self.loyalty_points >= 10000:
            self.vip_tier = "platinum"
        elif self.loyalty_points >= 5000:
            self.vip_tier = "gold"
        elif self.loyalty_points >= 2000:
            self.vip_tier = "silver"
        elif self.loyalty_points >= 500:
            self.vip_tier = "bronze"
    
    def get_discount_percentage(self) -> float:
        """Get discount percentage based on VIP tier"""
        discounts = {
            "bronze": 0.05,    # 5%
            "silver": 0.10,    # 10%
            "gold": 0.15,      # 15%
            "platinum": 0.20   # 20%
        }
        return discounts.get(self.vip_tier, 0.0)


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    newsletter_subscribed: bool = True

class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    profile: Optional[UserProfile] = None
    preferences: Optional[UserPreferences] = None

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str
    remember_me: bool = False

class PasswordReset(BaseModel):
    """Schema for password reset"""
    token: str
    new_password: str

class PasswordChange(BaseModel):
    """Schema for changing password"""
    current_password: str
    new_password: str