from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

# Contact Form Models
class ContactType(str, Enum):
    GENERAL_INQUIRY = "general_inquiry"
    PRODUCT_SUPPORT = "product_support"
    TECHNICAL_SUPPORT = "technical_support"
    SALES_INQUIRY = "sales_inquiry"
    PARTNERSHIP = "partnership"
    FEEDBACK = "feedback"
    COMPLAINT = "complaint"
    OTHER = "other"

class ContactPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ContactStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"

class ContactForm(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
    contact_type: ContactType = ContactType.GENERAL_INQUIRY
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=10, max_length=2000)
    priority: ContactPriority = ContactPriority.MEDIUM
    status: ContactStatus = ContactStatus.NEW
    
    # Admin fields
    assigned_to: Optional[str] = None  # Admin ID
    internal_notes: Optional[str] = None
    resolution: Optional[str] = None
    
    # Tracking fields
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

class ContactFormCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
    contact_type: ContactType = ContactType.GENERAL_INQUIRY
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=10, max_length=2000)

class ContactFormUpdate(BaseModel):
    priority: Optional[ContactPriority] = None
    status: Optional[ContactStatus] = None
    assigned_to: Optional[str] = None
    internal_notes: Optional[str] = None
    resolution: Optional[str] = None

class ContactFormResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str]
    company: Optional[str]
    contact_type: ContactType
    subject: str
    message: str
    priority: ContactPriority
    status: ContactStatus
    assigned_to: Optional[str]
    internal_notes: Optional[str]
    resolution: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]

# Newsletter Subscription Models
class NewsletterSubscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    is_active: bool = True
    subscription_source: str = "website"  # "website", "checkout", "admin", etc.
    interests: List[str] = Field(default_factory=list)  # ["products", "news", "promotions"]
    double_opt_in_confirmed: bool = False
    double_opt_in_token: Optional[str] = None
    unsubscribe_token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    unsubscribed_at: Optional[datetime] = None

class NewsletterSubscriptionCreate(BaseModel):
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    interests: List[str] = Field(default_factory=list)

# Email Template Models
class EmailTemplateType(str, Enum):
    WELCOME = "welcome"
    ORDER_CONFIRMATION = "order_confirmation"
    ORDER_SHIPPED = "order_shipped"
    ORDER_DELIVERED = "order_delivered"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"
    NEWSLETTER = "newsletter"
    CONTACT_CONFIRMATION = "contact_confirmation"
    SUPPORT_REPLY = "support_reply"
    PROMOTIONAL = "promotional"

class EmailTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    template_type: EmailTemplateType
    subject: str = Field(..., min_length=1, max_length=200)
    html_content: str = Field(..., min_length=1)
    text_content: Optional[str] = None
    variables: List[str] = Field(default_factory=list)  # ["first_name", "order_number", etc.]
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None  # Admin ID

class EmailTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    template_type: EmailTemplateType
    subject: str = Field(..., min_length=1, max_length=200)
    html_content: str = Field(..., min_length=1)
    text_content: Optional[str] = None
    variables: List[str] = Field(default_factory=list)

class EmailTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    subject: Optional[str] = Field(None, min_length=1, max_length=200)
    html_content: Optional[str] = Field(None, min_length=1)
    text_content: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None

# Email Log Models
class EmailStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    FAILED = "failed"
    UNSUBSCRIBED = "unsubscribed"

class EmailLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    recipient_email: EmailStr
    recipient_name: Optional[str] = None
    sender_email: EmailStr = "noreply@niteputterpro.com"
    sender_name: str = "Nite Putter Pro"
    template_type: EmailTemplateType
    subject: str
    html_content: str
    text_content: Optional[str] = None
    status: EmailStatus = EmailStatus.PENDING
    
    # Tracking
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    bounced_at: Optional[datetime] = None
    
    # Metadata
    user_id: Optional[str] = None
    order_id: Optional[str] = None
    campaign_id: Optional[str] = None
    tracking_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Technical details
    provider_message_id: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Support Ticket Models
class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"  
    HIGH = "high"
    CRITICAL = "critical"

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketCategory(str, Enum):
    TECHNICAL_SUPPORT = "technical_support"
    PRODUCT_INQUIRY = "product_inquiry"
    ORDER_SUPPORT = "order_support"
    BILLING_SUPPORT = "billing_support"
    INSTALLATION_SUPPORT = "installation_support"
    WARRANTY_CLAIM = "warranty_claim"
    GENERAL_INQUIRY = "general_inquiry"

class SupportTicket(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ticket_number: str = Field(default_factory=lambda: f"TICKET-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}")
    
    # Customer information
    user_id: Optional[str] = None
    customer_email: EmailStr
    customer_name: str = Field(..., min_length=1, max_length=100)
    
    # Ticket details
    category: TicketCategory = TicketCategory.GENERAL_INQUIRY
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN
    subject: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    
    # Assignment and resolution
    assigned_to: Optional[str] = None  # Admin ID
    resolution: Optional[str] = None
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)
    satisfaction_feedback: Optional[str] = None
    
    # Tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    last_customer_response: Optional[datetime] = None
    last_agent_response: Optional[datetime] = None

class SupportTicketCreate(BaseModel):
    customer_email: EmailStr
    customer_name: str = Field(..., min_length=1, max_length=100)
    category: TicketCategory = TicketCategory.GENERAL_INQUIRY
    priority: TicketPriority = TicketPriority.MEDIUM
    subject: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)

class SupportTicketUpdate(BaseModel):
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None

class TicketMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ticket_id: str
    sender_type: str  # "customer", "agent", "system"
    sender_id: Optional[str] = None  # User ID or Admin ID
    sender_name: str
    sender_email: EmailStr
    message: str = Field(..., min_length=1, max_length=2000)
    is_internal: bool = False  # Internal admin notes
    attachments: List[Dict[str, str]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TicketMessageCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    is_internal: bool = False

# FAQ Models
class FAQCategory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FAQ(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category_id: str
    question: str = Field(..., min_length=1, max_length=500)
    answer: str = Field(..., min_length=1, max_length=2000)
    sort_order: int = 0
    is_active: bool = True
    view_count: int = 0
    helpful_votes: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None  # Admin ID

class FAQCreate(BaseModel):
    category_id: str
    question: str = Field(..., min_length=1, max_length=500)
    answer: str = Field(..., min_length=1, max_length=2000)
    sort_order: int = 0

class FAQUpdate(BaseModel):
    category_id: Optional[str] = None
    question: Optional[str] = Field(None, min_length=1, max_length=500)
    answer: Optional[str] = Field(None, min_length=1, max_length=2000)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

# Notification Models
class NotificationType(str, Enum):
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"

class NotificationTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    notification_type: NotificationType
    trigger_event: str  # "order_placed", "low_stock", "user_registered", etc.
    template_content: str = Field(..., min_length=1, max_length=1000)
    variables: List[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationQueue(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    notification_type: NotificationType
    recipient: str  # Email, phone, user_id, etc.
    subject: Optional[str] = None
    content: str
    trigger_event: str
    status: str = "pending"  # "pending", "sent", "failed", "cancelled"
    retry_count: int = 0
    max_retries: int = 3
    scheduled_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)