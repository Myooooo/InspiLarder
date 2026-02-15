"""
服务层模块 - 灵感食仓 (InspiLarder)
导出所有服务类
"""

from app.services.ai_service import (
    AIService,
    ai_service,
    FoodRecognitionResult,
    RecipeRecommendation,
)
from app.services.image_service import (
    ImageService,
    image_service,
    ImageProcessingError,
)

__all__ = [
    # AI服务
    "AIService",
    "ai_service",
    "FoodRecognitionResult",
    "RecipeRecommendation",
    # 图片服务
    "ImageService",
    "image_service",
    "ImageProcessingError",
]