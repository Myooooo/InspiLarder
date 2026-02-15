# InspiLarder 灵感食仓

> AI 驱动的智能食物管理助手

## 功能特性

- ✅ 用户认证系统 (JWT)
- ✅ 食物库存管理 (CRUD、过期追踪、统计)
- ✅ 储存空间管理 (冰箱、冷藏室、冷冻室、储藏室等)
- ✅ AI 食物图片识别
- ✅ AI 食谱推荐 (支持多种场景: 快手菜、消耗临期食材、创意菜)
- ✅ 图片上传与处理
- ✅ 管理员面板 (用户管理、系统统计)

## 快速开始

### 1. 初始化数据库

```bash
mysql -u root -p < backend/database/init.sql
```

### 2. 配置环境

```bash
# 复制示例配置
cp backend/.env.example backend/.env

# 编辑 .env 填入配置
# - OPENAI_API_KEY: OpenAI API 密钥
# - DATABASE_URL: MySQL 连接字符串
# - SECRET_KEY: JWT 密钥
```

### 3. 启动服务

```bash
# 安装依赖
pip install -r backend/requirements.txt

# 启动服务（前后端统一在 8000 端口）
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问

- 打开 http://localhost:8000
- 默认管理员账号: `admin` / `admin123`

## 项目结构

```
InspiLarder/
├── backend/              # FastAPI + MySQL
│   ├── app/
│   │   ├── api/         # API 路由
│   │   │   └── v1/      # v1 版本
│   │   │       ├── auth.py      # 认证
│   │   │       ├── food.py      # 食物管理
│   │   │       ├── location.py  # 储存空间
│   │   │       ├── ai.py        # AI 功能
│   │   │       ├── recipe.py    # 食谱
│   │   │       └── admin.py     # 管理员
│   │   ├── core/        # 核心模块
│   │   ├── models/      # 数据模型
│   │   ├── schemas/     # Pydantic 模型
│   │   ├── services/    # 业务逻辑
│   │   └── db/          # 数据库
│   ├── database/
│   │   └── init.sql     # 数据库初始化
│   └── requirements.txt
├── frontend/             # 静态前端
│   ├── index.html
│   ├── css/styles.css
│   └── js/app.js
├── README.md
└── requirements.txt
```

## API 文档

启动后端后访问:

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 技术栈

- **后端**: FastAPI + SQLAlchemy 2.0 (Async)
- **数据库**: MySQL
- **认证**: JWT (python-jose)
- **密码加密**: Passlib (bcrypt)
- **AI 服务**: OpenAI API (GPT-4V + GPT-4)
- **图片处理**: Pillow

## 配置说明

### 环境变量 (.env)

```bash
# OpenAI 配置
OPENAI_API_KEY=sk-your-key
OPENAI_VISION_MODEL=gpt-4o      # 视觉模型 - 识别图片
OPENAI_TEXT_MODEL=gpt-4o-mini  # 文本模型 - 推荐菜谱

# 数据库
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/inspilarder

# JWT
SECRET_KEY=your-secret-key

# 应用
DEBUG=true
APP_NAME=灵感食仓
```

## 部署

### 简单部署 (Gunicorn)

后端已内置前端服务，直接启动即可：

```bash
cd backend
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:8000
```

### Ubuntu 服务器 (Systemd)

1. 上传代码到服务器：
```bash
cd /var/www
git clone <your-repo> inspiralarder
cd inspiralarder
```

2. 创建虚拟环境并安装依赖：
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

3. 配置环境变量：
```bash
cp backend/.env.example backend/.env
nano backend/.env
```

4. 创建 systemd 服务：
```bash
sudo cp deploy/inspilarder.service /etc/systemd/system/
sudo nano /etc/systemd/system/inspilarder.service
# 修改路径为实际路径
```

5. 启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start inspiralarder
sudo systemctl enable inspiralarder  # 开机自启
```

6. 查看状态：
```bash
sudo systemctl status inspiralarder
journalctl -u inspiralarder -f  # 查看日志
```

### 生产环境 (Nginx + Gunicorn)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/inspi-larder/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # 上传文件
    location /uploads/ {
        alias /var/www/inspi-larder/backend/uploads/;
    }
}
```

```bash
# 启动后端
cd backend
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app -b 127.0.0.1:8000
```

## 开发

```bash
# 代码格式化
ruff check --fix .
ruff format .

# 类型检查
mypy .
```

## 许可证

MIT
