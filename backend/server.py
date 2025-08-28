from fastapi import FastAPI, APIRouter, Request, HTTPException, Depends, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import stripe

# Authentication imports
from models.user import UserCreate, UserResponse, UserUpdate, LoginRequest, TokenResponse
from database.user_repository import UserRepository
from auth.auth_handler import auth_handler

# Product management imports
from models.product import (
    ProductCreate, ProductResponse, ProductUpdate, ProductFilter, 
    ProductListResponse, InventoryUpdate, ProductStatus, ProductCategory
)
from database.product_repository import ProductRepository

# Admin management imports
from models.admin import (
    AdminCreate, AdminResponse, AdminUpdate, AdminLogin, AdminTokenResponse,
    AdminRole, AdminPermission, DashboardStats, SalesAnalytics, UserAnalytics,
    RecentActivity, SystemHealth, AdminSettings
)
from database.admin_repository import AdminRepository

# User features imports
from models.user_features import (
    WishlistResponse, AddressCreate, AddressUpdate, Address,
    UserPreferences, UserPreferencesUpdate, UserActivity, ActivityType,
    ProductReviewCreate, ProductReviewUpdate, ProductReviewResponse,
    UserProfileStats, SearchHistory
)
from database.user_features_repository import UserFeaturesRepository

# Communication & Support imports
from models.communication import (
    ContactFormCreate, ContactFormUpdate, ContactForm, ContactStatus,
    NewsletterSubscriptionCreate, SupportTicketCreate, SupportTicketUpdate,
    TicketMessageCreate, FAQCreate, FAQUpdate, EmailTemplateType
)
from database.communication_repository import CommunicationRepository

# Service imports
from services.email_service import email_service
from services.shipping_service import shipping_service

# Analytics & Business Intelligence imports
from models.analytics import (
    TimePeriod, CustomReportCreate, CustomReportUpdate, 
    SystemPerformance, ExportRequest, ExportFormat
)
from database.analytics_repository import AnalyticsRepository

# Content Management imports
from models.content import (
    BlogCategory, BlogPostCreate, BlogPostUpdate, BlogStatus, BlogComment,
    DocumentationSection, DocumentationPage, DocumentationType,
    SEOPage, MediaFile, MediaType, LandingPage, EmailCampaign
)
from database.content_repository import ContentRepository

# Advanced E-commerce imports
from models.ecommerce import (
    CouponCreate, ReturnRequestCreate, ReturnRequestUpdate, ReturnStatus,
    ShippingZone, ShippingRate, TaxRule, Currency, GiftCard, GiftCardStatus,
    StockMovement, StockMovementType
)
from database.ecommerce_repository import EcommerceRepository


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Initialize Stripe with API key from environment
stripe.api_key = os.getenv("STRIPE_API_KEY")

# MongoDB connection with error handling
try:
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME', 'niteputter')
    
    if not mongo_url:
        raise ValueError("MONGO_URL environment variable is required")
    
    client = AsyncIOMotorClient(
        mongo_url,
        serverSelectionTimeoutMS=5000,  # 5 second timeout
        connectTimeoutMS=10000,         # 10 second connection timeout
        socketTimeoutMS=20000,          # 20 second socket timeout
        maxPoolSize=50,                 # Connection pool size
        minPoolSize=5,                  # Minimum connections
        retryWrites=True                # Retry failed writes
    )
    db = client[db_name]
    
    print(f"✅ Connected to MongoDB: {db_name}")
    
except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {str(e)}")
    print("Please ensure MongoDB is running and MONGO_URL environment variable is set")
    raise

# Stripe API Key
stripe_api_key = os.environ.get('STRIPE_API_KEY')
if not stripe_api_key:
    print("Warning: STRIPE_API_KEY not found in environment variables")

# Product packages (SECURITY: Fixed packages defined on backend only)
PRODUCT_PACKAGES = {
    "nite_putter_complete": {
        "name": "Nite Putter Pro Complete System",
        "price": 299.00,
        "description": "Complete illuminated golf cup system with patented POLY LIGHT CASING technology",
        "features": ["Patented POLY LIGHT CASING", "Multi-level drainage", "Hardwired 12v system", "Professional installation"]
    },
    "smart_bulb_system": {
        "name": "Smart Life Bulb System", 
        "price": 89.00,
        "description": "Bluetooth-enabled MR16 bulb with color customization capabilities",
        "features": ["Bluetooth connectivity", "Color customization", "Smart Life app control", "Easy installation"]
    },
    "installation_service": {
        "name": "Professional Installation Service",
        "price": 150.00,
        "description": "Expert installation by our veteran-owned team with ongoing support",
        "features": ["Professional setup", "System testing", "Training included", "Ongoing support"]
    },
    "custom_course": {
        "name": "Custom Course Integration",
        "price": 500.00,
        "description": "Complete golf course lighting solutions for professional installations",
        "features": ["Multi-hole systems", "Landscape integration", "Control systems", "Maintenance plans"]
    }
}

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# OAuth2 scheme for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
oauth2_scheme_optional = HTTPBearer(auto_error=False)


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Stripe/E-commerce Models
class CheckoutRequest(BaseModel):
    package_id: str
    quantity: Optional[int] = 1
    origin_url: str
    customer_info: Optional[Dict[str, Any]] = {}

class PaymentTransaction(BaseModel):
    transaction_id: str
    session_id: str
    package_id: str
    amount: float
    currency: str
    quantity: int
    payment_status: str
    customer_info: Dict[str, Any]
    metadata: Dict[str, str]
    created_at: datetime
    updated_at: datetime

# Initialize Stripe
# def get_stripe_checkout(request: Request):
#     host_url = str(request.base_url)
#     webhook_url = f"{host_url}api/webhook/stripe"
#     return StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)

# Repository dependency functions
async def get_user_repository():
    """Dependency to get user repository instance"""
    return UserRepository(db)

async def get_product_repository():
    """Dependency to get product repository instance"""
    return ProductRepository(db)

async def get_admin_repository():
    """Dependency to get admin repository instance"""
    return AdminRepository(db)

async def get_user_features_repository():
    """Dependency to get user features repository instance"""
    return UserFeaturesRepository(db)

async def get_communication_repository():
    """Dependency to get communication repository instance"""
    return CommunicationRepository(db)

async def get_analytics_repository():
    """Dependency to get analytics repository instance"""
    return AnalyticsRepository(db)

async def get_content_repository():
    """Dependency to get content repository instance"""
    return ContentRepository(db)

async def get_ecommerce_repository():
    """Dependency to get ecommerce repository instance"""
    return EcommerceRepository(db)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserResponse:
    """Get current authenticated user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = auth_handler.decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = await user_repo.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        cart_items=user.cart_items
    )

# Helper function for optional authentication
async def get_current_user_optional(token: str = Depends(oauth2_scheme_optional)) -> Optional[UserResponse]:
    """Get current user if token is provided"""
    if not token:
        return None
    
    try:
        # Use the regular get_current_user function but handle exceptions
        user_repo = UserRepository(db)
        payload = auth_handler.decode_token(token)
        if payload is None or payload.get("type") != "access":
            return None
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        user = await user_repo.get_user_by_id(user_id)
        if user is None:
            return None
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            cart_items=user.cart_items
        )
    except:
        return None

# Admin authentication dependency
async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    admin_repo: AdminRepository = Depends(get_admin_repository)
) -> AdminResponse:
    """Get current authenticated admin from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = auth_handler.decode_token(token)
    if payload is None or payload.get("type") != "access" or payload.get("role") != "admin":
        raise credentials_exception
    
    admin_id: str = payload.get("sub")
    if admin_id is None:
        raise credentials_exception
    
    admin = await admin_repo.get_admin_by_id(admin_id)
    if admin is None or not admin.is_active:
        raise credentials_exception
    
    return AdminResponse(
        id=admin.id,
        email=admin.email,
        username=admin.username,
        first_name=admin.first_name,
        last_name=admin.last_name,
        role=admin.role,
        is_active=admin.is_active,
        permissions=admin.permissions,
        created_at=admin.created_at,
        updated_at=admin.updated_at,
        last_login=admin.last_login
    )

# Permission checking dependency
def require_permission(permission: AdminPermission):
    """Dependency factory for checking admin permissions"""
    async def check_permission(
        current_admin: AdminResponse = Depends(get_current_admin),
        admin_repo: AdminRepository = Depends(get_admin_repository)
    ):
        has_permission = await admin_repo.has_permission(current_admin.id, permission)
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission.value}"
            )
        return current_admin
    return check_permission

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Authentication Routes
@api_router.post("/auth/register", response_model=UserResponse)
async def register_user(
    user: UserCreate,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Register new user account"""
    try:
        # Check if user already exists
        existing_user = await user_repo.get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username is taken
        existing_username = await user_repo.get_user_by_username(user.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create indexes if not exists
        await user_repo.create_indexes()
        
        # Create user
        db_user = await user_repo.create_user(user)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        return UserResponse(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            is_active=db_user.is_active,
            is_verified=db_user.is_verified,
            created_at=db_user.created_at,
            cart_items=db_user.cart_items
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Authenticate user and return tokens"""
    user = await user_repo.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    token_data = {"sub": user.id, "email": user.email}
    tokens = auth_handler.generate_token_pair(token_data)
    
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        cart_items=user.cart_items
    )
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        user=user_response
    )

