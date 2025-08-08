from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Keys
    openai_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    custom_llm_api_key: Optional[str] = None

    # API URLs
    custom_llm_base_url: str = "https://api.avalai.ir/v1"

    # App Settings
    app_name: str = "Skincare Recommendation API"
    debug: bool = False

    # LLM Settings
    primary_llm_provider: str = "openai"  # "openai", "groq", or "custom"
    vision_model: str = "gpt-4o-mini"  # OpenAI vision model
    custom_vision_model: str = "aval-vision-large"

    # Temporary image storage
    temp_image_base_url: str = "http://localhost:8000/temp_images"

    # Redis for analytics (optional)
    redis_url: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()