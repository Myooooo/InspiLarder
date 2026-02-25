"""
用户相关Pydantic模式 - 灵感食仓 (InspiLarder)
定义用户数据的请求和响应模型
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ============== 基础模式 ==============

class UserBase(BaseModel):
    """用户基础模式"""
    
    email: EmailStr = Field(
        ...,
        description="用户邮箱地址",
        examples=["user@example.com"],
    )
    username: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="用户名",
        examples=["美食家小王"],
    )
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """验证用户名格式"""
        v = v.strip()
        if not v:
            raise ValueError("用户名不能为空")
        if len(v) < 2:
            raise ValueError("用户名至少需要2个字符")
        # 检查是否只包含有效字符
        import re
        if not re.match(r"^[\w\-_.\u4e00-\u9fa5]+$", v):
            raise ValueError("用户名只能包含字母、数字、中文、下划线、横线和点")
        return v


# ============== 创建相关 ==============

class UserCreate(UserBase):
    """用户创建请求模式"""
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="密码，至少8位",
        examples=["SecurePass123!"],
    )
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码强度"""
        if len(v) < 8:
            raise ValueError("密码至少需要8个字符")
        # 检查密码复杂度（可选，根据需要启用）
        import re
        if not re.search(r"[A-Z]", v):
            raise ValueError("密码需要包含至少一个大写字母")
        if not re.search(r"[a-z]", v):
            raise ValueError("密码需要包含至少一个小写字母")
        if not re.search(r"\d", v):
            raise ValueError("密码需要包含至少一个数字")
        return v


class UserRegister(UserCreate):
    """用户注册请求模式（别名）"""
    pass


# ============== 响应相关 ==============

class UserInDB(UserBase):
    """数据库中的用户模型（内部使用）"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    hashed_password: str  # 内部使用，不暴露给API


class UserResponse(UserBase):
    """用户响应模式（API返回）"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="用户ID")
    nickname: Optional[str] = Field(default=None, description="昵称")
    role: str = Field(default="user", description="用户角色")
    is_active: bool = Field(default=True, description="账户是否激活")
    is_superuser: bool = Field(default=False, description="是否为管理员")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    last_login: Optional[datetime] = Field(default=None, description="最后登录时间")

    # 统计数据
    location_count: Optional[int] = Field(default=None, description="空间数量")
    food_count: Optional[int] = Field(default=None, description="食物数量")


class UserProfile(UserResponse):
    """用户资料响应模式（详细信息）"""
    
    email: EmailStr  # 在个人资料中显示邮箱


# ============== 更新相关 ==============

class UserUpdate(BaseModel):
    """用户更新请求模式"""
    
    username: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50,
        description="新用户名",
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="新邮箱地址",
    )
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """验证用户名"""
        if v is None:
            return v
        v = v.strip()
        if len(v) < 2:
            raise ValueError("用户名至少需要2个字符")
        import re
        if not re.match(r"^[\w\-_.\u4e00-\u9fa5]+$", v):
            raise ValueError("用户名包含无效字符")
        return v


class UserPasswordUpdate(BaseModel):
    """密码更新请求模式"""
    
    current_password: str = Field(
        ...,
        description="当前密码",
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="新密码，至少8位",
    )
    
    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """验证新密码强度"""
        if len(v) < 8:
            raise ValueError("密码至少需要8个字符")
        import re
        if not re.search(r"[A-Z]", v):
            raise ValueError("密码需要包含至少一个大写字母")
        if not re.search(r"[a-z]", v):
            raise ValueError("密码需要包含至少一个小写字母")
        if not re.search(r"\d", v):
            raise ValueError("密码需要包含至少一个数字")
        return v


# ============== 认证相关 ==============

class Token(BaseModel):
    """Token响应模式"""
    
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    user: Optional[UserResponse] = Field(default=None, description="用户信息")


class TokenPayload(BaseModel):
    """Token载荷模式"""
    
    sub: str = Field(..., description="主题（用户ID）")
    exp: datetime = Field(..., description="过期时间")
    iat: datetime = Field(..., description="签发时间")
    type: str = Field(default="access", description="令牌类型")


class UserLogin(BaseModel):
    """用户登录请求模式"""
    
    username: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="用户名",
        examples=["admin"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="密码",
        examples=["admin123"],
    )


# ============== 认证相关 ==============

class Token(BaseModel):
    """Token响应模式"""
    
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    user: Optional[UserResponse] = Field(default=None, description="用户信息")


class TokenPayload(BaseModel):
    """Token载荷模式"""
    
    sub: str = Field(..., description="主题（用户ID）")
    exp: datetime = Field(..., description="过期时间")
    iat: datetime = Field(..., description="签发时间")
    type: str = Field(default="access", description="令牌类型")


class UserLogin(BaseModel):
    """用户登录请求模式"""
    
    username: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="用户名",
        examples=["admin"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="密码",
        examples=["admin123"],
    )


# ============== 认证相关 ==============

class Token(BaseModel):
    """Token响应模式"""
    
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    user: Optional[UserResponse] = Field(default=None, description="用户信息")


class TokenPayload(BaseModel):
    """Token载荷模式"""
    
    sub: str = Field(..., description="主题（用户ID）")
    exp: datetime = Field(..., description="过期时间")
    iat: datetime = Field(..., description="签发时间")
    type: str = Field(default="access", description="令牌类型")


class UserLogin(BaseModel):
    """用户登录请求模式"""
    
    username: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="用户名",
        examples=["admin"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="密码",
        examples=["admin123"],
    )


# ============== 认证相关 ==============

class Token(BaseModel):
    """Token响应模式"""
    
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    user: Optional[UserResponse] = Field(default=None, description="用户信息")


class TokenPayload(BaseModel):
    """Token载荷模式"""
    
    sub: str = Field(..., description="主题（用户ID）")
    exp: datetime = Field(..., description="过期时间")
    iat: datetime = Field(..., description="签发时间")
    type: str = Field(default="access", description="令牌类型")


class UserLogin(BaseModel):
    """用户登录请求模式"""
    
    username: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="用户名",
        examples=["admin"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="密码",
        examples=["admin123"],
    )


# ============== 认证相关 ==============

class Token(BaseModel):
    """Token响应模式"""
    
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    user: Optional[UserResponse] = Field(default=None, description="用户信息")


class TokenPayload(BaseModel):
    """Token载荷模式"""
    
    sub: str = Field(..., description="主题（用户ID）")
    exp: datetime = Field(..., description="过期时间")
    iat: datetime = Field(..., description="签发时间")
    type: str = Field(default="access", description="令牌类型")


class UserLogin(BaseModel):
    """用户登录请求模式"""
    
    username: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="用户名",
        examples=["admin"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="密码",
        examples=["admin123"],
    )


# ============== 列表响应 ==============

class UserListResponse(BaseModel):
    """用户列表响应模式"""
    
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    pages: int


# 导出
__all__ = [
    # 基础
    "UserBase",
    # 创建
    "UserCreate",
    "UserRegister",
    # 登录
    "UserLogin",
    # 令牌
    "Token",
    "TokenPayload",
    # 响应
    "UserInDB",
    "UserResponse",
    "UserProfile",
    "UserListResponse",
    # 更新
    "UserUpdate",
    "UserPasswordUpdate",
]