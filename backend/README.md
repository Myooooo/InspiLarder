# InspiLarder 后端 API

灵感食仓 (InspiLarder) - 智能食物管理与灵感推荐系统的 FastAPI 后端。

## 功能特性

- ✅ 完整的用户认证系统（JWT Token）
- ✅ 食物库存管理（CRUD、过期追踪）
- ✅ 储存空间管理（冰箱、橱柜等）
- ✅ AI 食物图片识别
- ✅ AI 食谱推荐
- ✅ 图片上传与处理
- ✅ 完整的 RESTful API 文档

## 项目结构

```
backend/app/
├── core/               # 核心模块
│   ├── config.py      # 配置管理
│   └── security.py    # JWT 和加密
├── db/                 # 数据库
│   ├── base.py        # ORM 基类
│   └── session.py     # 会话管理
├── models/             # 数据模型
│   ├── user.py        # 用户模型
│   ├── location.py    # 储存空间模型
│   └── food.py        # 食物记录模型
├── schemas/            # Pydantic 模式
│   ├── user.py        # 用户模式
│   └── food.py        # 食物和空间模式
├── api/                # API 路由
│   ├── deps.py        # 依赖注入
│   └── v1/            # v1 版本
│       ├── auth.py    # 认证路由
│       ├── food.py    # 食物路由
│       ├── location.py# 空间路由
│       └── ai.py      # AI 路由
├── services/           # 业务逻辑
│   ├── ai_service.py  # AI 服务
│   └── image_service.py# 图片服务
└── main.py            # 应用入口
```

## 快速开始

### 1. 安装依赖

```bash
cd /Users/fmy/dev/InspiLarder/backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\\Scripts\\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
# 应用配置
DEBUG=true
SECRET_KEY=your-super-secret-key-change-in-production

# 数据库
DATABASE_URL=sqlite+aiosqlite:///./data/inspi_larder.db

# OpenAI（可选）
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
```

### 3. 启动服务

```bash
# 开发模式（带热重载）
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- 健康检查: http://localhost:8000/health

## API 端点概览

### 认证
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出
- `GET /api/v1/auth/me` - 获取当前用户信息

### 食物管理
- `GET /api/v1/food` - 获取食物列表
- `POST /api/v1/food` - 创建食物记录
- `GET /api/v1/food/{id}` - 获取食物详情
- `PUT /api/v1/food/{id}` - 更新食物记录
- `DELETE /api/v1/food/{id}` - 删除食物记录
- `GET /api/v1/food/stats/summary` - 获取食物统计

### 储存空间
- `GET /api/v1/locations` - 获取空间列表
- `POST /api/v1/locations` - 创建储存空间
- `GET /api/v1/locations/{id}` - 获取空间详情
- `PUT /api/v1/locations/{id}` - 更新空间信息
- `DELETE /api/v1/locations/{id}` - 删除储存空间

### AI 功能
- `POST /api/v1/ai/recognize` - 识别食物图片
- `POST /api/v1/ai/recipes` - 推荐食谱
- `GET /api/v1/ai/categories` - 获取食物分类列表

## 技术栈

- **框架**: FastAPI
- **ORM**: SQLAlchemy 2.0 (Async)
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **认证**: JWT (python-jose)
- **密码加密**: Passlib (bcrypt)
- **数据验证**: Pydantic V2
- **AI服务**: OpenAI API
- **图片处理**: Pillow

## 开发说明

### 代码规范
- 使用 `ruff` 进行代码格式化和检查
- 使用 `mypy` 进行类型检查
- 遵循 PEP 8 规范

### 测试
```bash
# 运行测试
pytest

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

### 数据库迁移（使用 Alembic）
```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

## 许可证

MIT License

## 联系方式

- 项目主页: https://github.com/yourusername/inspi-larder
- 问题反馈: https://github.com/yourusername/inspi-larder/issues