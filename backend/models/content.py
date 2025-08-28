from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import re

# Blog Models
class BlogStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"

class BlogCategory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=500)
    meta_title: Optional[str] = Field(None, max_length=60)
    meta_description: Optional[str] = Field(None, max_length=160)
    color: Optional[str] = "#007bff"  # Hex color code
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('slug')
    def validate_slug(cls, v):
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v

class BlogPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=220)
    excerpt: Optional[str] = Field(None, max_length=500)
    content: str = Field(..., min_length=1)
    featured_image: Optional[str] = None  # URL to featured image
    
    # Categorization and tagging
    category_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # Publishing
    status: BlogStatus = BlogStatus.DRAFT
    published_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    
    # SEO
    meta_title: Optional[str] = Field(None, max_length=60)
    meta_description: Optional[str] = Field(None, max_length=160)
    canonical_url: Optional[str] = None
    
    # Social sharing
    og_title: Optional[str] = Field(None, max_length=60)
    og_description: Optional[str] = Field(None, max_length=160)
    og_image: Optional[str] = None
    twitter_card: Optional[str] = "summary_large_image"
    
    # Analytics and engagement
    view_count: int = 0
    like_count: int = 0
    share_count: int = 0
    comment_count: int = 0
    
    # Content features
    is_featured: bool = False
    allow_comments: bool = True
    is_premium: bool = False  # Premium content requires login
    
    # Management
    author_id: Optional[str] = None  # User or Admin ID
    author_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('slug')
    def validate_slug(cls, v):
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v

class BlogPostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=220)
    excerpt: Optional[str] = Field(None, max_length=500)
    content: str = Field(..., min_length=1)
    featured_image: Optional[str] = None
    category_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    status: BlogStatus = BlogStatus.DRAFT
    scheduled_for: Optional[datetime] = None
    meta_title: Optional[str] = Field(None, max_length=60)
    meta_description: Optional[str] = Field(None, max_length=160)
    canonical_url: Optional[str] = None
    og_title: Optional[str] = Field(None, max_length=60)
    og_description: Optional[str] = Field(None, max_length=160)
    og_image: Optional[str] = None
    is_featured: bool = False
    allow_comments: bool = True
    is_premium: bool = False

class BlogPostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=220)
    excerpt: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    featured_image: Optional[str] = None
    category_id: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[BlogStatus] = None
    scheduled_for: Optional[datetime] = None
    meta_title: Optional[str] = Field(None, max_length=60)
    meta_description: Optional[str] = Field(None, max_length=160)
    canonical_url: Optional[str] = None
    og_title: Optional[str] = Field(None, max_length=60)
    og_description: Optional[str] = Field(None, max_length=160)
    og_image: Optional[str] = None
    is_featured: Optional[bool] = None
    allow_comments: Optional[bool] = None
    is_premium: Optional[bool] = None

class BlogComment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str
    parent_id: Optional[str] = None  # For threaded comments
    author_name: str = Field(..., min_length=1, max_length=100)
    author_email: str
    author_website: Optional[str] = None
    content: str = Field(..., min_length=1, max_length=2000)
    is_approved: bool = False
    is_spam: bool = False
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Documentation Models
class DocumentationType(str, Enum):
    API = "api"
    USER_GUIDE = "user_guide"
    TECHNICAL = "technical"
    FAQ = "faq"
    TUTORIAL = "tutorial"

class DocumentationSection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=500)
    doc_type: DocumentationType
    parent_id: Optional[str] = None  # For nested sections
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentationPage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=220)
    content: str = Field(..., min_length=1)
    excerpt: Optional[str] = Field(None, max_length=300)
    
    # Organization
    section_id: str
    sort_order: int = 0
    
    # Navigation
    prev_page_id: Optional[str] = None
    next_page_id: Optional[str] = None
    
    # SEO
    meta_title: Optional[str] = Field(None, max_length=60)
    meta_description: Optional[str] = Field(None, max_length=160)
    
    # Analytics
    view_count: int = 0
    helpful_votes: int = 0
    not_helpful_votes: int = 0
    
    # Management
    is_published: bool = True
    requires_auth: bool = False
    author_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# SEO Models
