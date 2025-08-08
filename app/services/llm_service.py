import json
import base64
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import httpx
from openai import OpenAI
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    @abstractmethod
    async def analyze_image(self, image_data: Optional[bytes] = None, image_url: Optional[str] = None,
                            prompt: str = "") -> Dict[str, Any]:
        pass


class OpenAIProvider(LLMProvider):
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(base_url="https://api.avalapis.ir/v1",api_key=settings.openai_api_key)

    async def analyze_image(self, image_data: Optional[bytes] = None, image_url: Optional[str] = None,
                            prompt: str = "") -> Dict[str, Any]:
        try:
            if image_data:
                # Use base64 encoded image
                base64_image = base64.b64encode(image_data).decode('utf-8')
                image_content = {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
                logger.info("Using base64 encoded image for OpenAI")
            elif image_url:
                # Use image URL
                image_content = {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
                logger.info(f"Using image URL for OpenAI: {image_url}")
            else:
                raise ValueError("Either image_data or image_url must be provided")

            response = self.client.chat.completions.create(
                model=settings.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            image_content
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1000
            )

            content = response.choices[0].message.content
            logger.info("OpenAI response received successfully")
            return json.loads(content)
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise


class CustomLLMProvider(LLMProvider):
    def __init__(self):
        if not settings.custom_llm_api_key:
            raise ValueError("Custom LLM API key is required")
        self.base_url = settings.custom_llm_base_url
        self.api_key = settings.custom_llm_api_key

    async def analyze_image(self, image_data: Optional[bytes] = None, image_url: Optional[str] = None,
                            prompt: str = "") -> Dict[str, Any]:
        if not image_url:
            raise ValueError("Custom LLM provider requires image_url. Please provide a publicly accessible image URL.")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.custom_vision_model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": image_url}
                                    }
                                ]
                            }
                        ],
                        "response_format": {"type": "json_object"}
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                logger.info("Custom LLM response received successfully")
                return json.loads(content)
        except Exception as e:
            logger.error(f"Custom LLM API error: {str(e)}")
            raise


class LLMService:
    def __init__(self):
        self.providers = {}

        # Initialize available providers
        try:
            if settings.openai_api_key:
                self.providers["openai"] = OpenAIProvider()
                logger.info("OpenAI provider initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI provider: {str(e)}")

        try:
            if settings.custom_llm_api_key:
                self.providers["custom"] = CustomLLMProvider()
                logger.info("Custom LLM provider initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Custom LLM provider: {str(e)}")

        if not self.providers:
            raise ValueError("No LLM providers are available. Please configure at least one API key.")

        # Set primary provider
        self.primary_provider = settings.primary_llm_provider
        if self.primary_provider not in self.providers:
            # Fallback to first available provider
            self.primary_provider = list(self.providers.keys())[0]
            logger.warning(f"Primary provider not available, using: {self.primary_provider}")

    async def analyze_skin(self, image_data: Optional[bytes] = None, image_url: Optional[str] = None) -> Dict[str, Any]:
        """Analyze skin from image using primary provider with fallback"""
        from app.utils.prompts import get_skin_analysis_prompt
        prompt = get_skin_analysis_prompt()

        logger.info(f"Starting skin analysis with provider: {self.primary_provider}")
        logger.info(f"Has image_data: {image_data is not None}, Has image_url: {image_url is not None}")

        # Try primary provider first
        try:
            if self.primary_provider in self.providers:
                result = await self.providers[self.primary_provider].analyze_image(
                    image_data=image_data,
                    image_url=image_url,
                    prompt=prompt
                )
                logger.info("Primary provider analysis successful")
                return result
        except Exception as e:
            logger.error(f"Primary provider ({self.primary_provider}) failed: {str(e)}")

            # Try fallback providers
            for provider_name, provider in self.providers.items():
                if provider_name != self.primary_provider:
                    try:
                        logger.info(f"Trying fallback provider: {provider_name}")
                        result = await provider.analyze_image(
                            image_data=image_data,
                            image_url=image_url,
                            prompt=prompt
                        )
                        logger.info(f"Fallback provider {provider_name} successful")
                        return result
                    except Exception as fallback_error:
                        logger.error(f"Fallback provider {provider_name} failed: {str(fallback_error)}")
                        continue

        # If all providers failed
        raise Exception("All LLM providers failed. Please check your configuration and try again.")

    async def get_recommendations(self, skin_analysis: Dict[str, Any], products_json: str) -> Dict[str, Any]:
        """Get product recommendations based on skin analysis"""
        from app.utils.prompts import get_product_recommendation_prompt
        prompt = get_product_recommendation_prompt(skin_analysis, products_json)

        logger.info("Starting product recommendation generation")

        # For recommendations, we can use a text-only model
        try:
            if "openai" in self.providers:
                client = OpenAI(api_key=settings.openai_api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    max_tokens=1000
                )
                content = response.choices[0].message.content
                logger.info("OpenAI recommendation generation successful")
                return json.loads(content)

            elif "custom" in self.providers:
                # Use custom LLM for text-only recommendation
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{settings.custom_llm_base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings.custom_llm_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "aval-llama-3-70b",  # Text model for recommendations
                            "messages": [{"role": "user", "content": prompt}],
                            "response_format": {"type": "json_object"}
                        },
                        timeout=30.0
                    )
                    response.raise_for_status()
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    logger.info("Custom LLM recommendation generation successful")
                    return json.loads(content)

            else:
                raise Exception("No available providers for recommendation generation")

        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            raise