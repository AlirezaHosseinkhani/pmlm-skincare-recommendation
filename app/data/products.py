from typing import List
from app.models.product import Product, SkinType, SkinConcern

class ProductDatabase:
    @staticmethod
    def get_all_products() -> List[Product]:
        return [
            Product(
                id="prod_001",
                name="HydraGlow Intensive Moisturizer",
                description="Deep hydration face cream with hyaluronic acid and ceramides",
                category="face_cream",
                price=45.99,
                suitable_skin_types=[SkinType.DRY, SkinType.NORMAL, SkinType.SENSITIVE],
                targets_concerns=[SkinConcern.DEHYDRATION, SkinConcern.WRINKLES, SkinConcern.DULLNESS],
                key_ingredients=["Hyaluronic Acid", "Ceramides", "Vitamin E"],
                benefits=["24-hour hydration", "Reduces fine lines", "Strengthens skin barrier"]
            ),
            Product(
                id="prod_002",
                name="ClearBalance Oil Control Cream",
                description="Lightweight mattifying cream for oily and acne-prone skin",
                category="face_cream",
                price=38.99,
                suitable_skin_types=[SkinType.OILY, SkinType.COMBINATION],
                targets_concerns=[SkinConcern.ACNE, SkinConcern.LARGE_PORES, SkinConcern.REDNESS],
                key_ingredients=["Salicylic Acid", "Niacinamide", "Tea Tree Extract"],
                benefits=["Controls excess oil", "Minimizes pores", "Prevents breakouts"]
            ),
            Product(
                id="prod_003",
                name="AgeLess Retinol Night Cream",
                description="Anti-aging night cream with retinol and peptides",
                category="face_cream",
                price=62.99,
                suitable_skin_types=[SkinType.NORMAL, SkinType.DRY, SkinType.COMBINATION],
                targets_concerns=[SkinConcern.WRINKLES, SkinConcern.DARK_SPOTS, SkinConcern.DULLNESS],
                key_ingredients=["Retinol", "Peptides", "Vitamin C"],
                benefits=["Reduces wrinkles", "Evens skin tone", "Boosts collagen production"]
            ),
            Product(
                id="prod_004",
                name="SensiCalm Soothing Cream",
                description="Gentle cream for sensitive and reactive skin",
                category="face_cream",
                price=42.99,
                suitable_skin_types=[SkinType.SENSITIVE, SkinType.DRY],
                targets_concerns=[SkinConcern.REDNESS, SkinConcern.DEHYDRATION],
                key_ingredients=["Centella Asiatica", "Allantoin", "Colloidal Oatmeal"],
                benefits=["Calms irritation", "Reduces redness", "Strengthens sensitive skin"]
            ),
            Product(
                id="prod_005",
                name="BrightGlow Vitamin C Cream",
                description="Brightening cream with stable vitamin C",
                category="face_cream",
                price=48.99,
                suitable_skin_types=[SkinType.NORMAL, SkinType.COMBINATION, SkinType.DRY],
                targets_concerns=[SkinConcern.DARK_SPOTS, SkinConcern.DULLNESS],
                key_ingredients=["Vitamin C", "Kojic Acid", "Alpha Arbutin"],
                benefits=["Brightens complexion", "Fades dark spots", "Antioxidant protection"]
            ),
            Product(
                id="prod_006",
                name="SilkTouch Luxury Hand Cream",
                description="Rich hand cream with shea butter and glycerin",
                category="hand_cream",
                price=22.99,
                suitable_skin_types=[SkinType.DRY, SkinType.NORMAL],
                targets_concerns=[SkinConcern.DEHYDRATION],
                key_ingredients=["Shea Butter", "Glycerin", "Vitamin E"],
                benefits=["Intense moisture", "Non-greasy formula", "Quick absorption"]
            )
        ]

product_db = ProductDatabase()