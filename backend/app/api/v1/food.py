"""
食物管理路由 - 灵感食仓 (InspiLarder)
处理食物记录的CRUD、搜索、统计等操作
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.food import FoodItem
from app.models.location import Location
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.food import (
    FoodItemCreate,
    FoodItemUpdate,
    FoodItemResponse,
    FoodItemListResponse,
    FoodItemConsumeRequest,
    FoodItemStats,
)

router = APIRouter(tags=["食物管理"])


@router.get(
    "",
    response_model=FoodItemListResponse,
    summary="获取食物列表",
    description="获取当前用户的食物记录列表，支持分页和筛选",
)
async def get_food_items(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    location_id: Optional[int] = Query(None, description="按空间筛选"),
    category: Optional[str] = Query(None, description="按分类筛选"),
    status: Optional[str] = Query(None, description="状态筛选: fresh, expiring_soon, expired"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向: asc, desc"),
) -> Any:
    """
    获取食物列表
    
    支持多种筛选条件:
    - **location_id**: 筛选指定空间的食物
    - **category**: 按分类筛选
    - **status**: 按状态筛选 (fresh, expiring_soon, expired)
    - **search**: 搜索食物名称和描述
    - **sort_by**: 排序字段 (created_at, expiry_date, name)
    - **sort_order**: 排序方向 (asc, desc)
    """
    # 构建基础查询
    query = select(FoodItem).where(
        and_(
            FoodItem.user_id == current_user.id,
            FoodItem.is_finished == False,
        )
    )
    
    # 应用筛选条件
    if location_id:
        # 验证空间所有权
        location_result = await db.execute(
            select(Location).where(
                and_(Location.id == location_id, Location.user_id == current_user.id)
            )
        )
        if not location_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="空间不存在或无权限访问",
            )
        query = query.where(FoodItem.location_id == location_id)
    
    if category:
        query = query.where(FoodItem.category == category)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                FoodItem.name.ilike(search_pattern),
                FoodItem.notes.ilike(search_pattern),
            )
        )
    
    # 状态筛选需要在Python中处理（因为expiry_status是计算属性）
    # 这里先查询所有数据，然后过滤
    
    # 应用排序
    sort_column = getattr(FoodItem, sort_by, FoodItem.created_at)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    # 应用状态筛选（如果需要）
    if status:
        items = [item for item in items if item.expiry_status == status]
        total = len(items)
    
    # 计算总页数
    pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.post(
    "",
    response_model=FoodItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建食物记录",
    description="创建新的食物库存记录",
)
async def create_food_item(
    food_data: FoodItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    创建食物记录
    
    添加新的食物到库存中，必须指定所在的空间。
    
    - **name**: 食物名称（必填）
    - **location_id**: 所在空间ID（必填）
    - **quantity**: 数量（默认1.0）
    - **unit**: 单位（默认"个"）
    - **category**: 分类（默认"other"）
    - **expiry_date**: 过期日期（可选）
    """
    # 验证空间所有权
    location_result = await db.execute(
        select(Location).where(
            and_(
                Location.id == food_data.location_id,
                Location.user_id == current_user.id,
            )
        )
    )
    location = location_result.scalar_one_or_none()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="空间不存在或无权限访问",
        )
    
    # 创建食物记录
    db_food = FoodItem(
        **food_data.model_dump(exclude_unset=True),
        user_id=current_user.id,
    )
    
    db.add(db_food)
    await db.commit()
    await db.refresh(db_food)
    
    return db_food


@router.get(
    "/{food_id}",
    response_model=FoodItemResponse,
    summary="获取食物详情",
    description="获取指定食物的详细信息",
)
async def get_food_item(
    food_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取食物详情
    
    返回指定ID的食物记录的完整信息
    """
    result = await db.execute(
        select(FoodItem).where(
            and_(
                FoodItem.id == food_id,
                FoodItem.user_id == current_user.id,
            )
        )
    )
    food = result.scalar_one_or_none()
    
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="食物记录不存在",
        )
    
    return food


@router.put(
    "/{food_id}",
    response_model=FoodItemResponse,
    summary="更新食物记录",
    description="更新指定食物的全部信息",
)
async def update_food_item(
    food_id: int,
    food_data: FoodItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    更新食物记录
    
    更新指定ID的食物记录的所有字段
    """
    result = await db.execute(
        select(FoodItem).where(
            and_(
                FoodItem.id == food_id,
                FoodItem.user_id == current_user.id,
            )
        )
    )
    food = result.scalar_one_or_none()
    
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="食物记录不存在",
        )
    
    # 如果更新了location_id，验证新空间的所有权
    if food_data.location_id is not None and food_data.location_id != food.location_id:
        location_result = await db.execute(
            select(Location).where(
                and_(
                    Location.id == food_data.location_id,
                    Location.user_id == current_user.id,
                )
            )
        )
        if not location_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="目标空间不存在或无权限访问",
            )
    
    # 更新字段
    update_data = food_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(food, field, value)
    
    await db.commit()
    await db.refresh(food)
    
    return food


