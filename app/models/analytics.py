from pydantic import BaseModel
from typing import Dict, List


class ProductAnalytics(BaseModel):
    product_id: str
    product_name: str
    recommendation_count: int

class AnalyticsResponse(BaseModel):
    total_recommendations: int
    product_stats: List[ProductAnalytics]