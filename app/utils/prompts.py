import json
from typing import Dict, List

def get_skin_analysis_prompt() -> str:
        """Generate prompt for comprehensive skin analysis"""
        return """You are an expert dermatologist with 20 years of experience in skin analysis and skincare recommendations. 
Analyze the provided facial image with professional precision and identify:

1. **Skin Type**: Classify as one of: dry, oily, combination, sensitive, normal
2. **Primary Concerns**: Identify up to 3 most prominent concerns from:
   - acne
   - wrinkles
   - dark_spots
   - redness
   - dullness
   - large_pores
   - dehydration
   - eczema
   - sensitivity
   - anti_aging
   - anti_oxidant
3. **Secondary Features**: Note any other relevant characteristics such as:
   - blackheads
   - whiteheads
   - rosacea
   - hyperpigmentation
   - dark_circles
   - puffiness
   - loss_of_elasticity
   - rough_texture
   - flakiness
4. **Age Category**: Categorize as: [0-12, 13-19, 20-35, 36-50, 50+]

Provide analysis in this exact JSON format:
{
    "suitable_skin_types": "dry/oily/combination/sensitive/normal",
    "targets_concerns": ["max 3 main concerns from predefined list"],
    "secondary_features": ["any additional observations"],
    "age_category": "0-12/13-19/20-35/36-50/50+"
}

Guidelines:
- Be conservative in assessments
- Only note clearly visible characteristics
- Use exact enum values provided
- For age: Prefer broader categories when uncertain
- For concerns: List by severity (most severe first)"""

def get_product_recommendation_prompt(skin_analysis: Dict, products: List[Dict]) -> str:
    """Generate prompt for product recommendations"""
    return f"""As a dermatologist, recommend products from our database that best match this skin profile:
```json
{json.dumps(skin_analysis, indent=2)}
{json.dumps(products[:3], indent=2)}
[showing first 3 of {len(products)} total products]

Generate recommendations with:
1. Match score (50-100) based on:
   - Skin type alignment (30% weight)
   - Primary concern targeting (50% weight)
   - Age appropriateness (20% weight)
2. Clear justification for each recommendation
3. Specific benefits for user's concerns
4. Ingredient compatibility analysis

Required Output (JSON):
{{
    "recommendations": [
        {{
            "product_id": "id",
            "match_score": 75,
            "match_breakdown": {{
                "suitable_skin_types": score/30,
                "concerns": score/50,
                "age": score/20
            }},
            "justification": "Concise explanation of suitability",
            "expected_benefits": ["Benefit 1", "Benefit 2"],
            "ingredient_analysis": {{
                "effective_ingredients": ["ing1", "ing2"],
                "potential_irritants": ["ing1", "ing2"]
            }}
        }}
    ],
    "skincare_routine_advice": {{
        "morning": ["Step 1 with timing", "Step 2 with timing"],
        "evening": ["Step 1 with timing", "Step 2 with timing"],
        "weekly": ["Special treatment with frequency"]
    }},
    "ingredients_to_look_for": ["List of beneficial ingredients"],
    "ingredients_to_avoid": ["List of potentially problematic ingredients"],
    "lifestyle_tips": ["Relevant lifestyle adjustment"]
}}

Additional Rules:
- Never recommend more than 3 products
- If no good matches exist, return empty recommendations with explanation
- Prioritize products that target multiple concerns
- Consider product price/quality ratio
- Flag any potential irritants for sensitive skin
- Include usage frequency recommendations"""

    @staticmethod
    def get_followup_questions(skin_analysis: Dict) -> str:
        """Generate follow-up questions to refine analysis"""
        return f"""Based on this initial skin analysis:
```json
{json.dumps(skin_analysis, indent=2)}"""