# MySQL客户端使用文档

## 概述

MySQL客户端模块提供了一个功能完善的数据库访问接口，支持连接池管理、CRUD操作、事务管理、自动重连和错误处理。

## 核心特性

- ✅ **连接池管理**：使用DBUtils实现高效的连接池
- ✅ **自动重连**：网络故障时自动重试（指数退避）
- ✅ **CRUD操作**：简洁的增删改查API
- ✅ **事务管理**：支持事务上下文管理器
- ✅ **健康检查**：提供连接健康检查功能
- ✅ **错误处理**：完善的异常处理和日志记录
- ✅ **类型安全**：返回字典类型结果（DictCursor）

## 快速开始

### 1. 基础使用

```python
from py_utility import get_mysql_client

# 获取客户端实例（自动从config.database加载配置）
client = get_mysql_client()

# 插入数据
user_id = client.insert('users', {
    'name': 'Alice',
    'email': 'alice@example.com',
    'age': 25
})

# 查询数据
user = client.query_one(
    "SELECT * FROM users WHERE id = %s",
    (user_id,)
)
print(user['name'])  # 输出: Alice

# 更新数据
client.update(
    'users',
    {'age': 26},
    'id = %s',
    (user_id,)
)

# 删除数据
client.delete('users', 'id = %s', (user_id,))
```

### 2. 自定义配置

```python
from py_utility import MySQLClient

# 自定义配置创建客户端
client = MySQLClient(
    host='localhost',
    port=3306,
    user='root',
    password='password',
    database='mydb',
    pool_size=10,
    max_connections=50,
    connect_timeout=10
)
```

### 3. 全局实例管理

```python
from py_utility import init_mysql_client, get_mysql_client

# 方式1: 显式初始化全局实例
init_mysql_client(
    host='localhost',
    database='mydb'
)

# 方式2: 使用时自动初始化（从配置读取）
client = get_mysql_client()
```

## API参考

### MySQLClient类

#### 构造函数

```python
MySQLClient(
    host=None,              # 数据库主机，None时从配置读取
    port=None,              # 端口，None时从配置读取
    user=None,              # 用户名，None时从配置读取
    password=None,          # 密码，None时从配置读取
    database=None,          # 数据库名，None时从配置读取
    pool_size=5,            # 连接池大小
    max_connections=20,     # 最大连接数
    connect_timeout=10,     # 连接超时（秒）
    read_timeout=30,        # 读取超时（秒）
    write_timeout=30        # 写入超时（秒）
)
```

### 查询方法

#### query() - 查询多条记录

```python
results = client.query(
    "SELECT * FROM users WHERE age > %s",
    (25,),
    retry_count=3,          # 重试次数
    retry_delay=0.5         # 重试延迟（秒）
)
# 返回: List[Dict[str, Any]]
```

#### query_one() - 查询单条记录

```python
user = client.query_one(
    "SELECT * FROM users WHERE id = %s",
    (user_id,)
)
# 返回: Optional[Dict[str, Any]]
```

### 执行方法

#### execute() - 执行SQL语句

```python
affected = client.execute(
    "UPDATE users SET age = %s WHERE id = %s",
    (26, user_id),
    retry_count=3,
    retry_delay=0.5
)
# 返回: int（影响的行数）
```

#### execute_many() - 批量执行

```python
users = [
    ('Alice', 25),
    ('Bob', 30),
    ('Carol', 28)
]
affected = client.execute_many(
    "INSERT INTO users (name, age) VALUES (%s, %s)",
    users
)
# 返回: int（影响的行数）
```

### CRUD方法

#### insert() - 插入记录

```python
user_id = client.insert('users', {
    'name': 'Alice',
    'email': 'alice@example.com',
    'age': 25
})
# 返回: int（插入记录的ID）
```

#### update() - 更新记录

```python
affected = client.update(
    'users',                    # 表名
    {'age': 26, 'email': '...'},  # 更新数据
    'id = %s',                  # WHERE条件
    (user_id,)                  # WHERE参数
)
# 返回: int（影响的行数）
```

#### delete() - 删除记录

