"""
应用配置模块
"""

from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
	"""应用配置类"""
	
	# 应用信息
	APP_NAME: str = "InspiLarder"
	DEBUG: bool = False
	SECRET_KEY: str = "your-secret-key-change-in-production"
	
	# 数据库配置
	DATABASE_URL: str = "mysql+aiomysql://user:password@localhost:3306/inspilarder"
	# 数据库配置 - 改为小写或添加映射
	DATABASE_URL: str = "mysql+aiomysql://user:password@localhost:3306/inspilarder"
	DB_ECHO: bool = False
	DB_POOL_SIZE: int = 5
	DB_MAX_OVERFLOW: int = 10

	# OpenAI配置 - 双模型支持
	OPENAI_API_KEY: str = ""
	OPENAI_BASE_URL: str = "https://api.openai.com/v1"
	
	# 视觉模型 - 用于分析图片、用于分析图片、识别食物
	OPENAI_VISION_MODEL: str = "gpt-4o"  # 支持图片输入的模型
	
	# 文本模型 - 用于菜谱推荐、对话等
	OPENAI_TEXT_MODEL: str = "gpt-4o-mini"  # 更快的文本模型
	
	# 文件上传配置
	UPLOAD_DIR: str = "uploads"
	MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

	# JWT配置
	ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
	ALGORITHM: str = "HS256"
	
	# 兼容性属性
	@property
	def upload_dir(self) -> str:
		return self.UPLOAD_DIR
	
	@property
	def upload_max_size(self) -> int:
		return self.MAX_FILE_SIZE
	
	@property
	def upload_allowed_types(self) -> list:
		return ["image/jpeg", "image/png", "image/webp", "image/gif"]
	
	@property
	def access_token_expire_minutes(self) -> int:
		return self.ACCESS_TOKEN_EXPIRE_MINUTES
	
	class Config:
		env_file = ".env"
		env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
	"""获取应用配置（单例模式）"""
	return Settings()

settings = get_settings()
