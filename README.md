# py-utility

Python工具库，提供配置管理、日志记录、数据库操作等通用功能。

## 功能特性

- **配置管理**: 基于Pydantic的配置管理，支持环境变量和配置文件
- **日志记录**: 结构化日志记录，支持JSON格式输出
- **数据库操作**: MySQL数据库客户端，支持连接池和事务管理
- **类型安全**: 完整的类型注解支持
- **易于使用**: 简洁的API设计

## 安装

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/your-username/py-utility.git
cd py-utility

# 安装依赖
pip install -r requirements.txt

# 安装包
pip install -e .
```

### 开发模式安装

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black src/
isort src/

# 类型检查
mypy src/
```

## 快速开始

### 配置管理

```python
from py_utility import get_settings, init_settings

# 初始化配置（可选）
settings = init_settings(env="dev")

# 获取配置实例
settings = get_settings()

# 访问配置
print(f"数据库主机: {settings.db_host}")
print(f"日志级别: {settings.logging.level}")

# 环境判断
if settings.is_development():
    print("当前为开发环境")
```

### 日志记录

```python
from py_utility import get_logger, init_logging

# 初始化日志系统
init_logging(log_level="INFO", log_file="logs/app.log")

# 获取logger
logger = get_logger(__name__)

# 记录日志
logger.info("应用启动", user_id=123, action="login")
logger.error("操作失败", error=str(e), user_id=123)

# 使用便捷函数
from py_utility import info, error
info("简单信息", key="value")
error("错误信息", error=str(e))
```

### 数据库操作

```python
from py_utility import MySQLClient, get_mysql_client

# 创建数据库客户端
client = MySQLClient(
    host="localhost",
    port=3306,
    user="root",
    password="password",
    database="my_db"
)

# 或者使用全局实例
client = get_mysql_client()

# 查询数据
users = client.query("SELECT * FROM users WHERE age > %s", (18,))
user = client.query_one("SELECT * FROM users WHERE id = %s", (1,))

# 插入数据
user_id = client.insert("users", {
    "name": "张三",
    "age": 25,
    "email": "zhangsan@example.com"
})

# 更新数据
affected = client.update(
    "users", 
    {"age": 26}, 
    "id = %s", 
    (user_id,)
)

# 删除数据
deleted = client.delete("users", "id = %s", (user_id,))

# 事务操作
with client.transaction() as cursor:
    cursor.execute("INSERT INTO users (name) VALUES (%s)", ("李四",))
    cursor.execute("INSERT INTO logs (action) VALUES (%s)", ("create_user",))
```

## 配置说明

### 环境变量

库支持通过环境变量进行配置：

```bash
# 数据库配置
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=password
export DB_NAME=my_database

# 日志配置
export LOG_LEVEL=INFO
export LOG_FILE=logs/app.log

# Redis配置
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=redis_password
export REDIS_DB=0

# API配置
export DATA_PROVIDER_API_KEY=your_api_key
export BROKER_API_KEY=your_broker_key
export BROKER_API_SECRET=your_broker_secret
```

### 配置文件

支持 `.env` 文件配置：

```bash
# .env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password
DB_NAME=my_database

LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## API 参考

### 配置管理

#### Settings

主配置类，提供所有配置项的访问。

```python
settings = get_settings()

# 数据库配置
db_config = settings.database
print(db_config.host)
print(db_config.url)

# 日志配置
log_config = settings.logging
print(log_config.level)

# 环境判断
settings.is_development()
settings.is_production()
settings.is_testing()
```

#### 配置子类

- `DatabaseConfig`: 数据库配置
- `RedisConfig`: Redis配置
- `LoggingConfig`: 日志配置
- `APIConfig`: API配置
- `CacheConfig`: 缓存配置
- `RateLimitConfig`: 频控配置

### 日志管理

#### LoggerManager

日志管理器类，负责日志系统的初始化。

```python
from py_utility import LoggerManager

# 初始化日志系统
LoggerManager.init_logging(log_level="DEBUG", log_file="logs/debug.log")

# 获取logger
logger = LoggerManager.get_logger(__name__)
```

#### 便捷函数

```python
from py_utility import debug, info, warning, error, critical, exception

debug("调试信息", key="value")
info("信息", user_id=123)
warning("警告", message="注意")
error("错误", error=str(e))
critical("严重错误", system="database")
exception("异常信息", error=str(e))  # 包含堆栈跟踪
```

### 数据库操作

#### MySQLClient

MySQL数据库客户端，提供完整的数据库操作功能。

```python
client = MySQLClient(
    host="localhost",
    port=3306,
    user="root", 
    password="password",
    database="my_db",
    pool_size=5,
    max_connections=20
)

# 健康检查
if client.ping():
    print("数据库连接正常")

# 执行SQL
affected = client.execute("UPDATE users SET status = %s", ("active",))

# 批量执行
params_list = [("user1",), ("user2",), ("user3",)]
affected = client.execute_many("INSERT INTO users (name) VALUES (%s)", params_list)

# 查询操作
results = client.query("SELECT * FROM users WHERE status = %s", ("active",))
user = client.query_one("SELECT * FROM users WHERE id = %s", (1,))

# CRUD操作
user_id = client.insert("users", {"name": "张三", "age": 25})
affected = client.update("users", {"age": 26}, "id = %s", (user_id,))
deleted = client.delete("users", "id = %s", (user_id,))

# 事务操作
with client.transaction() as cursor:
    cursor.execute("INSERT INTO users (name) VALUES (%s)", ("李四",))
    cursor.execute("INSERT INTO logs (action) VALUES (%s)", ("create_user",))

# 关闭连接
client.close()
```

## 开发指南

### 项目结构

```
py-utility/
├── src/
│   ├── __init__.py          # 包初始化和导出
│   ├── config.py           # 配置管理
│   ├── logging.py          # 日志记录
│   └── mysql_client.py     # 数据库客户端
├── tests/                  # 测试文件
├── setup.py               # 安装脚本
├── pyproject.toml         # 项目配置
├── requirements.txt       # 依赖列表
└── README.md             # 说明文档
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_config.py

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

### 代码质量

```bash
# 代码格式化
black src/ tests/

# 导入排序
isort src/ tests/

# 类型检查
mypy src/

# 代码检查
pylint src/
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0

- 初始版本发布
- 支持配置管理
- 支持结构化日志记录
- 支持MySQL数据库操作
- 完整的类型注解支持
