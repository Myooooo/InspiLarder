"""
储存空间模型 - 灵感食仓 (InspiLarder)
定义用户的储存空间（冰箱、橱柜等）
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.food import FoodItem
    from app.models.user import User


class Location(Base, TimestampMixin):
    """
    储存空间模型
    
    表示用户的物理储存空间，如冰箱、橱柜、储藏室等
    
    Attributes:
        id: 主键ID
        name: 空间名称
        icon: 图标标识
        description: 描述信息
        parent_id: 父级空间ID（支持二级目录）
        level: 层级（1=一级，2=二级）
        sort_order: 排序顺序
        user_id: 所属用户ID
    """
    
    __tablename__ = "locations"
    __table_args__ = {
        "comment": "储存空间表，管理用户的物理储存位置"
    }
    
    # 主键
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        comment="空间ID",
    )
    
    # 基本信息
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="空间名称，如'主冰箱'",
    )
    
    icon: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        default="📦",
        comment="图标标识",
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="描述信息",
    )
    
    # 层级结构（支持二级目录）
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            "locations.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
        comment="父级空间ID",
    )
    
    level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="层级：1=一级，2=二级",
    )
    
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="排序顺序",
    )

    # 外键关联 - 使用 user_id 匹配数据库表结构
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
        back_populates="locations",
    )
    
    food_items: Mapped[list["FoodItem"]] = relationship(
        "FoodItem",
        back_populates="location",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="FoodItem.expiry_date",
    )
    
    # 自引用关系 - 父子层级
    parent: Mapped[Optional["Location"]] = relationship(
        "Location",
        remote_side=[id],
        back_populates="children",
    )
    
    children: Mapped[list["Location"]] = relationship(
        "Location",
        back_populates="parent",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    
    # 常用查询属性
    @property
    def food_count(self) -> int:
        """当前空间中的食物数量"""
        return len(self.food_items) if self.food_items else 0
    
    @property
    def is_root(self) -> bool:
        """是否为根级空间"""
        return self.parent_id is None
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "description": self.description,
            "type": getattr(self, 'type', None),
            "parent_id": self.parent_id,
            "level": self.level,
            "sort_order": self.sort_order,
            "user_id": self.user_id,
            "owner_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "food_count": self.food_count,
        }

    def __str__(self) -> str:
        return f"<Location {self.id}: {self.name}>"

    def __repr__(self) -> str:
        return (
            f"Location(id={self.id}, "
            f"name='{self.name}', "
            f"user_id={self.user_id})"
        )