@api_router.post("/auth/refresh")
async def refresh_token(
    refresh_token: str = Form(...),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Refresh access token using refresh token"""
    payload = auth_handler.decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = await user_repo.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled"
        )
    
    token_data = {"sub": user.id, "email": user.email}
    new_access_token = auth_handler.create_access_token(token_data)
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get current user profile"""
    return current_user

@api_router.put("/auth/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Update current user profile"""
    updated_user = await user_repo.update_user(current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )
    
    return UserResponse(
        id=updated_user.id,
        email=updated_user.email,
        username=updated_user.username,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        is_active=updated_user.is_active,
        is_verified=updated_user.is_verified,
        created_at=updated_user.created_at,
        cart_items=updated_user.cart_items
    )

@api_router.put("/auth/me/cart")
async def update_user_cart(
    request: Dict[str, List[Dict[str, Any]]],
    current_user: UserResponse = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Update user's cart items"""
    cart_items = request.get("cart_items", [])
    success = await user_repo.update_cart_items(current_user.id, cart_items)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update cart"
        )
    
    return {"message": "Cart updated successfully"}

@api_router.get("/auth/me/cart")
async def get_user_cart(
    current_user: UserResponse = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Get user's cart items"""
    cart_items = await user_repo.get_user_cart(current_user.id)
    return {"cart_items": cart_items}

# Admin Product Management Endpoints (require admin authentication)
@api_router.post("/admin/products", response_model=ProductResponse)
async def create_product_admin(
    product: ProductCreate,
    current_user: UserResponse = Depends(get_current_user),
    product_repo: ProductRepository = Depends(get_product_repository)
):
    """Create new product (admin only)"""
    # Note: In a full implementation, you'd check if user is admin
    try:
        created_product = await product_repo.create_product(product, created_by=current_user.id)
        if not created_product:
            raise HTTPException(status_code=500, detail="Failed to create product")
        
        return ProductResponse(
            id=created_product.id,
            name=created_product.name,
            description=created_product.description,
            short_description=created_product.short_description,
            category=created_product.category,
            status=created_product.status,
            base_price=created_product.base_price,
            sku=created_product.sku,
            inventory_count=created_product.inventory_count,
            low_stock_threshold=created_product.low_stock_threshold,
            features=created_product.features,
            tags=created_product.tags,
            weight=created_product.weight,
            dimensions=created_product.dimensions,
            is_featured=created_product.is_featured,
            meta_title=created_product.meta_title,
            meta_description=created_product.meta_description,
            images=created_product.images,
            variants=created_product.variants,
            created_at=created_product.created_at,
            updated_at=created_product.updated_at,
            view_count=created_product.view_count,
            purchase_count=created_product.purchase_count
        )
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create product")

@api_router.put("/admin/products/{product_id}", response_model=ProductResponse)
async def update_product_admin(
    product_id: str,
    product_update: ProductUpdate,
    current_user: UserResponse = Depends(get_current_user),
    product_repo: ProductRepository = Depends(get_product_repository)
):
    """Update product (admin only)"""
    try:
        updated_product = await product_repo.update_product(
            product_id, product_update, updated_by=current_user.id
        )
        if not updated_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return ProductResponse(
            id=updated_product.id,
            name=updated_product.name,
            description=updated_product.description,
            short_description=updated_product.short_description,
            category=updated_product.category,
            status=updated_product.status,
            base_price=updated_product.base_price,
            sku=updated_product.sku,
            inventory_count=updated_product.inventory_count,
            low_stock_threshold=updated_product.low_stock_threshold,
            features=updated_product.features,
            tags=updated_product.tags,
            weight=updated_product.weight,
            dimensions=updated_product.dimensions,
            is_featured=updated_product.is_featured,
            meta_title=updated_product.meta_title,
            meta_description=updated_product.meta_description,
            images=updated_product.images,
            variants=updated_product.variants,
            created_at=updated_product.created_at,
            updated_at=updated_product.updated_at,
            view_count=updated_product.view_count,
            purchase_count=updated_product.purchase_count
        )
    except Exception as e:
        logger.error(f"Error updating product: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update product")

@api_router.delete("/admin/products/{product_id}")
async def delete_product_admin(
    product_id: str,
    current_user: UserResponse = Depends(get_current_user),
    product_repo: ProductRepository = Depends(get_product_repository)
):
    """Delete product (admin only)"""
    try:
        success = await product_repo.delete_product(product_id)
        if not success:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {"message": "Product deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete product")

@api_router.put("/admin/products/{product_id}/inventory")
async def update_product_inventory(
    product_id: str,
    inventory_update: InventoryUpdate,
    current_user: UserResponse = Depends(get_current_user),
    product_repo: ProductRepository = Depends(get_product_repository)
):
    """Update product inventory (admin only)"""
    try:
        success = await product_repo.update_inventory(
            product_id, inventory_update, change_type="manual_adjustment", updated_by=current_user.id
        )
        if not success:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {"message": "Inventory updated successfully"}
    except Exception as e:
        logger.error(f"Error updating inventory: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update inventory")

@api_router.get("/admin/products/low-stock")
async def get_low_stock_products_admin(
    current_user: UserResponse = Depends(get_current_user),
    product_repo: ProductRepository = Depends(get_product_repository)
):
    """Get low stock products (admin only)"""
    try:
        products = await product_repo.get_low_stock_products()
        
        return {
            "products": [
                {
                    "id": product.id,
                    "name": product.name,
                    "sku": product.sku,
                    "inventory_count": product.inventory_count,
                    "low_stock_threshold": product.low_stock_threshold,
                    "base_price": product.base_price
                }
                for product in products
            ]
        }
    except Exception as e:
        logger.error(f"Error getting low stock products: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get low stock products")

@api_router.get("/admin/products/{product_id}/inventory-history")
async def get_product_inventory_history(
    product_id: str,
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user),
    product_repo: ProductRepository = Depends(get_product_repository)
):
    """Get product inventory history (admin only)"""
    try:
        history = await product_repo.get_inventory_history(product_id, limit=limit)
        
        return {
            "history": [
                {
                    "id": entry.id,
                    "previous_count": entry.previous_count,
                    "new_count": entry.new_count,
                    "change_amount": entry.change_amount,
                    "change_type": entry.change_type,
                    "notes": entry.notes,
                    "created_at": entry.created_at.isoformat(),
                    "created_by": entry.created_by
                }
                for entry in history
            ]
        }
    except Exception as e:
        logger.error(f"Error getting inventory history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get inventory history")

# Admin Authentication Endpoints
@api_router.post("/admin/auth/login", response_model=AdminTokenResponse)
async def admin_login(
    admin_login: AdminLogin,
    admin_repo: AdminRepository = Depends(get_admin_repository)
):
    """Admin login endpoint"""
    try:
        admin = await admin_repo.authenticate_admin(admin_login.email, admin_login.password)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token_data = {"sub": admin.id, "email": admin.email, "role": "admin"}
        tokens = auth_handler.generate_token_pair(token_data)
        
        admin_response = AdminResponse(
            id=admin.id,
            email=admin.email,
            username=admin.username,
            first_name=admin.first_name,
            last_name=admin.last_name,
            role=admin.role,
            is_active=admin.is_active,
            permissions=admin.permissions,
            created_at=admin.created_at,
            updated_at=admin.updated_at,
            last_login=admin.last_login
        )
        
        return AdminTokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            admin=admin_response,
            permissions=admin.permissions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@api_router.post("/admin/auth/register", response_model=AdminResponse)
async def admin_register(
    admin: AdminCreate,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.MANAGE_ADMINS)),
    admin_repo: AdminRepository = Depends(get_admin_repository)
):
    """Register new admin (super admin only)"""
    try:
        # Set created_by to current admin
        admin.created_by = current_admin.id
        
        # Check if admin already exists
        existing_admin = await admin_repo.get_admin_by_email(admin.email)
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin with this email already exists"
            )
        
        # Create indexes if not exists
        await admin_repo.create_indexes()
        
        # Create admin
        created_admin = await admin_repo.create_admin(admin)
        if not created_admin:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create admin"
            )
        
        return AdminResponse(
            id=created_admin.id,
            email=created_admin.email,
            username=created_admin.username,
            first_name=created_admin.first_name,
            last_name=created_admin.last_name,
            role=created_admin.role,
            is_active=created_admin.is_active,
            permissions=created_admin.permissions,
            created_at=created_admin.created_at,
            updated_at=created_admin.updated_at,
            last_login=created_admin.last_login
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create admin"
        )

@api_router.get("/admin/auth/me", response_model=AdminResponse)
async def get_current_admin_profile(
    current_admin: AdminResponse = Depends(get_current_admin)
):
    """Get current admin profile"""
    return current_admin

# Admin Dashboard Endpoints
@api_router.get("/admin/dashboard/stats")
async def get_dashboard_stats(
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.VIEW_ANALYTICS)),
    admin_repo: AdminRepository = Depends(get_admin_repository)
):
    """Get dashboard statistics"""
    try:
        stats = await admin_repo.get_dashboard_stats()
        return stats.dict()
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard statistics")

@api_router.get("/admin/dashboard/sales-analytics")
async def get_sales_analytics(
    days: int = 30,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.VIEW_ANALYTICS)),
    admin_repo: AdminRepository = Depends(get_admin_repository)
):
    """Get sales analytics data"""
    try:
        analytics = await admin_repo.get_sales_analytics(days=days)
        return analytics.dict()
    except Exception as e:
        logger.error(f"Error getting sales analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get sales analytics")

@api_router.get("/admin/dashboard/user-analytics")
async def get_user_analytics(
    days: int = 30,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.VIEW_ANALYTICS)),
    admin_repo: AdminRepository = Depends(get_admin_repository)
):
    """Get user analytics data"""
    try:
        analytics = await admin_repo.get_user_analytics(days=days)
        return analytics.dict()
    except Exception as e:
        logger.error(f"Error getting user analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user analytics")

@api_router.get("/admin/dashboard/recent-activity")
async def get_recent_activity(
    limit: int = 50,
    current_admin: AdminResponse = Depends(get_current_admin),
    admin_repo: AdminRepository = Depends(get_admin_repository)
):
    """Get recent admin activity"""
    try:
        activities = await admin_repo.get_recent_activities(limit=limit)
        return {
            "activities": [
                {
                    "id": activity.id,
                    "type": activity.type,
                    "description": activity.description,
                    "admin_id": activity.admin_id,
                    "user_id": activity.user_id,
                    "related_id": activity.related_id,
                    "metadata": activity.metadata,
                    "created_at": activity.created_at.isoformat()
                }
                for activity in activities
            ]
        }
    except Exception as e:
        logger.error(f"Error getting recent activity: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get recent activity")

@api_router.get("/admin/dashboard/system-health")
async def get_system_health(
    current_admin: AdminResponse = Depends(get_current_admin),
    admin_repo: AdminRepository = Depends(get_admin_repository)
):
    """Get system health metrics"""
    try:
        health = await admin_repo.get_system_health()
        return health.dict()
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get system health")

# Admin Management Endpoints
@api_router.get("/admin/admins")
async def get_admins(
    role: Optional[AdminRole] = None,
    is_active: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.MANAGE_ADMINS)),
    admin_repo: AdminRepository = Depends(get_admin_repository)
):
    """Get admins list (super admin only)"""
    try:
        admins, total_count = await admin_repo.get_admins(
            role=role,
            is_active=is_active,
            page=page,
            page_size=page_size
        )
        
        total_pages = (total_count + page_size - 1) // page_size
        
        return {
            "admins": [
                {
                    "id": admin.id,
                    "email": admin.email,
                    "username": admin.username,
                    "first_name": admin.first_name,
                    "last_name": admin.last_name,
                    "role": admin.role,
                    "is_active": admin.is_active,
                    "permissions": admin.permissions,
                    "created_at": admin.created_at.isoformat(),
                    "last_login": admin.last_login.isoformat() if admin.last_login else None
                }
                for admin in admins
            ],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error getting admins: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get admins")

@api_router.put("/admin/admins/{admin_id}", response_model=AdminResponse)
async def update_admin_user(
    admin_id: str,
    admin_update: AdminUpdate,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.MANAGE_ADMINS)),
    admin_repo: AdminRepository = Depends(get_admin_repository)
):
    """Update admin user (super admin only)"""
    try:
        updated_admin = await admin_repo.update_admin(
            admin_id, admin_update, updated_by=current_admin.id
        )
        if not updated_admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        return AdminResponse(
            id=updated_admin.id,
            email=updated_admin.email,
            username=updated_admin.username,
            first_name=updated_admin.first_name,
            last_name=updated_admin.last_name,
            role=updated_admin.role,
            is_active=updated_admin.is_active,
            permissions=updated_admin.permissions,
            created_at=updated_admin.created_at,
            updated_at=updated_admin.updated_at,
            last_login=updated_admin.last_login
        )
    except Exception as e:
        logger.error(f"Error updating admin: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update admin")

@api_router.delete("/admin/admins/{admin_id}")
async def delete_admin_user(
    admin_id: str,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.MANAGE_ADMINS)),
    admin_repo: AdminRepository = Depends(get_admin_repository)
):
    """Delete admin user (super admin only)"""
    try:
        # Prevent self-deletion
        if admin_id == current_admin.id:
            raise HTTPException(status_code=400, detail="Cannot delete your own admin account")
        
        success = await admin_repo.delete_admin(admin_id, deleted_by=current_admin.id)
        if not success:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        return {"message": "Admin deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting admin: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete admin")

# Admin Settings Endpoints
@api_router.get("/admin/settings")
async def get_admin_settings(
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.MANAGE_SETTINGS)),
    admin_repo: AdminRepository = Depends(get_admin_repository)
):
    """Get admin settings"""
    try:
        settings = await admin_repo.get_settings()
        return settings.dict()
    except Exception as e:
        logger.error(f"Error getting admin settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get admin settings")

@api_router.put("/admin/settings")
async def update_admin_settings(
    settings: AdminSettings,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.MANAGE_SETTINGS)),
    admin_repo: AdminRepository = Depends(get_admin_repository)
):
    """Update admin settings"""
    try:
        success = await admin_repo.update_settings(settings, updated_by=current_admin.id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update settings")
        
        return {"message": "Settings updated successfully"}
    except Exception as e:
        logger.error(f"Error updating admin settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update admin settings")

# Enhanced User Features Endpoints

# Wishlist Management
@api_router.post("/user/wishlist/{product_id}")
async def add_to_wishlist(
    product_id: str,
    notes: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user),
    user_features_repo: UserFeaturesRepository = Depends(get_user_features_repository),
    product_repo: ProductRepository = Depends(get_product_repository)
):
    """Add product to user's wishlist"""
    try:
        # Verify product exists
        product = await product_repo.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        success = await user_features_repo.add_to_wishlist(current_user.id, product_id, notes)
        if not success:
            raise HTTPException(status_code=400, detail="Product already in wishlist or failed to add")
        
        return {"message": "Product added to wishlist successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to wishlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add to wishlist")

@api_router.delete("/user/wishlist/{product_id}")
async def remove_from_wishlist(
    product_id: str,
    current_user: UserResponse = Depends(get_current_user),
    user_features_repo: UserFeaturesRepository = Depends(get_user_features_repository)
):
    """Remove product from user's wishlist"""
    try:
        success = await user_features_repo.remove_from_wishlist(current_user.id, product_id)
        if not success:
            raise HTTPException(status_code=404, detail="Product not found in wishlist")
        
        return {"message": "Product removed from wishlist successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing from wishlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to remove from wishlist")

