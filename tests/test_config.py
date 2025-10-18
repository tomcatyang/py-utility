# -*- coding: utf-8 -*-
"""
配置管理模块测试
"""

import os
import pytest
from unittest.mock import patch
from py_utility import (
    Settings,
    DatabaseConfig,
    RedisConfig,
    LoggingConfig,
    get_settings,
    init_settings,
    reload_settings,
)


class TestDatabaseConfig:
    """数据库配置测试"""
    
    def test_default_values(self):
        """测试默认值"""
        config = DatabaseConfig()
        assert config.host == "localhost"
        assert config.port == 3306
        assert config.user == "root"
        assert config.password == ""
        assert config.name == "option_trade"
    
    def test_custom_values(self):
        """测试自定义值"""
        config = DatabaseConfig(
            host="test_host",
            port=3307,
            user="test_user",
            password="test_password",
            name="test_db"
        )
        assert config.host == "test_host"
        assert config.port == 3307
        assert config.user == "test_user"
        assert config.password == "test_password"
        assert config.name == "test_db"
    
    def test_url_property(self):
        """测试URL属性"""
        config = DatabaseConfig(
            host="localhost",
            port=3306,
            user="root",
            password="password",
            name="test_db"
        )
        expected_url = "mysql+pymysql://root:password@localhost:3306/test_db"
        assert config.url == expected_url


class TestRedisConfig:
    """Redis配置测试"""
    
    def test_default_values(self):
        """测试默认值"""
        config = RedisConfig()
        assert config.host == "localhost"
        assert config.port == 6379
        assert config.password is None
        assert config.db == 0
    
    def test_url_property_without_password(self):
        """测试无密码的URL"""
        config = RedisConfig(host="localhost", port=6379, db=0)
        expected_url = "redis://localhost:6379/0"
        assert config.url == expected_url
    
    def test_url_property_with_password(self):
        """测试有密码的URL"""
        config = RedisConfig(
            host="localhost",
            port=6379,
            password="password",
            db=0
        )
        expected_url = "redis://:password@localhost:6379/0"
        assert config.url == expected_url


class TestLoggingConfig:
    """日志配置测试"""
    
    def test_default_values(self):
        """测试默认值"""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert config.file is None
    
    def test_valid_log_levels(self):
        """测试有效的日志级别"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in valid_levels:
            config = LoggingConfig(level=level)
            assert config.level == level
    
    def test_invalid_log_level(self):
        """测试无效的日志级别"""
        with pytest.raises(ValueError):
            LoggingConfig(level="INVALID")


class TestSettings:
    """主配置类测试"""
    
    def test_default_values(self):
        """测试默认值"""
        settings = Settings()
        assert settings.env == "dev"
        assert settings.db_host == "localhost"
        assert settings.db_port == 3306
        assert settings.redis_host == "localhost"
        assert settings.redis_port == 6379
        assert settings.log_level == "INFO"
    
    def test_environment_detection(self):
        """测试环境检测"""
        # 开发环境
        with patch.dict(os.environ, {"ENV": "dev"}):
            settings = Settings()
            assert settings.is_development() is True
            assert settings.is_production() is False
            assert settings.is_testing() is False
        
        # 生产环境
        with patch.dict(os.environ, {"ENV": "prod"}):
            settings = Settings()
            assert settings.is_development() is False
            assert settings.is_production() is True
            assert settings.is_testing() is False
        
        # 测试环境
        with patch.dict(os.environ, {"ENV": "test"}):
            settings = Settings()
            assert settings.is_development() is False
            assert settings.is_production() is False
            assert settings.is_testing() is True
    
    def test_database_property(self):
        """测试数据库配置属性"""
        with patch.dict(os.environ, {
            "DB_HOST": "test_host",
            "DB_PORT": "3307",
            "DB_USER": "test_user",
            "DB_PASSWORD": "test_password",
            "DB_NAME": "test_db"
        }):
            settings = Settings()
            db_config = settings.database
            assert isinstance(db_config, DatabaseConfig)
            assert db_config.host == "test_host"
            assert db_config.port == 3307
            assert db_config.user == "test_user"
            assert db_config.password == "test_password"
            assert db_config.name == "test_db"
    
    def test_redis_property(self):
        """测试Redis配置属性"""
        with patch.dict(os.environ, {
            "REDIS_HOST": "redis_host",
            "REDIS_PORT": "6380",
            "REDIS_PASSWORD": "redis_password",
            "REDIS_DB": "1"
        }):
            settings = Settings()
            redis_config = settings.redis
            assert isinstance(redis_config, RedisConfig)
            assert redis_config.host == "redis_host"
            assert redis_config.port == 6380
            assert redis_config.password == "redis_password"
            assert redis_config.db == 1
    
    def test_logging_property(self):
        """测试日志配置属性"""
        with patch.dict(os.environ, {
            "LOG_LEVEL": "DEBUG",
            "LOG_FILE": "test.log"
        }):
            settings = Settings()
            log_config = settings.logging
            assert isinstance(log_config, LoggingConfig)
            assert log_config.level == "DEBUG"
            assert log_config.file == "test.log"
    


class TestGlobalFunctions:
    """全局函数测试"""
    
    def test_get_settings(self):
        """测试获取配置实例"""
        settings = get_settings()
        assert isinstance(settings, Settings)
    
    def test_init_settings(self):
        """测试初始化配置"""
        with patch.dict(os.environ, {"ENV": "test"}):
            settings = init_settings()
            assert settings.env == "test"
    
    def test_reload_settings(self):
        """测试重新加载配置"""
        with patch.dict(os.environ, {"ENV": "prod"}):
            settings = reload_settings()
            assert settings.env == "prod"


if __name__ == "__main__":
    pytest.main([__file__])
