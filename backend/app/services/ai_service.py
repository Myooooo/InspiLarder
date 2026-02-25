"""
AI服务模块 - 灵感食仓 (InspiLarder)
提供AI食物识别、过期预测和食谱推荐功能
"""

import json
import base64
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

from app.core.config import settings
from app.core.logging import get_logger

# 获取日志记录器
logger = get_logger(__name__)


@dataclass
class FoodRecognitionResult:
    """食物识别结果"""
    name: str
    category: str
    confidence: float
    icon: Optional[str] = None
    description: Optional[str] = None
    expiry_days: Optional[int] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "name": self.name,
            "icon": self.icon,
            "category": self.category,
            "confidence": self.confidence,
            "description": self.description,
            "expiry_days": self.expiry_days,
        }
        if self.quantity is not None:
            result["quantity"] = self.quantity
        if self.unit is not None:
            result["unit"] = self.unit
        return result


@dataclass
class RecipeRecommendation:
    """食谱推荐结果"""
    name: str
    description: str
    ingredients: List[str]
    steps: List[str]
    cooking_time: Optional[int] = None
    difficulty: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "ingredients": self.ingredients,
            "steps": self.steps,
            "cooking_time": self.cooking_time,
            "difficulty": self.difficulty,
        }


class AIService:
    """
    AI服务类
    
    提供食物识别、过期预测和食谱推荐功能
    """
    
    def __init__(self):
        """初始化AI服务"""
        self.api_key = settings.OPENAI_API_KEY
        self.vision_model = settings.OPENAI_VISION_MODEL
        self.vision_temperature = settings.VISION_TEMPERATURE
        self.vision_top_p = settings.VISION_TOP_P
        self.text_model = settings.OPENAI_TEXT_MODEL
        self.text_temperature = settings.TEXT_TEMPERATURE
        self.text_top_p = settings.TEXT_TOP_P
        self.base_url = settings.OPENAI_BASE_URL
        self._client = None
        
        logger.info(f"AI服务初始化完成，视觉模型: {self.vision_model}, 文本模型: {self.text_model}")
    
    @property
    def client(self):
        """获取OpenAI客户端（延迟加载）"""
        if self._client is None:
            try:
                import openai
                
                client_kwargs = {
                    "api_key": self.api_key,
                }
                
                if self.base_url:
                    client_kwargs["base_url"] = self.base_url
                
                self._client = openai.AsyncOpenAI(**client_kwargs)
                logger.info("OpenAI客户端初始化成功")
                
            except ImportError:
                logger.error("OpenAI库未安装，请运行: pip install openai")
                raise
            except Exception as e:
                logger.error(f"OpenAI客户端初始化失败: {e}")
                raise
        
        return self._client
    
    async def recognize_food(
        self,
        image_data: Union[str, bytes],
    ) -> List[FoodRecognitionResult]:
        """
        识别图片中的食物
        
        Args:
            image_data: 图片数据（base64字符串或bytes）
            
        Returns:
            List[FoodRecognitionResult]: 识别结果列表
        """
        if not self.api_key:
            logger.warning("未配置OpenAI API密钥，使用模拟数据")
            return self._mock_recognize_food()
        
        # 处理图片数据
        if isinstance(image_data, bytes):
            image_base64 = base64.b64encode(image_data).decode("utf-8")
        else:
            image_base64 = image_data
        
        # 构建系统提示
        system_prompt = self._build_recognition_prompt()
        
        try:
            response = await self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "请识别这张图片中的食物，按JSON格式返回。",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}",
                                },
                            },
                        ],
                    },
                ],
                temperature=self.vision_temperature,
                top_p=self.vision_top_p,
                max_tokens=1000,
            )
            
            # 解析响应
            content = response.choices[0].message.content
            # 清理 Markdown 代码块标记
            content = content.replace("```json", "").replace("```", "").strip()
            result_data = json.loads(content)
            
            # 转换为结果对象
            results = []
            for item in result_data.get("foods", []):
                results.append(
                    FoodRecognitionResult(
                        name=item.get("name", "未知食物"),
                        icon=item.get("icon"),
                        category=item.get("category", "other"),
                        confidence=item.get("confidence", 0.8),
                        description=item.get("description"),
                        expiry_days=item.get("expiry_days"),
                        quantity=item.get("quantity", 1),
                        unit=item.get("unit", "个"),
                    )
                )
            
            logger.info(f"食物识别成功，识别到 {len(results)} 种食物")
            return results
            
        except Exception as e:
            logger.error(f"食物识别失败: {e}")
            # 失败时返回模拟数据
            return self._mock_recognize_food()
    
    async def recommend_recipes(
        self,
        ingredients: List[str],
        dietary_preferences: Optional[List[str]] = None,
        cuisine_type: Optional[str] = None,
        count: int = 3,
    ) -> List[RecipeRecommendation]:
        """
        根据食材推荐食谱
        
        Args:
            ingredients: 可用食材列表
            dietary_preferences: 饮食偏好（如素食、无麸质等）
            cuisine_type: 菜系类型（如中餐、西餐等）
            count: 推荐数量
            
        Returns:
            List[RecipeRecommendation]: 食谱推荐列表
        """
        if not self.api_key:
            logger.warning("未配置OpenAI API密钥，使用模拟数据")
            return self._mock_recommend_recipes(ingredients, count)
        
        # 构建提示
        system_prompt = self._build_recipe_prompt(count)
        
        user_prompt = f"""
可用食材：{', '.join(ingredients)}
"""
        
        if dietary_preferences:
            user_prompt += f"\n饮食偏好：{', '.join(dietary_preferences)}"
        
        if cuisine_type:
            user_prompt += f"\n菜系：{cuisine_type}"
        
        try:
            response = await self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.text_temperature,
                top_p=self.text_top_p,
                max_tokens=2000,
            )
            
            # 解析响应
            content = response.choices[0].message.content
            # 清理 Markdown 代码块标记
            if content:
                content = content.replace("```json", "").replace("```", "").strip()
            result_data = json.loads(content)
            
            # 转换为结果对象
            recipes = []
            for item in result_data.get("recipes", []):
                recipes.append(
                    RecipeRecommendation(
                        name=item.get("name", "未命名食谱"),
                        description=item.get("description", ""),
                        ingredients=item.get("ingredients", []),
                        steps=item.get("steps", []),
                        cooking_time=item.get("cooking_time"),
                        difficulty=item.get("difficulty"),
                    )
                )
            
            logger.info(f"食谱推荐成功，推荐 {len(recipes)} 个食谱")
            return recipes
            
        except Exception as e:
            logger.error(f"食谱推荐失败: {e}")
            return self._mock_recommend_recipes(ingredients, count)
    
    async def recommend_recipes_with_scenario(
        self,
        ingredients: List[str],
        expiring_ingredients: Optional[List[str]] = None,
        scenario: str = "creative",
        custom_requirement: str = "",
        count: int = 3,
    ) -> List[RecipeRecommendation]:
        """
        根据场景推荐食谱
        
        Args:
            ingredients: 可用食材列表
            expiring_ingredients: 即将过期的食材列表
            scenario: 场景类型 (quick-快手, expiring-消耗, creative-创意, custom-自定义)
            custom_requirement: 自定义需求描述
            count: 推荐数量
            
        Returns:
            List[RecipeRecommendation]: 食谱推荐列表
        """
        if not self.api_key:
            logger.warning("未配置OpenAI API密钥，使用模拟数据")
            return self._mock_recommend_recipes(ingredients, count)
        
        # 根据场景构建不同的提示
        system_prompt = self._build_scenario_recipe_prompt(scenario, count)
        
        user_prompt = f"可用食材：{', '.join(ingredients)}"
        
        if expiring_ingredients:
            user_prompt += f"\n即将过期的食材（请优先使用）：{', '.join(expiring_ingredients)}"
        
        # 场景特定说明
        scenario_instructions = {
            "quick": "\n要求：烹饪时间必须在15分钟以内，步骤要简单",
            "expiring": "\n要求：必须优先使用即将过期的食材，可以是一次性消耗多种食材的大锅菜",
            "creative": "\n要求：尝试不同菜系的混搭，或者创新的烹饪方法",
            "custom": f"\n要求：{custom_requirement}"
        }
        user_prompt += scenario_instructions.get(scenario, "")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.text_temperature,
                top_p=self.text_top_p,
                max_tokens=2500,
            )
            
            content = response.choices[0].message.content
            # 清理 Markdown 代码块标记
            if content:
                content = content.replace("```json", "").replace("```", "").strip()
            result_data = json.loads(content)
            
            recipes = []
            for item in result_data.get("recipes", []):
                recipes.append(
                    RecipeRecommendation(
                        name=item.get("name", "未命名食谱"),
                        description=item.get("description", ""),
                        ingredients=item.get("ingredients", []),
                        steps=item.get("steps", []),
                        cooking_time=item.get("cooking_time"),
                        difficulty=item.get("difficulty"),
                    )
                )
            
            logger.info(f"场景化食谱推荐成功，场景: {scenario}，推荐 {len(recipes)} 个食谱")
            return recipes
            
        except Exception as e:
            logger.error(f"场景化食谱推荐失败: {e}")
            return self._mock_recommend_recipes(ingredients, count)
    
    def _build_scenario_recipe_prompt(self, scenario: str, count: int) -> str:
        scenario_descriptions = {
            "quick": "快手晚餐 - 15分钟内能完成的简单菜品",
            "expiring": "消耗大户 - 优先使用临期食材的菜谱",
            "creative": "创意混搭 - 利用剩余食材进行创新组合"
        }
        
        scenario_desc = scenario_descriptions.get(scenario, "创意菜谱")
        
        return f"""
你是一位专业的美食推荐官，专门推荐"{scenario_desc}，以中餐为主，偶尔推荐西餐"。

请根据用户提供的食材，推荐{count}个合适的食谱。

返回JSON格式：
{{
    "recipes": [
        {{
            "name": "食谱名称",
            "description": "简短描述这道菜的特点和口味",
            "ingredients": ["食材名称 用量", "食材名称 用量"],
            "steps": ["步骤1：具体操作，包含份量和时间", "步骤2：具体操作，包含份量和时间"],
            "cooking_time": 15,
            "difficulty": "简单",
            "servings": 2,
            "tags": ["标签1", "标签2"]
        }}
    ]
}}

关键要求（必须严格遵守）：
1. **ingredients 格式**：必须是 "食材名称 用量" 的字符串，如 "西兰花 500g"、"大蒜 4瓣"、"盐 适量"
2. **steps 格式**：每个步骤必须是完整的动作描述，包含：
   - 具体的份量（如：2勺、1茶匙、100ml、300g）
   - 具体的时间（如：2分钟、30秒、小火3分钟、大火收汁1分钟）
   - 精确的操作（如："锅中烧开水，加入少许盐和食用油，放入西兰花焯水1分钟至变色"）
3. 示例步骤格式：
   - "西兰花切成小朵，用清水浸泡5分钟后洗净，沥干水分备用"
   - "大蒜切末备用"
   - "锅中烧开水，加入少许盐（2克）和食用油（1勺），放入西兰花焯水1分钟至变色"
   - "捞出沥干水分备用"
   - "热锅下油（1勺），小火炒香蒜末（2瓣，切成蒜末）约15秒"
   - "放入西兰花，大火翻炒30秒，加入适量盐（2克）调味，翻炒均匀即可出锅"

4. **每道菜至少4步**，每步都要包含份量和时间信息
5. **cooking_time** 是总烹饪时间（分钟）
6. **difficulty** 可以是：简单、中等、困难
7. **servings** 是份数（1-6人）
8. **tags** 是标签数组，如 ["快手", "素食", "家常"]

只返回JSON格式，不要添加其他说明文字。
"""
    
    def _build_recognition_prompt(self) -> str:
        """构建食物识别提示"""
        return """
你是一个食物识别专家。请分析图片中的食物，并以JSON格式返回识别结果。

返回格式：
{
    "foods": [
        {
            "name": "食物名称（中文）",
            "icon": "推荐的相关Emoji图标，如🍎、🥬、🥩等",
            "category": "分类（vegetable/fruit/meat/seafood/dairy/grain/snack/drink/condiment/other）",
            "confidence": 0.95,
            "description": "简短描述（可选）",
            "expiry_days": 7,
            "quantity": 1,
            "unit": "个"
        }
    ]
}

注意：
- 识别图片中最主要的食物
- icon字段必须返回一个合适的中文Emoji，如苹果用🍎，白菜用🥬，肉类用🥩，鱼类用🐟等
- 如果有多种食物或是一道菜，则识别出菜品名称，并在description中列出主要食材
- confidence 是 0-1 之间的置信度
- expiry_days 是保质期，如果包装上有可见的保质期则填入，否则提供建议的保质期（天），如果不确定可以留空
- quantity 是数量，根据图片中食物的数量或包装上的数量填写，默认1
- unit 是单位，常用单位包括：个、克、千克、升、毫升、盒、瓶、包、袋、斤等，根据实际情况选择
- 只返回JSON，不要添加其他说明文字
"""
    
    def _build_recipe_prompt(self, count: int) -> str:
        """构建食谱推荐提示"""
        return f"""
你是一位专业的美食推荐官。请根据用户提供的食材，推荐{count}个美味且实用的食谱，以中餐为主，偶尔推荐西餐。

请以JSON格式返回，格式如下：
{{
    "recipes": [
        {{
            "name": "食谱名称",
            "description": "简短描述这道菜的特点",
            "ingredients": ["食材1", "食材2", "食材3"],
            "steps": ["步骤1", "步骤2", "步骤3"],
            "cooking_time": 30,
            "difficulty": "简单"
        }}
    ]
}}

注意：
- 优先使用用户提供的食材
- cooking_time 是烹饪时间（分钟）
- difficulty 可以是：简单、中等、困难
- 食谱应该实用且易于家庭制作
- 只返回JSON格式，不要添加其他说明文字
"""
    
    def _mock_recognize_food(self) -> List[FoodRecognitionResult]:
        """模拟食物识别（用于测试或API不可用时）"""
        return [
            FoodRecognitionResult(
                name="苹果",
                icon="🍎",
                category="fruit",
                confidence=0.95,
                description="新鲜的红苹果",
                expiry_days=14,
                quantity=3,
                unit="个",
            ),
            FoodRecognitionResult(
                name="香蕉",
                icon="🍌",
                category="fruit",
                confidence=0.92,
                description="黄色的香蕉",
                expiry_days=5,
                quantity=6,
                unit="个",
            ),
            FoodRecognitionResult(
                name="鸡蛋",
                icon="🥚",
                category="dairy",
                confidence=0.90,
                description="新鲜的鸡蛋",
                expiry_days=21,
                quantity=12,
                unit="个",
            ),
            FoodRecognitionResult(
                name="白菜",
                icon="🥬",
                category="vegetable",
                confidence=0.88,
                description="新鲜的白菜",
                expiry_days=7,
                quantity=1,
                unit="个",
            ),
            FoodRecognitionResult(
                name="牛奶",
                icon="🥛",
                category="dairy",
                confidence=0.85,
                description="新鲜的牛奶",
                expiry_days=7,
                quantity=1,
                unit="盒",
            ),
        ]
    
    def _mock_recommend_recipes(
        self,
        ingredients: List[str],
        count: int,
    ) -> List[RecipeRecommendation]:
        """模拟食谱推荐（用于测试或API不可用时）"""
        recipes = [
            RecipeRecommendation(
                name="清炒时蔬",
                description="清爽可口的家常菜",
                ingredients=["青菜", "蒜", "盐"],
                steps=["清洗蔬菜", "热锅下油", "快速翻炒"],
                cooking_time=10,
                difficulty="简单",
            ),
            RecipeRecommendation(
                name="蔬菜汤",
                description="营养丰富的汤品",
                ingredients=["蔬菜", "水", "盐"],
                steps=["切蔬菜", "烧水", "煮10分钟"],
                cooking_time=20,
                difficulty="简单",
            ),
        ]
        return recipes[:count]


# 全局AI服务实例
ai_service = AIService()


# 导出
__all__ = [
    "AIService",
    "ai_service",
    "FoodRecognitionResult",
    "RecipeRecommendation",
]