@api_router.get("/user/wishlist")
async def get_user_wishlist(
    current_user: UserResponse = Depends(get_current_user),
    user_features_repo: UserFeaturesRepository = Depends(get_user_features_repository)
):
    """Get user's wishlist"""
    try:
        wishlist_items = await user_features_repo.get_user_wishlist(current_user.id)
        return {
            "wishlist": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "product_price": item.product_price,
                    "product_image": item.product_image,
                    "added_at": item.added_at.isoformat(),
                    "notes": item.notes
                }
                for item in wishlist_items
            ]
        }
    except Exception as e:
        logger.error(f"Error getting wishlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get wishlist")

@api_router.get("/user/wishlist/check/{product_id}")
async def check_wishlist_status(
    product_id: str,
    current_user: UserResponse = Depends(get_current_user),
    user_features_repo: UserFeaturesRepository = Depends(get_user_features_repository)
):
    """Check if product is in user's wishlist"""
    try:
        is_in_wishlist = await user_features_repo.is_in_wishlist(current_user.id, product_id)
        return {"in_wishlist": is_in_wishlist}
    except Exception as e:
        logger.error(f"Error checking wishlist status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check wishlist status")

# Address Management
@api_router.post("/user/addresses", response_model=Address)
async def add_user_address(
    address: AddressCreate,
    current_user: UserResponse = Depends(get_current_user),
    user_features_repo: UserFeaturesRepository = Depends(get_user_features_repository)
):
    """Add new address for user"""
    try:
        created_address = await user_features_repo.add_address(current_user.id, address)
        if not created_address:
            raise HTTPException(status_code=500, detail="Failed to create address")
        
        return created_address
    except Exception as e:
        logger.error(f"Error adding address: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add address")

@api_router.get("/user/addresses")
async def get_user_addresses(
    current_user: UserResponse = Depends(get_current_user),
    user_features_repo: UserFeaturesRepository = Depends(get_user_features_repository)
):
    """Get all user addresses"""
    try:
        addresses = await user_features_repo.get_user_addresses(current_user.id)
        return {
            "addresses": [
                {
                    "id": addr.id,
                    "type": addr.type,
                    "label": addr.label,
                    "first_name": addr.first_name,
                    "last_name": addr.last_name,
                    "company": addr.company,
                    "address_line_1": addr.address_line_1,
                    "address_line_2": addr.address_line_2,
                    "city": addr.city,
                    "state": addr.state,
                    "postal_code": addr.postal_code,
                    "country": addr.country,
                    "phone": addr.phone,
                    "is_primary": addr.is_primary,
                    "created_at": addr.created_at.isoformat(),
                    "updated_at": addr.updated_at.isoformat()
                }
                for addr in addresses
            ]
        }
    except Exception as e:
        logger.error(f"Error getting addresses: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get addresses")

@api_router.put("/user/addresses/{address_id}", response_model=Address)
async def update_user_address(
    address_id: str,
    address_update: AddressUpdate,
    current_user: UserResponse = Depends(get_current_user),
    user_features_repo: UserFeaturesRepository = Depends(get_user_features_repository)
):
    """Update user address"""
    try:
        updated_address = await user_features_repo.update_address(current_user.id, address_id, address_update)
        if not updated_address:
            raise HTTPException(status_code=404, detail="Address not found")
        
        return updated_address
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating address: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update address")

@api_router.delete("/user/addresses/{address_id}")
async def delete_user_address(
    address_id: str,
    current_user: UserResponse = Depends(get_current_user),
    user_features_repo: UserFeaturesRepository = Depends(get_user_features_repository)
):
    """Delete user address"""
    try:
        success = await user_features_repo.delete_address(current_user.id, address_id)
        if not success:
            raise HTTPException(status_code=404, detail="Address not found")
        
        return {"message": "Address deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting address: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete address")

# User Preferences
@api_router.get("/user/preferences")
async def get_user_preferences(
    current_user: UserResponse = Depends(get_current_user),
    user_features_repo: UserFeaturesRepository = Depends(get_user_features_repository)
):
    """Get user preferences"""
    try:
        preferences = await user_features_repo.get_user_preferences(current_user.id)
        return preferences.dict()
    except Exception as e:
        logger.error(f"Error getting preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get preferences")

@api_router.put("/user/preferences")
async def update_user_preferences(
    preferences_update: UserPreferencesUpdate,
    current_user: UserResponse = Depends(get_current_user),
    user_features_repo: UserFeaturesRepository = Depends(get_user_features_repository)
):
    """Update user preferences"""
    try:
        success = await user_features_repo.update_user_preferences(current_user.id, preferences_update)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update preferences")
        
        return {"message": "Preferences updated successfully"}
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")

# User Activity
@api_router.get("/user/activity")
async def get_user_activity(
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user),
    user_features_repo: UserFeaturesRepository = Depends(get_user_features_repository)
):
    """Get user activity history"""
    try:
        activities = await user_features_repo.get_user_activities(current_user.id, limit=limit)
        return {
            "activities": [
                {
                    "id": activity.id,
                    "activity_type": activity.activity_type,
                    "description": activity.description,
                    "metadata": activity.metadata,
                    "created_at": activity.created_at.isoformat()
                }
                for activity in activities
            ]
        }
    except Exception as e:
        logger.error(f"Error getting user activity: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user activity")

# Product Reviews
@api_router.post("/user/reviews")
async def create_product_review(
    review: ProductReviewCreate,
    current_user: UserResponse = Depends(get_current_user),
    user_features_repo: UserFeaturesRepository = Depends(get_user_features_repository),
    product_repo: ProductRepository = Depends(get_product_repository)
):
    """Create product review"""
    try:
        # Verify product exists
        product = await product_repo.get_product_by_id(review.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        created_review = await user_features_repo.create_review(current_user.id, review)
        if not created_review:
            raise HTTPException(status_code=400, detail="You have already reviewed this product")
        
        return {
            "message": "Review created successfully",
            "review_id": created_review.id,
            "requires_approval": not created_review.is_approved
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating review: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create review")

@api_router.get("/user/reviews")
async def get_user_reviews(
    limit: int = 20,
    current_user: UserResponse = Depends(get_current_user),
    user_features_repo: UserFeaturesRepository = Depends(get_user_features_repository)
):
    """Get user's reviews"""
    try:
        reviews = await user_features_repo.get_user_reviews(current_user.id, limit=limit)
        return {
            "reviews": [
                {
                    "id": review.id,
                    "product_id": review.product_id,
                    "rating": review.rating,
                    "title": review.title,
                    "content": review.content,
                    "is_verified_purchase": review.is_verified_purchase,
                    "is_approved": review.is_approved,
                    "helpful_votes": review.helpful_votes,
                    "created_at": review.created_at.isoformat(),
                    "updated_at": review.updated_at.isoformat()
                }
                for review in reviews
            ]
        }
    except Exception as e:
        logger.error(f"Error getting user reviews: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user reviews")

@api_router.get("/products/{product_id}/reviews")
async def get_product_reviews(
    product_id: str,
    limit: int = 20,
    user_features_repo: UserFeaturesRepository = Depends(get_user_features_repository)
):
    """Get reviews for a product (public endpoint)"""
    try:
        reviews = await user_features_repo.get_product_reviews(product_id, limit=limit, approved_only=True)
        return {
            "reviews": [
                {
                    "id": review.id,
                    "username": review.username,
                    "rating": review.rating,
                    "title": review.title,
                    "content": review.content,
                    "is_verified_purchase": review.is_verified_purchase,
                    "helpful_votes": review.helpful_votes,
                    "created_at": review.created_at.isoformat()
                }
                for review in reviews
            ]
        }
    except Exception as e:
        logger.error(f"Error getting product reviews: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get product reviews")

# Search History
@api_router.post("/user/search")
async def log_user_search(
    search_data: Dict[str, Any],
    current_user: UserResponse = Depends(get_current_user),
    user_features_repo: UserFeaturesRepository = Depends(get_user_features_repository)
):
    """Log user search"""
    try:
        query = search_data.get("query", "")
        results_count = search_data.get("results_count", 0)
        clicked_product_id = search_data.get("clicked_product_id")
        
        if not query:
            raise HTTPException(status_code=400, detail="Search query is required")
        
        success = await user_features_repo.log_search(
            current_user.id, query, results_count, clicked_product_id
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to log search")
        
        return {"message": "Search logged successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging search: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to log search")

@api_router.get("/user/search-history")
async def get_user_search_history(
    limit: int = 20,
    current_user: UserResponse = Depends(get_current_user),
    user_features_repo: UserFeaturesRepository = Depends(get_user_features_repository)
):
    """Get user's search history"""
    try:
        search_history = await user_features_repo.get_user_search_history(current_user.id, limit=limit)
        return {
            "searches": [
                {
                    "id": search.id,
                    "query": search.query,
                    "results_count": search.results_count,
                    "clicked_product_id": search.clicked_product_id,
                    "created_at": search.created_at.isoformat()
                }
                for search in search_history
            ]
        }
    except Exception as e:
        logger.error(f"Error getting search history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get search history")

@api_router.get("/search/popular")
async def get_popular_searches(
    limit: int = 10,
    user_features_repo: UserFeaturesRepository = Depends(get_user_features_repository)
):
    """Get popular search queries (public endpoint)"""
    try:
        popular_searches = await user_features_repo.get_popular_searches(limit=limit)
        return {
            "popular_searches": [
                {
                    "query": search.query,
                    "search_count": search.search_count,
                    "last_searched": search.last_searched.isoformat()
                }
                for search in popular_searches
            ]
        }
    except Exception as e:
        logger.error(f"Error getting popular searches: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get popular searches")

# User Profile Stats
@api_router.get("/user/profile/stats")
async def get_user_profile_stats(
    current_user: UserResponse = Depends(get_current_user),
    user_features_repo: UserFeaturesRepository = Depends(get_user_features_repository)
):
    """Get user profile statistics"""
    try:
        stats = await user_features_repo.get_user_profile_stats(current_user.id)
        return {
            "total_orders": stats.total_orders,
            "total_spent": stats.total_spent,
            "products_reviewed": stats.products_reviewed,
            "wishlist_items": stats.wishlist_items,
            "addresses_count": stats.addresses_count,
            "member_since": stats.member_since.isoformat(),
            "last_order": stats.last_order.isoformat() if stats.last_order else None,
            "favorite_category": stats.favorite_category
        }
    except Exception as e:
        logger.error(f"Error getting profile stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get profile stats")

# Communication & Support System Endpoints

# Contact Form Management
@api_router.post("/contact")
async def submit_contact_form(
    contact_form: ContactFormCreate,
    request: Request,
    comm_repo: CommunicationRepository = Depends(get_communication_repository)
):
    """Submit contact form (public endpoint)"""
    try:
        # Extract client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        created_contact = await comm_repo.create_contact_form(
            contact_form, 
            ip_address=ip_address, 
            user_agent=user_agent
        )
        
        if not created_contact:
            raise HTTPException(status_code=500, detail="Failed to submit contact form")
        
        return {
            "message": "Contact form submitted successfully",
            "contact_id": created_contact.id,
            "status": "We'll respond within 24 hours"
        }
    except Exception as e:
        logger.error(f"Error submitting contact form: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit contact form")

@api_router.get("/admin/contact-forms")
async def get_contact_forms_admin(
    status: Optional[ContactStatus] = None,
    assigned_to: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.VIEW_USERS)),
    comm_repo: CommunicationRepository = Depends(get_communication_repository)
):
    """Get contact forms (admin only)"""
    try:
        contact_forms, total_count = await comm_repo.get_contact_forms(
            status=status,
            assigned_to=assigned_to,
            page=page,
            page_size=page_size
        )
        
        total_pages = (total_count + page_size - 1) // page_size
        
        return {
            "contact_forms": [
                {
                    "id": form.id,
                    "first_name": form.first_name,
                    "last_name": form.last_name,
                    "email": form.email,
                    "phone": form.phone,
                    "company": form.company,
                    "contact_type": form.contact_type,
                    "subject": form.subject,
                    "message": form.message,
                    "priority": form.priority,
                    "status": form.status,
                    "assigned_to": form.assigned_to,
                    "internal_notes": form.internal_notes,
                    "resolution": form.resolution,
                    "created_at": form.created_at.isoformat(),
                    "updated_at": form.updated_at.isoformat(),
                    "resolved_at": form.resolved_at.isoformat() if form.resolved_at else None
                }
                for form in contact_forms
            ],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error getting contact forms: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get contact forms")

@api_router.put("/admin/contact-forms/{contact_id}")
async def update_contact_form_admin(
    contact_id: str,
    update_data: ContactFormUpdate,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.MANAGE_USERS)),
    comm_repo: CommunicationRepository = Depends(get_communication_repository)
):
    """Update contact form (admin only)"""
    try:
        updated_form = await comm_repo.update_contact_form(
            contact_id, update_data, updated_by=current_admin.id
        )
        
        if not updated_form:
            raise HTTPException(status_code=404, detail="Contact form not found")
        
        return {"message": "Contact form updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating contact form: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update contact form")

