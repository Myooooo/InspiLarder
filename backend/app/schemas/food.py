"""
食物相关Pydantic模式 - 灵感食仓 (InspiLarder)
定义食物记录和储存空间的请求和响应模型
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============== 枚举值定义 ==============

# 食物分类选项
FOOD_CATEGORIES = [
    ("vegetable", "蔬菜"),
    ("fruit", "水果"),
    ("meat", "肉类"),
    ("seafood", "海鲜"),
    ("dairy", "乳制品"),
    ("grain", "粮油"),
    ("snack", "零食"),
    ("drink", "饮料"),
    ("condiment", "调味品"),
    ("prepared", "成品菜肴"),
    ("cooked_meat", "熟食肉类"),
    ("other", "其他"),
]

# 空间类型选项
LOCATION_TYPES = [
    ("refrigerator", "冰箱"),
    ("freezer", "冷冻室"),
    ("pantry", "储藏室"),
    ("cupboard", "橱柜"),
    ("other", "其他"),
]

# 单位选项
UNIT_OPTIONS = ['个', '克', '千克', '升', '毫升', '盒', '瓶', '包', '袋', '斤', '盘', '碗', '份']


# ============== 储存空间模式 ==============

class LocationBase(BaseModel):
    """储存空间基础模式"""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="空间名称",
        examples=["主冰箱"],
    )
    type: Optional[str] = Field(
        default=None,
        description="空间类型",
        examples=["refrigerator"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="空间描述",
    )
    icon: Optional[str] = Field(
        default="fridge",
        description="图标标识",
    )
    parent_id: Optional[int] = Field(
        default=None,
        description="父级空间ID（创建子空间时使用）",
    )
    
    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid_types = [t[0] for t in LOCATION_TYPES]
        if v not in valid_types:
            raise ValueError(f"无效的空间类型，可选: {valid_types}")
        return v


class LocationCreate(LocationBase):
    """储存空间创建请求"""
    pass


class LocationUpdate(BaseModel):
    """储存空间更新请求"""
    
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    type: Optional[str] = None
    description: Optional[str] = Field(default=None, max_length=500)
    icon: Optional[str] = None
    
    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        """验证空间类型"""
        if v is None:
            return v
        valid_types = [t[0] for t in LOCATION_TYPES]
        if v not in valid_types:
            raise ValueError(f"无效的空间类型，可选: {valid_types}")
        return v


class LocationResponse(BaseModel):
    """储存空间响应模式"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    icon: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    level: int
    sort_order: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    food_count: Optional[int] = None


class LocationListResponse(BaseModel):
    """储存空间列表响应"""
    
    items: list[LocationResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============== 食物记录模式 ==============

class FoodItemBase(BaseModel):
    """食物记录基础模式"""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="食物名称",
        examples=["苹果"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="详细描述",
    )
    quantity: Decimal = Field(
        default=Decimal("1.00"),
        gt=0,
        description="数量",
        examples=[Decimal("2.5")],
    )
    unit: str = Field(
        default="个",
        description="单位",
        examples=["个"],
    )
    category: str = Field(
        default="other",
        description="分类",
        examples=["fruit"],
    )
    location_id: int = Field(
        ...,
        description="所在空间ID",
        examples=[1],
    )
    purchase_date: Optional[date] = Field(
        default=None,
        description="购买日期",
    )
    expiry_date: Optional[date] = Field(
        default=None,
        description="过期日期",
    )
    reminder_days: int = Field(
        default=3,
        ge=0,
        description="提前提醒天数",
    )
    image_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="图片URL",
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="备注",
    )
    icon: Optional[str] = Field(
        default=None,
        max_length=10,
        description="图标emoji",
    )
    
    @field_validator("unit")
    @classmethod
    def validate_unit(cls, v: str) -> str:
        """验证单位"""
        valid_units = UNIT_OPTIONS
        if v not in valid_units:
            raise ValueError(f"无效的单位，可选: {valid_units}")
        return v
    
    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """验证分类"""
        valid_categories = [c[0] for c in FOOD_CATEGORIES]
        if v not in valid_categories:
            raise ValueError(f"无效的分类，可选: {valid_categories}")
        return v


class FoodItemCreate(FoodItemBase):
    """食物记录创建请求"""
    pass


class FoodItemUpdate(BaseModel):
    """食物记录更新请求"""

    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    quantity: Optional[Decimal] = Field(default=None, gt=0)
    unit: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = Field(default=None, max_length=10, description="图标emoji")
    location_id: Optional[int] = None
    purchase_date: Optional[date] = None
    expiry_date: Optional[date] = None
    is_opened: Optional[bool] = None
    is_finished: Optional[bool] = None
    finished_at: Optional[datetime] = None
    reminder_days: Optional[int] = Field(default=None, ge=0)
    image_url: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=2000)
    
    @field_validator("unit")
    @classmethod
    def validate_unit(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if v not in UNIT_OPTIONS:
            raise ValueError(f"无效的单位，可选: {UNIT_OPTIONS}")
        return v
    
    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid_categories = [c[0] for c in FOOD_CATEGORIES]
        if v not in valid_categories:
            raise ValueError(f"无效的分类，可选: {valid_categories}")
        return v


class FoodItemResponse(BaseModel):
    """食物记录响应模式"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    icon: Optional[str] = None
    quantity: Decimal
    unit: str
    location_id: Optional[int] = None
    expiry_date: Optional[date] = None
    shelf_life_days: Optional[int] = None
    storage_advice: Optional[str] = None
    image_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    ai_metadata: Optional[dict] = None
    ai_confidence: Optional[float] = None
    is_opened: bool
    is_finished: bool
    finished_at: Optional[datetime] = None
    tags: Optional[str] = None
    notes: Optional[str] = None
    user_id: int
    created_at: datetime
    updated_at: datetime

    # 计算字段
    is_expired: Optional[bool] = None
    days_until_expiry: Optional[int] = None
    expiry_status: Optional[str] = None
    category_display: Optional[str] = None
    
    # 位置字段
    location_name: Optional[str] = None
    parent_location_name: Optional[str] = None
    location_icon: Optional[str] = None


class FoodItemListResponse(BaseModel):
    """食物记录列表响应"""
    
    items: list[FoodItemResponse]
    total: int
    page: int
    page_size: int
    pages: int


class FoodItemConsumeRequest(BaseModel):
    """标记食物为已消耗请求"""
    
    quantity: Optional[Decimal] = Field(
        default=None,
        gt=0,
        description="消耗数量，不填表示全部消耗",
    )


class FoodItemStats(BaseModel):
    """食物统计信息"""
    
    total_count: int = Field(..., description="总数量")
    expiring_soon_count: int = Field(..., description="即将过期数量")
    expired_count: int = Field(..., description="已过期数量")
    fresh_count: int = Field(..., description="新鲜数量")
    category_distribution: dict[str, int] = Field(..., description="分类分布")
    location_distribution: dict[str, int] = Field(..., description="空间分布")


# 导出
__all__ = [
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