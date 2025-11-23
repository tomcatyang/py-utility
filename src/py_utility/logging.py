# -*- coding: utf-8 -*-
"""
日志管理模块

支持结构化日志输出（JSON格式）
根据环境自动设置日志级别
支持输出到控制台和文件
日志文件按日期自动分割（每天生成一个新文件）
"""

import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional
from datetime import datetime
import structlog
from structlog.typing import FilteringBoundLogger

from .config import get_config


class LoggerManager:
    """日志管理器"""
    
    _initialized = False
    _logger: Optional[FilteringBoundLogger] = None
    
    @classmethod
    def init_logging(cls, log_level: Optional[str] = None, log_file: Optional[str] = None) -> None:
        """
        初始化日志系统
        
        Args:
            log_level: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
            log_file: 日志文件路径，会自动添加日期后缀
                     例如：logs/app.log -> logs/app_2025-01-15.log
        """
        if cls._initialized:
            return
        
        # 从配置获取日志设置
        config = get_config()
        log_level = log_level or config.logging.level
        log_file = log_file or config.logging.file or 'logs/app.log'
        
        # 设置日志级别
        level = getattr(logging, log_level.upper(), logging.INFO)
        
        # 配置root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # 清除已有的handlers
        root_logger.handlers.clear()
        
        # 添加控制台handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter('%(message)s'))
        root_logger.addHandler(console_handler)
        
        # 添加文件handler（按日期分割）
        if log_file:
            log_path = Path(log_file)
            log_dir = log_path.parent
            log_dir.mkdir(parents=True, exist_ok=True)
            
            log_stem = log_path.stem
            # 使用当前日期生成初始文件名：app_2025-11-23.log
            current_date = datetime.now().strftime('%Y-%m-%d')
            initial_log_file = log_dir / f"{log_stem}_{current_date}.log"
            
            # 使用TimedRotatingFileHandler实现按日期自动轮转
            # 直接使用带日期的文件名作为基础文件名
            # when='midnight': 每天午夜自动切换
            # interval=1: 每1天轮转一次
            # backupCount=0: 保留所有旧文件
            file_handler = TimedRotatingFileHandler(
                str(initial_log_file),
                when='midnight',
                interval=1,
                backupCount=0,  # 保留所有旧文件
                encoding='utf-8',
                delay=False
            )
            # 设置日期后缀格式
            file_handler.suffix = '%Y-%m-%d'
            file_handler.setLevel(level)
            file_handler.setFormatter(logging.Formatter('%(message)s'))
            
            # 自定义文件命名函数，将轮转后的格式改为 app_YYYY-MM-DD.log
            # 轮转时，TimedRotatingFileHandler会生成：app_2025-11-23.log.2025-11-24
            # 我们需要将其转换为：app_2025-11-24.log
            def dated_namer(name):
                """自定义文件命名函数，确保文件名格式为 app_YYYY-MM-DD.log"""
                name_path = Path(name)
                base_name = name_path.name
                parent_dir = name_path.parent
                
                # 提取日期后缀（格式：app_2025-11-23.log.2025-11-24）
                if '.log.' in base_name:
                    parts = base_name.split('.log.')
                    if len(parts) == 2:
                        # 提取新日期（后缀部分）
                        date_part = parts[1]  # 2025-11-24（轮转后的新日期）
                        return str(parent_dir / f"{log_stem}_{date_part}.log")
                
                # 如果格式不匹配，返回原文件名
                return name
            
            file_handler.namer = dated_namer
            
            # 重写rotation_filename方法，确保轮转后创建的文件也包含日期
            original_rotation_filename = file_handler.rotation_filename
            
            def rotation_filename_with_date(default_name):
                """自定义轮转文件名生成，确保新文件包含日期"""
                # 默认会生成 app_2025-11-23.log.2025-11-24
                # 但我们需要创建 app_2025-11-24.log
                if '.log.' in default_name:
                    # 提取新日期
                    parts = default_name.split('.log.')
                    if len(parts) == 2:
                        date_part = parts[1]
                        new_file = log_dir / f"{log_stem}_{date_part}.log"
                        return str(new_file)
                return default_name
            
            # 替换rotation_filename方法
            file_handler.rotation_filename = rotation_filename_with_date
            
            root_logger.addHandler(file_handler)
        
        # 自定义文本格式处理器
        def custom_text_renderer(_, __, event_dict):
            """
            自定义文本格式渲染器：time level tag logtext
            """
            from datetime import datetime, timezone
            
            # 格式化时间戳为 YYYY/MM/DD HH:MM:SS.mmm（本地时间）
            timestamp_str = event_dict.pop('timestamp', '')
            if timestamp_str:
                try:
                    # 处理ISO格式时间戳（通常structlog生成的是UTC时间）
                    # 先将Z替换为+00:00以便fromisoformat能正确解析
                    if timestamp_str.endswith('Z'):
                        timestamp_str = timestamp_str.replace('Z', '+00:00')
                    
                    # 解析ISO格式时间戳
                    dt = datetime.fromisoformat(timestamp_str)
                    
                    # 如果时间戳没有时区信息，假设为UTC
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    
                    # 转换为本地时间
                    dt = dt.astimezone()
                    
                    # 格式化为 YYYY/MM/DD HH:MM:SS.mmm（本地时间）
                    timestamp = dt.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]  # 保留3位毫秒
                except Exception:
                    # 解析失败时使用当前本地时间
                    timestamp = datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
            else:
                # 没有时间戳时使用当前本地时间
                timestamp = datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
            
            level = event_dict.pop('level', 'INFO').upper()
            logger_name = event_dict.pop('logger', 'root')
            event = event_dict.pop('event', '')
            
            # 构建额外信息
            extras = []
            for key, value in event_dict.items():
                if key not in ['filename', 'lineno', 'func_name']:
                    extras.append(f"{key}={value}")
            
            # 格式：time level tag logtext
            result = f"{timestamp} {level} {logger_name} {event}"
            if extras:
                result += ' ' + ' '.join(extras)
            
            return result
        
        # 配置structlog
        structlog.configure(
            processors=[
                # 添加日志级别
                structlog.stdlib.add_log_level,
                # 添加logger名称
                structlog.stdlib.add_logger_name,
                # 添加时间戳
                structlog.processors.TimeStamper(fmt="iso"),
                # 添加调用信息（文件名、行号、函数名）
                structlog.processors.CallsiteParameterAdder(
                    [
                        structlog.processors.CallsiteParameter.FILENAME,
                        structlog.processors.CallsiteParameter.LINENO,
                        structlog.processors.CallsiteParameter.FUNC_NAME,
                    ]
                ),
                # 格式化堆栈信息
                structlog.processors.format_exc_info,
                # 使用自定义文本格式
                custom_text_renderer,
            ],
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, log_level.upper(), logging.INFO)
            ),
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        cls._initialized = True
    
    @classmethod
    def get_logger(cls, name: Optional[str] = None) -> FilteringBoundLogger:
        """
        获取logger实例
        
        Args:
            name: logger名称，通常使用模块名 __name__
            
        Returns:
            structlog logger实例
        """
        if not cls._initialized:
            cls.init_logging()
        
        return structlog.get_logger(name)
    
    @classmethod
    def reset(cls) -> None:
        """重置日志系统（主要用于测试）"""
        cls._initialized = False
        cls._logger = None


