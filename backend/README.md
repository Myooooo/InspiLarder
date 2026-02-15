# InspiLarder 后端 API

> 灵感食仓 - AI 驱动的智能食物管理助手

## 功能特性

- ✅ 用户认证系统 (JWT)
- ✅ 食物库存管理 (CRUD、过期追踪、统计)
- ✅ 储存空间管理 (冰箱、冷藏室、冷冻室、储藏室等)
- ✅ AI 食物图片识别
- ✅ AI 食谱推荐
- ✅ 图片上传与处理
- ✅ 管理员面板

## 快速开始

### 1. 安装依赖

```bash
cd backend

# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 填入配置
```

### 3. 初始化数据库

```bash
mysql -u root -p < database/init.sql
```

### 4. 启动服务

```bash
# 开发模式 (热重载)
uvicorn app.main:app --reload

# 或
python -m uvicorn app.main:app --reload
```

## 项目结构

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py           # 依赖注入
│   │   └── v1/              # v1 版本 API
│   │       ├── auth.py      # 认证
│   │       ├── food.py      # 食物管理
│   │       ├── location.py  # 储存空间
│   │       ├── ai.py        # AI 功能
│   │       ├── recipe.py    # 食谱
│   │       ├── admin.py     # 管理员
│   │       └── router.py    # 路由聚合
│   ├── core/
│   │   ├── config.py        # 配置
│   │   ├── security.py      # JWT 安全
│   │   └── logging.py      # 日志
│   ├── models/              # SQLAlchemy 模型
│   ├── schemas/             # Pydantic 模型
│   ├── services/            # 业务逻辑
│   ├── db/                 # 数据库
│   └── main.py             # 应用入口
├── database/
│   └── init.sql            # 数据库初始化
└── requirements.txt
```

## API 文档

启动后访问:

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- 健康检查: http://localhost:8000/health

## API 端点

### 认证
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/v1/auth/register | 用户注册 |
| POST | /api/v1/auth/login | 用户登录 |
| POST | /api/v1/auth/logout | 用户登出 |
| GET | /api/v1/auth/me | 当前用户信息 |
| POST | /api/v1/auth/refresh | 刷新令牌 |

### 食物管理
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/food | 食物列表 |
| POST | /api/v1/food | 创建食物 |
| GET | /api/v1/food/{id} | 食物详情 |
| PUT | /api/v1/food/{id} | 更新食物 |
| DELETE | /api/v1/food/{id} | 删除食物 |
| POST | /api/v1/food/{id}/consume | 标记已消耗 |
| GET | /api/v1/food/stats/summary | 统计信息 |

### 储存空间
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/locations | 空间列表 |
| POST | /api/v1/locations | 创建空间 |
| GET | /api/v1/locations/{id} | 空间详情 |
| PUT | /api/v1/locations/{id} | 更新空间 |
| DELETE | /api/v1/locations/{id} | 删除空间 |

### AI 功能
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/v1/ai/recognize | 识别食物图片 |
| POST | /api/v1/ai/recipes | 推荐食谱 |
| GET | /api/v1/ai/categories | 食物分类 |

### 食谱
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/recipes | 食谱列表 |
| GET | /api/v1/recipes/{id} | 食谱详情 |
| DELETE | /api/v1/recipes/{id} | 删除食谱 |

### 管理员
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/admin/users | 用户列表 |
| POST | /api/v1/admin/users | 创建用户 |
| GET | /api/v1/admin/users/{id}/stats | 用户统计 |
| GET | /api/v1/admin/stats | 系统统计 |
| PUT | /api/v1/admin/users/{id} | 更新用户 |
| DELETE | /api/v1/admin/users/{id} | 删除用户 |

## 环境变量

```bash
# 应用
DEBUG=true
APP_NAME=灵感食仓
SECRET_KEY=your-secret-key

# 数据库
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/inspilarder

# OpenAI
OPENAI_API_KEY=sk-your-key
OPENAI_VISION_MODEL=gpt-4o
OPENAI_TEXT_MODEL=gpt-4o-mini
```

## 技术栈

- **框架**: FastAPI
- **ORM**: SQLAlchemy 2.0 (Async)
- **数据库**: MySQL
- **认证**: JWT (python-jose)
- **密码加密**: Passlib (bcrypt)
- **数据验证**: Pydantic V2
- **AI**: OpenAI API
- **图片处理**: Pillow

## 开发

```bash
# 格式化代码
ruff check --fix .
ruff format .

# 类型检查
mypy .

# 运行测试
pytest
```

## 许可证

MIT
