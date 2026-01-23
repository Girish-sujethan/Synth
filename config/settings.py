"""Application settings and configuration management using Pydantic Settings."""

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, field_validator


class Settings(BaseSettings):
    """Application settings with Supabase database configuration."""

    # Supabase Configuration
    supabase_url: str = Field(
        ...,
        description="Supabase project URL",
        alias="SUPABASE_URL"
    )
    
    supabase_db_url: PostgresDsn = Field(
        ...,
        description="Supabase PostgreSQL database connection URL",
        alias="SUPABASE_DB_URL"
    )
    
    # Alternative database URL (falls back to supabase_db_url if not provided)
    database_url: PostgresDsn | None = Field(
        None,
        description="Direct PostgreSQL database connection URL",
        alias="DATABASE_URL"
    )
    
    # Supabase API Key (optional)
    supabase_key: str | None = Field(
        None,
        description="Supabase anon/service role key",
        alias="SUPABASE_KEY"
    )
    
    # Environment
    environment: Literal["development", "production", "testing"] = Field(
        "development",
        description="Application environment",
        alias="ENVIRONMENT"
    )
    
    # Database connection pool settings
    db_pool_size: int = Field(
        5,
        description="Database connection pool size",
        alias="DB_POOL_SIZE"
    )
    
    db_max_overflow: int = Field(
        10,
        description="Maximum overflow connections in pool",
        alias="DB_MAX_OVERFLOW"
    )
    
    db_pool_pre_ping: bool = Field(
        True,
        description="Enable connection pool pre-ping to verify connections",
        alias="DB_POOL_PRE_PING"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator("database_url", mode="before")
    @classmethod
    def set_database_url(cls, v: str | None, info) -> PostgresDsn | None:
        """Set database_url from supabase_db_url if not provided."""
        if v is None and hasattr(info, "data") and "supabase_db_url" in info.data:
            return info.data["supabase_db_url"]
        return v
    
    @property
    def effective_database_url(self) -> PostgresDsn:
        """Get the effective database URL to use."""
        return self.database_url or self.supabase_db_url
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


# Global settings instance
settings = Settings()

