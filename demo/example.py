#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
py-utility 使用示例
"""

import os
from py_utility import (
    init_settings,
    get_settings,
    init_logging,
    get_logger,
    MySQLClient,
    info,
    error,
)


def main():
    """主函数"""
    print("py-utility 使用示例")
    print("=" * 50)
    
    # 1. 配置管理示例
    print("\n1. 配置管理示例")
    print("-" * 30)

    # 初始化配置
    print("初始化配置")
    print("-" * 30)
    print("初始化配置: dev/test/prod")
    init_settings('dev')
    
    # 2. 日志记录示例
    print("\n2. 日志记录示例")
    print("-" * 30)
    
    # 初始化日志系统
    init_logging(log_level="INFO")
    
    # 获取logger
    logger = get_logger(__name__)
    
    # 记录日志
    logger.info("应用启动", version="1.0.0", user="admin")
    logger.warning("配置检查", message="使用默认配置")
    
    # 使用便捷函数
    info("用户登录", user_id=123, action="login")
    error("数据库连接失败", error="Connection timeout", retry_count=3)
    
    # 3. 数据库操作示例（模拟）
    print("\n3. 数据库操作示例")
    print("-" * 30)
    
    # 注意：这里只是展示API用法，实际需要真实的数据库连接
    print("MySQL客户端API示例:")
    print("- client = MySQLClient()")
    print("- users = client.query('SELECT * FROM users')")
    print("- user_id = client.insert('users', {'name': '张三'})")
    print("- client.update('users', {'age': 25}, 'id = %s', (user_id,))")
    print("- client.delete('users', 'id = %s', (user_id,))")
    
    # 4. 配置示例
    print("\n4. 环境变量配置示例")
    print("-" * 30)
    print("可以通过环境变量配置:")
    print("export DB_HOST=localhost")
    print("export DB_PORT=3306")
    print("export LOG_LEVEL=DEBUG")
    print("export ENV=prod")
    
    print("\n示例完成！")


if __name__ == "__main__":
    main()