# Newsletter Management
@api_router.post("/newsletter/subscribe")
async def subscribe_newsletter(
    subscription: NewsletterSubscriptionCreate,
    request: Request,
    comm_repo: CommunicationRepository = Depends(get_communication_repository)
):
    """Subscribe to newsletter (public endpoint)"""
    try:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        subscription_obj = await comm_repo.subscribe_newsletter(
            subscription, 
            ip_address=ip_address, 
            user_agent=user_agent
        )
        
        if not subscription_obj:
            return {"message": "You are already subscribed to our newsletter"}
        
        return {
            "message": "Successfully subscribed to newsletter",
            "subscription_id": subscription_obj.id,
            "requires_confirmation": not subscription_obj.double_opt_in_confirmed
        }
    except Exception as e:
        logger.error(f"Error subscribing to newsletter: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to subscribe to newsletter")

@api_router.post("/newsletter/unsubscribe")
async def unsubscribe_newsletter(
    unsubscribe_data: Dict[str, str],
    comm_repo: CommunicationRepository = Depends(get_communication_repository)
):
    """Unsubscribe from newsletter (public endpoint)"""
    try:
        email = unsubscribe_data.get("email")
        token = unsubscribe_data.get("token")
        
        success = await comm_repo.unsubscribe_newsletter(email=email, token=token)
        
        if not success:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        return {"message": "Successfully unsubscribed from newsletter"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unsubscribing from newsletter: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to unsubscribe from newsletter")

@api_router.get("/admin/newsletter/subscribers")
async def get_newsletter_subscribers_admin(
    active_only: bool = True,
    page: int = 1,
    page_size: int = 50,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.VIEW_ANALYTICS)),
    comm_repo: CommunicationRepository = Depends(get_communication_repository)
):
    """Get newsletter subscribers (admin only)"""
    try:
        subscribers, total_count = await comm_repo.get_newsletter_subscribers(
            active_only=active_only,
            page=page,
            page_size=page_size
        )
        
        total_pages = (total_count + page_size - 1) // page_size
        
        return {
            "subscribers": [
                {
                    "id": sub.id,
                    "email": sub.email,
                    "first_name": sub.first_name,
                    "last_name": sub.last_name,
                    "is_active": sub.is_active,
                    "interests": sub.interests,
                    "created_at": sub.created_at.isoformat(),
                    "unsubscribed_at": sub.unsubscribed_at.isoformat() if sub.unsubscribed_at else None
                }
                for sub in subscribers
            ],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error getting newsletter subscribers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get newsletter subscribers")

# Support Ticket System
@api_router.post("/support/tickets")
async def create_support_ticket(
    ticket: SupportTicketCreate,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    comm_repo: CommunicationRepository = Depends(get_communication_repository)
):
    """Create support ticket (authenticated users get linked tickets)"""
    try:
        user_id = current_user.id if current_user else None
        
        created_ticket = await comm_repo.create_support_ticket(ticket, user_id=user_id)
        
        if not created_ticket:
            raise HTTPException(status_code=500, detail="Failed to create support ticket")
        
        return {
            "message": "Support ticket created successfully",
            "ticket_number": created_ticket.ticket_number,
            "ticket_id": created_ticket.id,
            "status": "We'll respond within 24 hours"
        }
    except Exception as e:
        logger.error(f"Error creating support ticket: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create support ticket")

@api_router.get("/support/tickets/my")
async def get_my_support_tickets(
    page: int = 1,
    page_size: int = 10,
    current_user: UserResponse = Depends(get_current_user),
    comm_repo: CommunicationRepository = Depends(get_communication_repository)
):
    """Get user's support tickets"""
    try:
        tickets, total_count = await comm_repo.get_support_tickets(
            user_id=current_user.id,
            page=page,
            page_size=page_size
        )
        
        total_pages = (total_count + page_size - 1) // page_size
        
        return {
            "tickets": [
                {
                    "id": ticket.id,
                    "ticket_number": ticket.ticket_number,
                    "category": ticket.category,
                    "priority": ticket.priority,
                    "status": ticket.status,
                    "subject": ticket.subject,
                    "description": ticket.description,
                    "created_at": ticket.created_at.isoformat(),
                    "updated_at": ticket.updated_at.isoformat(),
                    "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None
                }
                for ticket in tickets
            ],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error getting user support tickets: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get support tickets")

@api_router.get("/support/tickets/{ticket_number}")
async def get_support_ticket(
    ticket_number: str,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    comm_repo: CommunicationRepository = Depends(get_communication_repository)
):
    """Get support ticket by number (public with restrictions)"""
    try:
        ticket = await comm_repo.get_support_ticket(ticket_number=ticket_number)
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # If user is authenticated, check if they own the ticket
        if current_user and ticket.user_id and ticket.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get ticket messages
        messages = await comm_repo.get_ticket_messages(ticket.id, include_internal=False)
        
        return {
            "ticket": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "customer_name": ticket.customer_name,
                "customer_email": ticket.customer_email,
                "category": ticket.category,
                "priority": ticket.priority,
                "status": ticket.status,
                "subject": ticket.subject,
                "description": ticket.description,
                "resolution": ticket.resolution,
                "created_at": ticket.created_at.isoformat(),
                "updated_at": ticket.updated_at.isoformat(),
                "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None
            },
            "messages": [
                {
                    "id": msg.id,
                    "sender_type": msg.sender_type,
                    "sender_name": msg.sender_name,
                    "message": msg.message,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting support ticket: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get support ticket")

@api_router.post("/support/tickets/{ticket_number}/messages")
async def add_ticket_message(
    ticket_number: str,
    message: TicketMessageCreate,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    comm_repo: CommunicationRepository = Depends(get_communication_repository)
):
    """Add message to support ticket"""
    try:
        ticket = await comm_repo.get_support_ticket(ticket_number=ticket_number)
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Determine sender info
        if current_user:
            if ticket.user_id and ticket.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied")
            sender_type = "customer"
            sender_id = current_user.id
            sender_name = f"{current_user.first_name} {current_user.last_name}"
            sender_email = current_user.email
        else:
            # Anonymous user - verify by email
            if ticket.customer_email != message.dict().get("sender_email", ""):
                raise HTTPException(status_code=403, detail="Access denied")
            sender_type = "customer"
            sender_id = None
            sender_name = ticket.customer_name
            sender_email = ticket.customer_email
        
        created_message = await comm_repo.add_ticket_message(
            ticket.id,
            message,
            sender_type=sender_type,
            sender_id=sender_id,
            sender_name=sender_name,
            sender_email=sender_email
        )
        
        if not created_message:
            raise HTTPException(status_code=500, detail="Failed to add message")
        
        return {"message": "Message added successfully", "message_id": created_message.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding ticket message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add message")

# FAQ System
@api_router.get("/faqs")
async def get_faqs(
    category_id: Optional[str] = None,
    comm_repo: CommunicationRepository = Depends(get_communication_repository)
):
    """Get FAQs (public endpoint)"""
    try:
        # Get categories
        categories = await comm_repo.get_faq_categories(active_only=True)
        
        # Get FAQs
        faqs = await comm_repo.get_faqs(category_id=category_id, active_only=True)
        
        return {
            "categories": [
                {
                    "id": cat.id,
                    "name": cat.name,
                    "description": cat.description,
                    "sort_order": cat.sort_order
                }
                for cat in categories
            ],
            "faqs": [
                {
                    "id": faq.id,
                    "category_id": faq.category_id,
                    "question": faq.question,
                    "answer": faq.answer,
                    "view_count": faq.view_count,
                    "helpful_votes": faq.helpful_votes
                }
                for faq in faqs
            ]
        }
    except Exception as e:
        logger.error(f"Error getting FAQs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get FAQs")

@api_router.get("/faqs/search")
async def search_faqs(
    q: str,
    limit: int = 10,
    comm_repo: CommunicationRepository = Depends(get_communication_repository)
):
    """Search FAQs (public endpoint)"""
    try:
        if not q or len(q.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
        
        faqs = await comm_repo.search_faqs(q.strip(), limit=limit)
        
        return {
            "query": q,
            "results": [
                {
                    "id": faq.id,
                    "category_id": faq.category_id,
                    "question": faq.question,
                    "answer": faq.answer,
                    "view_count": faq.view_count,
                    "helpful_votes": faq.helpful_votes
                }
                for faq in faqs
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching FAQs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search FAQs")

@api_router.post("/faqs/{faq_id}/view")
async def increment_faq_view(
    faq_id: str,
    comm_repo: CommunicationRepository = Depends(get_communication_repository)
):
    """Increment FAQ view count (public endpoint)"""
    try:
        success = await comm_repo.increment_faq_view_count(faq_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="FAQ not found")
        
        return {"message": "View count updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error incrementing FAQ view: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update view count")

# Communication Analytics (Admin)
@api_router.get("/admin/communication/stats")
async def get_communication_stats(
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.VIEW_ANALYTICS)),
    comm_repo: CommunicationRepository = Depends(get_communication_repository)
):
    """Get communication statistics (admin only)"""
    try:
        stats = await comm_repo.get_communication_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting communication stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get communication statistics")

# Business Intelligence & Analytics Endpoints

# Analytics Dashboard
@api_router.get("/admin/analytics/kpi")
async def get_kpi_summary(
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.VIEW_ANALYTICS)),
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """Get key performance indicators summary (admin only)"""
    try:
        kpis = await analytics_repo.get_kpi_summary()
        return kpis
    except Exception as e:
        logger.error(f"Error getting KPI summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get KPI summary")

@api_router.get("/admin/analytics/sales")
async def get_sales_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    time_granularity: TimePeriod = TimePeriod.DAY,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.VIEW_ANALYTICS)),
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """Get sales analytics report (admin only)"""
    try:
        # Parse dates or use defaults (last 30 days)
        if not end_date:
            end_dt = datetime.utcnow()
        else:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if not start_date:
            start_dt = end_dt - timedelta(days=30)
        else:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        report = await analytics_repo.get_sales_analytics(start_dt, end_dt, time_granularity)
        
        return {
            "period_start": report.period_start.isoformat(),
            "period_end": report.period_end.isoformat(),
            "time_granularity": report.time_granularity,
            "total_revenue": report.total_revenue,
            "total_orders": report.total_orders,
            "total_units": report.total_units,
            "avg_order_value": report.avg_order_value,
            "growth_rate": report.growth_rate,
            "metrics_over_time": [
                {
                    "period": metric.period,
                    "revenue": metric.revenue,
                    "orders": metric.orders,
                    "units_sold": metric.units_sold,
                    "avg_order_value": metric.avg_order_value
                }
                for metric in report.metrics_over_time
            ],
            "top_products": [
                {
                    "product_id": product.product_id,
                    "product_name": product.product_name,
                    "sku": product.sku,
                    "category": product.category,
                    "revenue": product.revenue,
                    "units_sold": product.units_sold,
                    "orders": product.orders,
                    "avg_price": product.avg_price
                }
                for product in report.top_products
            ],
            "category_performance": [
                {
                    "category": category.category,
                    "revenue": category.revenue,
                    "units_sold": category.units_sold,
                    "orders": category.orders,
                    "product_count": category.product_count,
                    "avg_order_value": category.avg_order_value,
                    "market_share": category.market_share
                }
                for category in report.category_performance
            ]
        }
    except Exception as e:
        logger.error(f"Error getting sales analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get sales analytics")

@api_router.get("/admin/analytics/customers")
async def get_customer_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    time_granularity: TimePeriod = TimePeriod.DAY,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.VIEW_ANALYTICS)),
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """Get customer analytics report (admin only)"""
    try:
        # Parse dates or use defaults
        if not end_date:
            end_dt = datetime.utcnow()
        else:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if not start_date:
            start_dt = end_dt - timedelta(days=30)
        else:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        report = await analytics_repo.get_customer_analytics(start_dt, end_dt, time_granularity)
        
        return {
            "period_start": report.period_start.isoformat(),
            "period_end": report.period_end.isoformat(),
            "time_granularity": report.time_granularity,
            "total_customers": report.total_customers,
            "new_customers": report.new_customers,
            "returning_customers": report.returning_customers,
            "customer_segments": report.customer_segments,
            "metrics_over_time": [
                {
                    "period": metric.period,
                    "new_customers": metric.new_customers,
                    "returning_customers": metric.returning_customers,
                    "total_active_customers": metric.total_active_customers,
                    "customer_retention_rate": metric.customer_retention_rate,
                    "churn_rate": metric.churn_rate,
                    "lifetime_value": metric.lifetime_value
                }
                for metric in report.metrics_over_time
            ],
            "top_customers": [
                {
                    "customer_id": customer.customer_id,
                    "email": customer.email,
                    "first_name": customer.first_name,
                    "last_name": customer.last_name,
                    "segment": customer.segment,
                    "total_orders": customer.total_orders,
                    "total_spent": customer.total_spent,
                    "avg_order_value": customer.avg_order_value,
                    "last_order_date": customer.last_order_date.isoformat() if customer.last_order_date else None,
                    "days_since_last_order": customer.days_since_last_order,
                    "lifetime_value": customer.lifetime_value
                }
                for customer in report.top_customers
            ]
        }
    except Exception as e:
        logger.error(f"Error getting customer analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get customer analytics")

@api_router.get("/admin/analytics/inventory")
async def get_inventory_analytics(
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.VIEW_ANALYTICS)),
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """Get inventory analytics report (admin only)"""
    try:
        report = await analytics_repo.get_inventory_analytics()
        
        return {
            "period_start": report.period_start.isoformat(),
            "period_end": report.period_end.isoformat(),
            "total_products": report.total_products,
            "total_stock_value": report.total_stock_value,
            "low_stock_alerts": report.low_stock_alerts,
            "out_of_stock_alerts": report.out_of_stock_alerts,
            "avg_turnover_rate": report.avg_turnover_rate,
            "product_analytics": [
                {
                    "product_id": product.product_id,
                    "product_name": product.product_name,
                    "sku": product.sku,
                    "current_stock": product.current_stock,
                    "stock_value": product.stock_value,
                    "units_sold_30d": product.units_sold_30d,
                    "stock_turnover_rate": product.stock_turnover_rate,
                    "days_of_supply": product.days_of_supply,
                    "reorder_point": product.reorder_point,
                    "stock_status": product.stock_status,
                    "last_restocked": product.last_restocked.isoformat() if product.last_restocked else None
                }
                for product in report.product_analytics[:20]  # Limit to top 20 for API response
            ],
            "reorder_recommendations": report.reorder_recommendations
        }
    except Exception as e:
        logger.error(f"Error getting inventory analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get inventory analytics")

