"""
Order Model for NitePutter Pro
Complete order processing and tracking system
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from decimal import Decimal
from enum import Enum
from .product import PyObjectId

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"

class PaymentMethod(str, Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"

class FulfillmentStatus(str, Enum):
    UNFULFILLED = "unfulfilled"
    PARTIALLY_FULFILLED = "partially_fulfilled"
    FULFILLED = "fulfilled"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    RETURNED = "returned"

class ShippingMethod(str, Enum):
    STANDARD = "standard"
    EXPRESS = "express"
    OVERNIGHT = "overnight"
    PICKUP = "pickup"

class Address(BaseModel):
    """Shipping/Billing address"""
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
    is_residential: bool = True

class OrderItem(BaseModel):
    """Individual order line item"""
    product_id: str
    product_sku: str
    product_name: str
    product_image: Optional[str] = None
    variant_id: Optional[str] = None
    variant_title: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    compare_at_price: Optional[Decimal] = None
    quantity: int = Field(..., gt=0)
    subtotal: Decimal = Field(..., gt=0)
    tax_amount: Decimal = Field(default=Decimal("0"))
    discount_amount: Decimal = Field(default=Decimal("0"))
    total: Decimal = Field(..., gt=0)
    fulfillment_status: FulfillmentStatus = FulfillmentStatus.UNFULFILLED
    fulfilled_quantity: int = 0
    
    @field_validator('subtotal', mode='before')
    @classmethod
    def calculate_subtotal(cls, v, info):
        if info.data.get('price') and info.data.get('quantity'):
            return info.data['price'] * info.data['quantity']
        return v
    
    @field_validator('total', mode='before')
    @classmethod
    def calculate_total(cls, v, info):
        if info.data.get('subtotal'):
            total = info.data['subtotal']
            if info.data.get('tax_amount'):
                total += info.data['tax_amount']
            if info.data.get('discount_amount'):
                total -= info.data['discount_amount']
            return max(Decimal("0"), total)
        return v

class ShippingInfo(BaseModel):
    """Shipping details"""
    method: ShippingMethod
    carrier: Optional[str] = None  # "USPS", "UPS", "FedEx"
    tracking_number: Optional[str] = None
    tracking_url: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cost: Decimal = Field(default=Decimal("0"))
    
class PaymentInfo(BaseModel):
    """Payment transaction details"""
    method: PaymentMethod
    status: PaymentStatus
    transaction_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    stripe_charge_id: Optional[str] = None
    amount: Decimal
    currency: str = "USD"
    card_last4: Optional[str] = None
    card_brand: Optional[str] = None
    receipt_url: Optional[str] = None
    paid_at: Optional[datetime] = None
    
class DiscountInfo(BaseModel):
    """Applied discounts/coupons"""
    code: str
    type: str  # "percentage", "fixed_amount", "free_shipping"
    value: Decimal
    amount_saved: Decimal
    description: Optional[str] = None

class RefundInfo(BaseModel):
    """Refund details"""
    refund_id: str
    amount: Decimal
    reason: str
    status: str
    created_at: datetime
    processed_at: Optional[datetime] = None
    notes: Optional[str] = None

class Order(BaseModel):
    """Complete order model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    
    # Order identification
    order_number: str = Field(..., description="Human-readable order number")
    
    # Customer information
    customer_id: Optional[str] = None
    customer_email: EmailStr
    customer_phone: str
    customer_note: Optional[str] = None
    
    # Addresses
    billing_address: Address
    shipping_address: Address
    
    # Order items
    items: List[OrderItem]
    
    # Financial summary
    subtotal: Decimal = Field(..., description="Sum of all item subtotals")
    shipping_total: Decimal = Field(default=Decimal("0"))
    tax_total: Decimal = Field(default=Decimal("0"))
    discount_total: Decimal = Field(default=Decimal("0"))
    total: Decimal = Field(..., description="Final order total")
    
    # Payment
    payment: PaymentInfo
    
    # Shipping
    shipping: ShippingInfo
    
    # Discounts
    discounts: List[DiscountInfo] = []
    
    # Refunds
    refunds: List[RefundInfo] = []
    total_refunded: Decimal = Field(default=Decimal("0"))
    
    # Status tracking
    status: OrderStatus = OrderStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING
    fulfillment_status: FulfillmentStatus = FulfillmentStatus.UNFULFILLED
    
    # Metadata
    source: str = "website"  # "website", "admin", "api"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    tags: List[str] = []
    admin_notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            str: str,  # PyObjectId handled by annotation
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
    )
    
    @field_validator('order_number', mode='before')
    @classmethod
    def generate_order_number(cls, v):
        if not v:
            # Generate order number: NPP-YYYYMMDD-XXXX
            import random
            from datetime import datetime
            date_str = datetime.utcnow().strftime("%Y%m%d")
            random_suffix = str(random.randint(1000, 9999))
            return f"NPP-{date_str}-{random_suffix}"
        return v
    
    @field_validator('total', mode='before')
    @classmethod
    def calculate_order_total(cls, v, info):
        if info.data.get('subtotal'):
            total = info.data['subtotal']
            if info.data.get('shipping_total'):
                total += info.data['shipping_total']
            if info.data.get('tax_total'):
                total += info.data['tax_total']
            if info.data.get('discount_total'):
                total -= info.data['discount_total']
            return max(Decimal("0"), total)
        return v
    
    def calculate_totals(self):
        """Recalculate all order totals"""
        self.subtotal = sum(item.subtotal for item in self.items)
        self.tax_total = sum(item.tax_amount for item in self.items)
        self.discount_total = sum(item.discount_amount for item in self.items)
        self.total = self.subtotal + self.shipping_total + self.tax_total - self.discount_total
        
    def get_profit_margin(self) -> Optional[Decimal]:
        """Calculate profit margin if cost data available"""
        # This would need product cost data
        return None
    
    def is_fulfilled(self) -> bool:
        """Check if order is completely fulfilled"""
        return all(
            item.fulfilled_quantity >= item.quantity 
            for item in self.items
        )
    
    def can_be_cancelled(self) -> bool:
        """Check if order can be cancelled"""
        return self.status in [OrderStatus.PENDING, OrderStatus.PROCESSING]
    
    def can_be_refunded(self) -> bool:
        """Check if order can be refunded"""
        return self.payment_status == PaymentStatus.COMPLETED


class OrderCreate(BaseModel):
    """Schema for creating an order"""
    customer_email: EmailStr
    customer_phone: str
    billing_address: Address
    shipping_address: Address
    items: List[OrderItem]
    shipping_method: ShippingMethod
    payment_method: PaymentMethod
    discount_codes: List[str] = []
    customer_note: Optional[str] = None


class OrderUpdate(BaseModel):
    """Schema for updating an order"""
    status: Optional[OrderStatus] = None
    fulfillment_status: Optional[FulfillmentStatus] = None
    tracking_number: Optional[str] = None
    admin_notes: Optional[str] = None
    tags: Optional[List[str]] = None