class SEOPage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url_path: str = Field(..., min_length=1, max_length=200)
    page_title: str = Field(..., min_length=1, max_length=60)
    meta_description: str = Field(..., min_length=1, max_length=160)
    meta_keywords: Optional[str] = Field(None, max_length=200)
    canonical_url: Optional[str] = None
    
    # Open Graph
    og_title: Optional[str] = Field(None, max_length=60)
    og_description: Optional[str] = Field(None, max_length=160)
    og_image: Optional[str] = None
    og_type: str = "website"
    
    # Twitter Card
    twitter_card: str = "summary_large_image"
    twitter_title: Optional[str] = Field(None, max_length=60)
    twitter_description: Optional[str] = Field(None, max_length=160)
    twitter_image: Optional[str] = None
    
    # Schema.org structured data
    schema_type: Optional[str] = None  # "Article", "Product", "Organization", etc.
    structured_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Indexing
    robots_meta: str = "index, follow"
    sitemap_priority: float = Field(default=0.5, ge=0.0, le=1.0)
    sitemap_changefreq: str = "weekly"  # "always", "hourly", "daily", "weekly", "monthly", "yearly", "never"
    
    # Analytics
    last_crawled: Optional[datetime] = None
    crawl_status: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SEOAnalytics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url_path: str
    date: datetime = Field(default_factory=lambda: datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0))
    
    # Traffic metrics
    page_views: int = 0
    unique_visitors: int = 0
    bounce_rate: float = 0.0
    avg_time_on_page: float = 0.0  # in seconds
    
    # SEO metrics
    search_impressions: int = 0
    search_clicks: int = 0
    avg_position: float = 0.0
    click_through_rate: float = 0.0
    
    # Conversion metrics
    conversions: int = 0
    conversion_rate: float = 0.0
    
    # Referrer data
    top_keywords: List[Dict[str, Any]] = Field(default_factory=list)
    top_pages: List[Dict[str, Any]] = Field(default_factory=list)
    referrer_sources: Dict[str, int] = Field(default_factory=dict)

# Media Models
class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"

class MediaFile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = Field(..., min_length=1, max_length=200)
    original_filename: str = Field(..., min_length=1, max_length=200)
    file_path: str = Field(..., min_length=1, max_length=500)
    file_url: str = Field(..., min_length=1, max_length=500)
    
    # File properties
    file_size: int = Field(..., ge=0)  # in bytes
    mime_type: str = Field(..., min_length=1, max_length=100)
    media_type: MediaType
    
    # Image-specific properties
    width: Optional[int] = Field(None, ge=0)
    height: Optional[int] = Field(None, ge=0)
    alt_text: Optional[str] = Field(None, max_length=200)
    
    # Metadata
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    tags: List[str] = Field(default_factory=list)
    
    # Organization
    folder_path: Optional[str] = Field(None, max_length=200)
    is_public: bool = True
    
    # Usage tracking
    usage_count: int = 0
    last_used: Optional[datetime] = None
    
    # Management
    uploaded_by: Optional[str] = None  # User or Admin ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Landing Page Models
class LandingPageSection(str, Enum):
    HERO = "hero"
    FEATURES = "features"
    TESTIMONIALS = "testimonials"
    PRICING = "pricing"
    CTA = "cta"
    FAQ = "faq"
    ABOUT = "about"
    CONTACT = "contact"

class LandingPageComponent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    section_type: LandingPageSection
    title: str = Field(..., min_length=1, max_length=200)
    subtitle: Optional[str] = Field(None, max_length=300)
    content: Optional[str] = None
    
    # Visual elements
    background_image: Optional[str] = None
    background_color: Optional[str] = "#ffffff"
    text_color: Optional[str] = "#333333"
    
    # Configuration
    config: Dict[str, Any] = Field(default_factory=dict)  # Section-specific settings
    
    # Layout
    sort_order: int = 0
    is_active: bool = True
    
    # A/B Testing
    variant_name: Optional[str] = None
    test_group: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LandingPage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=220)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    
    # Components
    components: List[str] = Field(default_factory=list)  # Component IDs
    
    # SEO
    meta_title: Optional[str] = Field(None, max_length=60)
    meta_description: Optional[str] = Field(None, max_length=160)
    canonical_url: Optional[str] = None
    
    # Analytics
    view_count: int = 0
    conversion_count: int = 0
    conversion_rate: float = 0.0
    
    # A/B Testing
    is_test_page: bool = False
    test_name: Optional[str] = None
    test_traffic_split: float = 50.0  # Percentage
    
    # Publishing
    is_published: bool = False
    published_at: Optional[datetime] = None
    
    # Management
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Newsletter and Email Content
class EmailCampaign(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=200)
    subject: str = Field(..., min_length=1, max_length=200)
    preview_text: Optional[str] = Field(None, max_length=150)
    
    # Content
    html_content: str = Field(..., min_length=1)
    text_content: Optional[str] = None
    
    # Targeting
    target_segments: List[str] = Field(default_factory=list)
    exclude_segments: List[str] = Field(default_factory=list)
    
    # Scheduling
    send_at: Optional[datetime] = None
    timezone: str = "UTC"
    
    # Analytics
    sent_count: int = 0
    delivered_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    unsubscribed_count: int = 0
    bounced_count: int = 0
    
    # Management
    status: str = "draft"  # "draft", "scheduled", "sending", "sent", "cancelled"
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None