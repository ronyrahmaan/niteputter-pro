from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class AdminRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    VIEWER = "viewer"

class AdminPermission(str, Enum):
    # Product permissions
    MANAGE_PRODUCTS = "manage_products"
    VIEW_PRODUCTS = "view_products"
    MANAGE_INVENTORY = "manage_inventory"
    
    # User permissions
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    
    # Order permissions
    MANAGE_ORDERS = "manage_orders"
    VIEW_ORDERS = "view_orders"
    PROCESS_REFUNDS = "process_refunds"
    
    # Analytics permissions
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_DATA = "export_data"
    
    # System permissions
    MANAGE_SETTINGS = "manage_settings"
    MANAGE_ADMINS = "manage_admins"
    VIEW_LOGS = "view_logs"
    
    # E-commerce permissions (Phase 7)
    MANAGE_PROMOTIONS = "manage_promotions"
    VIEW_PROMOTIONS = "view_promotions"
    MANAGE_SHIPPING = "manage_shipping"
    VIEW_SHIPPING = "view_shipping"
    MANAGE_TAXES = "manage_taxes"
    VIEW_TAXES = "view_taxes"
    MANAGE_RETURNS = "manage_returns"
    VIEW_RETURNS = "view_returns"
    MANAGE_GIFT_CARDS = "manage_gift_cards"
    VIEW_GIFT_CARDS = "view_gift_cards"

# Role-based permissions mapping
ROLE_PERMISSIONS = {
    AdminRole.SUPER_ADMIN: [
        AdminPermission.MANAGE_PRODUCTS, AdminPermission.VIEW_PRODUCTS, AdminPermission.MANAGE_INVENTORY,
        AdminPermission.MANAGE_USERS, AdminPermission.VIEW_USERS,
        AdminPermission.MANAGE_ORDERS, AdminPermission.VIEW_ORDERS, AdminPermission.PROCESS_REFUNDS,
        AdminPermission.VIEW_ANALYTICS, AdminPermission.EXPORT_DATA,
        AdminPermission.MANAGE_SETTINGS, AdminPermission.MANAGE_ADMINS, AdminPermission.VIEW_LOGS,
        # E-commerce permissions
        AdminPermission.MANAGE_PROMOTIONS, AdminPermission.VIEW_PROMOTIONS,
        AdminPermission.MANAGE_SHIPPING, AdminPermission.VIEW_SHIPPING,
        AdminPermission.MANAGE_TAXES, AdminPermission.VIEW_TAXES,
        AdminPermission.MANAGE_RETURNS, AdminPermission.VIEW_RETURNS,
        AdminPermission.MANAGE_GIFT_CARDS, AdminPermission.VIEW_GIFT_CARDS
    ],
    AdminRole.ADMIN: [
        AdminPermission.MANAGE_PRODUCTS, AdminPermission.VIEW_PRODUCTS, AdminPermission.MANAGE_INVENTORY,
        AdminPermission.VIEW_USERS,
        AdminPermission.MANAGE_ORDERS, AdminPermission.VIEW_ORDERS, AdminPermission.PROCESS_REFUNDS,
        AdminPermission.VIEW_ANALYTICS, AdminPermission.EXPORT_DATA,
        # E-commerce permissions (limited for regular admin)
        AdminPermission.VIEW_PROMOTIONS, AdminPermission.VIEW_SHIPPING, AdminPermission.VIEW_TAXES,
        AdminPermission.MANAGE_RETURNS, AdminPermission.VIEW_RETURNS,
        AdminPermission.VIEW_GIFT_CARDS
    ],
    AdminRole.MODERATOR: [
        AdminPermission.VIEW_PRODUCTS, AdminPermission.MANAGE_INVENTORY,
        AdminPermission.VIEW_USERS,
        AdminPermission.VIEW_ORDERS,
        AdminPermission.VIEW_ANALYTICS,
        # E-commerce permissions (view only for moderator)
        AdminPermission.VIEW_PROMOTIONS, AdminPermission.VIEW_SHIPPING, AdminPermission.VIEW_TAXES,
        AdminPermission.VIEW_RETURNS, AdminPermission.VIEW_GIFT_CARDS
    ],
    AdminRole.VIEWER: [
        AdminPermission.VIEW_PRODUCTS,
        AdminPermission.VIEW_USERS,
        AdminPermission.VIEW_ORDERS,
        AdminPermission.VIEW_ANALYTICS,
        # E-commerce permissions (view only)
        AdminPermission.VIEW_PROMOTIONS, AdminPermission.VIEW_SHIPPING, AdminPermission.VIEW_TAXES,
        AdminPermission.VIEW_RETURNS, AdminPermission.VIEW_GIFT_CARDS
    ]
}

class AdminBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    role: AdminRole = AdminRole.VIEWER
    is_active: bool = True
    permissions: List[AdminPermission] = Field(default_factory=list)

class AdminCreate(AdminBase):
    password: str = Field(..., min_length=8)
    created_by: Optional[str] = None  # Admin ID who created this admin

class AdminInDB(AdminBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Session management
    current_session_id: Optional[str] = None
    session_expires_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class AdminResponse(AdminBase):
    id: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    
class AdminUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    role: Optional[AdminRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)
    permissions: Optional[List[AdminPermission]] = None

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class AdminTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    admin: AdminResponse
    permissions: List[AdminPermission]

# Dashboard Analytics Models
class DashboardStats(BaseModel):
    total_users: int = 0
    active_users: int = 0
    total_orders: int = 0
    total_revenue: float = 0.0
    orders_today: int = 0
    revenue_today: float = 0.0
    products_count: int = 0
    low_stock_products: int = 0
    out_of_stock_products: int = 0
    pending_orders: int = 0

class SalesAnalytics(BaseModel):
    daily_sales: List[Dict[str, Any]] = Field(default_factory=list)  # Last 30 days
    monthly_sales: List[Dict[str, Any]] = Field(default_factory=list)  # Last 12 months
    top_products: List[Dict[str, Any]] = Field(default_factory=list)
    sales_by_category: List[Dict[str, Any]] = Field(default_factory=list)

class UserAnalytics(BaseModel):
    new_users_today: int = 0
    new_users_this_week: int = 0
    new_users_this_month: int = 0
    user_growth: List[Dict[str, Any]] = Field(default_factory=list)  # Last 30 days
    user_activity: Dict[str, int] = Field(default_factory=dict)

class RecentActivity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # "order", "user_registration", "product_update", "admin_action"
    description: str
    user_id: Optional[str] = None
    admin_id: Optional[str] = None
    related_id: Optional[str] = None  # product_id, order_id, etc.
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SystemHealth(BaseModel):
    database_status: str = "unknown"  # "healthy", "warning", "error"
    api_response_time: float = 0.0  # in milliseconds
    active_sessions: int = 0
    error_rate: float = 0.0  # percentage
    memory_usage: float = 0.0  # percentage
    disk_usage: float = 0.0  # percentage
    last_backup: Optional[datetime] = None

class NotificationSettings(BaseModel):
    email_notifications: bool = True
    low_stock_alerts: bool = True
    new_order_alerts: bool = True
    system_alerts: bool = True
    daily_reports: bool = False
    weekly_reports: bool = False

class AdminSettings(BaseModel):
    site_name: str = "Nite Putter Pro"
    site_description: str = "Professional Golf Lighting Systems"
    contact_email: EmailStr
    support_email: EmailStr
    company_address: str
    company_phone: str
    currency: str = "USD"
    tax_rate: float = 0.0
    shipping_rate: float = 0.0
    low_stock_threshold: int = 10
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    maintenance_mode: bool = False
    allow_registrations: bool = True
    require_email_verification: bool = True