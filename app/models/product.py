from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum

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

class Product(BaseModel):
    id: str
    name: str
    description: str
    category: str  # "face_cream" or "hand_cream" or "body_lotion" etc.
    price: float
    suitable_skin_types: List[SkinType]
    targets_concerns: List[SkinConcern]
    key_ingredients: List[str]
    benefits: List[str]
    image_url: Optional[str] = None
    volume: Optional[str] = None
    container_type: Optional[str] = None
    container_material: Optional[str] = None