# InspiLarder 后端 API

> 灵感食仓 - AI 驱动的智能食物管理助手

## 快速开始

### 环境要求

- Python 3.11+
- MySQL 8.0+
- OpenAI API Key

### 安装与启动

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY, DATABASE_URL, SECRET_KEY

# 4. 初始化数据库
mysql -u root -p < database/init.sql

# 5. 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 项目结构

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py          # 依赖注入 (get_current_user, get_db)
│   │   └── v1/              # v1 API 路由
│   │       ├── auth.py      # 认证 (注册/登录/JWT)
│   │       ├── food.py      # 食物管理 (CRUD/统计)
│   │       ├── location.py  # 储存空间管理
│   │       ├── ai.py        # AI 功能 (识别/推荐)
│   │       ├── recipe.py    # 食谱管理
│   │       ├── admin.py     # 管理员接口
│   │       └── router.py    # 路由聚合器
│   ├── core/
│   │   ├── config.py        # Pydantic Settings 配置
│   │   ├── security.py      # JWT 加密/验证
│   │   └── logging.py       # 日志配置
│   ├── models/              # SQLAlchemy 2.0 ORM 模型
│   ├── schemas/             # Pydantic v2 验证模型
│   ├── services/            # 业务逻辑层
│   │   ├── ai_service.py    # OpenAI API 调用
│   │   └── image_service.py # 图片处理 (Pillow)
│   ├── db/
│   │   ├── base.py          # SQLAlchemy Base
│   │   ├── session.py       # 异步会话管理
│   │   └── __init__.py
│   └── main.py              # FastAPI 应用入口
├── database/
│   └── init.sql             # 数据库初始化脚本
├── uploads/                 # 用户上传图片目录
└── requirements.txt         # Python 依赖
```

## API 文档

启动后访问：

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **健康检查**: http://localhost:8000/health

## 核心 API 端点

### 认证
```
POST   /api/v1/auth/register      # 用户注册
POST   /api/v1/auth/login         # 用户登录
GET    /api/v1/auth/me            # 当前用户信息
POST   /api/v1/auth/refresh       # 刷新 Token
```

### 食物管理
```
GET    /api/v1/food               # 食物列表 (支持筛选)
POST   /api/v1/food               # 创建食物
GET    /api/v1/food/{id}          # 食物详情
PUT    /api/v1/food/{id}          # 更新食物
DELETE /api/v1/food/{id}          # 删除食物
POST   /api/v1/food/{id}/consume  # 标记已消耗
GET    /api/v1/food/stats/summary # 统计信息
```

### AI 功能
```
POST   /api/v1/ai/recognize       # 识别食物图片
POST   /api/v1/ai/recipes         # 根据食材推荐食谱
GET    /api/v1/ai/categories      # 获取食物分类
```

### 管理员
```
GET    /api/v1/admin/users        # 用户列表
POST   /api/v1/admin/users        # 创建用户
GET    /api/v1/admin/stats        # 系统统计
```

完整 API 列表见 Swagger 文档。

## 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| Web 框架 | FastAPI | >=0.109.0 |
| ASGI 服务器 | Uvicorn | >=0.27.0 |
| ORM | SQLAlchemy | 2.0+ (异步) |
| 数据库驱动 | aiomysql | >=0.2.0 |
| 数据验证 | Pydantic | v2 |
| 认证 | python-jose + passlib | - |
| AI 服务 | OpenAI | >=1.30.0 |
| 图片处理 | Pillow | >=10.0.0 |

## 开发指南

### 代码规范

```bash
# 代码检查与格式化
ruff check --fix .
ruff format .

# 类型检查
mypy .

# 运行测试
pytest
```

### 添加新 API 端点

1. 在 `app/api/v1/` 创建路由文件
2. 在 `app/schemas/` 创建请求/响应模型
3. 在 `app/api/v1/router.py` 注册路由

示例：

```python
# app/api/v1/example.py
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/example")
async def example(current_user = Depends(get_current_user)):
    return {"message": "Hello"}
```

```python
# app/api/v1/router.py
from app.api.v1.example import router as example_router

api_router.include_router(example_router, prefix="/example", tags=["示例"])
```

### 关键约定

- **异步优先**: 所有数据库操作使用 `async/await`
- **依赖注入**: 使用 `app/api/deps.py` 中的 `get_db()` 和 `get_current_user()`
- **Pydantic v2**: 使用 `ConfigDict(from_attributes=True)` 替代旧版 `Config` 类
- **错误处理**: 使用 FastAPI 的 HTTPException，统一错误格式

## 环境变量

| 变量 | 说明 | 必填 |
|------|------|------|
| `DEBUG` | 调试模式 | 否 |
| `SECRET_KEY` | JWT 密钥 | **是** |
| `DATABASE_URL` | MySQL 连接字符串 | **是** |
| `OPENAI_API_KEY` | OpenAI API 密钥 | **是** |
| `OPENAI_VISION_MODEL` | 视觉模型 | 否 (默认: gpt-4o) |
| `OPENAI_TEXT_MODEL` | 文本模型 | 否 (默认: gpt-4o-mini) |
| `VISION_TEMPERATURE` | 视觉模型温度 | 否 (默认: 0.2) |
| `TEXT_TEMPERATURE` | 文本模型温度 | 否 (默认: 0.7) |

## 部署

### 生产环境启动

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:8000
```

### Systemd 服务

```bash
sudo cp ../deploy/inspilarder.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable inspiralarder
sudo systemctl start inspiralarder
```

## 目录导航

| 任务 | 路径 |
|------|------|
| 添加 API 路由 | `app/api/v1/<name>.py` → `router.py` |
| 修改数据模型 | `app/models/<name>.py` |
| 修改验证模型 | `app/schemas/<name>.py` |
| AI 业务逻辑 | `app/services/ai_service.py` |
| 图片处理 | `app/services/image_service.py` |
| 配置文件 | `app/core/config.py` |
| 认证依赖 | `app/api/deps.py` |

## 相关链接

- [项目根目录 README](../README.md)
- [项目知识库](../AGENTS.md)
- [后端应用知识库](./app/AGENTS.md)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 文档](https://docs.sqlalchemy.org/en/20/)

## 许可证

MIT
