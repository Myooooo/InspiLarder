"""
日志配置模块 - 灵感食仓 (InspiLarder)
统一日志格式和级别管理
"""

import logging
import sys
from typing import Any

# 日志格式
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 默认日志级别
DEFAULT_LOG_LEVEL = logging.INFO


def setup_logging(log_level: int = DEFAULT_LOG_LEVEL) -> None:
    """
    配置全局日志
    
    Args:
        log_level: 日志级别，默认为 INFO
    """
    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    
    # 降低某些库的日志级别
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称，通常使用 __name__
        
    Returns:
        logging.Logger: 配置好的日志记录器
        
    Example:
        logger = get_logger(__name__)
        logger.info("这是一条日志")
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    日志混入类
    
    为类提供便捷的日志功能
    
    Example:
        class MyService(LoggerMixin):
            def do_something(self):
                self.logger.info("正在执行...")
    """
    
    @property
    def logger(self) -> logging.Logger:
        """获取类日志记录器"""
        return get_logger(self.__class__.__module__ + "." + self.__class__.__name__)


# 导出
__all__ = [
    "LOG_FORMAT",
    "DATE_FORMAT",
    "DEFAULT_LOG_LEVEL",
    "setup_logging",
    "get_logger",
    "LoggerMixin",
]