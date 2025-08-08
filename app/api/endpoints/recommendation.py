from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from typing import Optional
from app.models.recommendation import RecommendationResponse
from app.services.recommendation_service import RecommendationService
from app.services.image_service import ImageService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def get_recommendation_service():
    """Dependency to get recommendation service"""
    return RecommendationService()


@router.post("/analyze", response_model=RecommendationResponse)
async def analyze_and_recommend(
        image: UploadFile = File(...),
        recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Analyze facial image and recommend suitable skincare products

    - **image**: Upload facial image file (JPEG, PNG, WebP - Max 5MB)

    Returns top 3 recommended products with personalized explanations
    """
    try:
        logger.info(f"Received image upload: {image.filename}")

        # Validate and process image
        image_data, temp_url = await ImageService.validate_and_process_image(image)
        logger.info("Image validation and processing completed")

        # Get recommendations
        recommendations = await recommendation_service.get_recommendations(
            image_data=image_data,
            image_url=temp_url
        )

        logger.info("Recommendations generated successfully")
        return recommendations

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )


@router.post("/analyze-url", response_model=RecommendationResponse)
async def analyze_from_url(
        image_url: str = Form(...),
        recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Analyze facial image from URL and recommend suitable skincare products

    - **image_url**: URL to facial image (must be publicly accessible)

    Returns top 3 recommended products with personalized explanations
    """
    try:
        logger.info(f"Processing image from URL: {image_url}")

        # Validate URL format
        if not image_url.startswith(('http://', 'https://')):
            raise HTTPException(
                status_code=400,
                detail="Invalid image URL. Must start with http:// or https://"
            )

        # Validate that URL points to an image
        # is_valid = await ImageService.validate_image_url(image_url)
        # if not is_valid:
        #     raise HTTPException(
        #         status_code=400,
        #         detail="URL does not point to a valid image or is not accessible"
        #     )

        # Get recommendations (no image_data for URL-based requests)
        recommendations = await recommendation_service.get_recommendations(
            image_data=None,
            image_url=image_url
        )

        logger.info("Recommendations generated successfully")
        return recommendations

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )