"""
Configuration Settings for NitePutter Pro
Centralized configuration management
"""

import os
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "NitePutter Pro"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="production", env="ENVIRONMENT")
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=4, env="WORKERS")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001",
            "https://niteputterpro.com",
            "https://www.niteputterpro.com"
        ],
        env="ALLOWED_ORIGINS"
    )
    
    # Database
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017",
        env="MONGODB_URL"
    )
    DATABASE_NAME: str = Field(
        default="niteputter_pro",
        env="DATABASE_NAME"
    )
    
    # Redis (for caching/sessions)
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # JWT Authentication
    JWT_SECRET_KEY: str = Field(
        default="your-super-secret-jwt-key-change-in-production",
        env="JWT_SECRET_KEY"
    )
    JWT_REFRESH_SECRET_KEY: str = Field(
        default="your-super-secret-refresh-key-change-in-production",
        env="JWT_REFRESH_SECRET_KEY"
    )
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Stripe Configuration
    STRIPE_SECRET_KEY: str = Field(
        default="",
        env="STRIPE_SECRET_KEY"
    )
    STRIPE_PUBLISHABLE_KEY: str = Field(
        default="",
        env="STRIPE_PUBLISHABLE_KEY"
    )
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(default=None, env="STRIPE_WEBHOOK_SECRET")
    STRIPE_SUCCESS_URL: str = Field(
        default="http://localhost:3000/checkout/success",
        env="STRIPE_SUCCESS_URL"
    )
    STRIPE_CANCEL_URL: str = Field(
        default="http://localhost:3000/checkout/cancel",
        env="STRIPE_CANCEL_URL"
    )
    
    # Email Configuration
    SMTP_HOST: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_USE_TLS: bool = Field(default=True, env="SMTP_USE_TLS")
    EMAIL_FROM: str = Field(default="noreply@niteputterpro.com", env="EMAIL_FROM")
    EMAIL_FROM_NAME: str = Field(default="NitePutter Pro", env="EMAIL_FROM_NAME")
    
    # AWS Configuration (for S3, etc.)
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    S3_BUCKET_NAME: Optional[str] = Field(default=None, env="S3_BUCKET_NAME")
    
    # Cloudinary (for image storage)
    CLOUDINARY_CLOUD_NAME: Optional[str] = Field(default=None, env="CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: Optional[str] = Field(default=None, env="CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: Optional[str] = Field(default=None, env="CLOUDINARY_API_SECRET")
    
    # Security
    SECRET_KEY: str = Field(
        default="your-application-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    BCRYPT_ROUNDS: int = Field(default=12, env="BCRYPT_ROUNDS")
    PASSWORD_MIN_LENGTH: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_PERIOD: int = Field(default=60, env="RATE_LIMIT_PERIOD")  # seconds
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Analytics
    GOOGLE_ANALYTICS_ID: Optional[str] = Field(default=None, env="GOOGLE_ANALYTICS_ID")
    MIXPANEL_TOKEN: Optional[str] = Field(default=None, env="MIXPANEL_TOKEN")
    
    # Social OAuth
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_SECRET")
    FACEBOOK_CLIENT_ID: Optional[str] = Field(default=None, env="FACEBOOK_CLIENT_ID")
    FACEBOOK_CLIENT_SECRET: Optional[str] = Field(default=None, env="FACEBOOK_CLIENT_SECRET")
    
    # Shipping
    USPS_API_KEY: Optional[str] = Field(default=None, env="USPS_API_KEY")
    UPS_API_KEY: Optional[str] = Field(default=None, env="UPS_API_KEY")
    FEDEX_API_KEY: Optional[str] = Field(default=None, env="FEDEX_API_KEY")
    DEFAULT_SHIPPING_RATE: float = Field(default=9.99, env="DEFAULT_SHIPPING_RATE")
    FREE_SHIPPING_THRESHOLD: float = Field(default=100.00, env="FREE_SHIPPING_THRESHOLD")
    
    # Inventory
    LOW_STOCK_THRESHOLD: int = Field(default=10, env="LOW_STOCK_THRESHOLD")
    RESERVE_STOCK_MINUTES: int = Field(default=15, env="RESERVE_STOCK_MINUTES")
    
    # Cart
    CART_EXPIRY_DAYS: int = Field(default=30, env="CART_EXPIRY_DAYS")
    ABANDONED_CART_HOURS: int = Field(default=1, env="ABANDONED_CART_HOURS")
    
    # Order
    ORDER_NUMBER_PREFIX: str = Field(default="NPP", env="ORDER_NUMBER_PREFIX")
    
    # Tax
    ENABLE_TAX_CALCULATION: bool = Field(default=True, env="ENABLE_TAX_CALCULATION")
    DEFAULT_TAX_RATE: float = Field(default=0.0875, env="DEFAULT_TAX_RATE")  # 8.75%
    
    # Features
    ENABLE_REVIEWS: bool = Field(default=True, env="ENABLE_REVIEWS")
    ENABLE_WISHLIST: bool = Field(default=True, env="ENABLE_WISHLIST")
    ENABLE_GUEST_CHECKOUT: bool = Field(default=True, env="ENABLE_GUEST_CHECKOUT")
    ENABLE_COUPONS: bool = Field(default=True, env="ENABLE_COUPONS")
    
    # URLs
    FRONTEND_URL: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    BACKEND_URL: str = Field(default="http://localhost:8000", env="BACKEND_URL")
    
    @field_validator("ALLOWED_ORIGINS", mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return v.upper()
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v):
        valid_envs = ["development", "staging", "production", "test"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Invalid environment. Must be one of: {valid_envs}")
        return v.lower()
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"  # Ignore extra environment variables
    }
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"
    
    def is_test(self) -> bool:
        """Check if running in test mode"""
        return self.ENVIRONMENT == "test"
    
    def get_database_url(self) -> str:
        """Get the database connection URL"""
        return self.MONGODB_URL
    
    def get_stripe_config(self) -> dict:
        """Get Stripe configuration"""
        return {
            "secret_key": self.STRIPE_SECRET_KEY,
            "publishable_key": self.STRIPE_PUBLISHABLE_KEY,
            "webhook_secret": self.STRIPE_WEBHOOK_SECRET,
            "success_url": self.STRIPE_SUCCESS_URL,
            "cancel_url": self.STRIPE_CANCEL_URL
        }
    
    def get_email_config(self) -> dict:
        """Get email configuration"""
        return {
            "host": self.SMTP_HOST,
            "port": self.SMTP_PORT,
            "username": self.SMTP_USERNAME,
            "password": self.SMTP_PASSWORD,
            "use_tls": self.SMTP_USE_TLS,
            "from_email": self.EMAIL_FROM,
            "from_name": self.EMAIL_FROM_NAME
        }
    
    def get_jwt_config(self) -> dict:
        """Get JWT configuration"""
        return {
            "secret_key": self.JWT_SECRET_KEY,
            "refresh_secret_key": self.JWT_REFRESH_SECRET_KEY,
            "algorithm": self.JWT_ALGORITHM,
            "access_token_expire_minutes": self.ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_expire_days": self.REFRESH_TOKEN_EXPIRE_DAYS
        }


# Create settings instance
settings = Settings()

# Export commonly used settings
DEBUG = settings.DEBUG
ENVIRONMENT = settings.ENVIRONMENT
DATABASE_URL = settings.MONGODB_URL
DATABASE_NAME = settings.DATABASE_NAME
STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY = settings.STRIPE_PUBLISHABLE_KEY