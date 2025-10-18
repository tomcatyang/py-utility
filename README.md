# py-utility

Python工具库，提供配置管理、日志记录、数据库操作等通用功能。

## 功能特性

- **配置管理**: 基于Pydantic的配置管理，支持环境变量和配置文件
- **日志记录**: 结构化日志记录，支持JSON格式输出
- **数据库操作**: MySQL数据库客户端，支持连接池和事务管理
- **类型安全**: 完整的类型注解支持
- **易于使用**: 简洁的API设计

## 安装

### 从源码安装，安装以后可直接修改源码，立即生效

```bash
# 克隆仓库，如果当前开发项目采用venv虚拟环境，请先启动虚拟环境，这样才是安装到当前项目虚拟环境
# 启动虚拟环境，如果没有使用虚拟环境，则跳过
python3 -m venv venv

git clone https://github.com/tomcatyang/py-utility.git
cd py-utility

# 安装依赖
pip install -r requirements.txt

# 安装包
pip install -e .
```


## 快速开始

## 配置说明

### 配置文件

库会在**当前工作目录**中查找配置文件：

1. **环境特定配置文件**: `.env.{环境名}` (如 `.env.dev`, `.env.prod`)
2. **基础配置文件**: `.env`

#### 配置文件示例

```bash
# .env.dev (开发环境)
# 环境标识 (dev/test/prod)
ENV=dev

# 数据库配置
DB_HOST=111.230.41.108
DB_PORT=3006
DB_USER=root
DB_PASSWORD=1qetADGzcb
DB_NAME=option_trade_dev

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# 日志配置
# dev: DEBUG, test: INFO, prod: WARNING
LOG_LEVEL=DEBUG
LOG_FILE=logs/app_dev.log

# .env.prod (生产环境)
ENV=prod
# 环境标识 (dev/test/prod)
ENV=dev

# 数据库配置
DB_HOST=111.230.41.108
DB_PORT=3006
DB_USER=root
DB_PASSWORD=1qetADGzcb
DB_NAME=option_trade_dev

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# 日志配置
# dev: DEBUG, test: INFO, prod: WARNING
LOG_LEVEL=INFO
LOG_FILE=logs/app_dev.log
```

#### 环境变量

也可以通过环境变量直接配置：

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

# 其他配置可以通过项目扩展
# 例如：API配置、缓存配置等
```

#### 配置文件查找规则

1. 库会在**当前工作目录**查找配置文件
2. 如果未找到配置文件，会显示警告信息
3. 配置文件优先级：环境变量 > 环境特定文件 > 基础文件

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

> 其他配置（如API、缓存等）可以通过项目扩展实现

#### 项目配置扩展

由于 `py-utility` 只提供核心的数据库、Redis和日志配置，其他业务相关的配置可以通过项目扩展实现：

```python
# 在你的项目中创建扩展配置
from py_utility import Settings, DatabaseConfig, RedisConfig, LoggingConfig
from pydantic import BaseModel, Field
from typing import Optional

class APIConfig(BaseModel):
    """API配置"""
    data_provider_key: Optional[str] = Field(default=None)
    data_provider_url: Optional[str] = Field(default=None)
    broker_key: Optional[str] = Field(default=None)
    broker_secret: Optional[str] = Field(default=None)

class CacheConfig(BaseModel):
    """缓存配置"""
    ttl_spot: int = Field(default=300)
    ttl_option: int = Field(default=60)
    ttl_vix: int = Field(default=3600)

class ExtendedSettings(Settings):
    """扩展配置类"""
    
    # API配置
    api_key: Optional[str] = Field(default=None, alias="API_KEY")
    api_url: Optional[str] = Field(default=None, alias="API_URL")
    
    # 缓存配置
    cache_ttl: int = Field(default=300, alias="CACHE_TTL")
    
    @property
    def api(self) -> APIConfig:
        """获取API配置"""
        return APIConfig(
            data_provider_key=self.api_key,
            data_provider_url=self.api_url,
            broker_key=self.api_key,
            broker_secret=self.api_key
        )
    
    @property
    def cache(self) -> CacheConfig:
        """获取缓存配置"""
        return CacheConfig(
            ttl_spot=self.cache_ttl,
            ttl_option=self.cache_ttl,
            ttl_vix=self.cache_ttl
        )

# 使用扩展配置
settings = ExtendedSettings()
print(f"API配置: {settings.api.data_provider_key}")
print(f"缓存配置: {settings.cache.ttl_spot}")
```

#### 配置文件扩展

在项目根目录创建 `.env` 文件，包含扩展配置：

```bash
# .env.dev
# 基础配置
ENV=dev
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=dev_password
DB_NAME=option_trade_dev
LOG_LEVEL=DEBUG
LOG_FILE=logs/dev.log

