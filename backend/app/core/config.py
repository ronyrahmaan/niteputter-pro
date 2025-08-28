"""
Enhanced Configuration Management for NitePutter Pro
Validates and manages all environment variables with type safety
"""

from typing import List, Optional, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, SecretStr, HttpUrl
from functools import lru_cache
import os
from pathlib import Path

class Settings(BaseSettings):
    """
    Application settings with validation and type safety
    """
    
    # Application Settings
    app_name: str = Field(default="NitePutter Pro", description="Application name")
    app_env: str = Field(default="development", description="Environment: development, staging, production")
    app_debug: bool = Field(default=False, description="Debug mode")
    app_url: str = Field(default="http://localhost:8000", description="Backend API URL")
    frontend_url: str = Field(default="http://localhost:5173", description="Frontend URL")
    allowed_origins: List[str] = Field(default=["http://localhost:5173"], description="CORS allowed origins")
    
    # Security
    secret_key: SecretStr = Field(..., description="Secret key for JWT encoding")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration in minutes")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiration in days")
    password_reset_token_expire_hours: int = Field(default=24, description="Password reset token expiration")
    
    # MongoDB Configuration
    mongodb_url: str = Field(..., description="MongoDB connection URL")
    mongodb_db_name: str = Field(default="niteputter_pro", description="MongoDB database name")
    mongodb_max_pool_size: int = Field(default=100, description="MongoDB connection pool max size")
    mongodb_min_pool_size: int = Field(default=10, description="MongoDB connection pool min size")
    
    # Redis Configuration
    redis_url: Optional[str] = Field(default=None, description="Redis connection URL")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_decode_responses: bool = Field(default=True, description="Decode Redis responses")
    redis_max_connections: int = Field(default=50, description="Redis max connections")
    
    # Stripe Configuration
    stripe_secret_key: SecretStr = Field(..., description="Stripe secret key")
    stripe_publishable_key: str = Field(..., description="Stripe publishable key")
    stripe_webhook_secret: Optional[SecretStr] = Field(default=None, description="Stripe webhook secret")
    stripe_api_version: str = Field(default="2023-10-16", description="Stripe API version")
    
    # Email Configuration (SendGrid)
    sendgrid_api_key: Optional[SecretStr] = Field(default=None, description="SendGrid API key")
    from_email: str = Field(default="orders@niteputter.com", description="From email address")
    support_email: str = Field(default="support@niteputter.com", description="Support email address")
    admin_email: str = Field(default="admin@niteputter.com", description="Admin email address")
    email_templates_dir: Path = Field(default=Path("./email_templates"), description="Email templates directory")
    
    # AWS S3 Configuration
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS access key ID")
    aws_secret_access_key: Optional[SecretStr] = Field(default=None, description="AWS secret access key")
    aws_s3_bucket_name: str = Field(default="niteputter-products", description="S3 bucket name")
    aws_s3_region: str = Field(default="us-east-1", description="AWS region")
    aws_s3_cdn_url: Optional[str] = Field(default=None, description="CDN URL for S3")
    aws_s3_max_file_size: int = Field(default=10485760, description="Max file size in bytes (10MB)")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[Path] = Field(default=None, description="Log file path")
    log_max_bytes: int = Field(default=10485760, description="Max log file size in bytes")
    log_backup_count: int = Field(default=5, description="Number of log backups to keep")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_default: str = Field(default="100/minute", description="Default rate limit")
    rate_limit_auth: str = Field(default="5/minute", description="Auth rate limit")
    rate_limit_checkout: str = Field(default="10/minute", description="Checkout rate limit")
    
    # Session Configuration
    session_secret_key: Optional[SecretStr] = Field(default=None, description="Session secret key")
    session_cookie_name: str = Field(default="niteputter_session", description="Session cookie name")
    session_cookie_secure: bool = Field(default=False, description="Secure session cookies")
    session_cookie_httponly: bool = Field(default=True, description="HTTP only session cookies")
    session_cookie_samesite: str = Field(default="lax", description="SameSite cookie attribute")
    session_expire_hours: int = Field(default=24, description="Session expiration in hours")
    
    # CORS Configuration
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials in CORS")
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed CORS methods"
    )
    cors_allow_headers: List[str] = Field(
        default=["Content-Type", "Authorization"],
        description="Allowed CORS headers"
    )
    
    # Monitoring & Analytics
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    google_analytics_id: Optional[str] = Field(default=None, description="Google Analytics ID")
    mixpanel_token: Optional[str] = Field(default=None, description="Mixpanel token")
    
    # Feature Flags
    feature_reviews: bool = Field(default=True, description="Enable product reviews")
    feature_wishlist: bool = Field(default=True, description="Enable wishlist feature")
    feature_coupons: bool = Field(default=True, description="Enable coupons")
    feature_newsletter: bool = Field(default=True, description="Enable newsletter")
    feature_social_login: bool = Field(default=False, description="Enable social login")
    
    # Pagination
    default_page_size: int = Field(default=20, description="Default page size")
    max_page_size: int = Field(default=100, description="Maximum page size")
    
    # Cache Settings (seconds)
    cache_product_ttl: int = Field(default=3600, description="Product cache TTL in seconds")
    cache_category_ttl: int = Field(default=7200, description="Category cache TTL in seconds")
    cache_user_ttl: int = Field(default=1800, description="User cache TTL in seconds")
    
    # Background Jobs
    celery_broker_url: Optional[str] = Field(default=None, description="Celery broker URL")
    celery_result_backend: Optional[str] = Field(default=None, description="Celery result backend")
    
    # External APIs
    shipping_api_key: Optional[str] = Field(default=None, description="Shipping API key")
    shipping_api_url: Optional[str] = Field(default=None, description="Shipping API URL")
    tax_api_key: Optional[str] = Field(default=None, description="Tax API key")
    tax_api_url: Optional[str] = Field(default=None, description="Tax API URL")
    
    # Testing
    test_database_name: str = Field(default="niteputter_test", description="Test database name")
    test_redis_db: int = Field(default=15, description="Test Redis database")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"  # Allow extra fields for flexibility
    )
    
    @field_validator("app_env")
    def validate_app_env(cls, v: str) -> str:
        """Validate application environment"""
        allowed = ["development", "staging", "production", "testing"]
        if v not in allowed:
            raise ValueError(f"app_env must be one of {allowed}")
        return v
    
    @field_validator("allowed_origins", mode="before")
    def parse_allowed_origins(cls, v: Any) -> List[str]:
        """Parse comma-separated allowed origins"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("cors_allow_methods", mode="before")
    def parse_cors_methods(cls, v: Any) -> List[str]:
        """Parse comma-separated CORS methods"""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v
    
    @field_validator("cors_allow_headers", mode="before")
    def parse_cors_headers(cls, v: Any) -> List[str]:
        """Parse comma-separated CORS headers"""
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v
    
    @field_validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v
    
    @field_validator("session_cookie_samesite")
    def validate_samesite(cls, v: str) -> str:
        """Validate SameSite attribute"""
        allowed = ["strict", "lax", "none"]
        v = v.lower()
        if v not in allowed:
            raise ValueError(f"session_cookie_samesite must be one of {allowed}")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.app_env == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.app_env == "development"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing"""
        return self.app_env == "testing"
    
    @property
    def database_url(self) -> str:
        """Get the appropriate database URL"""
        if self.is_testing:
            # Use test database for testing
            return self.mongodb_url.replace(
                self.mongodb_db_name, 
                self.test_database_name
            )
        return self.mongodb_url
    
    @property
    def redis_database(self) -> int:
        """Get the appropriate Redis database"""
        if self.is_testing:
            return self.test_redis_db
        return self.redis_db
    
    def get_stripe_key(self) -> str:
        """Get Stripe secret key value"""
        return self.stripe_secret_key.get_secret_value()
    
    def get_sendgrid_key(self) -> Optional[str]:
        """Get SendGrid API key value"""
        if self.sendgrid_api_key:
            return self.sendgrid_api_key.get_secret_value()
        return None
    
    def get_aws_secret(self) -> Optional[str]:
        """Get AWS secret access key value"""
        if self.aws_secret_access_key:
            return self.aws_secret_access_key.get_secret_value()
        return None
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get all feature flags"""
        return {
            "reviews": self.feature_reviews,
            "wishlist": self.feature_wishlist,
            "coupons": self.feature_coupons,
            "newsletter": self.feature_newsletter,
            "social_login": self.feature_social_login
        }
    
    def validate_production_config(self) -> List[str]:
        """Validate configuration for production environment"""
        errors = []
        
        if self.is_production:
            # Check critical production settings
            if self.app_debug:
                errors.append("Debug mode should be disabled in production")
            
            if not self.session_cookie_secure:
                errors.append("Session cookies should be secure in production")
            
            if "localhost" in self.app_url or "127.0.0.1" in self.app_url:
                errors.append("Production should not use localhost URLs")
            
            if not self.stripe_webhook_secret:
                errors.append("Stripe webhook secret is required in production")
            
            if not self.sendgrid_api_key:
                errors.append("SendGrid API key is required in production")
            
            if not self.aws_access_key_id or not self.aws_secret_access_key:
                errors.append("AWS credentials are required in production")
            
            if not self.sentry_dsn:
                errors.append("Sentry DSN is recommended for production error tracking")
        
        return errors


@lru_cache()
def get_settings() -> Settings:
    """
    Create cached settings instance
    This ensures settings are loaded only once
    """
    settings = Settings()
    
    # Validate production configuration
    if settings.is_production:
        errors = settings.validate_production_config()
        if errors:
            print("⚠️  Production configuration warnings:")
            for error in errors:
                print(f"   - {error}")
    
    return settings


# Create global settings instance
settings = get_settings()