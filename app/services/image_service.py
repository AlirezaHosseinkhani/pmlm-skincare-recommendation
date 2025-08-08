import io
import uuid
import os
from typing import Optional, Tuple
from PIL import Image
import httpx
from fastapi import UploadFile, HTTPException
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ImageService:
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_FORMATS = {"image/jpeg", "image/jpg", "image/png", "image/webp"}

    @staticmethod
    async def validate_and_process_image(file: UploadFile) -> Tuple[bytes, Optional[str]]:
        """
        Validate and process uploaded image file
        Returns: (image_bytes, temporary_url_if_needed)
        """
        logger.info(f"Processing uploaded file: {file.filename}, content_type: {file.content_type}")

        # Check file type
        if file.content_type not in ImageService.ALLOWED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(ImageService.ALLOWED_FORMATS)}"
            )

        # Read file
        contents = await file.read()
        logger.info(f"File size: {len(contents)} bytes")

        # Check file size
        if len(contents) > ImageService.MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {ImageService.MAX_IMAGE_SIZE / 1024 / 1024}MB"
            )

        # Validate it's actually an image
        try:
            image = Image.open(io.BytesIO(contents))
            logger.info(f"Image dimensions: {image.width}x{image.height}, format: {image.format}")

            # Resize if too large
            max_dimension = 1024
            if image.width > max_dimension or image.height > max_dimension:
                logger.info(f"Resizing image from {image.width}x{image.height}")
                image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                logger.info(f"Resized to {image.width}x{image.height}")

            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Convert back to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=85)
            contents = img_byte_arr.getvalue()

            logger.info(f"Processed image size: {len(contents)} bytes")

        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Generate temporary URL for custom LLM if needed
        temporary_url = None
        if settings.primary_llm_provider == "custom":
            temporary_url = await ImageService.upload_to_temporary_storage(contents)

        return contents, temporary_url

    @staticmethod
    async def upload_to_temporary_storage(image_data: bytes) -> str:
        """
        Upload image to temporary storage and return URL
        In production, use cloud storage like AWS S3, Google Cloud Storage, etc.
        For development, we'll use a simple local file server
        """
        try:
            # Create temp directory if it doesn't exist
            temp_dir = "temp_images"
            os.makedirs(temp_dir, exist_ok=True)

            # Generate unique filename
            filename = f"{uuid.uuid4()}.jpg"
            filepath = os.path.join(temp_dir, filename)

            # Save image to temp location
            with open(filepath, 'wb') as f:
                f.write(image_data)

            # Return URL (you'll need to serve this directory)
            # In production, this would be your cloud storage URL
            base_url = getattr(settings, 'temp_image_base_url', 'http://localhost:8000/temp_images')
            temp_url = f"{base_url}/{filename}"

            logger.info(f"Image uploaded to temporary storage: {temp_url}")
            return temp_url

        except Exception as e:
            logger.error(f"Failed to upload to temporary storage: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to process image for custom LLM provider"
            )

    @staticmethod
    async def validate_image_url(image_url: str) -> bool:
        """Validate that the URL points to a valid image"""
        try:
            async with httpx.AsyncClient() as client:
                # Just check headers first
                response = await client.head(image_url, timeout=10.0)
                response.raise_for_status()

                # Check content type
                content_type = response.headers.get('content-type', '').lower()
                valid_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']

                if not any(img_type in content_type for img_type in valid_types):
                    return False

                return True

        except Exception as e:
            logger.error(f"Failed to validate image URL: {str(e)}")
            return False

    @staticmethod
    async def download_image_from_url(image_url: str) -> bytes:
        """Download image from URL and return bytes"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=30.0)
                response.raise_for_status()

                # Validate content type
                content_type = response.headers.get('content-type', '')
                if not any(allowed in content_type.lower() for allowed in
                           ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']):
                    raise HTTPException(status_code=400, detail="URL does not point to a valid image")

                image_data = response.content

                # Validate it's actually an image
                try:
                    image = Image.open(io.BytesIO(image_data))
                    logger.info(f"Downloaded image: {image.width}x{image.height}, format: {image.format}")
                except Exception:
                    raise HTTPException(status_code=400, detail="Downloaded content is not a valid image")

                return image_data

        except httpx.HTTPError as e:
            logger.error(f"Failed to download image from URL: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to download image from URL: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing image URL: {str(e)}")
            raise HTTPException(status_code=500, detail="Error processing image URL")