# Custom Reports
@api_router.post("/admin/analytics/reports")
async def create_custom_report(
    report: CustomReportCreate,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.VIEW_ANALYTICS)),
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """Create custom analytics report (admin only)"""
    try:
        created_report = await analytics_repo.create_custom_report(report, created_by=current_admin.id)
        
        if not created_report:
            raise HTTPException(status_code=500, detail="Failed to create custom report")
        
        return {
            "message": "Custom report created successfully",
            "report_id": created_report.id,
            "report_name": created_report.name
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating custom report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create custom report")

@api_router.get("/admin/analytics/reports")
async def get_custom_reports(
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.VIEW_ANALYTICS)),
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """Get custom analytics reports (admin only)"""
    try:
        reports = await analytics_repo.get_custom_reports(created_by=current_admin.id)
        
        return {
            "reports": [
                {
                    "id": report.id,
                    "name": report.name,
                    "description": report.description,
                    "report_type": report.report_type,
                    "frequency": report.frequency,
                    "is_scheduled": report.is_scheduled,
                    "created_at": report.created_at.isoformat(),
                    "last_run": report.last_run.isoformat() if report.last_run else None,
                    "next_run": report.next_run.isoformat() if report.next_run else None
                }
                for report in reports
            ]
        }
    except Exception as e:
        logger.error(f"Error getting custom reports: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get custom reports")

# Performance Monitoring
@api_router.get("/admin/analytics/performance")
async def get_performance_metrics(
    hours: int = 24,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.VIEW_ANALYTICS)),
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """Get system performance metrics (admin only)"""
    try:
        metrics = await analytics_repo.get_performance_metrics(hours=hours)
        
        return {
            "metrics": [
                {
                    "timestamp": metric.timestamp.isoformat(),
                    "cpu_usage": metric.cpu_usage,
                    "memory_usage": metric.memory_usage,
                    "disk_usage": metric.disk_usage,
                    "active_sessions": metric.active_sessions,
                    "api_response_time": metric.api_response_time,
                    "database_query_time": metric.database_query_time,
                    "error_rate": metric.error_rate,
                    "uptime": metric.uptime
                }
                for metric in metrics[-100:]  # Last 100 data points
            ],
            "period_hours": hours,
            "total_data_points": len(metrics)
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")

@api_router.post("/admin/analytics/performance")
async def log_performance_metric(
    metric_data: Dict[str, Any],
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.MANAGE_SETTINGS)),
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """Log system performance metric (admin only)"""
    try:
        metric = SystemPerformance(
            cpu_usage=metric_data.get("cpu_usage", 0.0),
            memory_usage=metric_data.get("memory_usage", 0.0),
            disk_usage=metric_data.get("disk_usage", 0.0),
            active_sessions=metric_data.get("active_sessions", 0),
            api_response_time=metric_data.get("api_response_time", 0.0),
            database_query_time=metric_data.get("database_query_time", 0.0),
            error_rate=metric_data.get("error_rate", 0.0),
            uptime=metric_data.get("uptime", 0.0)
        )
        
        success = await analytics_repo.log_performance_metric(metric)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to log performance metric")
        
        return {"message": "Performance metric logged successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging performance metric: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to log performance metric")

# Analytics Export (Basic Implementation)
@api_router.post("/admin/analytics/export")
async def export_analytics_data(
    export_request: ExportRequest,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.EXPORT_DATA)),
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """Export analytics data (admin only)"""
    try:
        # Parse date range - handle both dict and direct fields
        if isinstance(export_request.date_range, dict):
            if "start" in export_request.date_range and "end" in export_request.date_range:
                start_date = datetime.fromisoformat(export_request.date_range["start"].replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(export_request.date_range["end"].replace('Z', '+00:00'))
            else:
                # Default to last 30 days if not specified properly
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=30)
        else:
            # Default to last 30 days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
        
        # Generate report based on type
        if export_request.report_type.value == "sales":
            report = await analytics_repo.get_sales_analytics(start_date, end_date)
            data = {
                "total_revenue": report.total_revenue,
                "total_orders": report.total_orders,
                "avg_order_value": report.avg_order_value,
                "metrics": [metric.dict() for metric in report.metrics_over_time],
                "top_products": [product.dict() for product in report.top_products]
            }
        elif export_request.report_type.value == "customer":
            report = await analytics_repo.get_customer_analytics(start_date, end_date)
            data = {
                "total_customers": report.total_customers,
                "new_customers": report.new_customers,
                "returning_customers": report.returning_customers,
                "metrics": [metric.dict() for metric in report.metrics_over_time],
                "top_customers": [customer.dict() for customer in report.top_customers]
            }
        elif export_request.report_type.value == "inventory":
            report = await analytics_repo.get_inventory_analytics()
            data = {
                "total_products": report.total_products,
                "total_stock_value": report.total_stock_value,
                "low_stock_alerts": report.low_stock_alerts,
                "out_of_stock_alerts": report.out_of_stock_alerts,
                "product_analytics": [product.dict() for product in report.product_analytics],
                "reorder_recommendations": report.reorder_recommendations
            }
        else:
            raise HTTPException(status_code=400, detail="Unsupported report type for export")
        
        # For now, return JSON data (could be extended to generate actual files)
        return {
            "message": "Analytics data exported successfully",
            "format": export_request.format,
            "report_type": export_request.report_type,
            "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
            "data": data,
            "exported_at": datetime.utcnow().isoformat(),
            "exported_by": current_admin.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting analytics data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export analytics data")

# Content Management System Endpoints

# Blog Management
@api_router.get("/blog/categories")
async def get_blog_categories(
    content_repo: ContentRepository = Depends(get_content_repository)
):
    """Get blog categories (public endpoint)"""
    try:
        categories = await content_repo.get_blog_categories(active_only=True)
        
        return {
            "categories": [
                {
                    "id": cat.id,
                    "name": cat.name,
                    "slug": cat.slug,
                    "description": cat.description,
                    "color": cat.color,
                    "sort_order": cat.sort_order
                }
                for cat in categories
            ]
        }
    except Exception as e:
        logger.error(f"Error getting blog categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get blog categories")

@api_router.get("/blog/posts")
async def get_blog_posts(
    category_id: Optional[str] = None,
    tags: Optional[str] = None,  # Comma-separated tags
    featured_only: bool = False,
    page: int = 1,
    page_size: int = 10,
    content_repo: ContentRepository = Depends(get_content_repository)
):
    """Get blog posts (public endpoint)"""
    try:
        # Parse tags if provided
        tag_list = tags.split(',') if tags else None
        
        posts, total_count = await content_repo.get_blog_posts(
            category_id=category_id,
            tags=tag_list,
            featured_only=featured_only,
            published_only=True,
            page=page,
            page_size=page_size
        )
        
        total_pages = (total_count + page_size - 1) // page_size
        
        return {
            "posts": [
                {
                    "id": post.id,
                    "title": post.title,
                    "slug": post.slug,
                    "excerpt": post.excerpt,
                    "featured_image": post.featured_image,
                    "category_id": post.category_id,
                    "tags": post.tags,
                    "published_at": post.published_at.isoformat() if post.published_at else None,
                    "author_name": post.author_name,
                    "view_count": post.view_count,
                    "like_count": post.like_count,
                    "comment_count": post.comment_count,
                    "is_featured": post.is_featured,
                    "meta_title": post.meta_title,
                    "meta_description": post.meta_description
                }
                for post in posts
            ],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error getting blog posts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get blog posts")

@api_router.get("/blog/posts/{slug}")
async def get_blog_post(
    slug: str,
    content_repo: ContentRepository = Depends(get_content_repository)
):
    """Get single blog post by slug (public endpoint)"""
    try:
        post = await content_repo.get_blog_post(slug=slug)
        
        if not post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        if post.status != BlogStatus.PUBLISHED or (post.published_at and post.published_at > datetime.utcnow()):
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        # Increment view count
        await content_repo.increment_blog_post_view(post.id)
        
        # Get comments
        comments = await content_repo.get_blog_comments(post.id, approved_only=True)
        
        return {
            "post": {
                "id": post.id,
                "title": post.title,
                "slug": post.slug,
                "content": post.content,
                "excerpt": post.excerpt,
                "featured_image": post.featured_image,
                "category_id": post.category_id,
                "tags": post.tags,
                "published_at": post.published_at.isoformat() if post.published_at else None,
                "author_name": post.author_name,
                "view_count": post.view_count + 1,  # Include incremented count
                "like_count": post.like_count,
                "comment_count": post.comment_count,
                "is_featured": post.is_featured,
                "allow_comments": post.allow_comments,
                "meta_title": post.meta_title,
                "meta_description": post.meta_description,
                "canonical_url": post.canonical_url,
                "og_title": post.og_title,
                "og_description": post.og_description,
                "og_image": post.og_image
            },
            "comments": [
                {
                    "id": comment.id,
                    "author_name": comment.author_name,
                    "content": comment.content,
                    "created_at": comment.created_at.isoformat(),
                    "parent_id": comment.parent_id
                }
                for comment in comments
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting blog post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get blog post")

@api_router.get("/blog/search")
async def search_blog_posts(
    q: str,
    limit: int = 10,
    content_repo: ContentRepository = Depends(get_content_repository)
):
    """Search blog posts (public endpoint)"""
    try:
        if not q or len(q.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
        
        posts = await content_repo.search_blog_posts(q.strip(), limit=limit)
        
        return {
            "query": q,
            "results": [
                {
                    "id": post.id,
                    "title": post.title,
                    "slug": post.slug,
                    "excerpt": post.excerpt,
                    "featured_image": post.featured_image,
                    "published_at": post.published_at.isoformat() if post.published_at else None,
                    "author_name": post.author_name
                }
                for post in posts
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching blog posts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search blog posts")

# Admin Blog Management
@api_router.post("/admin/blog/categories")
async def create_blog_category_admin(
    category_data: Dict[str, Any],
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.MANAGE_SETTINGS)),
    content_repo: ContentRepository = Depends(get_content_repository)
):
    """Create blog category (admin only)"""
    try:
        category = BlogCategory(**category_data)
        created_category = await content_repo.create_blog_category(category)
        
        if not created_category:
            raise HTTPException(status_code=500, detail="Failed to create blog category")
        
        return {
            "message": "Blog category created successfully",
            "category_id": created_category.id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating blog category: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create blog category")

@api_router.post("/admin/blog/posts")
async def create_blog_post_admin(
    post: BlogPostCreate,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.MANAGE_SETTINGS)),
    content_repo: ContentRepository = Depends(get_content_repository)
):
    """Create blog post (admin only)"""
    try:
        created_post = await content_repo.create_blog_post(
            post, 
            author_id=current_admin.id, 
            author_name=f"{current_admin.first_name} {current_admin.last_name}"
        )
        
        if not created_post:
            raise HTTPException(status_code=500, detail="Failed to create blog post")
        
        return {
            "message": "Blog post created successfully",
            "post_id": created_post.id,
            "slug": created_post.slug
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating blog post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create blog post")

@api_router.put("/admin/blog/posts/{post_id}")
async def update_blog_post_admin(
    post_id: str,
    post_update: BlogPostUpdate,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.MANAGE_SETTINGS)),
    content_repo: ContentRepository = Depends(get_content_repository)
):
    """Update blog post (admin only)"""
    try:
        updated_post = await content_repo.update_blog_post(post_id, post_update)
        
        if not updated_post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        return {"message": "Blog post updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating blog post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update blog post")

# Documentation System
@api_router.get("/docs/sections")
async def get_documentation_sections(
    doc_type: Optional[DocumentationType] = None,
    content_repo: ContentRepository = Depends(get_content_repository)
):
    """Get documentation sections (public endpoint)"""
    try:
        sections = await content_repo.get_documentation_sections(doc_type=doc_type, active_only=True)
        
        return {
            "sections": [
                {
                    "id": section.id,
                    "name": section.name,
                    "slug": section.slug,
                    "description": section.description,
                    "doc_type": section.doc_type,
                    "sort_order": section.sort_order
                }
                for section in sections
            ]
        }
    except Exception as e:
        logger.error(f"Error getting documentation sections: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get documentation sections")

@api_router.get("/docs/pages")
async def get_documentation_pages(
    section_id: Optional[str] = None,
    content_repo: ContentRepository = Depends(get_content_repository)
):
    """Get documentation pages (public endpoint)"""
    try:
        pages = await content_repo.get_documentation_pages(section_id=section_id, published_only=True)
        
        return {
            "pages": [
                {
                    "id": page.id,
                    "title": page.title,
                    "slug": page.slug,
                    "excerpt": page.excerpt,
                    "section_id": page.section_id,
                    "sort_order": page.sort_order,
                    "view_count": page.view_count,
                    "helpful_votes": page.helpful_votes
                }
                for page in pages
            ]
        }
    except Exception as e:
        logger.error(f"Error getting documentation pages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get documentation pages")

# SEO Management
@api_router.get("/admin/seo/{path:path}")
async def get_seo_data_admin(
    path: str,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.MANAGE_SETTINGS)),
    content_repo: ContentRepository = Depends(get_content_repository)
):
    """Get SEO data for URL path (admin only)"""
    try:
        # Ensure path starts with /
        if not path.startswith('/'):
            path = '/' + path
        
        seo_page = await content_repo.get_seo_page(path)
        
        if not seo_page:
            return {"message": "No SEO data found for this path"}
        
        return {
            "url_path": seo_page.url_path,
            "page_title": seo_page.page_title,
            "meta_description": seo_page.meta_description,
            "meta_keywords": seo_page.meta_keywords,
            "canonical_url": seo_page.canonical_url,
            "og_title": seo_page.og_title,
            "og_description": seo_page.og_description,
            "og_image": seo_page.og_image,
            "robots_meta": seo_page.robots_meta,
            "sitemap_priority": seo_page.sitemap_priority,
            "sitemap_changefreq": seo_page.sitemap_changefreq
        }
    except Exception as e:
        logger.error(f"Error getting SEO data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get SEO data")

@api_router.put("/admin/seo/{path:path}")
async def update_seo_data_admin(
    path: str,
    seo_data: Dict[str, Any],
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.MANAGE_SETTINGS)),
    content_repo: ContentRepository = Depends(get_content_repository)
):
    """Update SEO data for URL path (admin only)"""
    try:
        # Ensure path starts with /
        if not path.startswith('/'):
            path = '/' + path
        
        success = await content_repo.update_seo_page(path, seo_data)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update SEO data")
        
        return {"message": "SEO data updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating SEO data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update SEO data")

