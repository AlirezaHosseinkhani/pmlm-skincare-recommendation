from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Literal
from enum import Enum


# ========== ENUMS FOR ALL AVAILABLE OPTIONS ==========
class SkinType(str, Enum):
    DRY = "dry"
    OILY = "oily"
    COMBINATION = "combination"
    SENSITIVE = "sensitive"
    NORMAL = "normal"


class SkinConcern(str, Enum):
    ACNE = "acne"
    WRINKLES = "wrinkles"
    DARK_SPOTS = "dark_spots"
    REDNESS = "redness"
    DULLNESS = "dullness"
    LARGE_PORES = "large_pores"
    DEHYDRATION = "dehydration"
    ECZEMA = "eczema"
    SENSITIVITY = "sensitivity"
    MOISTURIZATION = "moisturization"
    ANTI_AGING = "anti_aging"
    ANTI_OXIDANT = "anti_oxidant"


class AgeCategory(str, Enum):
    TEEN = "13-19"
    YOUNG_ADULT = "20-35"
    MATURE = "36-50"
    SENIOR = "50+"


# class ProductCategory(str, Enum):
#     FACE_CREAM = "face_cream"
#     EYE_CREAM = "eye_cream"
#     FACE_WASH = "face_wash"
#     FACE_MASK = "face_mask"
#     HAND_CREAM = "hand_cream"
#     BODY_LOTION = "body_lotion"
#     FACE_SERUM = "face_serum"
#     SUNSCREEN = "sunscreen"
#     CHEMICAL_EXFOLIANT = "chemical_exfoliant"
#     NECK_CREAM = "neck_cream"
#     LIP_BALM = "lip_balm"
#     FACIAL_MIST = "facial_mist"
#     BB_CREAM = "bb_cream"
#     FACE_SCRUB = "face_scrub"
#     FACE_OIL = "face_oil"
#     AFTER_SHAVE = "after_shave"
#     LASH_SERUM = "lash_serum"
#     TINTED_MOISTURIZER = "tinted_moisturizer"
#     BODY_SCRUB = "body_scrub"
#     NIGHT_CREAM = "night_cream"
#     TONER = "toner"


# class ContainerType(str, Enum):
#     TUBE = "tube"
#     BOTTLE = "bottle"
#     JAR = "jar"
#     PUMP = "pump"
#     DROPPER = "dropper"
#     ROLLER = "roller"
#     STICK = "stick"
#     SPRAY = "spray"
#     PAD = "pad"
#     SHEET = "sheet"
#     AMPOULE = "ampoule"


# class ContainerMaterial(str, Enum):
#     PLASTIC = "plastic"
#     GLASS = "glass"
#     METAL = "metal"
#     CERAMIC = "ceramic"


# ========== CORE MODELS ==========
class SkinAnalysis(BaseModel):
    """Comprehensive skin analysis with all possible parameters from dataset"""
    skin_type: SkinType = Field(
        ...,
        description="Primary skin type from: dry, oily, combination, sensitive, normal"
    )

    primary_concerns: List[SkinConcern] = Field(
        ...,
        min_items=1,
        max_items=3,
        description="Main skin concerns from: "
                    "acne, wrinkles, dark_spots, redness, dullness, "
                    "large_pores, dehydration, eczema, sensitivity, "
                    "moisturization, anti_aging, anti_oxidant"
    )

    secondary_features: List[Literal[
        "enlarged_pores",
        "blackheads",
        "whiteheads",
        "rosacea",
        "hyperpigmentation",
        "melasma",
        "dark_circles",
        "puffiness",
        "loss_of_elasticity",
        "rough_texture",
        "flakiness",
        "oiliness",
        "shine"
    ]] = Field(
        default_factory=list,
        description="Additional observed skin characteristics"
    )

    age_category: AgeCategory = Field(
        ...,
        description="Age range category from: "
                    "teen (13-19), young_adult (20-35), "
                    "mature (36-50), senior (50+)"
    )

    @validator('primary_concerns')
    def validate_concerns(cls, v):
        if not v:
            raise ValueError("At least one primary concern must be identified")
        return list(set(v))  # Remove duplicates


class ProductRecommendation(BaseModel):
    """Complete product recommendation with all available fields"""
    product: 'Product' = Field(..., description="Recommended product")

    match_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Overall match score (0-100)"
    )

    match_breakdown: Dict[str, float] = Field(
        ...,
        description="Detailed scoring breakdown including: "
                    "skin_type_match, concerns_match, age_match, "
                    "ingredient_compatibility"
    )

    personalized_reason: str = Field(
        ...,
        min_length=20,
        description="Detailed explanation of why this product is recommended"
    )

    key_benefits: List[str] = Field(
        ...,
        min_items=2,
        description="Specific benefits for user's skin type and concerns"
    )

    usage_instructions: Optional[str] = Field(
        None,
        description="Recommended usage instructions for this user"
    )

    compatibility_warnings: Optional[List[str]] = Field(
        None,
        description="Any potential compatibility warnings"
    )


class Product(BaseModel):
    """Complete product model with all available fields from dataset"""
    id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., min_length=2, description="Product name")
    description: str = Field(..., min_length=10, description="Detailed description")

    # category: ProductCategory = Field(
    #     ...,
    #     description="Product category from available options"
    # )

    price: float = Field(..., gt=0, description="Price in Iranian Rial")

    suitable_skin_types: List[SkinType] = Field(
        ...,
        min_items=1,
        description="Compatible skin types: dry, oily, combination, sensitive, normal"
    )

    targets_concerns: List[SkinConcern] = Field(
        ...,
        min_items=1,
        description="Targeted skin concerns from full list"
    )

    key_ingredients: List[str] = Field(
        ...,
        min_items=3,
        description="Active/main ingredients"
    )

    benefits: List[str] = Field(
        ...,
        min_items=2,
        description="Primary benefits of the product"
    )

    volume: Optional[str] = Field(
        None,
        description="Product volume/weight (e.g., 50ml, 100g)"
    )
    #
    # container_type: Optional[ContainerType] = Field(
    #     None,
    #     description="Container type from available options"
    # )
    #
    # container_material: Optional[ContainerMaterial] = Field(
    #     None,
    #     description="Container material from available options"
    # )

    image_url: Optional[str] = Field(
        None,
        description="URL to product image"
    )

    is_vegan: Optional[bool] = Field(
        None,
        description="Whether the product is vegan"
    )

    is_cruelty_free: Optional[bool] = Field(
        None,
        description="Whether the product is cruelty-free"
    )

    @validator('price')
    def round_price(cls, v):
        return round(v, 2)


class RecommendationResponse(BaseModel):
    """Complete recommendation response with all possible fields"""
    skin_analysis: SkinAnalysis = Field(..., description="Detailed skin analysis")

    recommendations: List[ProductRecommendation] = Field(
        ...,
        min_items=1,
        max_items=3,
        description="Top product recommendations"
    )

    general_skincare_tips: List[str] = Field(
        ...,
        min_items=3,
        description="Personalized skincare advice"
    )

    routine_suggestions: Dict[
        Literal["morning", "evening", "weekly"],
        List[str]
    ] = Field(
        ...,
        description="Suggested skincare routines"
    )

    ingredients_to_seek: List[str] = Field(
        ...,
        min_items=2,
        description="Beneficial ingredients for user's skin"
    )

    ingredients_to_avoid: Optional[List[str]] = Field(
        None,
        description="Ingredients that may irritate user's skin"
    )

    seasonal_advice: Optional[str] = Field(
        None,
        description="Season-specific skincare recommendations"
    )


# Fix forward reference
ProductRecommendation.update_forward_refs()