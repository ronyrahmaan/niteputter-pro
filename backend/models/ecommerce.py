from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
from decimal import Decimal

# Coupon and Discount Models
class DiscountType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    FREE_SHIPPING = "free_shipping"
    BUY_X_GET_Y = "buy_x_get_y"

class CouponStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    USED_UP = "used_up"

class Coupon(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    
    # Discount configuration
    discount_type: DiscountType
    discount_value: float = Field(..., ge=0)  # Percentage (0-100) or fixed amount
    
    # Usage limits
    usage_limit: Optional[int] = Field(None, ge=0)  # Max total uses
    usage_limit_per_user: Optional[int] = Field(None, ge=0)  # Max uses per user
    usage_count: int = 0
    
    # Date constraints
    valid_from: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None
    
    # Order constraints
    minimum_order_amount: Optional[float] = Field(None, ge=0)
    maximum_discount_amount: Optional[float] = Field(None, ge=0)
    
    # Product constraints
    applicable_products: List[str] = Field(default_factory=list)  # Product IDs
    applicable_categories: List[str] = Field(default_factory=list)  # Category names
    excluded_products: List[str] = Field(default_factory=list)
    
    # Customer constraints
    applicable_customers: List[str] = Field(default_factory=list)  # User IDs (empty = all)
    new_customers_only: bool = False
    
    # Buy X Get Y configuration (for BUY_X_GET_Y type)
    buy_x_quantity: Optional[int] = Field(None, ge=1)
    get_y_quantity: Optional[int] = Field(None, ge=1)
    get_y_product_id: Optional[str] = None
    
    # Status and tracking
    status: CouponStatus = CouponStatus.ACTIVE
    is_stackable: bool = False  # Can be combined with other coupons
    
    # Management
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('code')
    def validate_code(cls, v):
        return v.upper().replace(' ', '')

class CouponCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    discount_type: DiscountType
    discount_value: float = Field(..., ge=0)
    usage_limit: Optional[int] = Field(None, ge=0)
    usage_limit_per_user: Optional[int] = Field(None, ge=0)
    valid_from: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None
    minimum_order_amount: Optional[float] = Field(None, ge=0)
    maximum_discount_amount: Optional[float] = Field(None, ge=0)
    applicable_products: List[str] = Field(default_factory=list)
    applicable_categories: List[str] = Field(default_factory=list)
    excluded_products: List[str] = Field(default_factory=list)
    applicable_customers: List[str] = Field(default_factory=list)
    new_customers_only: bool = False
    buy_x_quantity: Optional[int] = Field(None, ge=1)
    get_y_quantity: Optional[int] = Field(None, ge=1)
    get_y_product_id: Optional[str] = None
    is_stackable: bool = False

class CouponUsage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    coupon_id: str
    coupon_code: str
    user_id: Optional[str] = None
    order_id: str
    discount_amount: float
    used_at: datetime = Field(default_factory=datetime.utcnow)

# Shipping Models
class ShippingMethod(str, Enum):
    STANDARD = "standard"
    EXPRESS = "express"
    OVERNIGHT = "overnight"
    FREE = "free"
    PICKUP = "pickup"

class ShippingZone(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    countries: List[str] = Field(default_factory=list)  # ISO country codes
    states: List[str] = Field(default_factory=list)  # State codes
    postal_codes: List[str] = Field(default_factory=list)  # Postal code patterns
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ShippingRate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    method: ShippingMethod
    zone_id: str
    
    # Rate calculation
    base_rate: float = Field(..., ge=0)
    rate_per_kg: Optional[float] = Field(None, ge=0)  # Additional cost per kg
    rate_per_item: Optional[float] = Field(None, ge=0)  # Additional cost per item
    
    # Conditions
    min_order_value: Optional[float] = Field(None, ge=0)
    max_order_value: Optional[float] = Field(None, ge=0)
    min_weight: Optional[float] = Field(None, ge=0)
    max_weight: Optional[float] = Field(None, ge=0)
    
    # Delivery time
    min_delivery_days: int = Field(default=1, ge=0)
    max_delivery_days: int = Field(default=7, ge=1)
    
    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ShippingCalculation(BaseModel):
    shipping_method: ShippingMethod
    shipping_zone: str
    rate_name: str
    base_rate: float
    weight_charge: float = 0.0
    item_charge: float = 0.0
    total_shipping_cost: float
    estimated_delivery_min: int
    estimated_delivery_max: int
    is_free_shipping: bool = False

# Tax Models
class TaxClass(str, Enum):
    STANDARD = "standard"
    REDUCED = "reduced"
    ZERO = "zero"
    EXEMPT = "exempt"

class TaxRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    
    # Geographic scope
    country: str = Field(..., min_length=2, max_length=2)  # ISO country code
    state: Optional[str] = Field(None, max_length=10)  # State code
    city: Optional[str] = Field(None, max_length=100)
    postal_code_pattern: Optional[str] = None  # Regex pattern for postal codes
    
    # Tax configuration
    tax_rate: float = Field(..., ge=0, le=100)  # Percentage
    tax_class: TaxClass = TaxClass.STANDARD
    
    # Applicability
    applies_to_shipping: bool = False
    compound_tax: bool = False  # Applied after other taxes
    
    # Priority for overlapping rules
    priority: int = Field(default=0, ge=0)
    
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TaxCalculation(BaseModel):
    subtotal: float
    shipping_cost: float
    tax_breakdown: List[Dict[str, Any]] = Field(default_factory=list)
    total_tax: float = 0.0
    total_amount: float = 0.0

# Return and Refund Models
class ReturnReason(str, Enum):
    DEFECTIVE = "defective"
    WRONG_ITEM = "wrong_item"
    NOT_AS_DESCRIBED = "not_as_described"
    CHANGED_MIND = "changed_mind"
    SIZE_ISSUE = "size_issue"
    DAMAGED_SHIPPING = "damaged_shipping"
    OTHER = "other"

class ReturnStatus(str, Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_TRANSIT = "in_transit"
    RECEIVED = "received"
    INSPECTED = "inspected"
    REFUNDED = "refunded"
    EXCHANGED = "exchanged"
    CLOSED = "closed"

class RefundMethod(str, Enum):
    ORIGINAL_PAYMENT = "original_payment"
    STORE_CREDIT = "store_credit"
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"

class ReturnRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    return_number: str = Field(default_factory=lambda: f"RET-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}")
    
    # Order information
    order_id: str
    user_id: Optional[str] = None
    customer_email: str
    
    # Return details
    items: List[Dict[str, Any]] = Field(default_factory=list)  # [{product_id, quantity, reason}]
    reason: ReturnReason
    description: str = Field(..., min_length=10, max_length=1000)
    
    # Refund information
    requested_refund_amount: float = Field(..., ge=0)
    approved_refund_amount: Optional[float] = Field(None, ge=0)
    refund_method: RefundMethod = RefundMethod.ORIGINAL_PAYMENT
    
    # Status tracking
    status: ReturnStatus = ReturnStatus.REQUESTED
    
    # Tracking information
    return_tracking_number: Optional[str] = None
    return_carrier: Optional[str] = None
    
    # Processing details
    approved_by: Optional[str] = None  # Admin ID
    approved_at: Optional[datetime] = None
    processed_by: Optional[str] = None  # Admin ID
    processed_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ReturnRequestCreate(BaseModel):
    order_id: str
    customer_email: str
    items: List[Dict[str, Any]]
    reason: ReturnReason
    description: str = Field(..., min_length=10, max_length=1000)
    requested_refund_amount: float = Field(..., ge=0)
    refund_method: RefundMethod = RefundMethod.ORIGINAL_PAYMENT

class ReturnRequestUpdate(BaseModel):
    status: Optional[ReturnStatus] = None
    approved_refund_amount: Optional[float] = Field(None, ge=0)
    refund_method: Optional[RefundMethod] = None
    return_tracking_number: Optional[str] = None
    return_carrier: Optional[str] = None

# Multi-Currency Models
class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"

class CurrencyRate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    base_currency: Currency = Currency.USD
    target_currency: Currency
    exchange_rate: float = Field(..., gt=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    source: str = "manual"  # "manual", "api", "bank"
    is_active: bool = True

class CurrencyConversion(BaseModel):
    amount: float
    from_currency: Currency
    to_currency: Currency
    exchange_rate: float
    converted_amount: float
    conversion_date: datetime = Field(default_factory=datetime.utcnow)

# Inventory Management Models
class StockMovementType(str, Enum):
    SALE = "sale"
    RETURN = "return"
    RESTOCK = "restock"
    ADJUSTMENT = "adjustment"
    DAMAGED = "damaged"
    TRANSFER = "transfer"

class StockMovement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    movement_type: StockMovementType
    quantity: int  # Positive for increases, negative for decreases
    previous_stock: int
    new_stock: int
    
    # Reference information
    reference_type: Optional[str] = None  # "order", "return", "manual"
    reference_id: Optional[str] = None  # Order ID, Return ID, etc.
    
    # Details
    notes: Optional[str] = Field(None, max_length=500)
    cost_per_unit: Optional[float] = Field(None, ge=0)
    total_cost: Optional[float] = Field(None, ge=0)
    
    # Management
    created_by: Optional[str] = None  # Admin or system ID
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LowStockAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    product_name: str
    current_stock: int
    threshold: int
    suggested_reorder_quantity: int
    priority: str = "medium"  # "low", "medium", "high", "critical"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None

# Advanced Order Models
class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    sku: str
    quantity: int = Field(..., ge=1)
    unit_price: float = Field(..., ge=0)
    total_price: float = Field(..., ge=0)
    
    # Tax information
    tax_rate: float = 0.0
    tax_amount: float = 0.0
    
    # Discounts
    discount_amount: float = 0.0
    coupon_codes: List[str] = Field(default_factory=list)

class EnhancedOrder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_number: str = Field(default_factory=lambda: f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}")
    
    # Customer information
    user_id: Optional[str] = None
    customer_email: str
    customer_name: str
    
    # Order details
    items: List[OrderItem]
    currency: Currency = Currency.USD
    
    # Pricing breakdown
    subtotal: float = Field(..., ge=0)
    discount_total: float = 0.0
    tax_total: float = 0.0
    shipping_total: float = 0.0
    total_amount: float = Field(..., ge=0)
    
    # Applied discounts
    applied_coupons: List[str] = Field(default_factory=list)
    
    # Shipping information
    shipping_method: Optional[ShippingMethod] = None
    shipping_address: Optional[Dict[str, Any]] = None
    billing_address: Optional[Dict[str, Any]] = None
    
    # Status tracking
    order_status: OrderStatus = OrderStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING
    
    # Fulfillment
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Gift Card Models
class GiftCardStatus(str, Enum):
    ACTIVE = "active"
    REDEEMED = "redeemed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class GiftCard(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str = Field(default_factory=lambda: str(uuid.uuid4()).replace('-', '').upper()[:16])
    
    # Value information
    initial_amount: float = Field(..., gt=0)
    current_balance: float = Field(..., ge=0)
    currency: Currency = Currency.USD
    
    # Recipient information
    recipient_email: Optional[str] = None
    recipient_name: Optional[str] = None
    personal_message: Optional[str] = Field(None, max_length=500)
    
    # Sender information
    sender_email: Optional[str] = None
    sender_name: Optional[str] = None
    
    # Usage constraints
    valid_from: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None
    minimum_order_amount: Optional[float] = Field(None, ge=0)
    
    # Status and tracking
    status: GiftCardStatus = GiftCardStatus.ACTIVE
    redeemed_by: Optional[str] = None  # User ID
    redeemed_at: Optional[datetime] = None
    
    # Management
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class GiftCardTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    gift_card_id: str
    transaction_type: str  # "purchase", "redemption", "refund"
    amount: float
    balance_before: float
    balance_after: float
    order_id: Optional[str] = None
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)