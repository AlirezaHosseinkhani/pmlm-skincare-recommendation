import json
from typing import List, Dict, Any, Optional
from app.models.product import Product
from app.models.recommendation import (
    SkinAnalysis, ProductRecommendation, RecommendationResponse
)
from app.services.llm_service import LLMService
from app.data.products import product_db
from app.config import settings
import logging

# Add Redis import with error handling
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


class RecommendationService:
    def __init__(self):
        try:
            self.llm_service = LLMService()
            logger.info("LLM service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {str(e)}")
            raise

        self.redis_client = None
        if REDIS_AVAILABLE and settings.redis_url:
            try:
                self.redis_client = redis.from_url(settings.redis_url)
                # Test connection
                self.redis_client.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.warning(f"Redis connection failed: {str(e)}")
                self.redis_client = None

    async def get_recommendations(
            self,
            image_data: Optional[bytes] = None,
            image_url: Optional[str] = None
    ) -> RecommendationResponse:
        """Get skincare recommendations based on facial image analysis"""

        logger.info("Starting recommendation process")
        logger.info(f"Input - image_data: {image_data is not None}, image_url: {image_url is not None}")

        # Validate input
        if not image_data and not image_url:
            raise ValueError("Either image_data or image_url must be provided")

        try:
            # Step 1: Analyze skin
            logger.info("Step 1: Analyzing skin...")
            skin_analysis_data = await self.llm_service.analyze_skin(
                image_data=image_data,
                image_url=image_url
            )

            if not skin_analysis_data:
                raise ValueError("Skin analysis returned empty result")

            logger.info(f"Skin analysis result: {skin_analysis_data}")

            # Validate required fields
            required_fields = ["skin_type", "concerns", "age_range"]
            for field in required_fields:
                if field not in skin_analysis_data:
                    raise ValueError(f"Missing required field in skin analysis: {field}")

            skin_analysis = SkinAnalysis(
                skin_type=skin_analysis_data["skin_type"],
                concerns=skin_analysis_data["concerns"],
                age_range=skin_analysis_data["age_range"],
                additional_observations=skin_analysis_data.get("additional_observations", [])
            )

            # Step 2: Get all products and filter face creams
            logger.info("Step 2: Getting product database...")
            all_products = product_db.get_all_products()
            face_creams = [p for p in all_products if p.category == "face_cream"]

            if not face_creams:
                raise ValueError("No face creams found in product database")

            logger.info(f"Found {len(face_creams)} face creams in database")

            # Convert products to JSON for LLM
            products_json = json.dumps([p.dict() for p in face_creams], indent=2)

            # Step 3: Get recommendations from LLM
            logger.info("Step 3: Getting product recommendations...")
            recommendations_data = await self.llm_service.get_recommendations(
                skin_analysis_data,
                products_json
            )

            if not recommendations_data or "recommendations" not in recommendations_data:
                raise ValueError("Invalid recommendations response from LLM")

            logger.info(f"Received {len(recommendations_data.get('recommendations', []))} recommendations")

            # Step 4: Build response
            recommendations = []
            product_map = {p.id: p for p in face_creams}

            for rec in recommendations_data["recommendations"][:3]:  # Top 3
                product_id = rec.get("product_id")
                if not product_id:
                    logger.warning("Recommendation missing product_id, skipping")
                    continue

                product = product_map.get(product_id)
                if not product:
                    logger.warning(f"Product {product_id} not found in database, skipping")
                    continue

                recommendations.append(ProductRecommendation(
                    product=product,
                    match_score=rec.get("match_score", 0),
                    personalized_reason=rec.get("personalized_reason", "Suitable for your skin type"),
                    key_benefits_for_user=rec.get("key_benefits_for_user", [])
                ))

                # Track recommendation in Redis if available
                if self.redis_client:
                    try:
                        self.redis_client.hincrby("product_recommendations", product.id, 1)
                        logger.debug(f"Tracked recommendation for product {product.id}")
                    except Exception as e:
                        logger.error(f"Redis tracking failed: {str(e)}")

            if not recommendations:
                raise ValueError("No valid recommendations could be generated")

            logger.info(f"Successfully generated {len(recommendations)} recommendations")

            return RecommendationResponse(
                skin_analysis=skin_analysis,
                recommendations=recommendations,
                general_skincare_tips=recommendations_data.get("general_skincare_tips", [])
            )

        except Exception as e:
            logger.error(f"Recommendation process failed: {str(e)}")
            raise

    def get_analytics(self) -> Dict[str, Any]:
        """Get recommendation analytics"""
        if not self.redis_client:
            logger.warning("Redis not available, returning empty analytics")
            return {
                "total_recommendations": 0,
                "product_stats": []
            }

        try:
            # Get all recommendation counts
            counts = self.redis_client.hgetall("product_recommendations")

            # Get product details
            all_products = product_db.get_all_products()
            product_map = {p.id: p for p in all_products}

            product_stats = []
            total = 0

            for product_id, count in counts.items():
                if isinstance(product_id, bytes):
                    product_id = product_id.decode('utf-8')
                count = int(count)
                total += count

                if product_id in product_map:
                    product_stats.append({
                        "product_id": product_id,
                        "product_name": product_map[product_id].name,
                        "recommendation_count": count
                    })

            # Sort by count
            product_stats.sort(key=lambda x: x["recommendation_count"], reverse=True)

            return {
                "total_recommendations": total,
                "product_stats": product_stats
            }
        except Exception as e:
            logger.error(f"Analytics retrieval failed: {str(e)}")
            return {
                "total_recommendations": 0,
                "product_stats": []
            }