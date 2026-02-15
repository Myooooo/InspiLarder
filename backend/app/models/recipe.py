"""
食谱模型 - 灵感食仓 (InspiLarder)
存储用户生成的食谱记录
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Recipe(Base, TimestampMixin):
    """
    食谱模型
    
    存储用户通过AI生成的食谱，支持分类（快手晚餐、消耗临期、创意混搭）
    
    Attributes:
        id: 主键ID
        name: 食谱名称
        description: 食谱描述
        ingredients: 食材列表（JSON格式）
        steps: 烹饪步骤（JSON格式）
        cooking_time: 烹饪时间（分钟）
        difficulty: 难度级别
        servings: 份数
        tags: 标签列表
        category: 分类（quick-快手晚餐, expiring-消耗临期, creative-创意混搭）
        user_id: 所属用户ID
    """
    
    __tablename__ = "recipes"
    __table_args__ = {
        "comment": "食谱表，存储用户生成的AI食谱"
    }
    
    # 主键
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        comment="食谱ID",
    )
    
    # 基本信息
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
        comment="食谱名称",
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="食谱描述",
    )
    
    # 食材和步骤（JSON格式存储）
    ingredients: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True,
        comment="食材列表",
    )
    
    steps: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True,
        comment="烹饪步骤",
    )
    
    # 烹饪信息
    cooking_time: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="烹饪时间（分钟）",
    )
    
    difficulty: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="难度：简单/中等/困难",
    )
    
    servings: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=2,
        comment="份数",
    )
    
    tags: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True,
        comment="标签列表",
    )
    
    # 分类
    category: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="分类：quick-快手晚餐, expiring-消耗临期, creative-创意混搭",
    )
    
    # 外键关联
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
        comment="所属用户ID",
    )
    
    # 关系定义
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="recipes",
    )
    
    def __str__(self) -> str:
        return f"<Recipe {self.id}: {self.name}>"
    
    def __repr__(self) -> str:
        return f"Recipe(id={self.id}, name='{self.name}', category='{self.category}')"
