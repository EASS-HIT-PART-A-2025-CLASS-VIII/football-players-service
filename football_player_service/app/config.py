from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "Football Player Service"
    default_page_size: int = 20
    feature_preview: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",      # Load from .env file
        env_prefix="PLAYER_", # Only read PLAYER_* variables
        extra="ignore",       # Ignore unknown env vars
    )
