from pydantic import BaseModel
from typing import List, Optional
from .product import Product, SkinType, SkinConcern

class SkinAnalysis(BaseModel):
    skin_type: SkinType
    concerns: List[SkinConcern]
    age_range: str
    additional_observations: List[str]

class ProductRecommendation(BaseModel):
    product: Product
    match_score: float
    personalized_reason: str
    key_benefits_for_user: List[str]

class RecommendationResponse(BaseModel):
    skin_analysis: SkinAnalysis
    recommendations: List[ProductRecommendation]
    general_skincare_tips: List[str]