# InspiLarder 灵感食仓

> AI 驱动的智能食物管理助手

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-00a393.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 功能特性

- **用户认证系统** - JWT 认证，支持普通用户和管理员角色
- **食物库存管理** - CRUD 操作、过期追踪、消耗统计
- **储存空间管理** - 支持冰箱、冷藏室、冷冻室、储藏室等多级位置
- **AI 食物识别** - 拍照识别食物名称、类别、保质期
- **AI 食谱推荐** - 根据库存食材智能推荐菜谱（快手菜、临期消耗、创意菜）
- **图片上传处理** - 自动压缩、格式转换、本地存储
- **管理员面板** - 用户管理、系统统计、数据监控

## 快速开始

### 环境要求

- Python 3.11+
- MySQL 8.0+
- OpenAI API Key

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd InspiLarder
```

### 2. 初始化数据库

```bash
mysql -u root -p < backend/database/init.sql
```

### 3. 配置环境变量

```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env 填入以下配置：
# - OPENAI_API_KEY: OpenAI API 密钥
# - DATABASE_URL: MySQL 连接字符串
# - SECRET_KEY: JWT 密钥（生产环境必须修改）
```

### 4. 启动服务

```bash
# 安装依赖
pip install -r backend/requirements.txt

# 启动开发服务器（前后端统一在 8000 端口）
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问应用

- 应用首页: http://localhost:8000
- API 文档: http://localhost:8000/api/docs (Swagger)
- 健康检查: http://localhost:8000/health

**默认管理员账号:** `admin` / `admin123`（首次登录后请修改密码）

## 项目结构

```
InspiLarder/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/         # API 路由
│   │   ├── core/           # 配置、安全、日志
│   │   ├── models/         # SQLAlchemy 模型
│   │   ├── schemas/        # Pydantic 验证模型
│   │   ├── services/       # 业务逻辑（AI、图片处理）
│   │   └── db/             # 数据库会话
│   ├── database/
│   │   └── init.sql        # 数据库初始化脚本
│   ├── uploads/            # 用户上传图片
│   └── requirements.txt    # Python 依赖
├── frontend/                # 静态前端
│   ├── index.html          # SPA 入口
│   ├── css/styles.css      # 样式
│   └── js/app.js           # 前端逻辑
├── deploy/                  # 部署配置
│   └── inspiralarder.service  # Systemd 服务
└── AGENTS.md               # 项目知识库
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0 (异步) |
| 数据库 | MySQL + aiomysql |
| 认证 | JWT (python-jose) + bcrypt |
| AI 服务 | OpenAI GPT-4o / GPT-4o-mini |
| 图片处理 | Pillow |
| 前端 | Vanilla JS + Tailwind CSS |

## 部署

### Docker 部署（推荐）

```bash
# 构建镜像
docker build -t inspiralarder .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=sk-your-key \
  -e DATABASE_URL=mysql+aiomysql://user:pass@host/db \
  -e SECRET_KEY=your-secret-key \
  --name inspiralarder \
  inspiralarder
```

### Systemd 部署

```bash
# 1. 上传代码到服务器
cd /var/www
git clone <your-repo> inspiralarder
cd inspiralarder

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 3. 配置环境变量
cp backend/.env.example backend/.env
nano backend/.env

# 4. 配置并启动 Systemd 服务
sudo cp deploy/inspilarder.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable inspiralarder
sudo systemctl start inspiralarder
```

### Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 开发指南

### 代码规范

```bash
# 代码格式化
ruff check --fix .
ruff format .

# 类型检查
mypy .

# 运行测试
pytest
```

### 项目约定

- 使用 **Pydantic v2** 进行数据验证
- 使用 **异步 SQLAlchemy 2.0** 进行数据库操作
- API 路由统一使用 `/api/v1/` 前缀
- JWT Token 有效期为 7 天
- 图片上传限制 10MB，支持 jpeg/png/webp/gif

### 目录导航

| 任务 | 路径 |
|------|------|
| 添加 API 接口 | `backend/app/api/v1/` |
| 修改数据模型 | `backend/app/models/` |
| 修改验证模型 | `backend/app/schemas/` |
| AI 业务逻辑 | `backend/app/services/ai_service.py` |
| 配置文件 | `backend/app/core/config.py` |
| 前端页面 | `frontend/index.html` |
| 前端逻辑 | `frontend/js/app.js` |

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEBUG` | 调试模式 | `false` |
| `APP_NAME` | 应用名称 | `InspiLarder` |
| `SECRET_KEY` | JWT 密钥 | **必须修改** |
| `DATABASE_URL` | 数据库连接 | **必须配置** |
| `OPENAI_API_KEY` | OpenAI API 密钥 | **必须配置** |
| `OPENAI_VISION_MODEL` | 视觉模型 | `gpt-4o` |
| `OPENAI_TEXT_MODEL` | 文本模型 | `gpt-4o-mini` |
| `UPLOAD_DIR` | 上传目录 | `uploads` |
| `MAX_FILE_SIZE` | 最大文件大小 | `10485760` (10MB) |

## 常见问题

**Q: 前端如何连接后端？**  
A: 后端同时提供 API 服务和静态文件服务，访问 `http://localhost:8000` 即可。

**Q: 如何修改默认管理员密码？**  
A: 登录后进入个人中心修改密码，或在数据库中直接修改 `users` 表的 `hashed_password` 字段。

**Q: 支持哪些数据库？**  
A: 目前仅支持 MySQL。使用 `aiomysql` 驱动实现异步操作。

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 相关链接

- [AGENTS.md](./AGENTS.md) - 项目知识库
- [backend/README.md](./backend/README.md) - 后端详细文档
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
