"""
食物记录模型 - 灵感食仓 (InspiLarder)
定义用户的食物库存记录
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    JSON,
    Float,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.location import Location
    from app.models.user import User


class FoodItem(Base, TimestampMixin):
    """
    食物记录模型
    
    表示用户库存中的单个食物项目，包含名称、数量、保质期等信息
    
    Attributes:
        id: 主键ID
        name: 食物名称
        category: 分类（蔬菜/水果/肉类等）
        icon: 图标
        quantity: 数量
        unit: 单位（个/克/升等）
        expiry_date: 过期日期
        shelf_life_days: 保质期天数
        location_id: 所在空间ID
        storage_advice: 储存建议
        image_path: 图片路径
        thumbnail_path: 缩略图路径
        ai_metadata: AI识别元数据
        ai_confidence: AI识别置信度
        is_opened: 是否已开封
        is_finished: 是否已用完
        finished_at: 用完时间
        tags: 标签
        notes: 备注
        user_id: 所属用户ID
    """
    
    __tablename__ = "food_items"
    __table_args__ = {
        "comment": "食物记录表，管理用户的库存食物"
    }
    
    # 主键
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        comment="食物ID",
    )
    
    # 基本信息
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
        comment="食物名称",
    )
    
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="other",
        index=True,
        comment="分类: vegetable, fruit, meat, seafood, dairy, grain, snack, drink, condiment, other",
    )
    
    icon: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="图标",
    )
    
    # 数量和单位
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("1.00"),
        comment="数量",
    )
    
    unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="个",
        comment="单位: 个, 克, 千克, 升, 毫升, 盒, 瓶, 包, 袋, 其他",
    )
    
    # 位置关联
    location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            "locations.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
        comment="所在空间ID",
    )
    
    # 日期信息
    expiry_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        index=True,
        comment="过期日期",
    )
    
    shelf_life_days: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="保质期天数",
    )
    
    # 储存建议和图片
    storage_advice: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="储存建议",
    )
    
    image_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="图片路径",
    )
    
    thumbnail_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="缩略图路径",
    )
    
    # AI 相关字段
    ai_metadata: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="AI识别元数据",
    )
    
    ai_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="AI识别置信度",
    )
    
    # 状态字段
    is_opened: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否已开封",
    )
    
    is_finished: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否已用完",
    )
    
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="用完时间",
    )
    
    # 标签和备注
    tags: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="标签",
    )
    
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="备注",
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
        back_populates="food_items",
    )
    
    location: Mapped[Optional["Location"]] = relationship(
        "Location",
        back_populates="food_items",
    )
    
    # 计算属性
    @property
    def is_expired(self) -> bool:
        """检查食物是否已过期"""
        if not self.expiry_date:
            return False
        return self.expiry_date < date.today()
    
    @property
    def days_until_expiry(self) -> Optional[int]:
        """计算距离过期的天数"""
        if not self.expiry_date:
            return None
        delta = self.expiry_date - date.today()
        return delta.days
    
    @property
    def expiry_status(self) -> str:
        """
        获取过期状态
        
        Returns:
            str: "expired" | "expiring_soon" | "fresh"
        """
        if self.is_expired:
            return "expired"
        
        days = self.days_until_expiry
        if days is None:
            return "fresh"
        
        # 默认提醒天数为 3 天
        reminder_days = 3
        if days <= reminder_days:
            return "expiring_soon"
        
        return "fresh"
    
    @property
    def category_display(self) -> str:
        """获取分类的显示名称"""
        category_names = {
            "vegetable": "蔬菜",
            "fruit": "水果",
            "meat": "肉类",
            "seafood": "海鲜",
            "dairy": "乳制品",
            "grain": "粮油",
            "snack": "零食",
            "drink": "饮料",
            "condiment": "调味品",
            "other": "其他",
        }
        return category_names.get(self.category, "其他")
    
    def mark_as_finished(self) -> None:
        """标记食物为已用完"""
        self.is_finished = True
        self.finished_at = datetime.now(timezone.utc)
    
    def __str__(self) -> str:
        return f"<FoodItem {self.id}: {self.name} ({self.quantity} {self.unit})>"
    
    def __repr__(self) -> str:
        return (
            f"FoodItem(id={self.id}, "
            f"name='{self.name}', "
            f"quantity={self.quantity}, "
            f"unit='{self.unit}', "
            f"location_id={self.location_id})"
        )