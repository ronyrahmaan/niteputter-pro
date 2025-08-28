from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from enum import Enum

class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"

class ProductCategory(str, Enum):
    COMPLETE_SYSTEMS = "complete_systems"
    COMPONENTS = "components"
    SERVICES = "services"
    ACCESSORIES = "accessories"

class ProductImage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str
    alt_text: str
    is_primary: bool = False
    sort_order: int = 0

class ProductVariant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    price: float = Field(..., gt=0)
    sku: str
    inventory_count: int = Field(default=0, ge=0)
    attributes: Dict[str, str] = Field(default_factory=dict)  # e.g., {"color": "red", "size": "large"}

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    short_description: str = Field(..., min_length=1, max_length=500)
    category: ProductCategory
    status: ProductStatus = ProductStatus.ACTIVE
    base_price: float = Field(..., gt=0)
    sku: str = Field(..., min_length=1, max_length=50)
    inventory_count: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=5, ge=0)
    features: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    weight: Optional[float] = Field(None, ge=0)  # in pounds
    dimensions: Optional[Dict[str, float]] = None  # {"length": 12, "width": 8, "height": 4}
    is_featured: bool = False
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    
class ProductCreate(ProductBase):
    images: List[ProductImage] = Field(default_factory=list)
    variants: List[ProductVariant] = Field(default_factory=list)
    
    @validator('sku')
    def validate_sku(cls, v):
        if not v.isalnum() and '_' not in v and '-' not in v:
            raise ValueError('SKU must contain only alphanumeric characters, hyphens, and underscores')
        return v.upper()

class ProductInDB(ProductBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    images: List[ProductImage] = Field(default_factory=list)
    variants: List[ProductVariant] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None  # User ID who created the product
    updated_by: Optional[str] = None  # User ID who last updated the product
    
    # Analytics/tracking fields
    view_count: int = Field(default=0, ge=0)
    purchase_count: int = Field(default=0, ge=0)
    last_purchased: Optional[datetime] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class ProductResponse(ProductBase):
    id: str
    images: List[ProductImage]
    variants: List[ProductVariant]
    created_at: datetime
    updated_at: datetime
    view_count: int
    purchase_count: int
    is_low_stock: bool = False
    is_out_of_stock: bool = False
    
    @validator('is_low_stock', pre=False, always=True)
    def set_low_stock(cls, v, values):
        inventory = values.get('inventory_count', 0)
        threshold = values.get('low_stock_threshold', 5)
        return inventory <= threshold and inventory > 0
    
    @validator('is_out_of_stock', pre=False, always=True)  
    def set_out_of_stock(cls, v, values):
        return values.get('inventory_count', 0) == 0

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    short_description: Optional[str] = Field(None, min_length=1, max_length=500)
    category: Optional[ProductCategory] = None
    status: Optional[ProductStatus] = None
    base_price: Optional[float] = Field(None, gt=0)
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    inventory_count: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    features: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    weight: Optional[float] = Field(None, ge=0)
    dimensions: Optional[Dict[str, float]] = None
    is_featured: Optional[bool] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    images: Optional[List[ProductImage]] = None
    variants: Optional[List[ProductVariant]] = None
    
    @validator('sku')
    def validate_sku(cls, v):
        if v is not None:
            if not v.isalnum() and '_' not in v and '-' not in v:
                raise ValueError('SKU must contain only alphanumeric characters, hyphens, and underscores')
            return v.upper()
        return v

class ProductFilter(BaseModel):
    category: Optional[ProductCategory] = None
    status: Optional[ProductStatus] = None
    is_featured: Optional[bool] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    search: Optional[str] = None  # Search in name and description
    low_stock_only: Optional[bool] = None
    out_of_stock_only: Optional[bool] = None

class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    
class InventoryUpdate(BaseModel):
    inventory_count: int = Field(..., ge=0)
    notes: Optional[str] = None
    
class InventoryHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    previous_count: int
    new_count: int
    change_amount: int
    change_type: str  # "sale", "restock", "adjustment", "return"
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None  # User ID who made the change