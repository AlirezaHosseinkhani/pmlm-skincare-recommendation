import json
from typing import List, Dict, Any, Optional
from pydantic import ValidationError
from app.models.product import Product
from app.models.recommendation import (
    SkinAnalysis,
    ProductRecommendation,
    RecommendationResponse,
    RecommendationAnalytics
)
from app.services.llm_service import LLMService
from app.data.products import product_db
from app.config import settings
import logging
from datetime import datetime

# Redis import with better error handling
try:
    import redis
    from redis.exceptions import RedisError

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None  # type: ignore
    RedisError = Exception  # type: ignore

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for generating skincare product recommendations based on skin analysis."""

    def __init__(self, llm_service: Optional[LLMService] = None):
        """
        Initialize the recommendation service with optional dependencies.

        Args:
            llm_service: Pre-configured LLMService instance (for testing)
        """
        self.llm_service = llm_service or LLMService()
        self.redis_client = self._init_redis()

    def _init_redis(self) -> Optional[redis.Redis]:  # type: ignore
        """Initialize Redis client if available."""
        if not REDIS_AVAILABLE or not settings.redis_url:
            return None

        try:
            client = redis.from_url(
                settings.redis_url,
                socket_timeout=5,
                socket_connect_timeout=5,
                health_check_interval=30
            )
            client.ping()
            logger.info("Redis connection established")
            return client
        except RedisError as e:
            logger.warning(f"Redis connection failed: {str(e)}")
            return None

    async def get_recommendations(
            self,
            image_data: Optional[bytes] = None,
            image_url: Optional[str] = None,
            user_concerns: Optional[List[str]] = None
    ) -> RecommendationResponse:
        """
        Get personalized skincare recommendations based on facial analysis.

        Args:
            image_data: Raw image bytes
            image_url: URL to fetch image from
            user_concerns: Optional list of user-reported skin concerns

        Returns:
            RecommendationResponse with analysis and product matches

        Raises:
            ValueError: For invalid input or processing errors
            ServiceError: For underlying service failures
        """
        logger.info("Starting recommendation process")

        # Validate input
        if not any([image_data, image_url, user_concerns]):
            raise ValueError("Either image_data, image_url or user_concerns must be provided")

        try:
            # Step 1: Analyze skin (if image provided)
            skin_analysis = await self._analyze_skin(image_data, image_url, user_concerns)

            # Step 2: Get filtered products
            face_creams = self._get_filtered_products(skin_analysis)

            # Step 3: Get recommendations
            recommendations_data = await self._get_llm_recommendations(skin_analysis, face_creams)

            # Step 4: Build and validate response
            return self._build_response(skin_analysis, recommendations_data, face_creams)

        except ValidationError as e:
            logger.error(f"Data validation failed: {str(e)}")
            raise ValueError("Invalid data received from services") from e
        except Exception as e:
            logger.error(f"Recommendation process failed: {str(e)}")
            raise ServiceError("Recommendation service unavailable") from e

    async def _analyze_skin(
            self,
            image_data: Optional[bytes],
            image_url: Optional[str],
            user_concerns: Optional[List[str]]
    ) -> SkinAnalysis:
        """Perform skin analysis using image and/or user concerns."""
        analysis_data = {}

        if image_data or image_url:
            logger.info("Performing visual skin analysis...")
            analysis_data = await self.llm_service.analyze_skin(
                image_data=image_data,
                image_url=image_url
            )

        # Merge with user-reported concerns if provided
        # if user_concerns:
        #     analysis_data["concerns"] = list(set(
        #         analysis_data.get("concerns", []) + user_concerns
        #     ))

        return SkinAnalysis(**analysis_data)

    def _get_filtered_products(self, skin_analysis: SkinAnalysis) -> List[Product]:
        """Get products filtered by analysis criteria."""
        all_products = product_db.get_all_products()

        return [
            p for p in all_products
            if (p.category == "face_cream" and
                skin_analysis.skin_type in p.suitable_skin_types and
                any(c in p.targets_concerns for c in skin_analysis.concerns))
        ]

    async def _get_llm_recommendations(
            self,
            skin_analysis: SkinAnalysis,
            products: List[Product]
    ) -> Dict[str, Any]:
        """Get recommendations from LLM service."""
        products_json = json.dumps([p.dict() for p in products], indent=2)
        return await self.llm_service.get_recommendations(
            skin_analysis.dict(),
            products_json
        )

    def _build_response(
            self,
            skin_analysis: SkinAnalysis,
            recommendations_data: Dict[str, Any],
            available_products: List[Product]
    ) -> RecommendationResponse:
        """Build and validate the final response."""
        product_map = {p.id: p for p in available_products}
        recommendations = []

        for rec in recommendations_data.get("recommendations", [])[:3]:
            if not rec.get("product_id"):
                continue

            product = product_map.get(rec["product_id"])
            if not product:
                continue

            recommendations.append(ProductRecommendation(
                product=product,
                match_score=min(max(rec.get("match_score", 0), 0), 100),
                personalized_reason=rec.get("personalized_reason", ""),
                key_benefits_for_user=rec.get("key_benefits_for_user", [])
            ))

            self._track_recommendation(product.id)

        return RecommendationResponse(
            skin_analysis=skin_analysis,
            recommendations=recommendations,
            general_skincare_tips=recommendations_data.get("general_skincare_tips", []),
            routine_advice=recommendations_data.get("routine_advice", {}),
            ingredients_guidance=recommendations_data.get("ingredients_guidance", {})
        )

    def _track_recommendation(self, product_id: str) -> None:
        """Track recommendation in analytics (Redis)."""
        if not self.redis_client:
            return

        try:
            with self.redis_client.pipeline() as pipe:
                pipe.hincrby("product_recommendations", product_id, 1)
                pipe.zincrby("recommendations_by_date", 1, datetime.today().strftime("%Y-%m-%d"))
                pipe.execute()
        except RedisError as e:
            logger.error(f"Failed to track recommendation: {str(e)}")

    def get_analytics(self) -> RecommendationAnalytics:
        """Get recommendation analytics data."""
        if not self.redis_client:
            return RecommendationAnalytics()

        try:
            counts = self.redis_client.hgetall("product_recommendations")
            date_stats = self.redis_client.zrange(
                "recommendations_by_date",
                0, -1,
                withscores=True
            )

            return RecommendationAnalytics(
                product_stats=self._parse_product_counts(counts),
                daily_stats=self._parse_date_stats(date_stats)
            )
        except RedisError as e:
            logger.error(f"Analytics retrieval failed: {str(e)}")
            return RecommendationAnalytics()

    def _parse_product_counts(self, counts: Dict) -> List[Dict[str, Any]]:
        """Parse Redis product count data."""
        all_products = product_db.get_all_products()
        product_map = {p.id: p for p in all_products}

        return sorted([
            {
                "product_id": pid.decode() if isinstance(pid, bytes) else pid,
                "product_name": product_map[pid].name,
                "count": int(count)
            }
            for pid, count in counts.items()
            if pid in product_map
        ], key=lambda x: x["count"], reverse=True)

    def _parse_date_stats(self, date_stats: List) -> List[Dict[str, Any]]:
        """Parse Redis date-based statistics."""
        return [
            {
                "date": date.decode() if isinstance(date, bytes) else date,
                "count": int(count)
            }
            for date, count in date_stats
        ]


class ServiceError(Exception):
    """Custom exception for recommendation service errors."""
    pass