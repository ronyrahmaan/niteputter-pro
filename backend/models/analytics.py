from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid

# Analytics Time Periods
class TimePeriod(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class MetricType(str, Enum):
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    PERCENTAGE = "percentage"
    RATE = "rate"

# Sales Analytics Models
class SalesMetric(BaseModel):
    period: str  # Date string
    revenue: float = 0.0
    orders: int = 0
    units_sold: int = 0
    avg_order_value: float = 0.0
    conversion_rate: float = 0.0
    refunds: float = 0.0
    net_revenue: float = 0.0

class ProductPerformance(BaseModel):
    product_id: str
    product_name: str
    sku: str
    category: str
    revenue: float = 0.0
    units_sold: int = 0
    orders: int = 0
    avg_price: float = 0.0
    profit_margin: Optional[float] = None
    view_to_purchase_rate: float = 0.0
    return_rate: float = 0.0
    customer_rating: Optional[float] = None

class CategoryPerformance(BaseModel):
    category: str
    revenue: float = 0.0
    units_sold: int = 0
    orders: int = 0
    product_count: int = 0
    avg_order_value: float = 0.0
    market_share: float = 0.0

class SalesAnalyticsReport(BaseModel):
    period_start: datetime
    period_end: datetime
    time_granularity: TimePeriod
    total_revenue: float = 0.0
    total_orders: int = 0
    total_units: int = 0
    avg_order_value: float = 0.0
    metrics_over_time: List[SalesMetric] = Field(default_factory=list)
    top_products: List[ProductPerformance] = Field(default_factory=list)
    category_performance: List[CategoryPerformance] = Field(default_factory=list)
    growth_rate: float = 0.0
    period_comparison: Optional[Dict[str, float]] = None

# Customer Analytics Models
class CustomerSegment(str, Enum):
    NEW = "new"
    RETURNING = "returning"
    VIP = "vip"
    DORMANT = "dormant"
    CHURNED = "churned"

class CustomerMetric(BaseModel):
    period: str
    new_customers: int = 0
    returning_customers: int = 0
    total_active_customers: int = 0
    customer_retention_rate: float = 0.0
    churn_rate: float = 0.0
    lifetime_value: float = 0.0

class CustomerBehavior(BaseModel):
    customer_id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    segment: CustomerSegment
    total_orders: int = 0
    total_spent: float = 0.0
    avg_order_value: float = 0.0
    last_order_date: Optional[datetime] = None
    days_since_last_order: Optional[int] = None
    lifetime_value: float = 0.0
    predicted_ltv: Optional[float] = None
    favorite_category: Optional[str] = None
    engagement_score: float = 0.0

class CustomerAnalyticsReport(BaseModel):
    period_start: datetime
    period_end: datetime
    time_granularity: TimePeriod
    total_customers: int = 0
    new_customers: int = 0
    returning_customers: int = 0
    customer_segments: Dict[str, int] = Field(default_factory=dict)
    metrics_over_time: List[CustomerMetric] = Field(default_factory=list)
    top_customers: List[CustomerBehavior] = Field(default_factory=list)
    retention_analysis: Dict[str, float] = Field(default_factory=dict)
    cohort_analysis: List[Dict[str, Any]] = Field(default_factory=list)

# Traffic Analytics Models
class TrafficSource(str, Enum):
    ORGANIC = "organic"
    DIRECT = "direct"
    SOCIAL = "social"
    EMAIL = "email"
    PAID = "paid"
    REFERRAL = "referral"
    AFFILIATE = "affiliate"

class PageMetric(BaseModel):
    page_path: str
    page_title: Optional[str] = None
    views: int = 0
    unique_views: int = 0
    bounce_rate: float = 0.0
    avg_time_on_page: float = 0.0
    conversions: int = 0
    conversion_rate: float = 0.0

class TrafficMetric(BaseModel):
    period: str
    total_sessions: int = 0
    unique_visitors: int = 0
    page_views: int = 0
    bounce_rate: float = 0.0
    avg_session_duration: float = 0.0
    conversion_rate: float = 0.0

class TrafficAnalyticsReport(BaseModel):
    period_start: datetime
    period_end: datetime
    time_granularity: TimePeriod
    total_sessions: int = 0
    unique_visitors: int = 0
    total_page_views: int = 0
    bounce_rate: float = 0.0
    avg_session_duration: float = 0.0
    metrics_over_time: List[TrafficMetric] = Field(default_factory=list)
    top_pages: List[PageMetric] = Field(default_factory=list)
    traffic_sources: Dict[str, int] = Field(default_factory=dict)
    device_breakdown: Dict[str, int] = Field(default_factory=dict)
    geographic_breakdown: Dict[str, int] = Field(default_factory=dict)

# Financial Analytics Models
class FinancialMetric(BaseModel):
    period: str
    gross_revenue: float = 0.0
    net_revenue: float = 0.0
    refunds: float = 0.0
    taxes: float = 0.0
    shipping_costs: float = 0.0
    processing_fees: float = 0.0
    profit_margin: float = 0.0
    operating_expenses: float = 0.0
    net_profit: float = 0.0

class FinancialAnalyticsReport(BaseModel):
    period_start: datetime
    period_end: datetime
    time_granularity: TimePeriod
    total_gross_revenue: float = 0.0
    total_net_revenue: float = 0.0
    total_profit: float = 0.0
    profit_margin: float = 0.0
    metrics_over_time: List[FinancialMetric] = Field(default_factory=list)
    revenue_by_source: Dict[str, float] = Field(default_factory=dict)
    expense_breakdown: Dict[str, float] = Field(default_factory=dict)
    cash_flow: List[Dict[str, Any]] = Field(default_factory=list)
    forecasts: Dict[str, float] = Field(default_factory=dict)

# Inventory Analytics Models
class InventoryMetric(BaseModel):
    period: str
    total_stock_value: float = 0.0
    low_stock_items: int = 0
    out_of_stock_items: int = 0
    inventory_turnover: float = 0.0
    avg_stock_age: float = 0.0

class InventoryAnalytics(BaseModel):
    product_id: str
    product_name: str
    sku: str
    current_stock: int = 0
    stock_value: float = 0.0
    units_sold_30d: int = 0
    stock_turnover_rate: float = 0.0
    days_of_supply: int = 0
    reorder_point: int = 0
    stock_status: str = "normal"  # "normal", "low", "out", "overstock"
    last_restocked: Optional[datetime] = None

class InventoryAnalyticsReport(BaseModel):
    period_start: datetime
    period_end: datetime
    total_products: int = 0
    total_stock_value: float = 0.0
    low_stock_alerts: int = 0
    out_of_stock_alerts: int = 0
    avg_turnover_rate: float = 0.0
    metrics_over_time: List[InventoryMetric] = Field(default_factory=list)
    product_analytics: List[InventoryAnalytics] = Field(default_factory=list)
    category_stock_levels: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    reorder_recommendations: List[Dict[str, Any]] = Field(default_factory=list)

# Custom Reports Models
class ReportType(str, Enum):
    SALES = "sales"
    CUSTOMER = "customer"
    PRODUCT = "product"
    TRAFFIC = "traffic"
    FINANCIAL = "financial"
    INVENTORY = "inventory"
    CUSTOM = "custom"

class ReportFrequency(str, Enum):
    MANUAL = "manual"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

class CustomReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    report_type: ReportType
    frequency: ReportFrequency = ReportFrequency.MANUAL
    
    # Report configuration
    date_range: Dict[str, Any] = Field(default_factory=dict)  # start, end, period
    filters: Dict[str, Any] = Field(default_factory=dict)
    metrics: List[str] = Field(default_factory=list)
    dimensions: List[str] = Field(default_factory=list)
    
    # Scheduling
    is_scheduled: bool = False
    schedule_config: Optional[Dict[str, Any]] = None
    recipients: List[str] = Field(default_factory=list)  # Email addresses
    
    # Metadata
    created_by: Optional[str] = None  # Admin ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    
    is_active: bool = True

class CustomReportCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    report_type: ReportType
    frequency: ReportFrequency = ReportFrequency.MANUAL
    date_range: Dict[str, Any] = Field(default_factory=dict)
    filters: Dict[str, Any] = Field(default_factory=dict)
    metrics: List[str] = Field(default_factory=list)
    dimensions: List[str] = Field(default_factory=list)
    is_scheduled: bool = False
    schedule_config: Optional[Dict[str, Any]] = None
    recipients: List[str] = Field(default_factory=list)

class CustomReportUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    frequency: Optional[ReportFrequency] = None
    date_range: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    metrics: Optional[List[str]] = None
    dimensions: Optional[List[str]] = None
    is_scheduled: Optional[bool] = None
    schedule_config: Optional[Dict[str, Any]] = None
    recipients: Optional[List[str]] = None
    is_active: Optional[bool] = None

# Dashboard Models
class DashboardWidget(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    widget_type: str  # "chart", "metric", "table", "map"
    data_source: str  # "sales", "customers", "products", etc.
    config: Dict[str, Any] = Field(default_factory=dict)
    position: Dict[str, int] = Field(default_factory=dict)  # x, y, width, height
    refresh_interval: int = 300  # seconds
    
class CustomDashboard(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    widgets: List[DashboardWidget] = Field(default_factory=list)
    layout: Dict[str, Any] = Field(default_factory=dict)
    is_default: bool = False
    is_public: bool = False
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Export Models
class ExportFormat(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"
    JSON = "json"

class ExportRequest(BaseModel):
    report_type: ReportType
    format: ExportFormat = ExportFormat.CSV
    date_range: Dict[str, Any]
    filters: Dict[str, Any] = Field(default_factory=dict)
    include_charts: bool = False
    
class ExportJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    export_request: ExportRequest
    status: str = "pending"  # "pending", "processing", "completed", "failed"
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None

# Performance Monitoring Models
class SystemPerformance(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    active_sessions: int = 0
    api_response_time: float = 0.0
    database_query_time: float = 0.0
    error_rate: float = 0.0
    uptime: float = 0.0

class PerformanceAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: str  # "cpu", "memory", "disk", "response_time", "error_rate"
    threshold: float
    current_value: float
    severity: str = "warning"  # "info", "warning", "error", "critical"
    message: str
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    is_active: bool = True

# Analytics Query Builder
class AnalyticsQuery(BaseModel):
    data_source: str  # "orders", "users", "products", etc.
    metrics: List[str]  # ["count", "sum:revenue", "avg:order_value"]
    dimensions: List[str] = Field(default_factory=list)  # ["date", "category", "customer_segment"]
    filters: List[Dict[str, Any]] = Field(default_factory=list)
    date_range: Dict[str, Any]  # {"start": "2024-01-01", "end": "2024-12-31"}
    time_granularity: TimePeriod = TimePeriod.DAY
    sort: List[Dict[str, str]] = Field(default_factory=list)  # [{"field": "revenue", "order": "desc"}]
    limit: Optional[int] = None

class AnalyticsResult(BaseModel):
    query: AnalyticsQuery
    data: List[Dict[str, Any]]
    total_rows: int
    execution_time: float  # milliseconds
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    cache_expires_at: Optional[datetime] = None