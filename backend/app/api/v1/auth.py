"""
认证路由 - 灵感食仓 (InspiLarder)
处理用户注册、登录、登出等认证相关操作
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserRegister,
    UserResponse,
    Token,
    UserLogin,
)
from app.api.deps import get_current_user

# 创建路由
router = APIRouter(tags=["认证"])

# 安全方案
security = HTTPBearer()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="注册新用户账户，邮箱和用户名必须唯一",
)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册",
        )
    
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已被使用",
        )
    
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        is_active=True,
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    from app.models.location import Location
    from app.models.food import FoodItem
    from datetime import date, timedelta
    
    fridge = Location(
        name="冰箱",
        icon="🧊",
        description="家用冰箱",
        level=1,
        sort_order=1,
        user_id=db_user.id,
    )
    db.add(fridge)
    await db.flush()
    
    fridge_cold = Location(
        name="冷藏室",
        icon="🥬",
        description="冰箱冷藏室",
        parent_id=fridge.id,
        level=2,
        sort_order=1,
        user_id=db_user.id,
    )
    fridge_frozen = Location(
        name="冷冻室",
        icon="🧊",
        description="冰箱冷冻室",
        parent_id=fridge.id,
        level=2,
        sort_order=2,
        user_id=db_user.id,
    )
    db.add(fridge_cold)
    db.add(fridge_frozen)
    
    pantry = Location(
        name="储藏室",
        icon="📦",
        description="干货储藏室",
        level=1,
        sort_order=2,
        user_id=db_user.id,
    )
    db.add(pantry)
    await db.flush()
    
    pantry_dry = Location(
        name="干货区",
        icon="🌾",
        description="米面粮油存放区",
        parent_id=pantry.id,
        level=2,
        sort_order=1,
        user_id=db_user.id,
    )
    pantry_condiment = Location(
        name="调料区",
        icon="🧂",
        description="调味品存放区",
        parent_id=pantry.id,
        level=2,
        sort_order=2,
        user_id=db_user.id,
    )
    db.add(pantry_dry)
    db.add(pantry_condiment)
    await db.flush()
    
    today = date.today()
    sample_foods = [
        FoodItem(
            name="新鲜鸡蛋",
            category="dairy",
            icon="🥚",
            quantity=6,
            unit="个",
            expiry_date=today + timedelta(days=14),
            shelf_life_days=14,
            location_id=fridge_cold.id,
            storage_advice="尖端朝下存放更保鲜",
            user_id=db_user.id,
        ),
        FoodItem(
            name="鲜牛奶",
            category="dairy",
            icon="🥛",
            quantity=1,
            unit="升",
            expiry_date=today + timedelta(days=5),
            shelf_life_days=5,
            location_id=fridge_cold.id,
            storage_advice="开封后建议3天内喝完",
            user_id=db_user.id,
        ),
        FoodItem(
            name="红苹果",
            category="fruit",
            icon="🍎",
            quantity=3,
            unit="个",
            expiry_date=today + timedelta(days=7),
            shelf_life_days=7,
            location_id=fridge_cold.id,
            storage_advice="冷藏可延长保鲜期",
            user_id=db_user.id,
        ),
        FoodItem(
            name="新鲜菠菜",
            category="vegetable",
            icon="🥬",
            quantity=300,
            unit="克",
            expiry_date=today + timedelta(days=2),
            shelf_life_days=2,
            location_id=fridge_cold.id,
            storage_advice="洗净后沥干水分保存",
            user_id=db_user.id,
        ),
        FoodItem(
            name="鸡胸肉",
            category="meat",
            icon="🍗",
            quantity=500,
            unit="克",
            expiry_date=today + timedelta(days=3),
            shelf_life_days=3,
            location_id=fridge_cold.id,
            storage_advice="建议冷藏保存，尽快食用",
            user_id=db_user.id,
        ),
        FoodItem(
            name="五常大米",
            category="grain",
            icon="🍚",
            quantity=2,
            unit="千克",
            expiry_date=today + timedelta(days=180),
            shelf_life_days=180,
            location_id=pantry_dry.id,
            storage_advice="密封防潮保存",
            user_id=db_user.id,
        ),
        FoodItem(
            name="生抽酱油",
            category="condiment",
            icon="🧂",
            quantity=1,
            unit="瓶",
            expiry_date=today + timedelta(days=365),
            shelf_life_days=365,
            location_id=pantry_condiment.id,
            storage_advice="避光阴凉处保存",
            user_id=db_user.id,
        ),
    ]
    
    for food in sample_foods:
        db.add(food)
    
    await db.commit()
    
    return db_user


@router.post(
    "/login",
    response_model=Token,
    summary="用户登录",
    description="使用用户名或邮箱和密码登录，返回访问令牌",
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    用户登录

    - **username**: 用户名或邮箱地址
    - **password**: 账户密码

    成功登录后返回 JWT 访问令牌，用于后续 API 请求的认证
    """
    # 查找用户（支持用户名或邮箱登录）
    result = await db.execute(
        select(User).where(
            or_(
                User.username == credentials.username,
                User.email == credentials.username
            )
        )
    )
    user = result.scalar_one_or_none()
    
    # 验证用户存在且密码正确
    if not user or not verify_password(credentials.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查账户是否激活
    if not bool(user.is_active):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用，请联系管理员",
        )
    
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "is_active": bool(user.is_active),
        "is_superuser": user.role == "admin",
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }
    
    # 更新最后登录时间
    from datetime import datetime, timezone
    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    
    # 生成访问令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
        additional_claims={
            "email": user.email,
            "username": user.username,
        },
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": user_data,
    }


@router.post(
    "/logout",
    summary="用户登出",
    description="客户端应删除本地存储的令牌",
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Any:
    """
    用户登出
    
    由于使用 JWT 无状态认证，服务端无需特殊处理。
    客户端应删除本地存储的访问令牌。
    
    可选：将令牌加入黑名单实现主动失效（高级功能）
    """
    # 这里可以添加令牌黑名单逻辑
    # 例如将令牌存入 Redis，设置过期时间
    
    return {
        "message": "登出成功",
        "detail": "请删除客户端存储的访问令牌",
    }


@router.get(
    "/me",
    response_model=UserResponse,
    summary="获取当前用户信息",
    description="获取当前登录用户的详细信息",
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取当前用户信息
    
    返回当前登录用户的详细资料，包括统计数据
    """
    return current_user


@router.post(
    "/refresh",
    response_model=Token,
    summary="刷新访问令牌",
    description="使用现有令牌获取新的访问令牌",
)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    刷新访问令牌
    
    验证现有令牌的有效性，为用户颁发新的访问令牌。
    用于在令牌过期前主动刷新，避免重新登录。
    
    注意：仅当现有令牌仍然有效时才能刷新
    """
    token = credentials.credentials
    
    # 解码现有令牌
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 获取用户ID
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌中未找到用户标识",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 查询用户
    result = await db.execute(
        select(User).where(User.id == int(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成新的访问令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
        additional_claims={
            "email": user.email,
            "username": user.username,
        },
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": user.to_dict(),
    }


# 导出
__all__ = ["router"]