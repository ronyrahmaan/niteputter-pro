"""
Professional Configuration Management
Senior-level environment and settings handling
"""
from pydantic import BaseSettings, validator
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Database
    mongodb_url: str = "mongodb://localhost:27017/niteputter"
    mongodb_test_url: str = "mongodb://localhost:27017/niteputter_test"
    
    # Authentication
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    
    # Security
    cors_origins: List[str] = ["http://localhost:3000"]
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    
    # Application
    environment: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api"
    project_name: str = "Nite Putter Pro API"
    version: str = "1.0.0"
    
    # External Services
    stripe_api_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    
    # Email
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # File Upload
    upload_dir: Path = Path("./uploads")
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('allowed_hosts', pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(',')]
        return v
    
    @validator('upload_dir')
    def create_upload_dir(cls, v):
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    
    @property
    def is_testing(self) -> bool:
        return self.environment.lower() == "testing"
    
    @property
    def database_url(self) -> str:
        return self.mongodb_test_url if self.is_testing else self.mongodb_url
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Dependency injection for FastAPI"""
    return settings