"""
AI识别路由 - 灵感食仓 (InspiLarder)
处理食物图片识别、食谱推荐等AI相关功能
"""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.ai_service import ai_service
from app.core.logging import get_logger

# 获取日志记录器
logger = get_logger(__name__)

# 创建路由
router = APIRouter(tags=["AI识别"])


@router.post(
    "/recognize",
    summary="识别食物图片",
    description="上传食物图片，AI自动识别其中的食物种类和信息",
)
async def recognize_food_image(
    image: UploadFile = File(..., description="食物图片文件"),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    识别食物图片
    
    上传图片，AI将识别其中的食物并返回:
    - 食物名称
    - 分类
    - 置信度
    - 建议保质期
    
    - **image**: 图片文件（支持JPEG、PNG、WebP）
    """
    # 验证文件类型
    content_type = image.content_type
    if not content_type or not content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请上传有效的图片文件",
        )
    
    # 读取图片数据
    try:
        image_data = await image.read()
        
        if len(image_data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="图片文件为空",
            )
        
        # 检查文件大小
        if len(image_data) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="图片文件过大，最大支持10MB",
            )
        
        logger.info(f"用户 {current_user.id} 上传图片进行识别，大小: {len(image_data)} bytes")
        
        # 调用AI服务进行识别
        results = await ai_service.recognize_food(
            image_data=image_data,
        )
        
        # 转换为响应格式
        return {
            "success": True,
            "count": len(results),
            "results": [r.to_dict() for r in results],
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"图片识别失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片识别失败: {str(e)}",
        )


@router.post(
    "/recipes",
    summary="推荐食谱",
    description="根据提供的食材推荐合适的食谱，支持多种场景",
)
async def recommend_recipes(
    request_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    try:
        scenario = request_data.get("scenario", "creative")
        foods = request_data.get("foods", [])
        expiring_foods = request_data.get("expiringFoods", [])
        custom_requirement = request_data.get("custom_requirement", "")
        servings = request_data.get("servings", 2)
        
        logger.info(f"用户 {current_user.id} 请求食谱推荐，场景: {scenario}，食用人数: {servings}")
        
        if not foods:
            return {
                "success": True,
                "scenario": scenario,
                "count": 0,
                "message": "暂无食材数据，请先添加食材",
                "recipes": []
            }
        
        ingredient_list = []
        for f in foods:
            if f.get("name") and f.get("category") != "prepared":
                quantity = f.get("quantity", 1)
                unit = f.get("unit", "个")
                if quantity and quantity != 1:
                    ingredient_list.append(f"{f.get('name')}({quantity}{unit})")
                else:
                    ingredient_list.append(f.get("name", ""))
        
        try:
            recipes = await ai_service.recommend_recipes_with_scenario(
                ingredients=ingredient_list,
                expiring_ingredients=expiring_foods,
                scenario=scenario,
                custom_requirement=custom_requirement if scenario == "custom" else "",
                count=3,
                servings=servings,
            )
            
            scenario_messages = {
                "quick": f"今天冰箱里有 {len(foods)} 种食材，我为您挑选了3道快手菜，15分钟内就能上桌！",
                "expiring": f"发现您有 {len(expiring_foods)} 种食材即将过期，这些菜谱可以帮您快速消耗！",
                "creative": f"利用您现有的 {len(foods)} 种食材，我为您设计了一些创意组合，让剩余食材焕发新生！",
                "custom": f"根据您的需求「{custom_requirement}」，我为您推荐以下菜谱："
            }
            
            recipe_dicts = []
            for r in recipes:
                recipe_data = r.to_dict() if hasattr(r, 'to_dict') else r
                recipe_dicts.append(recipe_data)
                
                from app.models.recipe import Recipe
                db_recipe = Recipe(
                    name=recipe_data.get("name", "未命名食谱"),
                    description=recipe_data.get("description", ""),
                    ingredients=recipe_data.get("ingredients", []),
                    steps=recipe_data.get("steps", []),
                    cooking_time=recipe_data.get("cooking_time") or recipe_data.get("cookingTime"),
                    difficulty=recipe_data.get("difficulty"),
                    servings=recipe_data.get("servings", 2),
                    tags=recipe_data.get("tags", []),
                    category=scenario,
                    user_id=current_user.id,
                )
                db.add(db_recipe)
            
            await db.commit()
            
            return {
                "success": True,
                "scenario": scenario,
                "message": scenario_messages.get(scenario, "为您推荐以下菜谱："),
                "count": len(recipe_dicts),
                "recipes": recipe_dicts,
            }
            
        except Exception as ai_error:
            logger.warning(f"AI服务调用失败，使用模拟数据: {ai_error}")
            mock_result = get_mock_recipes_by_scenario(scenario, foods, expiring_foods, custom_requirement)
            
            from app.models.recipe import Recipe
            for r in mock_result.get("recipes", []):
                db_recipe = Recipe(
                    name=r.get("name", "未命名食谱"),
                    description=r.get("description", ""),
                    ingredients=r.get("ingredients", []),
                    steps=r.get("steps", []),
                    cooking_time=r.get("cooking_time") or r.get("cookingTime"),
                    difficulty=r.get("difficulty"),
                    servings=r.get("servings", 2),
                    tags=r.get("tags", []),
                    category=scenario,
                    user_id=current_user.id,
                )
                db.add(db_recipe)
            
            await db.commit()
            
            return mock_result
        
    except Exception as e:
        logger.error(f"食谱推荐失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"食谱推荐失败: {str(e)}",
        )


def get_mock_recipes_by_scenario(scenario: str, foods: list, expiring_foods: list, custom_requirement: str = "") -> dict:
    """根据场景返回模拟食谱数据"""
    if scenario == "custom":
        return {
            "success": True,
            "scenario": scenario,
            "message": f"根据您的需求「{custom_requirement}」，我为您推荐以下菜谱：",
            "count": 3,
            "recipes": [
                {
                    "id": 1,
                    "name": "家常快手菜",
                    "description": "简单易做，满足您的需求",
                    "cookingTime": 20,
                    "difficulty": "简单",
                    "servings": 2,
                    "ingredients": [{"name": f, "amount": "适量", "have": True} for f in foods[:3]],
                    "steps": [
                        "准备食材",
                        "清洗切配",
                        "热锅下油",
                        "翻炒调味",
                        "出锅装盘"
                    ],
                    "tags": ["家常", "自定义"]
                },
                {
                    "id": 2,
                    "name": "营养餐",
                    "description": "营养均衡，健康美味",
                    "cookingTime": 25,
                    "difficulty": "中等",
                    "servings": 2,
                    "ingredients": [{"name": f, "amount": "适量", "have": True} for f in foods[2:5] if foods],
                    "steps": [
                        "准备食材",
                        "腌制肉类",
                        "热锅翻炒",
                        "勾芡出锅"
                    ],
                    "tags": ["营养", "自定义"]
                },
                {
                    "id": 3,
                    "name": "创意料理",
                    "description": "发挥创意，美味升级",
                    "cookingTime": 30,
                    "difficulty": "中等",
                    "servings": 2,
                    "ingredients": [{"name": f, "amount": "适量", "have": True} for f in foods[:2]],
                    "steps": [
                        "创意搭配食材",
                        "特殊处理",
                        "精心烹饪",
                        "摆盘装饰"
                    ],
                    "tags": ["创意", "自定义"]
                }
            ]
        }
    
    scenario_data = {
        "quick": {
            "message": f"今天冰箱里有 {len(foods)} 种食材，我为您挑选了3道快手菜！",
            "recipes": [
                {
                    "id": 1,
                    "name": "蒜蓉炒时蔬",
                    "description": "清爽快手，5分钟上桌，保留蔬菜原汁原味",
                    "cookingTime": 5,
                    "difficulty": "简单",
                    "servings": 2,
                    "ingredients": [
                        {"name": "青菜", "amount": "300克", "have": True},
                        {"name": "大蒜", "amount": "3瓣", "have": True},
                        {"name": "食用油", "amount": "适量", "have": True}
                    ],
                    "steps": [
                        "青菜洗净沥干水分",
                        "大蒜切末备用",
                        "热锅下油爆香蒜末",
                        "大火快炒青菜1分钟",
                        "加盐调味即可出锅"
                    ],
                    "tags": ["快手", "素食", "5分钟"]
                },
                {
                    "id": 2,
                    "name": "番茄鸡蛋汤面",
                    "description": "经典家常，10分钟搞定一顿饭",
                    "cookingTime": 10,
                    "difficulty": "简单",
                    "servings": 1,
                    "ingredients": [
                        {"name": "番茄", "amount": "2个", "have": True},
                        {"name": "鸡蛋", "amount": "2个", "have": True},
                        {"name": "面条", "amount": "1份", "have": True}
                    ],
                    "steps": [
                        "番茄切块，鸡蛋打散",
                        "煮面条至8分熟捞出",
                        "番茄炒出汁水",
                        "加水煮开，淋入蛋液",
                        "放入面条煮1分钟即可"
                    ],
                    "tags": ["面食", "10分钟", "一人食"]
                },
                {
                    "id": 3,
                    "name": "葱油拌面",
                    "description": "懒人必备，葱香四溢",
                    "cookingTime": 8,
                    "difficulty": "简单",
                    "servings": 1,
                    "ingredients": [
                        {"name": "面条", "amount": "1份", "have": True},
                        {"name": "小葱", "amount": "3根", "have": True},
                        {"name": "生抽", "amount": "2勺", "have": True}
                    ],
                    "steps": [
                        "小葱切段，分开葱白葱绿",
                        "小火慢炸葱白至金黄",
                        "加入葱绿炸香",
                        "加入生抽和糖调味",
                        "拌入煮好的面条"
                    ],
                    "tags": ["懒人", "8分钟", "葱香"]
                }
            ]
        },
        "expiring": {
            "message": f"发现您有 {len(expiring_foods)} 种食材即将过期，这些菜谱可以帮您快速消耗！",
            "recipes": [
                {
                    "id": 1,
                    "name": "大杂烩蔬菜汤",
                    "description": "一锅炖，消耗各种剩余蔬菜的最佳选择",
                    "cookingTime": 20,
                    "difficulty": "简单",
                    "servings": 4,
                    "ingredients": [
                        {"name": "蔬菜", "amount": "各种剩余", "have": True, "note": "优先使用"},
                        {"name": "土豆", "amount": "2个", "have": True},
                        {"name": "高汤/水", "amount": "适量", "have": True}
                    ],
                    "steps": [
                        "所有蔬菜洗净切块",
                        "土豆先下锅煮10分钟",
                        "加入其他蔬菜继续煮10分钟",
                        "加盐和胡椒调味",
                        "撒上香菜即可"
                    ],
                    "tags": ["消耗食材", "一锅出", "4人份"]
                },
                {
                    "id": 2,
                    "name": "剩菜炒饭",
                    "description": "利用剩饭剩菜，变废为宝",
                    "cookingTime": 15,
                    "difficulty": "简单",
                    "servings": 2,
                    "ingredients": [
                        {"name": "剩饭", "amount": "2碗", "have": True, "note": "必须"},
                        {"name": "剩余肉类", "amount": "适量", "have": True},
                        {"name": "剩余蔬菜", "amount": "适量", "have": True}
                    ],
                    "steps": [
                        "剩饭提前打散",
                        "肉类蔬菜切丁备用",
                        "热锅下油炒香配料",
                        "加入米饭大火翻炒",
                        "加酱油调味出锅"
                    ],
                    "tags": ["剩菜改造", "炒饭", "不浪费"]
                },
                {
                    "id": 3,
                    "name": "蔬菜蛋饼",
                    "description": "将剩余蔬菜做成早餐饼",
                    "cookingTime": 15,
                    "difficulty": "简单",
                    "servings": 2,
                    "ingredients": [
                        {"name": "鸡蛋", "amount": "3个", "have": True},
                        {"name": "蔬菜丁", "amount": "1碗", "have": True, "note": "切碎"},
                        {"name": "面粉", "amount": "50克", "have": True}
                    ],
                    "steps": [
                        "蔬菜切小丁",
                        "鸡蛋打散加入面粉",
                        "加入蔬菜丁和盐拌匀",
                        "平底锅刷油",
                        "倒入面糊煎至两面金黄"
                    ],
                    "tags": ["早餐", "消耗蔬菜", "蛋饼"]
                }
            ]
        },
        "creative": {
            "message": f"利用您现有的 {len(foods)} 种食材，我为您设计了一些创意组合！",
            "recipes": [
                {
                    "id": 1,
                    "name": "地中海风烤蔬菜",
                    "description": "西式做法，让普通蔬菜焕发异域风情",
                    "cookingTime": 30,
                    "difficulty": "中等",
                    "servings": 2,
                    "ingredients": [
                        {"name": "蔬菜", "amount": "随意组合", "have": True},
                        {"name": "橄榄油", "amount": "3勺", "have": True},
                        {"name": "迷迭香/香草", "amount": "适量", "have": False, "note": "可用干料替代"}
                    ],
                    "steps": [
                        "蔬菜切块，大小均匀",
                        "拌入橄榄油、盐、胡椒",
                        "烤箱200度预热",
                        "烤20-25分钟至微焦",
                        "撒上香草碎装饰"
                    ],
                    "tags": ["西式", "烤箱菜", "创意"]
                },
                {
                    "id": 2,
                    "name": "东南亚风味炒菜",
                    "description": "酸甜辣香，给家常菜加点异国风味",
                    "cookingTime": 15,
                    "difficulty": "中等",
                    "servings": 2,
                    "ingredients": [
                        {"name": "蔬菜/肉类", "amount": "300克", "have": True},
                        {"name": "鱼露", "amount": "1勺", "have": False, "note": "可用酱油替代"},
                        {"name": "柠檬汁", "amount": "半个", "have": True}
                    ],
                    "steps": [
                        "食材切片备用",
                        "热锅爆香蒜末",
                        "大火快炒食材",
                        "加入鱼露、糖调味",
                        "挤入柠檬汁提鲜"
                    ],
                    "tags": ["东南亚风", "酸辣", "创意"]
                },
                {
                    "id": 3,
                    "name": "日式照烧饭团",
                    "description": "剩饭变身精致日式便当",
                    "cookingTime": 20,
                    "difficulty": "中等",
                    "servings": 2,
                    "ingredients": [
                        {"name": "剩饭", "amount": "2碗", "have": True},
                        {"name": "剩余肉类", "amount": "100克", "have": True},
                        {"name": "海苔", "amount": "2片", "have": False, "note": "可选"}
                    ],
                    "steps": [
                        "肉类切碎炒熟调味",
                        "米饭温热后拌入肉碎",
                        "手上沾水捏成三角形",
                        "平底锅煎至表面微焦",
                        "包上海苔片即可"
                    ],
                    "tags": ["日式", "便当", "精致"]
                }
            ]
        }
    }
    
    data = scenario_data.get(scenario, scenario_data["creative"])
    return {
        "success": True,
        "scenario": scenario,
        "message": data["message"],
        "count": len(data["recipes"]),
        "recipes": data["recipes"]
    }


@router.get(
    "/categories",
    summary="获取食物分类列表",
    description="获取系统支持的所有食物分类",
)
async def get_food_categories() -> Any:
    """
    获取食物分类列表
    
    返回系统支持的所有食物分类及其说明
    """
    categories = [
        {"id": "vegetable", "name": "蔬菜", "icon": "🥬"},
        {"id": "fruit", "name": "水果", "icon": "🍎"},
        {"id": "meat", "name": "肉类", "icon": "🥩"},
        {"id": "seafood", "name": "海鲜", "icon": "🦐"},
        {"id": "dairy", "name": "乳制品", "icon": "🥛"},
        {"id": "grain", "name": "粮油", "icon": "🍚"},
        {"id": "snack", "name": "零食", "icon": "🍪"},
        {"id": "drink", "name": "饮料", "icon": "🥤"},
        {"id": "condiment", "name": "调味品", "icon": "🧂"},
        {"id": "prepared", "name": "成品菜肴", "icon": "🍱"},
        {"id": "other", "name": "其他", "icon": "📦"},
    ]
    
    return {
        "success": True,
        "count": len(categories),
        "categories": categories,
    }


# 导出
__all__ = ["router"]