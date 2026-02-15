"""
API v1 路由配置模块 - 灵感食仓 (InspiLarder)
聚合所有v1版本的路由
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.food import router as food_router
from app.api.v1.location import router as location_router
from app.api.v1.ai import router as ai_router
from app.api.v1.admin import router as admin_router
from app.api.v1.recipe import router as recipe_router

# 创建v1路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(food_router, prefix="/food", tags=["食物管理"])
api_router.include_router(location_router, prefix="/locations", tags=["储存空间"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI识别"])
api_router.include_router(recipe_router, prefix="/recipes", tags=["食谱管理"])
api_router.include_router(admin_router, prefix="/admin", tags=["管理员"])

# 导出
__all__ = ["api_router"]