# 扩展配置
API_KEY=your_api_key_here
API_URL=https://api.example.com
CACHE_TTL=300
```

#### 环境变量映射

扩展配置通过环境变量映射到配置类：

```python
class ExtendedSettings(Settings):
    """扩展配置类"""
    
    # 环境变量映射
    api_key: Optional[str] = Field(default=None, alias="API_KEY")
    api_url: Optional[str] = Field(default=None, alias="API_URL")
    cache_ttl: int = Field(default=300, alias="CACHE_TTL")
    
    # 业务配置
    business_name: str = Field(default="MyApp", alias="BUSINESS_NAME")
    max_retries: int = Field(default=3, alias="MAX_RETRIES")
    timeout: int = Field(default=30, alias="TIMEOUT")
```

对应的 `.env` 文件：

```bash
# .env.dev
# 基础配置
ENV=dev
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=dev_password
DB_NAME=option_trade_dev
LOG_LEVEL=DEBUG
LOG_FILE=logs/dev.log

# 扩展配置
API_KEY=your_api_key_here
API_URL=https://api.example.com
CACHE_TTL=300
BUSINESS_NAME=MyTradingApp
MAX_RETRIES=5
TIMEOUT=60
```

#### 多环境配置

为不同环境创建不同的配置文件：

```bash
# .env.dev (开发环境)
ENV=dev
DB_HOST=localhost
DB_PORT=3306
DB_USER=dev_user
DB_PASSWORD=dev_password
DB_NAME=trading_dev
LOG_LEVEL=DEBUG
LOG_FILE=logs/dev.log
API_KEY=dev_api_key
API_URL=https://dev-api.example.com
CACHE_TTL=60

# .env.test (测试环境)
ENV=test
DB_HOST=test-db.example.com
DB_PORT=3306
DB_USER=test_user
DB_PASSWORD=test_password
DB_NAME=trading_test
LOG_LEVEL=INFO
LOG_FILE=logs/test.log
API_KEY=test_api_key
API_URL=https://test-api.example.com
CACHE_TTL=120

# .env.prod (生产环境)
ENV=prod
DB_HOST=prod-db.example.com
DB_PORT=3306
DB_USER=prod_user
DB_PASSWORD=prod_password
DB_NAME=trading_prod
LOG_LEVEL=WARNING
LOG_FILE=/var/log/trading/app.log
API_KEY=prod_api_key
API_URL=https://api.example.com
CACHE_TTL=300
```

#### 配置验证

扩展配置支持Pydantic的验证功能：

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class ExtendedSettings(Settings):
    """扩展配置类"""
    
    # 带验证的配置
    api_key: Optional[str] = Field(default=None, alias="API_KEY")
    api_url: Optional[str] = Field(default=None, alias="API_URL")
    cache_ttl: int = Field(default=300, alias="CACHE_TTL", ge=1, le=3600)
    max_retries: int = Field(default=3, alias="MAX_RETRIES", ge=0, le=10)
    
    @field_validator('api_url')
    @classmethod
    def validate_api_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('API_URL must start with http:// or https://')
        return v
    
    @field_validator('cache_ttl')
    @classmethod
    def validate_cache_ttl(cls, v):
        if v < 1 or v > 3600:
            raise ValueError('CACHE_TTL must be between 1 and 3600 seconds')
        return v
```

#### 使用示例

```python
# 在项目中使用扩展配置
from py_utility import Settings
from pydantic import BaseModel, Field
from typing import Optional

class ExtendedSettings(Settings):
    """扩展配置类"""
    
    # API配置
    api_key: Optional[str] = Field(default=None, alias="API_KEY")
    api_url: Optional[str] = Field(default=None, alias="API_URL")
    
    # 缓存配置
    cache_ttl: int = Field(default=300, alias="CACHE_TTL")
    
    # 业务配置
    business_name: str = Field(default="MyApp", alias="BUSINESS_NAME")
    max_retries: int = Field(default=3, alias="MAX_RETRIES")
    
    @property
    def api_config(self):
        """获取API配置"""
        return {
            "key": self.api_key,
            "url": self.api_url,
            "retries": self.max_retries
        }

# 使用配置
settings = ExtendedSettings()
print(f"业务名称: {settings.business_name}")
print(f"API配置: {settings.api_config}")
print(f"缓存TTL: {settings.cache_ttl}")
```

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
