"""
数据库基础模块 - 灵感食仓 (InspiLarder)
提供SQLAlchemy基类和通用字段
"""

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import DateTime, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    """
    SQLAlchemy声明式基类
    
    所有数据模型都继承此类，提供:
    - 异步支持 (AsyncAttrs)
    - 自动表名生成
    - 通用时间戳字段
    """
    
    # 允许使用任意类型注解
    type_annotation_map: dict[type, Any] = {
        datetime: DateTime(timezone=True),
    }
    
    def __repr__(self) -> str:
        """默认字符串表示"""
        columns = [f"{col.key}={getattr(self, col.key)}" 
                  for col in self.__table__.columns]
        return f"<{self.__class__.__name__}({', '.join(columns)})>"
    
    def to_dict(self) -> dict:
        """
        将模型实例转换为字典
        
        Returns:
            dict: 包含所有字段的字典
        """
        return {
            column.key: getattr(self, column.key)
            for column in self.__table__.columns
        }


class TimestampMixin:
    """
    时间戳混入类
    
    为模型自动添加创建时间和更新时间字段
    使用方法: class MyModel(Base, TimestampMixin)
    """
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )


class SoftDeleteMixin:
    """
    软删除混入类
    
    为模型添加软删除功能，删除时设置 deleted_at 时间戳
    使用方法: class MyModel(Base, SoftDeleteMixin)
    """
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="删除时间，NULL表示未删除",
    )
    
    @property
    def is_deleted(self) -> bool:
        """检查记录是否已删除"""
        return self.deleted_at is not None
    
    def soft_delete(self) -> None:
        """执行软删除"""
        self.deleted_at = datetime.now(timezone.utc)
    
    def restore(self) -> None:
        """恢复已删除的记录"""
        self.deleted_at = None


# 导出所有基类
__all__ = [
    "Base",
    "TimestampMixin", 
    "SoftDeleteMixin",
]