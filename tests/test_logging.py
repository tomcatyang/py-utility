# -*- coding: utf-8 -*-
"""
日志管理模块测试
"""

import logging
import tempfile
import os
from unittest.mock import patch, MagicMock
from py_utility import (
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


class TestLoggerManager:
    """日志管理器测试"""
    
    def test_init_logging(self):
        """测试初始化日志系统"""
        # 重置状态
        LoggerManager.reset()
        
        # 初始化日志系统
        LoggerManager.init_logging(log_level="DEBUG")
        
        # 验证已初始化
        assert LoggerManager._initialized is True
    
    def test_get_logger(self):
        """测试获取logger"""
        # 重置状态
        LoggerManager.reset()
        
        # 获取logger（会自动初始化）
        logger = LoggerManager.get_logger("test_module")
        assert logger is not None
        
        # 验证已初始化
        assert LoggerManager._initialized is True
    
    def test_reset(self):
        """测试重置日志系统"""
        # 先初始化
        LoggerManager.init_logging()
        assert LoggerManager._initialized is True
        
        # 重置
        LoggerManager.reset()
        assert LoggerManager._initialized is False
        assert LoggerManager._logger is None


class TestLoggingFunctions:
    """日志函数测试"""
    
    def test_init_logging_function(self):
        """测试初始化日志函数"""
        # 重置状态
        LoggerManager.reset()
        
        # 使用函数初始化
        init_logging(log_level="INFO")
        
        # 验证已初始化
        assert LoggerManager._initialized is True
    
    def test_get_logger_function(self):
        """测试获取logger函数"""
        # 重置状态
        LoggerManager.reset()
        
        # 获取logger
        logger = get_logger("test_module")
        assert logger is not None
        
        # 验证已初始化
        assert LoggerManager._initialized is True
    
    def test_convenience_functions(self):
        """测试便捷函数"""
        # 重置状态
        LoggerManager.reset()
        
        # 这些函数应该能正常调用而不抛出异常
        debug("debug message", key="value")
        info("info message", key="value")
        warning("warning message", key="value")
        error("error message", key="value")
        critical("critical message", key="value")
        exception("exception message", key="value")
        
        # 验证已初始化
        assert LoggerManager._initialized is True


class TestLoggingWithFile:
    """带文件的日志测试"""
    
    def test_logging_to_file(self):
        """测试日志输出到文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            
            # 重置状态
            LoggerManager.reset()
            
            # 初始化日志系统，输出到文件
            init_logging(log_level="INFO", log_file=log_file)
            
            # 记录日志
            info("test message", key="value")
            
            # 验证文件存在
            assert os.path.exists(log_file)
            
            # 验证文件内容
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "test message" in content
                assert "key=value" in content


class TestLoggingLevels:
    """日志级别测试"""
    
    def test_different_log_levels(self):
        """测试不同日志级别"""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in levels:
            # 重置状态
            LoggerManager.reset()
            
            # 使用不同级别初始化
            init_logging(log_level=level)
            
            # 验证已初始化
            assert LoggerManager._initialized is True
    
    def test_invalid_log_level(self):
        """测试无效的日志级别"""
        # 重置状态
        LoggerManager.reset()
        
        # 使用无效级别初始化（应该使用默认级别）
        init_logging(log_level="INVALID")
        
        # 验证已初始化（应该使用默认级别）
        assert LoggerManager._initialized is True


class TestLoggerUsage:
    """Logger使用测试"""
    
    def test_logger_with_context(self):
        """测试带上下文的logger"""
        # 重置状态
        LoggerManager.reset()
        
        # 获取logger
        logger = get_logger("test_module")
        
        # 记录带上下文的日志
        logger.info("user login", user_id=123, action="login")
        logger.error("database error", error="connection failed", table="users")
        
        # 验证已初始化
        assert LoggerManager._initialized is True
    
    def test_logger_exception(self):
        """测试异常日志"""
        # 重置状态
        LoggerManager.reset()
        
        # 获取logger
        logger = get_logger("test_module")
        
        # 记录异常
        try:
            raise ValueError("test error")
        except ValueError as e:
            logger.exception("exception occurred", error=str(e))
        
        # 验证已初始化
        assert LoggerManager._initialized is True


if __name__ == "__main__":
    pytest.main([__file__])