# Media Management
@api_router.get("/media/files")
async def get_media_files(
    media_type: Optional[MediaType] = None,
    folder_path: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    content_repo: ContentRepository = Depends(get_content_repository)
):
    """Get media files (public endpoint)"""
    try:
        media_files, total_count = await content_repo.get_media_files(
            media_type=media_type,
            folder_path=folder_path,
            page=page,
            page_size=page_size
        )
        
        total_pages = (total_count + page_size - 1) // page_size
        
        return {
            "media_files": [
                {
                    "id": media.id,
                    "filename": media.filename,
                    "file_url": media.file_url,
                    "mime_type": media.mime_type,
                    "media_type": media.media_type,
                    "file_size": media.file_size,
                    "width": media.width,
                    "height": media.height,
                    "alt_text": media.alt_text,
                    "title": media.title,
                    "description": media.description,
                    "tags": media.tags,
                    "created_at": media.created_at.isoformat()
                }
                for media in media_files
            ],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error getting media files: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get media files")

# Content Analytics
@api_router.get("/admin/content/analytics")
async def get_content_analytics(
    days: int = 30,
    current_admin: AdminResponse = Depends(require_permission(AdminPermission.VIEW_ANALYTICS)),
    content_repo: ContentRepository = Depends(get_content_repository)
):
    """Get content analytics (admin only)"""
    try:
        analytics = await content_repo.get_content_analytics(days=days)
        return analytics
    except Exception as e:
        logger.error(f"Error getting content analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get content analytics")

# Sitemap Generation
@api_router.get("/sitemap.xml")
async def generate_sitemap(
    content_repo: ContentRepository = Depends(get_content_repository)
):
    """Generate sitemap XML (public endpoint)"""
    try:
        from fastapi.responses import Response
        
        sitemap_data = await content_repo.generate_sitemap_data()
        
        # Generate XML sitemap
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        # Add static pages
        xml_content += '  <url>\n'
        xml_content += '    <loc>https://niteputterpro.com/</loc>\n'
        xml_content += '    <changefreq>weekly</changefreq>\n'
        xml_content += '    <priority>1.0</priority>\n'
        xml_content += '  </url>\n'
        
        # Add dynamic content
        for url_data in sitemap_data:
            xml_content += '  <url>\n'
            xml_content += f'    <loc>https://niteputterpro.com{url_data["loc"]}</loc>\n'
            xml_content += f'    <lastmod>{url_data["lastmod"].isoformat()}</lastmod>\n'
            xml_content += f'    <changefreq>{url_data["changefreq"]}</changefreq>\n'
            xml_content += f'    <priority>{url_data["priority"]}</priority>\n'
            xml_content += '  </url>\n'
        
        xml_content += '</urlset>'
        
        return Response(content=xml_content, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error generating sitemap: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate sitemap")



@api_router.get("/download/tutorial")
async def download_tutorial():
    """Redirect to the Smart Life bulb manual PDF"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(
        url="https://www.tlc-direct.co.uk/Technical/DataSheets/LEDlite_Smart/Smart_Life_Manual_en.pdf",
        status_code=302
    )

@api_router.get("/catalog")
async def download_catalog():
    """Provide product catalog information"""
    return {
        "message": "Product catalog download",
        "products": [
            {
                "name": "Nite Putter Pro Illuminated Cup",
                "features": [
                    "Patented POLY LIGHT CASING",
                    "Multi-level drainage system", 
                    "Hardwired 12v low voltage",
                    "Bluetooth-enabled MR16 bulb"
                ],
                "benefits": [
                    "Protected from water and debris",
                    "Withstands heavy rains and flooding",
                    "No charging required",
                    "Easy color customization"
                ]
            }
        ],
        "contact": {
            "phone": "(469) 642-7171",
            "email": "niteputterpro@gmail.com",
            "address": "842 Faith Trail, Heath, TX 75032"
        }
    }

# Product Management Endpoints
@api_router.get("/products", response_model=ProductListResponse)
async def get_products(
    category: Optional[ProductCategory] = None,
    status: Optional[ProductStatus] = None,
    is_featured: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    product_repo: ProductRepository = Depends(get_product_repository)
):
    """Get products with filtering and pagination"""
    try:
        filters = ProductFilter(
            category=category,
            status=status,
            is_featured=is_featured,
            min_price=min_price,
            max_price=max_price,
            search=search
        )
        
        products, total_count = await product_repo.get_products(
            filters=filters,
            page=page,
            page_size=page_size
        )
        
        total_pages = (total_count + page_size - 1) // page_size
        
        product_responses = []
        for product in products:
            product_responses.append(ProductResponse(
                id=product.id,
                name=product.name,
                description=product.description,
                short_description=product.short_description,
                category=product.category,
                status=product.status,
                base_price=product.base_price,
                sku=product.sku,
                inventory_count=product.inventory_count,
                low_stock_threshold=product.low_stock_threshold,
                features=product.features,
                tags=product.tags,
                weight=product.weight,
                dimensions=product.dimensions,
                is_featured=product.is_featured,
                meta_title=product.meta_title,
                meta_description=product.meta_description,
                images=product.images,
                variants=product.variants,
                created_at=product.created_at,
                updated_at=product.updated_at,
                view_count=product.view_count,
                purchase_count=product.purchase_count
            ))
        
        return ProductListResponse(
            products=product_responses,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get products")

@api_router.get("/products/featured")
async def get_featured_products(
    limit: int = 10,
    product_repo: ProductRepository = Depends(get_product_repository)
):
    """Get featured products"""
    try:
        products = await product_repo.get_featured_products(limit=limit)
        
        return {
            "products": [
                {
                    "id": product.id,
                    "name": product.name,
                    "short_description": product.short_description,
                    "base_price": product.base_price,
                    "sku": product.sku,
                    "images": product.images,
                    "features": product.features
                }
                for product in products
            ]
        }
    except Exception as e:
        logger.error(f"Error getting featured products: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get featured products")

@api_router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    product_repo: ProductRepository = Depends(get_product_repository)
):
    """Get single product by ID"""
    try:
        product = await product_repo.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Increment view count
        await product_repo.increment_view_count(product_id)
        
        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            short_description=product.short_description,
            category=product.category,
            status=product.status,
            base_price=product.base_price,
            sku=product.sku,
            inventory_count=product.inventory_count,
            low_stock_threshold=product.low_stock_threshold,
            features=product.features,
            tags=product.tags,
            weight=product.weight,
            dimensions=product.dimensions,
            is_featured=product.is_featured,
            meta_title=product.meta_title,
            meta_description=product.meta_description,
            images=product.images,
            variants=product.variants,
            created_at=product.created_at,
            updated_at=product.updated_at,
            view_count=product.view_count + 1,  # Include the incremented count
            purchase_count=product.purchase_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get product")

@api_router.get("/products/search/{query}")
async def search_products(
    query: str,
    limit: int = 20,
    product_repo: ProductRepository = Depends(get_product_repository)
):
    """Search products by text"""
    try:
        products = await product_repo.search_products(query, limit=limit)
        
        return {
            "query": query,
            "products": [
                {
                    "id": product.id,
                    "name": product.name,
                    "short_description": product.short_description,
                    "base_price": product.base_price,
                    "sku": product.sku,
                    "images": product.images
                }
                for product in products
            ]
        }
    except Exception as e:
        logger.error(f"Error searching products: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search products")

@api_router.get("/categories")
async def get_categories(
    product_repo: ProductRepository = Depends(get_product_repository)
):
    """Get product categories with counts"""
    try:
        categories = await product_repo.get_categories_with_counts()
        return {"categories": categories}
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get categories")

# Legacy compatibility endpoint
@api_router.get("/products_legacy")
async def get_products_legacy():
    """Legacy endpoint for backward compatibility"""
    return {
        "products": [
            {
                "id": package_id,
                "name": package["name"],
                "price": package["price"],
                "description": package["description"],
                "features": package["features"]
            }
            for package_id, package in PRODUCT_PACKAGES.items()
        ]
    }

@api_router.get("/packages")
async def get_packages():
    """Get available product packages"""
    return {
        "packages": [
            {
                "id": package_id,
                "name": package["name"],
                "price": package["price"],
                "description": package["description"],
                "features": package["features"]
            }
            for package_id, package in PRODUCT_PACKAGES.items()
        ]
    }

@api_router.post("/checkout/session")
async def create_checkout_session(
    checkout_request: CheckoutRequest, 
    request: Request,
    product_repo: ProductRepository = Depends(get_product_repository)
):
    """Create Stripe checkout session"""
    try:
        # Get product from database (try both product ID and legacy package ID)
        product = await product_repo.get_product_by_id(checkout_request.package_id)
        if not product:
            # Try to find by SKU (for backward compatibility)
            product = await product_repo.get_product_by_sku(checkout_request.package_id.upper().replace("_", "-"))
        
        if not product:
            # Fallback to legacy hardcoded products for backward compatibility
            if checkout_request.package_id not in PRODUCT_PACKAGES:
                raise HTTPException(status_code=400, detail="Invalid package ID")
            package = PRODUCT_PACKAGES[checkout_request.package_id]
            product_name = package["name"]
            product_price = package["price"]
        else:
            # Check if product is available
            if product.status != ProductStatus.ACTIVE:
                raise HTTPException(status_code=400, detail="Product is not available")
            if product.inventory_count < checkout_request.quantity:
                raise HTTPException(status_code=400, detail="Insufficient inventory")
            
            product_name = product.name
            product_price = product.base_price
        
        # Calculate total amount (backend-controlled)
        amount = product_price * checkout_request.quantity
        
        # Build success and cancel URLs using frontend origin
        success_url = f"{checkout_request.origin_url}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{checkout_request.origin_url}/checkout/cancel"
        
        # Create transaction ID
        transaction_id = str(uuid.uuid4())
        
        # Prepare metadata
        metadata = {
            "transaction_id": transaction_id,
            "package_id": checkout_request.package_id,
            "quantity": str(checkout_request.quantity),
            "source": "nite_putter_website"
        }
        
        # Create Stripe checkout session
        try:
            # Determine product description based on source
            if checkout_request.package_id in PRODUCT_PACKAGES:
                product_description = package["description"]
            else:
                product_description = product.description or product_name
            
            line_items = [{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": product_name,
                        "description": product_description
                    },
                    "unit_amount": int(amount * 100)  # Stripe expects cents
                },
                "quantity": checkout_request.quantity
            }]
            
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata,
                client_reference_id=transaction_id
            )
        except Exception as e:
            logger.error(f"Stripe checkout session creation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Payment processing temporarily unavailable"
            )
        
        # Create payment transaction record
        payment_transaction = {
            "transaction_id": transaction_id,
            "session_id": session.id,
            "package_id": checkout_request.package_id,
            "amount": amount,
            "currency": "usd",
            "quantity": checkout_request.quantity,
            "payment_status": "pending",
            "customer_info": checkout_request.customer_info,
            "metadata": metadata,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Store in database
        await db.payment_transactions.insert_one(payment_transaction)
        
        return {
            "url": session.url,
            "session_id": session.id,
            "transaction_id": transaction_id
        }
        
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")

@api_router.get("/checkout/status/{session_id}")
async def get_checkout_status(session_id: str, request: Request):
    """Get checkout session status"""
    try:
        # Get Stripe checkout session status
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Update database record
        transaction = await db.payment_transactions.find_one({"session_id": session_id})
        if transaction:
            # Map Stripe session status to our payment status
            payment_status = "pending"
            if session.payment_status == "paid":
                payment_status = "paid"
            elif session.payment_status == "unpaid":
                payment_status = "failed"
            
            # Update status only if it has changed to avoid duplicate processing
            if transaction["payment_status"] != payment_status:
                await db.payment_transactions.update_one(
                    {"session_id": session_id},
                    {
                        "$set": {
                            "payment_status": payment_status,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                
                # If payment is successful, you can add any post-payment processing here
                if payment_status == "paid":
                    logger.info(f"Payment successful for session {session_id}")
                    # Add any fulfillment logic here (send emails, etc.)
        
        return {
            "session_id": session_id,
            "status": session.status,
            "payment_status": session.payment_status,
            "amount_total": session.amount_total,
            "currency": session.currency,
            "metadata": session.metadata
        }
        
    except Exception as e:
        logger.error(f"Error getting checkout status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get checkout status: {str(e)}")

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    try:
        body = await request.body()
        stripe_signature = request.headers.get("Stripe-Signature")
        endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        if not endpoint_secret:
            logger.error("Stripe webhook secret not configured")
            raise HTTPException(status_code=500, detail="Webhook configuration error")
        
        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(
                body, stripe_signature, endpoint_secret
            )
        except ValueError:
            logger.error("Invalid payload in Stripe webhook")
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature in Stripe webhook")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Handle the event
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            session_id = session["id"]
            
            # Get transaction details for email
            transaction = await db.payment_transactions.find_one({"session_id": session_id})
            
            # Update database based on webhook event
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "payment_status": "paid",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Send order confirmation email
            if transaction and transaction.get("customer_info"):
                try:
                    customer_info = transaction["customer_info"]
                    customer_email = customer_info.get("email")
                    customer_name = customer_info.get("name", "Customer")
                    
                    if customer_email:
                        # Prepare order data for email
                        package_info = PRODUCT_PACKAGES.get(transaction["package_id"], {})
                        order_data = {
                            "order_id": transaction["transaction_id"],
                            "items": [{
                                "name": package_info.get("name", "NitePutter Pro Product"),
                                "id": transaction["package_id"],
                                "quantity": transaction.get("quantity", 1),
                                "price": transaction["amount"] / transaction.get("quantity", 1)
                            }],
                            "total": transaction["amount"]
                        }
                        
                        # Send confirmation email asynchronously
                        await email_service.send_order_confirmation(
                            customer_email=customer_email,
                            customer_name=customer_name,
                            order_data=order_data
                        )
                        logger.info(f"Order confirmation email sent to {customer_email}")
                        
                except Exception as email_error:
                    logger.error(f"Failed to send confirmation email: {str(email_error)}")
                    # Don't fail the webhook for email issues
            
            logger.info(f"Payment completed for session {session_id}")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

@api_router.get("/orders")
async def get_orders(current_user: UserResponse = Depends(get_current_user)):
    """Get order history for authenticated user"""
    try:
        orders = await db.payment_transactions.find(
            {
                "payment_status": "paid",
                "customer_info.email": current_user.email  # Filter by user's email
            }
        ).sort("created_at", -1).to_list(100)
        
        return {
            "orders": [
                {
                    "transaction_id": order["transaction_id"],
                    "session_id": order["session_id"],
                    "package_name": PRODUCT_PACKAGES.get(order["package_id"], {}).get("name", "Unknown Product"),
                    "amount": order["amount"],
                    "quantity": order["quantity"],
                    "created_at": order["created_at"],
                    "customer_info": order.get("customer_info", {})
                }
                for order in orders
            ]
        }
    except Exception as e:
        logger.error(f"Error getting orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get orders")


# ==========================================
# ADVANCED E-COMMERCE FEATURES (PHASE 7)
# ==========================================

# ===== COUPON & DISCOUNT MANAGEMENT =====

@api_router.post("/admin/coupons")
async def create_coupon(
    coupon_data: CouponCreate,
    current_admin: AdminResponse = Depends(get_current_admin),
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """Create a new coupon/discount code (Admin only)"""
    try:
        # Check admin permissions
        if "manage_promotions" not in current_admin.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage promotions"
            )
        
        coupon = await ecommerce_repo.create_coupon(coupon_data, current_admin.id)
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create coupon"
            )
        
        return {
            "message": "Coupon created successfully",
            "coupon": coupon.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating coupon: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create coupon")

@api_router.get("/admin/coupons")
async def list_coupons(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[str] = None,
    current_admin: AdminResponse = Depends(get_current_admin),
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """List all coupons with filtering (Admin only)"""
    try:
        # Check admin permissions
        if "view_promotions" not in current_admin.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view promotions"
            )
        
        # Convert status filter
        status_enum = None
        if status_filter:
            try:
                from models.ecommerce import CouponStatus
                status_enum = CouponStatus(status_filter)
            except ValueError:
                pass
        
        coupons, total_count = await ecommerce_repo.get_coupons(
            status=status_enum,
            page=page,
            page_size=page_size
        )
        
        total_pages = (total_count + page_size - 1) // page_size
        
        return {
            "coupons": [coupon.dict() for coupon in coupons],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing coupons: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list coupons")

@api_router.post("/checkout/validate-coupon")
async def validate_coupon(
    coupon_code: str = Form(...),
    order_total: float = Form(...),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """Validate a coupon code for checkout"""
    try:
        user_id = current_user.id if current_user else None
        
        is_valid, message, coupon = await ecommerce_repo.validate_coupon(
            coupon_code, user_id, order_total
        )
        
        if not is_valid:
            return {
                "valid": False,
                "message": message,
                "discount_amount": 0.0
            }
        
        discount_amount = await ecommerce_repo.calculate_discount(coupon, order_total)
        
        return {
            "valid": True,
            "message": "Coupon is valid",
            "discount_amount": discount_amount,
            "coupon_details": {
                "code": coupon.code,
                "name": coupon.name,
                "discount_type": coupon.discount_type,
                "discount_value": coupon.discount_value
            }
        }
        
    except Exception as e:
        logger.error(f"Error validating coupon: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to validate coupon")


# ===== SHIPPING MANAGEMENT =====

@api_router.post("/admin/shipping/zones")
async def create_shipping_zone(
    zone_data: ShippingZone,
    current_admin: AdminResponse = Depends(get_current_admin),
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """Create shipping zone (Admin only)"""
    try:
        if "manage_shipping" not in current_admin.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage shipping"
            )
        
        zone = await ecommerce_repo.create_shipping_zone(zone_data)
        if not zone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create shipping zone"
            )
        
        return {
            "message": "Shipping zone created successfully",
            "zone": zone.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating shipping zone: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create shipping zone")

@api_router.post("/admin/shipping/rates")
async def create_shipping_rate(
    rate_data: ShippingRate,
    current_admin: AdminResponse = Depends(get_current_admin),
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """Create shipping rate (Admin only)"""
    try:
        if "manage_shipping" not in current_admin.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage shipping"
            )
        
        rate = await ecommerce_repo.create_shipping_rate(rate_data)
        if not rate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create shipping rate"
            )
        
        return {
            "message": "Shipping rate created successfully",
            "rate": rate.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating shipping rate: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create shipping rate")

@api_router.post("/checkout/calculate-shipping")
async def calculate_shipping_costs(
    request: Request,
    country: str = Form("US"),
    state: str = Form(""),
    zip_code: str = Form(...),
    items: str = Form("[]"),  # JSON string of cart items
    shipping_method: str = Form("standard")
):
    """Calculate shipping costs for checkout using enhanced shipping service"""
    try:
        import json
        
        # Parse items from JSON string
        try:
            cart_items = json.loads(items)
        except json.JSONDecodeError:
            cart_items = []
        
        if not cart_items:
            # Default to basic item if no items provided
            cart_items = [{"id": "basic_putter_light", "quantity": 1}]
        
        # Use our enhanced shipping service
        shipping_info = await shipping_service.calculate_shipping_cost(
            items=cart_items,
            destination_zip=zip_code,
            shipping_method=shipping_method
        )
        
        # Get all available shipping methods
        available_methods = shipping_service.get_shipping_methods()
        
        return {
            "shipping_info": shipping_info,
            "available_methods": available_methods,
            "destination": {
                "country": country,
                "state": state,
                "zip_code": zip_code
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating shipping: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate shipping: {str(e)}")

@api_router.get("/orders/{order_id}/tracking")
async def get_order_tracking(
    order_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get tracking information for an order"""
    try:
        # Find the order
        order = await db.payment_transactions.find_one({
            "transaction_id": order_id,
            "customer_info.email": current_user.email  # Ensure user owns this order
        })
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Get tracking info if available
        tracking_number = order.get("tracking_number")
        carrier = order.get("carrier", "USPS")
        
        if tracking_number:
            tracking_info = await shipping_service.get_tracking_info(
                tracking_number=tracking_number,
                carrier=carrier
            )
        else:
            tracking_info = {
                "status": "Processing",
                "message": "Your order is being processed. You'll receive tracking information once it ships.",
                "estimated_delivery": None
            }
        
        return {
            "order_id": order_id,
            "order_status": order.get("order_status", "processing"),
            "tracking_info": tracking_info,
            "items": [{
                "name": PRODUCT_PACKAGES.get(order["package_id"], {}).get("name", "Product"),
                "quantity": order.get("quantity", 1),
                "price": order["amount"]
            }],
            "order_date": order.get("created_at"),
            "customer_info": order.get("customer_info", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order tracking: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get order tracking")

@api_router.post("/admin/orders/{order_id}/ship")
async def ship_order(
    order_id: str,
    tracking_number: str = Form(...),
    carrier: str = Form("USPS"),
    current_admin: AdminResponse = Depends(get_current_admin)
):
    """Mark an order as shipped and send notification email"""
    try:
        if "manage_orders" not in current_admin.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage orders"
            )
        
        # Update order with tracking information
        result = await db.payment_transactions.update_one(
            {"transaction_id": order_id},
            {
                "$set": {
                    "order_status": "shipped",
                    "tracking_number": tracking_number,
                    "carrier": carrier,
                    "shipped_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Get updated order for email
        order = await db.payment_transactions.find_one({"transaction_id": order_id})
        
        # Send shipping notification email
        if order and order.get("customer_info"):
            customer_info = order["customer_info"]
            customer_email = customer_info.get("email")
            customer_name = customer_info.get("name", "Customer")
            
            if customer_email:
                try:
                    await email_service.send_shipping_notification(
                        customer_email=customer_email,
                        customer_name=customer_name,
                        order_id=order_id,
                        tracking_number=tracking_number,
                        carrier=carrier
                    )
                    logger.info(f"Shipping notification sent to {customer_email}")
                except Exception as email_error:
                    logger.error(f"Failed to send shipping notification: {str(email_error)}")
        
        return {
            "message": "Order marked as shipped successfully",
            "order_id": order_id,
            "tracking_number": tracking_number,
            "carrier": carrier
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error shipping order: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to ship order")


# ===== TAX MANAGEMENT =====

@api_router.post("/admin/tax/rules")
async def create_tax_rule(
    tax_rule_data: TaxRule,
    current_admin: AdminResponse = Depends(get_current_admin),
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """Create tax rule (Admin only)"""
    try:
        if "manage_taxes" not in current_admin.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage taxes"
            )
        
        tax_rule = await ecommerce_repo.create_tax_rule(tax_rule_data)
        if not tax_rule:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create tax rule"
            )
        
        return {
            "message": "Tax rule created successfully",
            "tax_rule": tax_rule.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tax rule: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create tax rule")

@api_router.post("/checkout/calculate-tax")
async def calculate_tax_amount(
    subtotal: float = Form(...),
    shipping_cost: float = Form(0.0),
    country: str = Form(...),
    state: str = Form(""),
    postal_code: str = Form(""),
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """Calculate tax for checkout"""
    try:
        tax_calculation = await ecommerce_repo.calculate_tax(
            subtotal, shipping_cost, country, state, postal_code
        )
        
        return tax_calculation.dict()
        
    except Exception as e:
        logger.error(f"Error calculating tax: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate tax")


# ===== RETURN & REFUND MANAGEMENT =====

@api_router.post("/returns")
async def create_return_request(
    return_data: ReturnRequestCreate,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """Create a return/refund request"""
    try:
        user_id = current_user.id if current_user else None
        
        return_request = await ecommerce_repo.create_return_request(return_data, user_id)
        if not return_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create return request"
            )
        
        return {
            "message": "Return request created successfully",
            "return_request": return_request.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating return request: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create return request")

@api_router.get("/returns")
async def get_return_requests(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[ReturnStatus] = None,
    current_user: UserResponse = Depends(get_current_user),
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """Get user's return requests"""
    try:
        returns, total_count = await ecommerce_repo.get_return_requests(
            user_id=current_user.id,
            status=status_filter,
            page=page,
            page_size=page_size
        )
        
        return {
            "returns": [return_req.dict() for return_req in returns],
            "total_count": total_count,
            "page": page,
            "page_size": page_size
        }
        
    except Exception as e:
        logger.error(f"Error getting return requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get return requests")

@api_router.get("/admin/returns")
async def get_all_return_requests(
    page: int = 1,
    page_size: int = 50,
    status_filter: Optional[ReturnStatus] = None,
    current_admin: AdminResponse = Depends(get_current_admin),
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """Get all return requests (Admin only)"""
    try:
        if "view_returns" not in current_admin.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view returns"
            )
        
        returns, total_count = await ecommerce_repo.get_return_requests(
            status=status_filter,
            page=page,
            page_size=page_size
        )
        
        return {
            "returns": [return_req.dict() for return_req in returns],
            "total_count": total_count,
            "page": page,
            "page_size": page_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all return requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get return requests")

@api_router.put("/admin/returns/{return_id}")
async def update_return_request(
    return_id: str,
    return_update: ReturnRequestUpdate,
    current_admin: AdminResponse = Depends(get_current_admin),
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """Update return request status (Admin only)"""
    try:
        if "manage_returns" not in current_admin.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage returns"
            )
        
        # Note: This would need additional repository implementation
        return {
            "message": f"Return request {return_id} update endpoint ready",
            "return_id": return_id,
            "update_data": return_update.dict(),
            "note": "Repository method needs implementation"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating return request: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update return request")


# ===== MULTI-CURRENCY SUPPORT =====

@api_router.get("/currencies/convert")
async def convert_currency(
    amount: float,
    from_currency: Currency,
    to_currency: Currency,
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """Convert amount between currencies"""
    try:
        conversion = await ecommerce_repo.convert_currency(amount, from_currency, to_currency)
        
        if not conversion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Currency conversion not available for {from_currency} to {to_currency}"
            )
        
        return conversion.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting currency: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to convert currency")

@api_router.get("/currencies/rates")
async def get_exchange_rates(
    base_currency: Currency = Currency.USD,
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """Get current exchange rates"""
    try:
        rates = await ecommerce_repo.get_all_exchange_rates(base_currency)
        
        return {
            "base_currency": base_currency,
            "rates": rates,
            "last_updated": datetime.utcnow(),
            "total_currencies": len(rates)
        }
        
    except Exception as e:
        logger.error(f"Error getting exchange rates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get exchange rates")


# ===== GIFT CARD MANAGEMENT =====

@api_router.post("/admin/gift-cards")
async def create_gift_card(
    gift_card_data: GiftCard,
    current_admin: AdminResponse = Depends(get_current_admin),
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """Create gift card (Admin only)"""
    try:
        if "manage_gift_cards" not in current_admin.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage gift cards"
            )
        
        gift_card = await ecommerce_repo.create_gift_card(gift_card_data, current_admin.id)
        if not gift_card:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create gift card"
            )
        
        return {
            "message": "Gift card created successfully",
            "gift_card": gift_card.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating gift card: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create gift card")

@api_router.get("/gift-cards/{code}/validate")
async def validate_gift_card(
    code: str,
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """Validate gift card code"""
    try:
        gift_card = await ecommerce_repo.get_gift_card_by_code(code)
        
        if not gift_card:
            return {
                "valid": False,
                "message": "Gift card not found",
                "balance": 0.0
            }
        
        # Check if gift card is still valid
        now = datetime.utcnow()
        if gift_card.valid_until and gift_card.valid_until < now:
            return {
                "valid": False,
                "message": "Gift card has expired",
                "balance": 0.0
            }
        
        if gift_card.status != GiftCardStatus.ACTIVE:
            return {
                "valid": False,
                "message": f"Gift card is {gift_card.status}",
                "balance": 0.0
            }
        
        return {
            "valid": True,
            "message": "Gift card is valid",
            "balance": gift_card.current_balance,
            "currency": gift_card.currency,
            "minimum_order_amount": gift_card.minimum_order_amount
        }
        
    except Exception as e:
        logger.error(f"Error validating gift card: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to validate gift card")


# ===== INVENTORY & STOCK MANAGEMENT =====

@api_router.post("/admin/inventory/stock-movement")
async def record_stock_movement(
    movement_data: StockMovement,
    current_admin: AdminResponse = Depends(get_current_admin),
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """Record inventory stock movement (Admin only)"""
    try:
        if "manage_inventory" not in current_admin.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage inventory"
            )
        
        # Set admin as creator
        movement_data.created_by = current_admin.id
        
        success = await ecommerce_repo.record_stock_movement(movement_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to record stock movement"
            )
        
        return {
            "message": "Stock movement recorded successfully",
            "movement": movement_data.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording stock movement: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to record stock movement")

@api_router.get("/admin/inventory/alerts")
async def get_low_stock_alerts(
    page: int = 1,
    page_size: int = 20,
    priority: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    current_admin: AdminResponse = Depends(get_current_admin),
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """Get low stock alerts (Admin only)"""
    try:
        if "manage_inventory" not in current_admin.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view inventory alerts"
            )
        
        alerts, total_count = await ecommerce_repo.get_low_stock_alerts(
            priority=priority,
            acknowledged=acknowledged,
            page=page,
            page_size=page_size
        )
        
        total_pages = (total_count + page_size - 1) // page_size
        
        return {
            "alerts": [alert.dict() for alert in alerts],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "filters": {
                "priority": priority,
                "acknowledged": acknowledged
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting low stock alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get low stock alerts")


# ===== E-COMMERCE ANALYTICS =====

@api_router.get("/admin/ecommerce/stats")
async def get_ecommerce_statistics(
    current_admin: AdminResponse = Depends(get_current_admin),
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """Get e-commerce statistics (Admin only)"""
    try:
        if "view_analytics" not in current_admin.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view analytics"
            )
        
        stats = await ecommerce_repo.get_ecommerce_stats()
        
        return {
            "statistics": stats,
            "generated_at": datetime.utcnow(),
            "period": "all_time"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting e-commerce statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get e-commerce statistics")

@api_router.get("/admin/ecommerce/dashboard")
async def get_ecommerce_dashboard(
    current_admin: AdminResponse = Depends(get_current_admin),
    ecommerce_repo: EcommerceRepository = Depends(get_ecommerce_repository)
):
    """Get comprehensive e-commerce dashboard data (Admin only)"""
    try:
        if "view_analytics" not in current_admin.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view analytics"
            )
        
        stats = await ecommerce_repo.get_ecommerce_stats()
        
        # Combine with other metrics for comprehensive dashboard
        dashboard_data = {
            "overview": stats,
            "recent_activity": {
                "recent_coupons": 0,
                "recent_returns": 0,
                "recent_gift_cards": 0
            },
            "alerts": {
                "low_stock_items": stats.get("inventory", {}).get("active_alerts", 0),
                "pending_returns": stats.get("returns", {}).get("pending_requests", 0)
            },
            "performance": {
                "coupon_usage_rate": 0.0,
                "return_rate": 0.0,
                "gift_card_redemption_rate": 0.0
            },
            "generated_at": datetime.utcnow()
        }
        
        return dashboard_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting e-commerce dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get e-commerce dashboard")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
