from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.recipe import Recipe
from app.models.user import User

router = APIRouter(tags=["食谱管理"])


class RecipeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    ingredients: Optional[List[str]] = None
    steps: Optional[List[str]] = None
    cooking_time: Optional[int] = None
    difficulty: Optional[str] = None
    servings: Optional[int] = 2
    tags: Optional[List[str]] = None
    category: str


class RecipeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    ingredients: Optional[List[str]] = None
    steps: Optional[List[str]] = None
    cooking_time: Optional[int] = None
    difficulty: Optional[str] = None
    servings: Optional[int] = None
    tags: Optional[List[str]] = None
    category: str
    created_at: str

    class Config:
        from_attributes = True


class RecipeListResponse(BaseModel):
    total: int
    items: List[RecipeResponse]


@router.get("", response_model=RecipeListResponse)
async def get_recipes(
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    offset = (page - 1) * page_size
    
    query = select(Recipe).where(Recipe.user_id == current_user.id)
    count_query = select(func.count(Recipe.id)).where(Recipe.user_id == current_user.id)
    
    if category:
        query = query.where(Recipe.category == category)
        count_query = count_query.where(Recipe.category == category)
    
    query = query.order_by(Recipe.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    recipes = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    return {
        "total": total,
        "items": [
            RecipeResponse(
                id=r.id,
                name=r.name,
                description=r.description,
                ingredients=r.ingredients,
                steps=r.steps,
                cooking_time=r.cooking_time,
                difficulty=r.difficulty,
                servings=r.servings,
                tags=r.tags,
                category=r.category,
                created_at=r.created_at.isoformat() if r.created_at else "",
            )
            for r in recipes
        ],
    }


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(Recipe).where(
            Recipe.id == recipe_id,
            Recipe.user_id == current_user.id
        )
    )
    recipe = result.scalar_one_or_none()
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="食谱不存在",
        )
    
    return RecipeResponse(
        id=recipe.id,
        name=recipe.name,
        description=recipe.description,
        ingredients=recipe.ingredients,
        steps=recipe.steps,
        cooking_time=recipe.cooking_time,
        difficulty=recipe.difficulty,
        servings=recipe.servings,
        tags=recipe.tags,
        category=recipe.category,
        created_at=recipe.created_at.isoformat() if recipe.created_at else "",
    )


@router.delete("/{recipe_id}")
async def delete_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(Recipe).where(
            Recipe.id == recipe_id,
            Recipe.user_id == current_user.id
        )
    )
    recipe = result.scalar_one_or_none()
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="食谱不存在",
        )
    
    await db.delete(recipe)
    await db.commit()
    
    return {"message": "食谱已删除"}
