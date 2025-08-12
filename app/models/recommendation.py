from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from enum import Enum
from datetime import date
from .product import Product, SkinType, SkinConcern


class AgeCategory(str, Enum):
    """Standardized age categories for skincare."""
    CHILD = "0-12"
    TEEN = "13-19"
    YOUNG_ADULT = "20-35"
    MATURE = "36-50"
    SENIOR = "50+"


class SkinAnalysis(BaseModel):
    """Detailed analysis of user's skin characteristics."""
    suitable_skin_types: SkinType = Field(..., description="Primary skin type classification")
    targets_concerns: List[SkinConcern] = Field(
        default_factory=list,
        description="Identified skin concerns",
        max_items=5
    )
    age_category: AgeCategory = Field(..., description="Standardized age range")
    secondary_features: List[str] = Field(
        default_factory=list,
        description="Additional observed characteristics"
    )

    @validator('targets_concerns')
    def validate_concerns(cls, v):
        if not v:
            raise ValueError("At least one concern must be identified")
        return list(set(v))  # Remove duplicates


class ProductMatch(BaseModel):
    """Detailed scoring breakdown for a product recommendation."""
    suitable_skin_types: float = Field(..., ge=0, le=30, description="Skin type match score (0-30)")
    concerns: float = Field(..., ge=0, le=50, description="Concerns match score (0-50)")
    age: float = Field(..., ge=0, le=20, description="Age appropriateness score (0-20)")


class ProductRecommendation(BaseModel):
    """Individual product recommendation with justification."""
    product: Product = Field(..., description="Recommended product details")
    match_score: float = Field(..., ge=0, le=100, description="Overall match score (0-100)")
    match_breakdown: ProductMatch = Field(..., description="Detailed scoring breakdown")
    justification: str = Field(..., min_length=20, description="Explanation of suitability")
    expected_benefits: List[str] = Field(
        default_factory=list,
        description="Specific benefits for user's skin"
    )


class RoutineAdvice(BaseModel):
    """Recommended skincare routine steps."""
    morning: List[str] = Field(default_factory=list)
    evening: List[str] = Field(default_factory=list)
    weekly: List[str] = Field(default_factory=list)


class IngredientsGuidance(BaseModel):
    """Ingredient recommendations and warnings."""
    beneficial: List[str] = Field(default_factory=list)
    avoid: List[str] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    """Complete recommendation response package."""
    skin_analysis: SkinAnalysis = Field(..., description="Detailed skin analysis")
    recommendations: List[ProductRecommendation] = Field(
        default_factory=list,
        max_items=3,
        description="Top product matches"
    )
    routine_advice: RoutineAdvice = Field(
        default_factory=RoutineAdvice,
        description="Personalized routine guidance"
    )
    ingredients_guidance: IngredientsGuidance = Field(
        default_factory=IngredientsGuidance,
        description="Ingredient recommendations"
    )


class ProductStat(BaseModel):
    """Product recommendation statistics."""
    product_id: str
    product_name: str
    count: int


class DailyStat(BaseModel):
    """Daily recommendation statistics."""
    date: date
    count: int


class RecommendationAnalytics(BaseModel):
    """Aggregated analytics data."""
    product_stats: List[ProductStat] = Field(default_factory=list)
    daily_stats: List[DailyStat] = Field(default_factory=list)
    total_recommendations: int = 0