```python
affected = client.delete(
    'users',        # 表名
    'id = %s',      # WHERE条件
    (user_id,)      # WHERE参数
)
# 返回: int（影响的行数）
```

### 事务管理

#### transaction() - 事务上下文管理器

```python
with client.transaction() as cursor:
    cursor.execute(
        "INSERT INTO users (name, age) VALUES (%s, %s)",
        ('Alice', 25)
    )
    cursor.execute(
        "UPDATE accounts SET balance = balance - 100 WHERE user_id = %s",
        (user_id,)
    )
    # 自动提交，异常时自动回滚
```

### 健康检查

#### ping() - 连接健康检查

```python
is_healthy = client.ping()
if not is_healthy:
    print("数据库连接异常")
```

### 资源管理

#### close() - 关闭连接池

```python
client.close()
```

## 配置说明

客户端通过 `config.database` 属性读取配置：

```python
from py_utility import get_config

config = get_config()
db_config = config.database  # 获取数据库配置对象

# 配置属性
db_config.host      # 数据库主机地址
db_config.port      # 数据库端口
db_config.user      # 数据库用户名
db_config.password  # 数据库密码
db_config.name      # 数据库名称
db_config.url       # SQLAlchemy连接URL（自动生成）
```

配置项对应的环境变量：

| 环境变量 | config.database属性 | 说明 | 默认值 |
|---------|-------------------|------|--------|
| DB_HOST | host | 数据库主机地址 | localhost |
| DB_PORT | port | 数据库端口 | 3306 |
| DB_USER | user | 数据库用户名 | root |
| DB_PASSWORD | password | 数据库密码 | (空) |
| DB_NAME | name | 数据库名称 | option_trade |

### 环境变量配置示例

```bash
# .env.dev
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=mypassword
DB_NAME=trade_system_dev
```

## 高级特性

### 1. 自动重连机制

客户端在遇到连接错误时会自动重试：

- 默认重试3次
- 使用指数退避策略（0.5s → 1s → 2s）
- 适用于所有查询和执行操作

```python
# 自定义重试参数
results = client.query(
    "SELECT * FROM users",
    retry_count=5,      # 重试5次
    retry_delay=1.0     # 初始延迟1秒
)
```

### 2. 连接池管理

连接池自动管理连接的创建、复用和释放：

- 支持并发访问
- 自动检测和清理失效连接
- 配置连接池大小和最大连接数

```python
client = MySQLClient(
    pool_size=10,           # 初始连接数
    max_connections=50      # 最大连接数
)
```

### 3. 参数化查询

所有查询和执行方法都支持参数化，防止SQL注入：

```python
# ✅ 正确：使用参数化查询
user = client.query_one(
    "SELECT * FROM users WHERE name = %s",
    (username,)
)

# ❌ 错误：直接拼接字符串（有SQL注入风险）
user = client.query_one(
    f"SELECT * FROM users WHERE name = '{username}'"
)
```

### 4. 批量操作

使用批量方法提高性能：

```python
# 批量插入
users = [
    ('Alice', 25),
    ('Bob', 30),
    ('Carol', 28)
]
client.execute_many(
    "INSERT INTO users (name, age) VALUES (%s, %s)",
    users
)
```

### 5. 事务隔离

事务确保数据一致性：

```python
try:
    with client.transaction() as cursor:
        # 转账操作
        cursor.execute(
            "UPDATE accounts SET balance = balance - %s WHERE user_id = %s",
            (100, from_user_id)
        )
        cursor.execute(
            "UPDATE accounts SET balance = balance + %s WHERE user_id = %s",
            (100, to_user_id)
        )
        # 自动提交
except Exception as e:
    # 发生异常时自动回滚
    print(f"转账失败: {e}")
```

## 错误处理

### 常见错误类型

1. **连接错误**（pymysql.OperationalError）
   - 数据库服务不可用
   - 网络故障
   - 自动重试

2. **SQL语法错误**（pymysql.ProgrammingError）
   - SQL语句有误
   - 表或列不存在
   - 不会重试

3. **数据完整性错误**（pymysql.IntegrityError）
   - 违反唯一约束
   - 外键约束失败
   - 不会重试

### 错误处理示例

