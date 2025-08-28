"""
Shopping Cart Model for NitePutter Pro
Persistent cart storage with session and user support
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, field_validator, ConfigDict
from decimal import Decimal
from enum import Enum
from .product import PyObjectId

class CartStatus(str, Enum):
    ACTIVE = "active"
    ABANDONED = "abandoned"
    CONVERTED = "converted"
    EXPIRED = "expired"
    MERGED = "merged"

class CartItemStatus(str, Enum):
    AVAILABLE = "available"
    OUT_OF_STOCK = "out_of_stock"
    LIMITED_STOCK = "limited_stock"
    PRICE_CHANGED = "price_changed"
    DISCONTINUED = "discontinued"

class CartItem(BaseModel):
    """Individual item in shopping cart"""
    product_id: str
    product_sku: str
    product_name: str
    product_image: Optional[str] = None
    variant_id: Optional[str] = None
    variant_title: Optional[str] = None
    
    # Pricing
    unit_price: Decimal = Field(..., gt=0)
    original_price: Optional[Decimal] = None  # For tracking price changes
    quantity: int = Field(..., gt=0)
    subtotal: Decimal = Field(..., ge=0)
    
    # Applied discounts
    discount_amount: Decimal = Field(default=Decimal("0"))
    discount_code: Optional[str] = None
    
    # Status tracking
    status: CartItemStatus = CartItemStatus.AVAILABLE
    stock_available: Optional[int] = None
    reserved_until: Optional[datetime] = None
    
    # Metadata
    added_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    
    @field_validator('subtotal', mode='before')
    @classmethod
    def calculate_subtotal(cls, v, info):
        if info.data.get('unit_price') and info.data.get('quantity'):
            subtotal = info.data['unit_price'] * info.data['quantity']
            if info.data.get('discount_amount'):
                subtotal -= info.data['discount_amount']
            return max(Decimal("0"), subtotal)
        return v

class AppliedCoupon(BaseModel):
    """Coupon applied to cart"""
    code: str
    type: str  # percentage, fixed_amount, free_shipping
    value: Decimal
    discount_amount: Decimal
    min_purchase: Optional[Decimal] = None
    description: Optional[str] = None
    applied_at: datetime = Field(default_factory=datetime.utcnow)

class CartTotals(BaseModel):
    """Cart totals calculation"""
    subtotal: Decimal = Field(default=Decimal("0"))
    discount_total: Decimal = Field(default=Decimal("0"))
    tax_amount: Decimal = Field(default=Decimal("0"))
    shipping_estimate: Decimal = Field(default=Decimal("0"))
    total: Decimal = Field(default=Decimal("0"))
    
    # Breakdown
    item_count: int = 0
    total_quantity: int = 0
    savings_amount: Decimal = Field(default=Decimal("0"))
    savings_percentage: Optional[float] = None

class ShoppingCart(BaseModel):
    """Complete shopping cart model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    # Session/User association
    session_id: str = Field(..., description="Session identifier for guest carts")
    user_id: Optional[str] = Field(None, description="User ID if logged in")
    customer_email: Optional[str] = None
    
    # Cart items
    items: List[CartItem] = []
    
    # Applied coupons
    coupons: List[AppliedCoupon] = []
    
    # Totals
    totals: CartTotals = Field(default_factory=CartTotals)
    currency: str = "USD"
    
    # Shipping estimate
    shipping_zip: Optional[str] = None
    shipping_country: str = "US"
    shipping_method: Optional[str] = None
    
    # Cart state
    status: CartStatus = CartStatus.ACTIVE
    
    # Recovery
    abandonment_email_sent: bool = False
    abandonment_email_sent_at: Optional[datetime] = None
    recovery_token: Optional[str] = None
    
    # Analytics
    source: str = "website"  # website, mobile_app, api
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    
    # Metadata
    notes: Optional[str] = None
    tags: List[str] = []
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    converted_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            str: str,  # PyObjectId handled by annotation
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
    )
    
    def calculate_totals(self):
        """Recalculate cart totals"""
        # Calculate subtotal
        self.totals.subtotal = sum(item.subtotal for item in self.items)
        self.totals.item_count = len(self.items)
        self.totals.total_quantity = sum(item.quantity for item in self.items)
        
        # Calculate discounts
        self.totals.discount_total = sum(coupon.discount_amount for coupon in self.coupons)
        self.totals.discount_total += sum(item.discount_amount for item in self.items)
        
        # Calculate savings
        original_total = sum(
            (item.original_price or item.unit_price) * item.quantity 
            for item in self.items
        )
        self.totals.savings_amount = original_total - self.totals.subtotal
        if original_total > 0:
            self.totals.savings_percentage = (self.totals.savings_amount / original_total) * 100
        
        # Calculate total (without tax and shipping for now)
        self.totals.total = self.totals.subtotal - self.totals.discount_total
        self.totals.total = max(Decimal("0"), self.totals.total)
        
        self.updated_at = datetime.utcnow()
    
    def add_item(self, product: Dict[str, Any], quantity: int = 1) -> CartItem:
        """Add item to cart"""
        # Check if item already exists
        existing_item = None
        for item in self.items:
            if item.product_id == product["id"]:
                existing_item = item
                break
        
        if existing_item:
            # Update quantity
            existing_item.quantity += quantity
            existing_item.subtotal = existing_item.unit_price * existing_item.quantity
            existing_item.updated_at = datetime.utcnow()
        else:
            # Create new item
            new_item = CartItem(
                product_id=product["id"],
                product_sku=product["sku"],
                product_name=product["name"],
                product_image=product.get("image"),
                unit_price=Decimal(str(product["price"])),
                original_price=Decimal(str(product.get("compare_at_price", product["price"]))),
                quantity=quantity,
                subtotal=Decimal(str(product["price"])) * quantity
            )
            self.items.append(new_item)
            existing_item = new_item
        
        self.calculate_totals()
        return existing_item
    
    def update_item_quantity(self, product_id: str, quantity: int) -> bool:
        """Update item quantity"""
        for item in self.items:
            if item.product_id == product_id:
                if quantity <= 0:
                    self.items.remove(item)
                else:
                    item.quantity = quantity
                    item.subtotal = item.unit_price * quantity
                    item.updated_at = datetime.utcnow()
                self.calculate_totals()
                return True
        return False
    
    def remove_item(self, product_id: str) -> bool:
        """Remove item from cart"""
        for item in self.items:
            if item.product_id == product_id:
                self.items.remove(item)
                self.calculate_totals()
                return True
        return False
    
    def apply_coupon(self, coupon: Dict[str, Any]) -> bool:
        """Apply coupon to cart"""
        # Check if already applied
        if any(c.code == coupon["code"] for c in self.coupons):
            return False
        
        # Check minimum purchase
        if coupon.get("min_purchase") and self.totals.subtotal < Decimal(str(coupon["min_purchase"])):
            return False
        
        # Calculate discount
        discount_amount = Decimal("0")
        if coupon["type"] == "percentage":
            discount_amount = self.totals.subtotal * (Decimal(str(coupon["value"])) / 100)
        elif coupon["type"] == "fixed_amount":
            discount_amount = Decimal(str(coupon["value"]))
        elif coupon["type"] == "free_shipping":
            discount_amount = self.totals.shipping_estimate
        
        applied_coupon = AppliedCoupon(
            code=coupon["code"],
            type=coupon["type"],
            value=Decimal(str(coupon["value"])),
            discount_amount=discount_amount,
            min_purchase=Decimal(str(coupon.get("min_purchase", 0))),
            description=coupon.get("description")
        )
        
        self.coupons.append(applied_coupon)
        self.calculate_totals()
        return True
    
    def remove_coupon(self, code: str) -> bool:
        """Remove coupon from cart"""
        for coupon in self.coupons:
            if coupon.code == code:
                self.coupons.remove(coupon)
                self.calculate_totals()
                return True
        return False
    
    def clear(self):
        """Clear all items from cart"""
        self.items = []
        self.coupons = []
        self.calculate_totals()
    
    def merge_with(self, other_cart: 'ShoppingCart'):
        """Merge another cart into this one"""
        for item in other_cart.items:
            self.add_item({
                "id": item.product_id,
                "sku": item.product_sku,
                "name": item.product_name,
                "image": item.product_image,
                "price": str(item.unit_price),
                "compare_at_price": str(item.original_price) if item.original_price else str(item.unit_price)
            }, item.quantity)
        
        # Mark other cart as merged
        other_cart.status = CartStatus.MERGED
    
    def is_expired(self) -> bool:
        """Check if cart has expired"""
        return self.expires_at < datetime.utcnow()
    
    def is_abandoned(self) -> bool:
        """Check if cart is abandoned (not updated for 1 hour)"""
        return (datetime.utcnow() - self.updated_at).total_seconds() > 3600
    
    def mark_as_converted(self, order_id: str):
        """Mark cart as converted to order"""
        self.status = CartStatus.CONVERTED
        self.converted_at = datetime.utcnow()
        self.notes = f"Converted to order: {order_id}"
    
    def reserve_stock(self, duration_minutes: int = 15):
        """Reserve stock for items in cart"""
        reservation_expires = datetime.utcnow() + timedelta(minutes=duration_minutes)
        for item in self.items:
            item.reserved_until = reservation_expires


class CartCreate(BaseModel):
    """Schema for creating a cart"""
    session_id: str
    user_id: Optional[str] = None
    source: str = "website"

class CartItemAdd(BaseModel):
    """Schema for adding item to cart"""
    product_id: str
    quantity: int = 1
    variant_id: Optional[str] = None

class CartItemUpdate(BaseModel):
    """Schema for updating cart item"""
    quantity: int

class CartCouponApply(BaseModel):
    """Schema for applying coupon"""
    code: str

class CartShippingEstimate(BaseModel):
    """Schema for shipping estimate"""
    zip_code: str
    country: str = "US"
    method: Optional[str] = None