from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from enum import Enum

# Wishlist Models
class WishlistItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    added_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

class WishlistResponse(BaseModel):
    id: str
    product_id: str
    product_name: Optional[str] = None
    product_price: Optional[float] = None
    product_image: Optional[str] = None
    added_at: datetime
    notes: Optional[str] = None

# Address Models
class AddressType(str, Enum):
    HOME = "home"
    WORK = "work"
    BILLING = "billing"
    SHIPPING = "shipping"
    OTHER = "other"

class Address(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: AddressType = AddressType.HOME
    label: Optional[str] = None  # Custom label like "Mom's House"
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    company: Optional[str] = Field(None, max_length=100)
    address_line_1: str = Field(..., min_length=1, max_length=200)
    address_line_2: Optional[str] = Field(None, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=50)
    postal_code: str = Field(..., min_length=5, max_length=10)
    country: str = Field(default="US", min_length=2, max_length=2)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    is_primary: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AddressCreate(BaseModel):
    type: AddressType = AddressType.HOME
    label: Optional[str] = None
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    company: Optional[str] = Field(None, max_length=100)
    address_line_1: str = Field(..., min_length=1, max_length=200)
    address_line_2: Optional[str] = Field(None, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=50)
    postal_code: str = Field(..., min_length=5, max_length=10)
    country: str = Field(default="US", min_length=2, max_length=2)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    is_primary: bool = False

class AddressUpdate(BaseModel):
    type: Optional[AddressType] = None
    label: Optional[str] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    company: Optional[str] = Field(None, max_length=100)
    address_line_1: Optional[str] = Field(None, min_length=1, max_length=200)
    address_line_2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=50)
    postal_code: Optional[str] = Field(None, min_length=5, max_length=10)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    is_primary: Optional[bool] = None

# User Preferences Models
class NotificationPreferences(BaseModel):
    email_marketing: bool = True
    email_order_updates: bool = True
    email_product_updates: bool = False
    email_newsletters: bool = False
    push_notifications: bool = True

class PrivacyPreferences(BaseModel):
    profile_visibility: str = "private"  # "public", "private", "friends"
    show_purchase_history: bool = False
    allow_recommendations: bool = True
    data_sharing: bool = False

class UserPreferences(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    notifications: NotificationPreferences = Field(default_factory=NotificationPreferences)
    privacy: PrivacyPreferences = Field(default_factory=PrivacyPreferences)
    language: str = "en"
    timezone: str = "America/Chicago"
    currency: str = "USD"
    theme: str = "dark"  # "light", "dark", "auto"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserPreferencesUpdate(BaseModel):
    notifications: Optional[NotificationPreferences] = None
    privacy: Optional[PrivacyPreferences] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    theme: Optional[str] = None

# User Activity Models
class ActivityType(str, Enum):
    PRODUCT_VIEW = "product_view"
    PRODUCT_SEARCH = "product_search"
    CART_ADD = "cart_add"
    CART_REMOVE = "cart_remove"
    WISHLIST_ADD = "wishlist_add"
    WISHLIST_REMOVE = "wishlist_remove"
    ORDER_PLACED = "order_placed"
    ORDER_CANCELLED = "order_cancelled"
    PROFILE_UPDATE = "profile_update"
    ADDRESS_ADD = "address_add"
    ADDRESS_UPDATE = "address_update"
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"

class UserActivity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    activity_type: ActivityType
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserActivityResponse(BaseModel):
    id: str
    activity_type: ActivityType
    description: str
    metadata: Dict[str, Any]
    created_at: datetime

# Product Review Models
class ReviewRating(int, Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

class ProductReview(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    product_id: str
    rating: ReviewRating
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=10, max_length=2000)
    is_verified_purchase: bool = False
    is_approved: bool = False
    helpful_votes: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProductReviewCreate(BaseModel):
    product_id: str
    rating: ReviewRating
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=10, max_length=2000)

class ProductReviewUpdate(BaseModel):
    rating: Optional[ReviewRating] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=10, max_length=2000)

class ProductReviewResponse(BaseModel):
    id: str
    user_id: str
    username: Optional[str] = None
    product_id: str
    rating: ReviewRating
    title: str
    content: str
    is_verified_purchase: bool
    is_approved: bool
    helpful_votes: int
    created_at: datetime
    updated_at: datetime

# User Profile Enhancement Models
class UserProfileStats(BaseModel):
    total_orders: int = 0
    total_spent: float = 0.0
    products_reviewed: int = 0
    wishlist_items: int = 0
    addresses_count: int = 0
    member_since: datetime
    last_order: Optional[datetime] = None
    favorite_category: Optional[str] = None

class UserAccountSettings(BaseModel):
    two_factor_enabled: bool = False
    login_notifications: bool = True
    password_last_changed: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked_until: Optional[datetime] = None

# Search History Models
class SearchHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    query: str
    results_count: int = 0
    clicked_product_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PopularSearch(BaseModel):
    query: str
    search_count: int
    last_searched: datetime

# User Engagement Models
class UserEngagement(BaseModel):
    user_id: str
    session_duration_avg: float = 0.0  # in minutes
    pages_per_session_avg: float = 0.0
    bounce_rate: float = 0.0  # percentage
    last_active: datetime
    total_sessions: int = 0
    total_page_views: int = 0
    conversion_rate: float = 0.0  # percentage