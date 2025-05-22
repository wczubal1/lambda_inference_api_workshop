from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    LAMBDA_INFERENCE_API_KEY: str = Field(..., env="LAMBDA_INFERENCE_API_KEY")
    LAMBDA_CLOUD_API_KEY: str = Field(..., env="LAMBDA_CLOUD_API_KEY")
    LAMBDA_INFERENCE_API_BASE: str = Field(
        default="https://api.lambda.ai/v1",
        env="LAMBDA_INFERENCE_API_BASE"
    )
    LAMBDA_CLOUD_API_BASE: str = Field(
        default="https://cloud.lambda.ai/api/v1",
        env="LAMBDA_CLOUD_API_BASE"
    )
    DEFAULT_MODEL: str = Field(
        default="deepseek-r1-671b",
        env="DEFAULT_MODEL"
    )
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    SSH_KEY_NAME: str = Field(..., env="SSH_KEY_NAME")

    class Config:
        env_file = ".env"
        case_sensitive = True


def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Export settings instance
settings = get_settings()