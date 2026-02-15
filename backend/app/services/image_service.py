"""
图片处理服务模块 - 灵感食仓 (InspiLarder)
提供图片上传、压缩、格式转换等功能
"""

import base64
import hashlib
import io
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Tuple, Union

from app.core.config import settings
from app.core.logging import get_logger

# 获取日志记录器
logger = get_logger(__name__)

# 支持的图片格式
SUPPORTED_FORMATS = {"jpeg", "jpg", "png", "webp", "gif"}

# MIME类型映射
MIME_TYPE_MAP = {
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
    "gif": "image/gif",
}


class ImageProcessingError(Exception):
    """图片处理错误"""
    pass


class ImageService:
    """
    图片服务类
    
    提供图片处理、上传、压缩等功能
    """
    
    def __init__(self):
        """初始化图片服务"""
        self.upload_dir = Path(settings.upload_dir)
        self.max_size = settings.upload_max_size
        self.allowed_types = settings.upload_allowed_types
        
        # 确保上传目录存在
        self._ensure_upload_dir()
        
        logger.info(f"图片服务初始化完成，上传目录: {self.upload_dir}")
    
    def _ensure_upload_dir(self) -> None:
        """确保上传目录存在"""
        try:
            self.upload_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"创建上传目录失败: {e}")
            raise ImageProcessingError(f"无法创建上传目录: {e}")
    
    def _validate_image(
        self,
        image_data: Union[bytes, BinaryIO],
        filename: Optional[str] = None,
    ) -> Tuple[str, int]:
        """
        验证图片数据
        
        Args:
            image_data: 图片数据
            filename: 文件名（用于判断格式）
            
        Returns:
            Tuple[str, int]: (MIME类型, 文件大小)
            
        Raises:
            ImageProcessingError: 验证失败
        """
        # 获取数据大小
        if hasattr(image_data, "seek") and hasattr(image_data, "read"):
            # 文件对象
            image_data.seek(0, 2)  # 移动到末尾
            size = image_data.tell()
            image_data.seek(0)  # 重置到开头
        else:
            # bytes
            size = len(image_data)
        
        # 检查文件大小
        if size > self.max_size:
            raise ImageProcessingError(
                f"文件过大，最大允许 {self.max_size / 1024 / 1024:.1f}MB"
            )
        
        # 尝试识别文件类型
        mime_type = self._detect_mime_type(image_data, filename)
        
        if mime_type not in self.allowed_types:
            raise ImageProcessingError(
                f"不支持的文件类型: {mime_type}，允许的类型: {', '.join(self.allowed_types)}"
            )
        
        return mime_type, size
    
    def _detect_mime_type(
        self,
        image_data: Union[bytes, BinaryIO],
        filename: Optional[str] = None,
    ) -> str:
        """
        检测图片的MIME类型
        
        Args:
            image_data: 图片数据
            filename: 文件名
            
        Returns:
            str: MIME类型
        """
        # 尝试从文件扩展名判断
        if filename:
            ext = filename.lower().split(".")[-1] if "." in filename else ""
            if ext in MIME_TYPE_MAP:
                return MIME_TYPE_MAP[ext]
        
        # 从文件头判断
        try:
            if hasattr(image_data, "read"):
                header = image_data.read(12)
                image_data.seek(0)
            else:
                header = image_data[:12]
            
            # PNG: 89 50 4E 47
            if header.startswith(b"\\x89PNG"):
                return "image/png"
            
            # JPEG: FF D8 FF
            if header.startswith(b"\\xff\\xd8\\xff"):
                return "image/jpeg"
            
            # GIF: GIF87a 或 GIF89a
            if header[:6] in (b"GIF87a", b"GIF89a"):
                return "image/gif"
            
            # WebP: RIFF....WEBP
            if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
                return "image/webp"
            
        except Exception as e:
            logger.warning(f"检测文件类型失败: {e}")
        
        # 默认返回 JPEG
        return "image/jpeg"
    
    def _generate_filename(self, mime_type: str) -> str:
        """
        生成唯一的文件名
        
        Args:
            mime_type: MIME类型
            
        Returns:
            str: 生成的文件名
        """
        # 获取文件扩展名
        ext = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "image/gif": "gif",
        }.get(mime_type, "jpg")
        
        # 生成唯一文件名：日期 + UUID
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = uuid.uuid4().hex[:8]
        
        return f"{timestamp}_{unique_id}.{ext}"
    
    async def save_image(
        self,
        image_data: Union[bytes, BinaryIO],
        filename: Optional[str] = None,
        validate: bool = True,
    ) -> Dict[str, Any]:
        """
        保存上传的图片
        
        Args:
            image_data: 图片数据
            filename: 原始文件名
            validate: 是否验证图片
            
        Returns:
            Dict[str, Any]: 保存结果，包含文件路径、URL等信息
            
        Raises:
            ImageProcessingError: 处理失败
        """
        # 验证图片
        if validate:
            mime_type, size = self._validate_image(image_data, filename)
        else:
            mime_type = self._detect_mime_type(image_data, filename)
            size = len(image_data) if isinstance(image_data, bytes) else 0
        
        # 生成文件名
        new_filename = self._generate_filename(mime_type)
        
        # 按日期组织目录
        date_dir = datetime.now().strftime("%Y/%m")
        target_dir = self.upload_dir / date_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        file_path = target_dir / new_filename
        
        try:
            if hasattr(image_data, "read"):
                # 文件对象
                with open(file_path, "wb") as f:
                    while chunk := image_data.read(8192):
                        f.write(chunk)
            else:
                # bytes
                with open(file_path, "wb") as f:
                    f.write(image_data)
            
            logger.info(f"图片保存成功: {file_path}")
            
            # 计算文件哈希
            file_hash = self._calculate_file_hash(file_path)
            
            # 构建URL路径
            relative_path = f"{date_dir}/{new_filename}"
            
            return {
                "filename": new_filename,
                "original_filename": filename,
                "path": str(file_path),
                "relative_path": relative_path,
                "url": f"/uploads/{relative_path}",
                "mime_type": mime_type,
                "size": size,
                "hash": file_hash,
            }
            
        except Exception as e:
            logger.error(f"保存图片失败: {e}")
            raise ImageProcessingError(f"保存图片失败: {e}")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        计算文件MD5哈希
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: MD5哈希值
        """
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
        except Exception as e:
            logger.warning(f"计算文件哈希失败: {e}")
        
        return hash_md5.hexdigest()
    
    async def get_image_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        获取图片信息
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            Dict[str, Any]: 图片信息
        """
        path = Path(file_path)
        
        if not path.exists():
            raise ImageProcessingError(f"文件不存在: {file_path}")
        
        stat = path.stat()
        mime_type = self._detect_mime_type(None, path.name)
        
        # 尝试获取图片尺寸
        width, height = None, None
        try:
            from PIL import Image
            with Image.open(path) as img:
                width, height = img.size
        except Exception as e:
            logger.debug(f"无法获取图片尺寸: {e}")
        
        return {
            "path": str(path),
            "filename": path.name,
            "size": stat.st_size,
            "mime_type": mime_type,
            "width": width,
            "height": height,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
        }


# 全局图片服务实例
image_service = ImageService()


# 导出
__all__ = [
    "ImageService",
    "image_service",
    "ImageProcessingError",
]