"""
Product Model for NitePutter Pro
Real production schema for golf lighting products
"""

from typing import Optional, List, Dict, Any, Annotated
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict, BeforeValidator
from pydantic.functional_validators import AfterValidator
from bson import ObjectId
from decimal import Decimal
from enum import Enum

class ProductCategory(str, Enum):
    BASIC = "basic"
    PRO = "pro"
    COMPLETE = "complete"
    ACCESSORIES = "accessories"

class ProductStatus(str, Enum):
    ACTIVE = "active"
    DRAFT = "draft"
    ARCHIVED = "archived"
    OUT_OF_STOCK = "out_of_stock"

def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")

# PyObjectId for Pydantic v2
PyObjectId = Annotated[ObjectId, BeforeValidator(validate_object_id)]

class ProductImage(BaseModel):
    """Product image with metadata"""
    url: str
    alt_text: str
    is_primary: bool = False
    display_order: int = 0

class ProductSpecification(BaseModel):
    """Technical specifications"""
    battery_life: str  # "8-10 hours continuous use"
    charging_time: str  # "2 hours full charge"
    led_brightness: str  # "500 lumens"
    weight: str  # "45g"
    material: str  # "Aircraft-grade aluminum"
    water_resistance: str  # "IPX6 rated"
    warranty: str  # "2 year warranty"

class ShippingInfo(BaseModel):
    """Shipping dimensions and weight"""
    weight: float = Field(..., description="Weight in pounds")
    length: float = Field(..., description="Length in inches")
    width: float = Field(..., description="Width in inches")  
    height: float = Field(..., description="Height in inches")
    ships_separately: bool = False

class InventoryInfo(BaseModel):
    """Inventory tracking"""
    quantity: int = 0
    reserved_quantity: int = 0
    low_stock_threshold: int = 10
    track_inventory: bool = True
    allow_backorder: bool = False

class SEOInfo(BaseModel):
    """SEO metadata"""
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    url_slug: str
    keywords: List[str] = []

class Product(BaseModel):
    """Complete product model for NitePutter Pro"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    # Basic Information
    sku: str = Field(..., description="Stock Keeping Unit")
    name: str = Field(..., description="Product name")
    slug: str = Field(..., description="URL-friendly slug")
    category: ProductCategory
    status: ProductStatus = ProductStatus.ACTIVE
    
    # Descriptions
    short_description: str = Field(..., max_length=160)
    description: str = Field(..., description="Full HTML description")
    features: List[str] = Field(default_factory=list, description="Key features list")
    whats_included: List[str] = Field(default_factory=list, description="What's in the box")
    
    # Pricing
    price: Decimal = Field(..., gt=0, description="Current selling price")
    compare_at_price: Optional[Decimal] = Field(None, description="Original price for sales")
    cost_per_unit: Optional[Decimal] = Field(None, description="Cost for profit calculation")
    
    # Media
    images: List[ProductImage] = Field(default_factory=list)
    video_url: Optional[str] = None
    instruction_manual_url: Optional[str] = None
    
    # Specifications
    specifications: ProductSpecification
    
    # Shipping
    shipping: ShippingInfo
    
    # Inventory
    inventory: InventoryInfo
    
    # SEO
    seo: SEOInfo
    
    # Reviews
    average_rating: float = Field(default=0.0, ge=0, le=5)
    review_count: int = Field(default=0, ge=0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    
    # Relationships
    related_products: List[str] = Field(default_factory=list, description="SKUs of related products")
    cross_sells: List[str] = Field(default_factory=list, description="SKUs for cross-selling")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat(),
            Decimal: float
        },
        json_schema_extra={
            "example": {
                "sku": "NPP-BASIC-001",
                "name": "NitePutter Basic LED Light",
                "slug": "niteputter-basic-led-light",
                "category": "basic",
                "short_description": "Essential LED lighting for night putting practice",
                "price": 149.99
            }
        }
    )
    
    @field_validator('slug', mode='before')
    @classmethod
    def generate_slug(cls, v, info):
        if not v and info.data.get('name'):
            # Generate slug from name
            import re
            slug = info.data['name'].lower()
            slug = re.sub(r'[^\w\s-]', '', slug)
            slug = re.sub(r'[-\s]+', '-', slug)
            return slug
        return v
    
    def get_available_quantity(self) -> int:
        """Calculate available quantity (total - reserved)"""
        return max(0, self.inventory.quantity - self.inventory.reserved_quantity)
    
    def is_in_stock(self) -> bool:
        """Check if product is in stock"""
        return self.get_available_quantity() > 0 or self.inventory.allow_backorder
    
    def is_low_stock(self) -> bool:
        """Check if product is low in stock"""
        available = self.get_available_quantity()
        return 0 < available <= self.inventory.low_stock_threshold
    
    def calculate_discount_percentage(self) -> Optional[float]:
        """Calculate discount percentage if on sale"""
        if self.compare_at_price and self.compare_at_price > self.price:
            discount = ((self.compare_at_price - self.price) / self.compare_at_price) * 100
            return round(discount, 1)
        return None


class ProductCreate(BaseModel):
    """Schema for creating a new product"""
    sku: str
    name: str
    category: ProductCategory
    short_description: str
    description: str
    price: Decimal
    compare_at_price: Optional[Decimal] = None
    cost_per_unit: Optional[Decimal] = None
    features: List[str] = []
    whats_included: List[str] = []
    specifications: ProductSpecification
    shipping: ShippingInfo
    inventory: InventoryInfo
    seo: SEOInfo
    

class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    name: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    compare_at_price: Optional[Decimal] = None
    features: Optional[List[str]] = None
    whats_included: Optional[List[str]] = None
    status: Optional[ProductStatus] = None
    inventory: Optional[InventoryInfo] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProductListResponse(BaseModel):
    """Response schema for product listing"""
    products: List[Product]
    total: int
    page: int
    page_size: int
    total_pages: int