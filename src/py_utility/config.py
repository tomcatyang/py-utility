# -*- coding: utf-8 -*-
"""
改进的配置管理模块

使用Pydantic Settings提供更好的类型验证和配置管理
"""

import os
from typing import Any, Dict, Optional, Union
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class DatabaseConfig(BaseModel):
    """数据库配置"""
    host: str = Field(default="localhost")
    port: int = Field(default=3306)
    user: str = Field(default="root")
    password: str = Field(default="")
    name: str = Field(default="option_trade")
    
    @property
    def url(self) -> str:
        """获取数据库连接URL"""
        return (
            f"mysql+pymysql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class RedisConfig(BaseModel):
    """Redis配置"""
    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    password: Optional[str] = Field(default=None)
    db: int = Field(default=0)
    
    @property
    def url(self) -> str:
        """获取Redis连接URL"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        else:
            return f"redis://{self.host}:{self.port}/{self.db}"


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = Field(default="INFO")
    file: Optional[str] = Field(default=None)
    
    @field_validator('level')
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'LOG_LEVEL must be one of {valid_levels}')
        return v.upper()


class APIConfig(BaseModel):
    """API配置"""
    data_provider_key: Optional[str] = Field(default=None)
    data_provider_url: Optional[str] = Field(default=None)
    broker_key: Optional[str] = Field(default=None)
    broker_secret: Optional[str] = Field(default=None)
    broker_url: Optional[str] = Field(default=None)


class CacheConfig(BaseModel):
    """缓存配置"""
    ttl_spot: int = Field(default=300)  # 5分钟
    ttl_option: int = Field(default=60)  # 1分钟
    ttl_vix: int = Field(default=3600)  # 1小时


class RateLimitConfig(BaseModel):
    """频控配置"""
    enabled: bool = Field(default=True)
    calls_per_second: int = Field(default=10)


class Settings(BaseSettings):
    """主配置类"""
    
    # 环境标识
    env: str = Field(default="dev", alias="ENV")
    
    # 数据库配置
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=3306, alias="DB_PORT")
    db_user: str = Field(default="root", alias="DB_USER")
    db_password: str = Field(default="", alias="DB_PASSWORD")
    db_name: str = Field(default="option_trade", alias="DB_NAME")
    
    # Redis配置
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    
    # 日志配置
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, alias="LOG_FILE")
    
    # API配置
    data_provider_api_key: Optional[str] = Field(default=None, alias="DATA_PROVIDER_API_KEY")
    data_provider_base_url: Optional[str] = Field(default=None, alias="DATA_PROVIDER_BASE_URL")
    broker_api_key: Optional[str] = Field(default=None, alias="BROKER_API_KEY")
    broker_api_secret: Optional[str] = Field(default=None, alias="BROKER_API_SECRET")
    broker_base_url: Optional[str] = Field(default=None, alias="BROKER_BASE_URL")
    
    # 缓存配置
    cache_ttl_spot: int = Field(default=300, alias="CACHE_TTL_SPOT")
    cache_ttl_option: int = Field(default=60, alias="CACHE_TTL_OPTION")
    cache_ttl_vix: int = Field(default=3600, alias="CACHE_TTL_VIX")
    
    # 频控配置
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_calls_per_second: int = Field(default=10, alias="RATE_LIMIT_CALLS_PER_SECOND")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "forbid"
    }
    
    def __init__(self, **kwargs):
        # 手动加载环境特定的.env文件
        self._load_env_files()
        super().__init__(**kwargs)
    
    def _load_env_files(self):
        """加载环境特定的配置文件"""
        project_root = Path(__file__).parent.parent.parent
        
        # 加载环境特定的.env文件
        env = os.getenv('ENV', 'dev')
        env_file = project_root / f'.env.{env}'
        if env_file.exists():
            load_dotenv(env_file, override=False)
        
        # 加载基础.env文件
        base_env_file = project_root / '.env'
        if base_env_file.exists():
            load_dotenv(base_env_file, override=False)
    
    @property
    def database(self) -> DatabaseConfig:
        """获取数据库配置"""
        return DatabaseConfig(
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_password,
            name=self.db_name
        )
    
    @property
    def redis(self) -> RedisConfig:
        """获取Redis配置"""
        return RedisConfig(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_password,
            db=self.redis_db
        )
    
    @property
    def logging(self) -> LoggingConfig:
        """获取日志配置"""
        return LoggingConfig(
            level=self.log_level,
            file=self.log_file
        )
    
    @property
    def api(self) -> APIConfig:
        """获取API配置"""
        return APIConfig(
            data_provider_key=self.data_provider_api_key,
            data_provider_url=self.data_provider_base_url,
            broker_key=self.broker_api_key,
            broker_secret=self.broker_api_secret,
            broker_url=self.broker_base_url
        )
    
    @property
    def cache(self) -> CacheConfig:
        """获取缓存配置"""
        return CacheConfig(
            ttl_spot=self.cache_ttl_spot,
            ttl_option=self.cache_ttl_option,
            ttl_vix=self.cache_ttl_vix
        )
    
    @property
    def rate_limit(self) -> RateLimitConfig:
        """获取频控配置"""
        return RateLimitConfig(
            enabled=self.rate_limit_enabled,
            calls_per_second=self.rate_limit_calls_per_second
        )
    
    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return self.env.lower() == 'prod'
    
    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return self.env.lower() == 'dev'
    
    def is_testing(self) -> bool:
        """判断是否为测试环境"""
        return self.env.lower() == 'test'


# 全局配置实例
_settings_instance: Optional[Settings] = None


def init_settings(env: Optional[str] = None) -> Settings:
    """
    初始化配置实例
    
    Args:
        env: 环境标识 (dev/test/prod)
        
    Returns:
        Settings实例
    """
    global _settings_instance
    if env:
        os.environ['ENV'] = env
    _settings_instance = Settings()
    return _settings_instance


def get_settings() -> Settings:
    """
    获取全局配置实例
    
    Returns:
        Settings实例
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance


def reload_settings(env: Optional[str] = None) -> Settings:
    """
    重新加载配置
    
    Args:
        env: 环境标识 (dev/test/prod)
        
    Returns:
        新的Settings实例
    """
    return init_settings(env)


# 向后兼容的别名
Config = Settings
get_config = get_settings
init_config = init_settings
reload_config = reload_settings
