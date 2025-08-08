from fastapi import APIRouter, Depends
from app.models.analytics import AnalyticsResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter()


@router.get("/stats", response_model=AnalyticsResponse)
async def get_recommendation_stats(
        recommendation_service: RecommendationService = Depends(lambda: RecommendationService())
):
    """
    Get analytics on product recommendations

    Returns count of how many times each product has been recommended
    """
    stats = recommendation_service.get_analytics()
    return AnalyticsResponse(**stats)