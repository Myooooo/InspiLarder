"""
管理员路由 - 灵感食仓 (InspiLarder)
处理管理员专属功能：用户管理、系统统计等
"""

from typing import Any, List, Optional
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import get_password_hash
from app.models.food import FoodItem
from app.models.location import Location
from app.models.user import User

# 获取日志记录器
logger = get_logger(__name__)

# 创建路由
router = APIRouter(tags=["管理员"], prefix="/admin")


# ============== 请求/响应模式 ==============

class UserCreateRequest(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    email: Optional[str] = Field(default=None, max_length=100, description="邮箱")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    role: str = Field(default="user", description="角色: admin/user")
    nickname: Optional[str] = Field(default=None, max_length=50, description="昵称")
    is_active: bool = Field(default=True, description="是否激活")
    
    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ["admin", "user"]:
            raise ValueError("角色必须是 admin 或 user")
        return v


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: Optional[str]
    role: str
    is_active: bool
    nickname: Optional[str]
    avatar: Optional[str]
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""
    items: List[UserResponse]
    total: int
    page: int
    page_size: int
    pages: int


class SystemStatsResponse(BaseModel):
    """系统统计响应"""
    total_users: int
    total_food_items: int
    total_locations: int
    active_users_7d: int
    new_users_7d: int
    food_items_added_7d: int
    food_items_expiring_7d: int
    storage_stats: dict


class UserStatsResponse(BaseModel):
    """单个用户统计响应"""
    user_id: int
    username: str
    total_food_items: int
    total_locations: int
    expiring_soon: int
    expired: int
    recently_added: int
    recently_consumed: int


# ============== API端点 ==============

@router.get(
    "/users",
    response_model=UserListResponse,
    summary="获取用户列表",
    description="获取所有用户的列表（管理员专属）",
)
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索用户名或邮箱"),
    role: Optional[str] = Query(None, description="按角色筛选"),
    is_active: Optional[bool] = Query(None, description="按状态筛选"),
) -> Any:
    """
    获取用户列表（管理员专属）
    
    返回系统中所有用户的基本信息，支持分页和筛选。
    只有管理员角色可以访问此接口。
    """
    # 检查是否为管理员
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    
    # 构建查询
    query = select(User)
    
    # 应用筛选条件
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern),
            )
        )
    
    if role:
        query = query.where(User.role == role)
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(User.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    # 计算总页数
    pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return {
        "items": users,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
    description="创建新用户账户（管理员专属）",
)
async def create_user(
    user_data: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    创建用户（管理员专属）
    
    创建新的用户账户，可以指定角色为普通用户或管理员。
    只有管理员角色可以访问此接口。
    """
    # 检查是否为管理员
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    
    # 检查用户名是否已存在
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已被使用",
        )
    
    # 检查邮箱是否已注册
    if user_data.email:
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注册",
            )
    
    # 创建新用户
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        nickname=user_data.nickname or user_data.username,
        is_active=user_data.is_active,
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # 为新用户创建示例存储空间和食材
    
    # 创建冰箱及其子空间
    fridge = Location(
        name="冰箱",
        icon="🧊",
        description="智能冰箱",
        level=1,
        sort_order=1,
        user_id=db_user.id,
    )
    db.add(fridge)
    await db.flush()
    
    fridge_cold = Location(
        name="冷藏室",
        icon="❄️",
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
    
    logger.info(f"管理员 {current_user.username} 创建了新用户 {db_user.username}，并添加了示例数据")
    
    return db_user


@router.get(
    "/users/{user_id}/stats",
    response_model=UserStatsResponse,
    summary="获取用户统计",
    description="获取指定用户的详细统计信息",
)
async def get_user_stats(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取用户统计（管理员专属）
    
    返回指定用户的食物库存统计，包括总数、即将过期、已过期等。
    """
    # 检查是否为管理员
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    
    # 查询用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    
    # 获取用户统计
    
    # 总食物数
    result = await db.execute(
        select(func.count()).where(
            and_(FoodItem.user_id == user_id, FoodItem.is_finished == False)
        )
    )
    total_food_items = result.scalar()
    
    # 空间数
    result = await db.execute(
        select(func.count()).where(Location.user_id == user_id)
    )
    total_locations = result.scalar()
    
    # 即将过期（3天内）
    expiring_soon_date = date.today() + timedelta(days=3)
    result = await db.execute(
        select(func.count()).where(
            and_(
                FoodItem.user_id == user_id,
                FoodItem.is_finished == False,
                FoodItem.expiry_date <= expiring_soon_date,
            )
        )
    )
    expiring_soon = result.scalar()
    
    # 已过期
    result = await db.execute(
        select(func.count()).where(
            and_(
                FoodItem.user_id == user_id,
                FoodItem.is_finished == False,
                FoodItem.expiry_date < date.today(),
            )
        )
    )
    expired = result.scalar()
    
    # 最近7天新增
    week_ago = date.today() - timedelta(days=7)
    result = await db.execute(
        select(func.count()).where(
            and_(
                FoodItem.user_id == user_id,
                FoodItem.created_at >= week_ago,
            )
        )
    )
    recently_added = result.scalar()
    
    # 最近7天消耗
    result = await db.execute(
        select(func.count()).where(
            and_(
                FoodItem.user_id == user_id,
                FoodItem.is_finished == True,
                FoodItem.finished_at >= week_ago,
            )
        )
    )
    recently_consumed = result.scalar()
    
    return {
        "user_id": user_id,
        "username": user.username,
        "total_food_items": total_food_items,
        "total_locations": total_locations,
        "expiring_soon": expiring_soon,
        "expired": expired,
        "recently_added": recently_added,
        "recently_consumed": recently_consumed,
    }


@router.get(
    "/stats",
    response_model=SystemStatsResponse,
    summary="获取系统统计",
    description="获取系统整体的统计数据（管理员专属）",
)
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取系统统计（管理员专属）
    
    返回系统整体的统计数据，包括用户数、食物数、库存统计等。
    """
    # 检查是否为管理员
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    
    # 总用户数
    result = await db.execute(select(func.count()).select_from(User))
    total_users = result.scalar()
    
    # 总食物数
    result = await db.execute(select(func.count()).select_from(FoodItem))
    total_food_items = result.scalar()
    
    # 总空间数
    result = await db.execute(select(func.count()).select_from(Location))
    total_locations = result.scalar()
    
    # 7天内有活动的用户数
    week_ago = date.today() - timedelta(days=7)
    result = await db.execute(
        select(func.count()).where(
            or_(
                User.last_login >= week_ago,
                User.created_at >= week_ago,
            )
        )
    )
    active_users_7d = result.scalar()
    
    # 最近7天新增用户数
    result = await db.execute(
        select(func.count()).where(User.created_at >= week_ago)
    )
    new_users_7d = result.scalar()
    
    # 最近7天新增食物数
    result = await db.execute(
        select(func.count()).where(FoodItem.created_at >= week_ago)
    )
    food_items_added_7d = result.scalar()
    
    # 7天内即将过期的食物数
    expiring_soon_date = date.today() + timedelta(days=7)
    result = await db.execute(
        select(func.count()).where(
            and_(
                FoodItem.expiry_date <= expiring_soon_date,
                FoodItem.expiry_date >= date.today(),
                FoodItem.is_finished == False,
            )
        )
    )
    food_items_expiring_7d = result.scalar()
    
    # 空间分布统计
    result = await db.execute(
        select(Location.name, func.count(FoodItem.id))
        .join(FoodItem, FoodItem.location_id == Location.id, isouter=True)
        .group_by(Location.id, Location.name)
    )
    location_stats = {name: count for name, count in result.all()}
    
    return {
        "total_users": total_users,
        "total_food_items": total_food_items,
        "total_locations": total_locations,
        "active_users_7d": active_users_7d,
        "new_users_7d": new_users_7d,
        "food_items_added_7d": food_items_added_7d,
        "food_items_expiring_7d": food_items_expiring_7d,
        "storage_stats": location_stats,
    }


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="更新用户",
    description="更新用户信息（管理员专属）",
)
async def update_user(
    user_id: int,
    user_data: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    更新用户（管理员专属）

    更新指定用户的信息，包括用户名、邮箱、角色、昵称、密码等。
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    if user_data.username != user.username:
        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户名已被使用",
            )
        user.username = user_data.username

    if user_data.email and user_data.email != user.email:
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注册",
            )
        user.email = user_data.email

    user.role = user_data.role
    user.nickname = user_data.nickname or user_data.username
    user.is_active = user_data.is_active
    user.hashed_password = get_password_hash(user_data.password)

    await db.commit()
    await db.refresh(user)

    logger.info(f"管理员 {current_user.username} 更新了用户 {user.username}")

    return user


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除用户",
    description="删除用户账户（管理员专属）",
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    删除用户（管理员专属）

    永久删除指定用户账户及其所有数据。
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除当前登录的管理员账户",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    await db.delete(user)
    await db.commit()

    logger.info(f"管理员 {current_user.username} 删除了用户 {user.username}")


# 导出
__all__ = ["router"]