```python
try:
    client.insert('users', {'name': 'Alice', 'email': 'alice@example.com'})
except pymysql.IntegrityError:
    print("用户已存在（邮箱重复）")
except pymysql.OperationalError:
    print("数据库连接失败")
except Exception as e:
    print(f"未知错误: {e}")
```

## 最佳实践

### 1. 使用全局实例

推荐使用全局单例模式：

```python
from py_utility import get_mysql_client

def my_function():
    client = get_mysql_client()
    # 使用client...
```

### 2. 参数化查询

始终使用参数化查询防止SQL注入：

```python
# ✅ 正确
client.query("SELECT * FROM users WHERE id = %s", (user_id,))

# ❌ 错误
client.query(f"SELECT * FROM users WHERE id = {user_id}")
```

### 3. 使用事务

对于需要原子性的操作使用事务：

```python
with client.transaction() as cursor:
    cursor.execute("INSERT INTO ...")
    cursor.execute("UPDATE ...")
```

### 4. 异常处理

合理处理异常，区分不同错误类型：

```python
try:
    client.insert('users', data)
except pymysql.IntegrityError:
    # 处理重复数据
    pass
except Exception as e:
    logger.error("插入失败", error=str(e))
    raise
```

### 5. 资源清理

在应用退出时关闭连接池：

```python
import atexit
from py_utility import get_mysql_client

def cleanup():
    get_mysql_client().close()

atexit.register(cleanup)
```

### 6. 查询优化

- 使用索引字段作为查询条件
- 避免SELECT *，只查询需要的列
- 使用LIMIT限制返回行数
- 批量操作使用execute_many

```python
# ✅ 好的实践
client.query(
    "SELECT id, name, email FROM users WHERE status = %s LIMIT 100",
    ('active',)
)

# ❌ 不推荐
client.query("SELECT * FROM users")
```

## 日志记录

客户端会记录以下日志：

- **DEBUG**: SQL执行详情、连接池状态
- **INFO**: 客户端初始化、连接成功
- **WARNING**: 连接失败重试
- **ERROR**: 执行失败、重试耗尽

查看日志：

```python
from py_utility import get_logger

logger = get_logger(__name__)
logger.info("开始查询用户数据")
```

## 测试

### 运行集成测试

```bash
# 设置测试数据库环境变量
export TEST_DB_HOST=localhost
export TEST_DB_PORT=3306
export TEST_DB_USER=root
export TEST_DB_PASSWORD=password
export TEST_DB_NAME=test_trade_system

# 运行测试
cd py-utility
python run_tests.py
```

### 跳过数据库测试

如果没有可用的测试数据库：

```bash
export SKIP_DB_TESTS=1
pytest tests/test_mysql_client.py
```

## 常见问题

### Q1: 如何处理连接超时？

A: 调整超时参数：

```python
client = MySQLClient(
    connect_timeout=30,  # 连接超时30秒
    read_timeout=60,     # 读取超时60秒
    write_timeout=60     # 写入超时60秒
)
```

### Q2: 如何查看连接池状态？

A: 使用ping检查连接健康状态：

```python
if not client.ping():
    logger.warning("数据库连接不健康")
```

### Q3: 如何处理大批量数据？

A: 使用分批处理：

```python
batch_size = 1000
for i in range(0, len(data), batch_size):
    batch = data[i:i+batch_size]
    client.execute_many(sql, batch)
```

### Q4: 为什么WHERE条件必填？

A: 为了防止误操作删除或更新全表数据：

```python
# 如果确实需要删除全表，使用execute方法
client.execute("DELETE FROM users")
```

## 性能建议

1. **使用连接池**：避免频繁创建和关闭连接
2. **批量操作**：使用execute_many代替多次execute
3. **索引优化**：确保查询字段有合适的索引
4. **限制结果集**：使用LIMIT限制返回数据量
5. **预编译语句**：使用参数化查询（已内置）
6. **连接复用**：使用全局实例而不是每次创建新实例

## 相关文档

- [配置管理文档](../README.md#配置管理)
- [日志管理文档](./README_LOGGING.md)
- [项目主文档](../README.md)