# 便捷函数
def init_logging(log_level: Optional[str] = None, log_file: Optional[str] = None) -> None:
    """
    初始化日志系统
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径，会自动添加日期后缀
                 例如：logs/app.log -> logs/app_2025-01-15.log
    """
    LoggerManager.init_logging(log_level, log_file)


def get_logger(name: Optional[str] = None) -> FilteringBoundLogger:
    """
    获取logger实例
    
    Args:
        name: logger名称，通常使用 __name__
        
    Returns:
        structlog logger实例
        
    Example:
        logger = get_logger(__name__)
        logger.info("message", key="value")
        logger.error("error occurred", error=str(e))
    """
    return LoggerManager.get_logger(name)


# 全局logger（用于不需要特定名称的场景）
def debug(msg: str, **kwargs) -> None:
    """记录DEBUG级别日志"""
    get_logger().debug(msg, **kwargs)


def info(msg: str, **kwargs) -> None:
    """记录INFO级别日志"""
    get_logger().info(msg, **kwargs)


def warning(msg: str, **kwargs) -> None:
    """记录WARNING级别日志"""
    get_logger().warning(msg, **kwargs)


def error(msg: str, **kwargs) -> None:
    """记录ERROR级别日志"""
    get_logger().error(msg, **kwargs)


def critical(msg: str, **kwargs) -> None:
    """记录CRITICAL级别日志"""
    get_logger().critical(msg, **kwargs)


def exception(msg: str, **kwargs) -> None:
    """记录异常信息（包含堆栈跟踪）"""
    get_logger().exception(msg, **kwargs)


if __name__ == "__main__":
    # 初始化日志系统，日志文件会按日期自动分割
    # 例如：logs/info.log -> logs/info_2025-01-15.log
    init_logging(log_level='INFO', log_file='logs/info.log')
    logger = get_logger(__name__)
    
    logger.info("这是信息日志", key="value")
    logger.debug("这是调试日志（不会输出）", debug_key="debug_value")

