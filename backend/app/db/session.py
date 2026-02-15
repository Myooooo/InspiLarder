"""
数据库会话管理模块 - 灵感食仓 (InspiLarder)
提供异步数据库引擎和会话管理
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.logging import get_logger

# 获取日志记录器
logger = get_logger(__name__)

# 全局引擎实例（延迟初始化）
_engine: Optional[AsyncEngine] = None

# 会话工厂（延迟初始化）
_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


def get_engine() -> AsyncEngine:
    """
    获取或创建数据库引擎（单例模式）
    
    Returns:
        AsyncEngine: 异步数据库引擎实例
    """
    global _engine
    
    if _engine is None:
        logger.info("创建数据库引擎...")
        _engine = create_async_engine(
            settings.DATABASE_URL,  
            echo=getattr(settings, "DB_ECHO", False), 
            pool_size=getattr(settings, "DB_POOL_SIZE", 5),
            max_overflow=getattr(settings, "DB_MAX_OVERFLOW", 10),
            pool_pre_ping=True,  # 连接前ping，检测失效连接
            pool_recycle=3600,   # 连接回收时间（秒）
        )
        logger.info("数据库引擎创建成功")
    
    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """
    获取会话工厂（单例模式）
    
    Returns:
        async_sessionmaker: 异步会话工厂
    """
    global _session_maker
    
    if _session_maker is None:
        engine = get_engine()
        _session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,  # 提交后不过期对象
            autocommit=False,
            autoflush=False,
        )
    
    return _session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    依赖注入函数：获取数据库会话
    
    用于FastAPI的依赖注入系统
    
    Yields:
        AsyncSession: 异步数据库会话
        
    Example:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    上下文管理器：获取数据库会话
    
    用于非依赖注入场景，如后台任务、脚本等
    
    Yields:
        AsyncSession: 异步数据库会话
        
    Example:
        async with get_db_context() as db:
            result = await db.execute(query)
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db() -> None:
    """
    关闭数据库连接池
    
    应在应用关闭时调用
    """
    global _engine, _session_maker
    
    if _engine is not None:
        logger.info("关闭数据库连接...")
        await _engine.dispose()
        _engine = None
        _session_maker = None
        logger.info("数据库连接已关闭")


async def init_db() -> None:
    """
    初始化数据库
    
    创建所有表结构
    """
    from app.db.base import Base
    from app.models import load_all_models
    
    # 加载所有模型以确保表被注册
    load_all_models()
    
    engine = get_engine()
    
    async with engine.begin() as conn:
        # 在开发环境中可以启用这行来重新创建表
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("数据库表结构初始化完成")


# 显式创建 engine 实例供外部导入
engine = get_engine()

# 建议同时也导出 SessionLocal，这是 FastAPI 常见的命名习惯
SessionLocal = get_session_maker()

# 导出
__all__ = [
    "engine",          # 添加这一行
    "SessionLocal",    # 添加这一行
    "get_engine",
    "get_session_maker",
    "get_db",
    "get_db_context",
    "close_db",
    "init_db",
]