"""
Pydantic模式包 - 灵感食仓 (InspiLarder)
导出所有请求和响应模式
"""

# 用户相关
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserRegister,
    UserInDB,
    UserResponse,
    UserProfile,
    UserListResponse,
    UserUpdate,
    UserPasswordUpdate,
    Token,
    TokenPayload,
)

# 食物相关
from app.schemas.food import (
    # 枚举
    FOOD_CATEGORIES,
    LOCATION_TYPES,
    UNIT_OPTIONS,
    # 空间
    LocationBase,
    LocationCreate,
    LocationUpdate,
    LocationResponse,
    LocationListResponse,
    # 食物
    FoodItemBase,
    FoodItemCreate,
    FoodItemUpdate,
    FoodItemResponse,
    FoodItemListResponse,
    FoodItemConsumeRequest,
    FoodItemStats,
)

# 导出列表
__all__ = [
    # 用户
    "UserBase",
    "UserCreate",
    "UserRegister",
    "UserLogin",
    "UserInDB",
    "UserResponse",
    "UserProfile",
    "UserListResponse",
    "UserUpdate",
    "UserPasswordUpdate",
    "Token",
    "TokenPayload",
    # 枚举
    "FOOD_CATEGORIES",
    "LOCATION_TYPES",
    "UNIT_OPTIONS",
    # 空间
    "LocationBase",
    "LocationCreate",
    "LocationUpdate",
    "LocationResponse",
    "LocationListResponse",
    # 食物
    "FoodItemBase",
    "FoodItemCreate",
    "FoodItemUpdate",
    "FoodItemResponse",
    "FoodItemListResponse",
    "FoodItemConsumeRequest",
    "FoodItemStats",
]