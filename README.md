# 灵感食仓 (InspiLarder)

> AI驱动的智能食物管理助手

## 🚀 快速启动

```bash
# 1. 初始化数据库
mysql -u root -p < backend/database/init.sql

# 2. 配置环境
cp backend/.env.example backend/.env
# 编辑 .env 填入 OpenAI API Key

# 3. 启动后端
pip install -r backend/requirements.txt
cd backend && uvicorn app.main:app --reload

# 4. 启动前端（新终端）
cd frontend && python server.py

# 5. 访问 http://localhost:3000 🎉
# 默认账号: admin / admin123
```

## 📁 项目结构

```
InspiLarder/
├── backend/              # FastAPI + MySQL
│   ├── app/              # API路由、模型、服务
│   ├── database/
│   │   └── init.sql      # 数据库铺底文件 ⭐
│   └── requirements.txt
├── frontend/             # HTML5 + Tailwind
│   ├── index.html
│   ├── css/styles.css
│   └── js/app.js
└── README.md
```

## 🔧 配置说明

### 环境变量 (.env)

`.env` 文件会覆盖 `config.py` 中的默认值：

```bash
# OpenAI配置
OPENAI_API_KEY=sk-your-key
OPENAI_VISION_MODEL=gpt-4o      # 视觉模型 - 识别图片
OPENAI_TEXT_MODEL=gpt-4o-mini  # 文本模型 - 推荐菜谱

# 数据库
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/inspilarder

# JWT密钥
SECRET_KEY=your-secret-key
```

## 🌐 Nginx 部署配置

**为什么前后端要分开启动？**

开发阶段分开启动便于调试。生产环境应使用 Nginx 统一服务：

```nginx
# /etc/nginx/sites-available/inspi-larder
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/inspi-larder/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 上传文件
    location /uploads/ {
        alias /var/www/inspi-larder/backend/uploads/;
    }
}
```

启动命令（生产环境）：
```bash
# 1. 启动后端（使用gunicorn）
cd backend
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app -b 127.0.0.1:8000

# 2. 启动nginx
sudo systemctl restart nginx
```

## 🤖 双模型配置

```python
# backend/app/core/config.py

# 视觉模型 - 分析图片、识别食物
OPENAI_VISION_MODEL: str = "gpt-4o"

# 文本模型 - 菜谱推荐、对话
OPENAI_TEXT_MODEL: str = "gpt-4o-mini"
```

## 📱 移动端优化

- ✅ 底部导航栏（移动端专属）
- ✅ 触摸友好按钮（44px+）
- ✅ iPhone 安全区域适配
- ✅ 响应式侧边栏（桌面端）

## 📄 数据库铺底

**文件位置**: `backend/database/init.sql`

包含：
- 3 个核心表结构（users, locations, food_items）
- 管理员账号（admin / admin123）
- 索引和外键约束

```bash
# 初始化数据库
mysql -u root -p < backend/database/init.sql
```

---

**Made with ❤️ and 🍊**
