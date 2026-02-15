"""
数据模型包 - 灵感食仓 (InspiLarder)
导出所有SQLAlchemy模型
"""

# 先导入基类
from app.db.base import Base

# 按依赖顺序导入模型
from app.models.user import User
from app.models.location import Location
from app.models.food import FoodItem
from app.models.recipe import Recipe

# 导出列表
__all__ = [
    "Base",
    "User",
    "Location",
    "FoodItem",
    "Recipe",
]


def load_all_models() -> None:
    """
    加载所有模型模块
    
    确保所有模型类被导入，以便 SQLAlchemy 正确注册表结构
    在初始化数据库时调用
    """
    # 由于上面已经导入了所有模型，这里不需要额外操作
    # 但为了代码清晰，保留此函数
    pass