@router.patch(
    "/{food_id}",
    response_model=FoodItemResponse,
    summary="部分更新食物记录",
    description="部分更新指定食物的信息",
)
async def patch_food_item(
    food_id: int,
    food_data: FoodItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    部分更新食物记录
    
    与PUT类似，但只更新提供的字段
    """
    # 复用update逻辑
    return await update_food_item(food_id, food_data, db, current_user)


@router.delete(
    "/{food_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除食物记录",
    description="删除指定的食物记录",
)
async def delete_food_item(
    food_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    删除食物记录
    
    永久删除指定的食物记录
    """
    result = await db.execute(
        select(FoodItem).where(
            and_(
                FoodItem.id == food_id,
                FoodItem.user_id == current_user.id,
            )
        )
    )
    food = result.scalar_one_or_none()
    
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="食物记录不存在",
        )
    
    await db.delete(food)
    await db.commit()


@router.post(
    "/{food_id}/consume",
    response_model=FoodItemResponse,
    summary="标记食物为已消耗",
    description="将食物标记为已消耗状态",
)
async def consume_food_item(
    food_id: int,
    consume_data: Optional[FoodItemConsumeRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    标记食物为已消耗
    
    将食物状态更新为已消耗，可指定消耗数量
    """
    result = await db.execute(
        select(FoodItem).where(
            and_(
                FoodItem.id == food_id,
                FoodItem.user_id == current_user.id,
            )
        )
    )
    food = result.scalar_one_or_none()
    
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="食物记录不存在",
        )
    
    if food.is_finished:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该食物已经被标记为已消耗",
        )
    
    # 处理部分消耗
    if consume_data and consume_data.quantity:
        if consume_data.quantity >= food.quantity:
            # 全部消耗
            food.mark_as_finished()
        else:
            # 部分消耗，创建新记录或更新数量
            # 这里简化处理：只更新原记录数量
            food.quantity -= consume_data.quantity
    else:
        # 全部消耗
        food.mark_as_finished()
    
    await db.commit()
    await db.refresh(food)
    
    return food


@router.get(
    "/stats/summary",
    response_model=FoodItemStats,
    summary="获取食物统计信息",
    description="获取当前用户的食物库存统计概览",
)
async def get_food_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取食物统计信息
    
    返回当前用户的食物库存统计，包括:
    - 总数、即将过期、已过期、新鲜数量
    - 分类分布
    - 空间分布
    """
    # 获取所有未消耗的食物，预加载location关系
    result = await db.execute(
        select(FoodItem).options(
            selectinload(FoodItem.location)
        ).where(
            and_(
                FoodItem.user_id == current_user.id,
                FoodItem.is_finished == False,
            )
        )
    )
    foods = result.scalars().all()
    
    # 统计
    total_count = len(foods)
    expiring_soon_count = sum(1 for f in foods if f.expiry_status == "expiring_soon")
    expired_count = sum(1 for f in foods if f.expiry_status == "expired")
    fresh_count = sum(1 for f in foods if f.expiry_status == "fresh")
    
    # 分类分布
    category_distribution: dict[str, int] = {}
    for food in foods:
        cat = food.category or "other"
        category_distribution[cat] = category_distribution.get(cat, 0) + 1
    
    # 空间分布
    location_distribution: dict[str, int] = {}
    for food in foods:
        if food.location:
            loc_name = food.location.name
            location_distribution[loc_name] = location_distribution.get(loc_name, 0) + 1
    
    return {
        "total_count": total_count,
        "expiring_soon_count": expiring_soon_count,
        "expired_count": expired_count,
        "fresh_count": fresh_count,
        "category_distribution": category_distribution,
        "location_distribution": location_distribution,
    }


# 导出
__all__ = ["router"]