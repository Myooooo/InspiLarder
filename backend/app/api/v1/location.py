"""
储存空间路由 - 灵感食仓 (InspiLarder)
处理储存空间的CRUD操作
"""

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.location import Location
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.food import (
    LocationCreate,
    LocationUpdate,
    LocationResponse,
    LocationListResponse,
)

router = APIRouter(tags=["储存空间"])


@router.get(
    "",
    response_model=LocationListResponse,
    summary="获取空间列表",
    description="获取当前用户的所有储存空间",
)
async def get_locations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
) -> Any:
    """
    获取储存空间列表
    
    返回当前用户的所有储存空间，支持分页
    """
    # 构建查询
    query = select(Location).where(Location.user_id == current_user.id)
    
    # 计算总数
    count_query = select(Location).where(Location.user_id == current_user.id)
    
    from sqlalchemy import func
    total_result = await db.execute(
        select(func.count()).select_from(count_query.subquery())
    )
    total = total_result.scalar()
    
    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(Location.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    locations = result.scalars().all()

    # 计算总页数
    pages = (total + page_size - 1) // page_size if total > 0 else 0

    return {
        "items": [loc.to_dict() for loc in locations],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.post(
    "",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建储存空间",
    description="创建新的储存空间（冰箱、橱柜等）",
)
async def create_location(
    location_data: LocationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    创建储存空间
    
    添加新的储存空间，可以是冰箱、冷冻室、储藏室等
    
    - **name**: 空间名称（必填）
    - **type**: 空间类型（refrigerator, freezer, pantry, cupboard, other）
    - **description**: 描述（可选）
    - **icon**: 图标（可选）
    """
    # 创建空间
    data = location_data.model_dump()
    data.pop('type', None)
    
    parent_id = data.pop('parent_id', None)
    if parent_id:
        data['parent_id'] = parent_id
        data['level'] = 2
    else:
        data['level'] = 1
    
    db_location = Location(
        **data,
        user_id=current_user.id,
    )
    
    db.add(db_location)
    await db.commit()
    await db.refresh(db_location)

    return db_location.to_dict()


@router.get(
    "/{location_id}",
    response_model=LocationResponse,
    summary="获取空间详情",
    description="获取指定储存空间的详细信息",
)
async def get_location(
    location_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取储存空间详情
    
    返回指定ID的空间完整信息，包括其中存储的食物数量
    """
    result = await db.execute(
        select(Location).where(
            and_(
                Location.id == location_id,
                Location.user_id == current_user.id,
            )
        )
    )
    location = result.scalar_one_or_none()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="储存空间不存在",
        )
    
    return location


@router.put(
    "/{location_id}",
    response_model=LocationResponse,
    summary="更新储存空间",
    description="更新指定储存空间的信息",
)
async def update_location(
    location_id: int,
    location_data: LocationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    更新储存空间
    
    更新指定空间的信息，如名称、类型、描述等
    """
    result = await db.execute(
        select(Location).where(
            and_(
                Location.id == location_id,
                Location.user_id == current_user.id,
            )
        )
    )
    location = result.scalar_one_or_none()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="储存空间不存在",
        )
    
    # 更新字段
    update_data = location_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(location, field, value)
    
    await db.commit()
    await db.refresh(location)
    
    return location


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除储存空间",
    description="删除指定的储存空间及其中的所有食物",
)
async def delete_location(
    location_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    删除储存空间
    
    删除指定的空间及其中的所有食物记录，此操作不可恢复
    """
    result = await db.execute(
        select(Location).where(
            and_(
                Location.id == location_id,
                Location.user_id == current_user.id,
            )
        )
    )
    location = result.scalar_one_or_none()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="储存空间不存在",
        )
    
    # 删除空间（关联的食物会通过cascade自动删除）
    await db.delete(location)
    await db.commit()


# 导出
__all__ = ["router"]