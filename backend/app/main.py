"""
InspiLarder - 灵感食仓
FastAPI 应用主入口
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.api.v1.router import api_router
from app.db.base import Base
from app.db.session import engine

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description="AI驱动的食物记录与管理Web应用",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["http://localhost", "http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# 静态文件服务（用于上传的图片）
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

import pathlib
frontend_path = pathlib.Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    @app.get("/")
    async def serve_index():
        from fastapi.responses import FileResponse
        return FileResponse(frontend_path / "index.html")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        
        file_path = frontend_path / full_path
        if file_path.is_file():
            from fastapi.responses import FileResponse
            return FileResponse(file_path)
        
        from fastapi.responses import FileResponse
        return FileResponse(frontend_path / "index.html")

# 异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误", "message": str(exc) if settings.DEBUG else None}
    )

# 生命周期事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print(f"🚀 {settings.APP_NAME} 启动成功!")
    print(f"📚 API文档: http://localhost:8000/api/docs")
    
    # 创建数据库表（如果不存在）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    print(f"👋 {settings.APP_NAME} 已关闭")
    await engine.dispose()

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "app": settings.APP_NAME}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
