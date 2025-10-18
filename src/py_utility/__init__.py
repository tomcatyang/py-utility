# -*- coding: utf-8 -*-
"""
py-utility 工具库

提供配置管理、日志记录、数据库操作等通用功能。

主要模块：
- config: 配置管理，支持环境变量和配置文件
- logging: 结构化日志记录
- mysql_client: MySQL数据库客户端，支持连接池和事务
"""

# 版本信息
__version__ = "1.0.0"
__author__ = "Yang XP"
__email__ = "yangxp@example.com"

# 配置管理模块
from .config import (
    Settings,
    DatabaseConfig,
    RedisConfig,
    LoggingConfig,
    APIConfig,
    CacheConfig,
    RateLimitConfig,
    get_settings,
    init_settings,
    reload_settings,
    # 向后兼容的别名
    Config,
    get_config,
    init_config,
    reload_config,
)

# 日志模块
from .logging import (
    LoggerManager,
    get_logger,
    init_logging,
    debug,
    info,
    warning,
    error,
    critical,
    exception,
)

# 数据库模块
from .mysql_client import (
    MySQLClient,
    get_mysql_client,
    init_mysql_client,
)

# 导出所有公共API
__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    "__email__",
    
    # 配置管理
    "Settings",
    "DatabaseConfig", 
    "RedisConfig",
    "LoggingConfig",
    "APIConfig",
    "CacheConfig",
    "RateLimitConfig",
    "get_settings",
    "init_settings", 
    "reload_settings",
    "Config",
    "get_config",
    "init_config",
    "reload_config",
    
    # 日志管理
    "LoggerManager",
    "get_logger",
    "init_logging",
    "debug",
    "info", 
    "warning",
    "error",
    "critical",
    "exception",
    
    # 数据库操作
    "MySQLClient",
    "get_mysql_client",
    "init_mysql_client",
]
