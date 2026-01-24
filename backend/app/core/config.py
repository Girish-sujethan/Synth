"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Supabase configuration
    supabase_url: str = ""
    supabase_key: str = ""  # Maps to SUPABASE_KEY
    supabase_db_url: str = ""  # Maps to SUPABASE_DB_URL
    database_url: str = ""  # Maps to DATABASE_URL
    supabase_service_role_key: str = ""  # Maps to SUPABASE_SERVICE_ROLE_KEY
    supabase_jwt_secret: str = ""  # JWT secret for token validation (get from Supabase dashboard)

    # Cerebras configuration
    cerebras_api_key: str = ""
    cerebras_model: str = "zai-glm-4.7"

    # Application settings
    app_name: str = "Synth API"
    app_version: str = "0.1.0"
    environment: str = "development"  # Maps to ENVIRONMENT
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields in .env
    )

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"


settings = Settings()
