"""
Production configuration with environment variables and validation
"""

import os
from typing import Optional
from pydantic import BaseSettings, validator
from functools import lru_cache


class ProductionSettings(BaseSettings):
    """Production settings with validation"""
    
    # Environment
    environment: str = "production"
    debug: bool = False
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30 * 24 * 60  # 30 days
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # GitHub OAuth
    github_client_id: str
    github_client_secret: str
    
    # URLs
    base_url: str
    dashboard_url: str
    
    # Rate limiting
    rate_limit_calls: int = 100
    rate_limit_period: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "/app/logs/api.log"
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    @validator('environment')
    def validate_environment(cls, v):
        allowed = ['development', 'staging', 'production']
        if v not in allowed:
            raise ValueError(f'environment must be one of: {allowed}')
        return v
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('secret_key must be at least 32 characters long')
        return v
    
    @validator('github_client_id')
    def validate_github_client_id(cls, v):
        if not v.startswith('Ov23li'):
            raise ValueError('github_client_id appears to be invalid')
        return v
    
    @validator('github_client_secret')
    def validate_github_client_secret(cls, v):
        if len(v) < 20:
            raise ValueError('github_client_secret must be at least 20 characters long')
        return v
    
    class Config:
        env_file = ".env.production"
        case_sensitive = False


@lru_cache()
def get_production_settings() -> ProductionSettings:
    """Get cached production settings"""
    return ProductionSettings()


# Environment-specific settings
def get_settings():
    """Get settings based on environment"""
    env = os.getenv('ENVIRONMENT', 'development').lower()
    
    if env == 'production':
        return get_production_settings()
    else:
        # Import development settings for non-production
        from ..config import settings
        return settings
