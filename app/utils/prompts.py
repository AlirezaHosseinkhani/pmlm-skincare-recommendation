def get_skin_analysis_prompt() -> str:
    return """You are an expert dermatologist with 20 years of experience in skin analysis and skincare recommendations. 
Analyze the provided facial image with professional precision and identify:

1. **Skin Type**: Determine if the skin is dry, oily, combination, sensitive, or normal
2. **Skin Concerns**: Identify visible concerns such as:
   - Acne or blemishes
   - Fine lines or wrinkles
   - Dark spots or hyperpigmentation
   - Redness or irritation
   - Dullness or uneven texture
   - Large or visible pores
   - Dehydration signs

3. **Age Range**: Estimate the approximate age range (e.g., "20-30", "30-40", etc.)
4. **Additional Observations**: Note any other relevant skin characteristics

Provide your analysis in the following JSON format:
{
    "skin_type": "one of: dry, oily, combination, sensitive, normal",
    "concerns": ["list of identified concerns from the options above"],
    "age_range": "estimated age range",
    "additional_observations": ["any other relevant observations about the skin"]
}

Be thorough but realistic in your assessment. Focus on clearly visible characteristics."""

def get_product_recommendation_prompt(skin_analysis: dict, products: list) -> str:
    return f"""Based on the following skin analysis:
- Skin Type: {skin_analysis['skin_type']}
- Concerns: {', '.join(skin_analysis['concerns'])}
- Age Range: {skin_analysis['age_range']}
- Additional Observations: {', '.join(skin_analysis['additional_observations'])}

Review these skincare products and recommend the TOP 3 most suitable face creams:

Products Database:
{products}

For each recommended product, provide:
1. A match score (0-100) based on how well it addresses the user's skin needs
2. A personalized explanation of why this product is suitable for their specific skin
3. Key benefits that directly address their concerns

Also provide 3 general skincare tips based on their skin analysis.

Return your recommendations in this JSON format:
{{
    "recommendations": [
        {{
            "product_id": "product id",
            "match_score": 85,
            "personalized_reason": "This cream is perfect for your skin because...",
            "key_benefits_for_user": ["Benefit 1 specific to user", "Benefit 2 specific to user"]
        }}
    ],
    "general_skincare_tips": ["Tip 1", "Tip 2", "Tip 3"]
}}"""