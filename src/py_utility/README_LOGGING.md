# 日志管理模块使用指南

## 功能特性

- ✅ 结构化日志（JSON格式）
- ✅ 多日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
- ✅ 自动根据环境设置日志级别
- ✅ 同时输出到控制台和文件
- ✅ 包含丰富的上下文信息（时间戳、文件名、行号、函数名）
- ✅ 支持异常堆栈跟踪
- ✅ 支持日志上下文绑定

## 快速开始

### 基本使用

```python
from app.common.logging import get_logger

# 获取logger实例
logger = get_logger(__name__)

# 记录日志
logger.info("application started")
logger.debug("debug information", user_id=123)
logger.warning("warning message", reason="timeout")
logger.error("error occurred", error_code=500)
```

### 全局函数

```python
from app.common.logging import info, error, debug

# 使用全局函数快速记录日志
info("user logged in", user_id=123)
error("connection failed", host="localhost")
debug("processing data", count=100)
```

## 日志输出格式

日志以JSON格式输出，包含以下字段：

```json
{
  "event": "user action",
  "level": "info",
  "timestamp": "2025-10-12T12:34:56.789012Z",
  "logger": "app.module",
  "filename": "module.py",
  "lineno": 42,
  "func_name": "process_data",
  "user_id": 123,
  "action": "login"
}
```

### 字段说明

- **event**: 日志消息
- **level**: 日志级别（debug/info/warning/error/critical）
- **timestamp**: ISO格式时间戳
- **logger**: logger名称
- **filename**: 源文件名
- **lineno**: 源代码行号
- **func_name**: 函数名
- **自定义字段**: 任何额外传入的参数

## 日志级别

### 级别说明

| 级别 | 数值 | 用途 |
|------|------|------|
| DEBUG | 10 | 详细的调试信息 |
| INFO | 20 | 一般信息 |
| WARNING | 30 | 警告信息 |
| ERROR | 40 | 错误信息 |
| CRITICAL | 50 | 严重错误 |

### 环境默认级别

- **dev**: DEBUG（显示所有日志）
- **test**: INFO（忽略DEBUG日志）
- **prod**: WARNING（只显示警告和错误）

## 初始化

### 自动初始化

```python
from app.common.logging import get_logger

# 第一次调用时自动初始化
# 使用配置文件中的LOG_LEVEL和LOG_FILE
logger = get_logger(__name__)
```

### 手动初始化

```python
from app.common.logging import init_logging

# 手动指定日志级别和文件
init_logging(log_level='DEBUG', log_file='logs/custom.log')
```

### 从配置初始化

```python
from app.common.config import get_config
from app.common.logging import init_logging

config = get_config()
init_logging(
    log_level=config.get('LOG_LEVEL'),
    log_file=config.get('LOG_FILE')
)
```

## 使用示例

### 1. 基本日志记录

```python
from app.common.logging import get_logger

logger = get_logger(__name__)

# 简单消息
logger.info("application started")

# 带参数
logger.info("user logged in", user_id=123, username="alice")

# 多行
logger.info(
    "database query",
    query="SELECT * FROM users",
    duration_ms=45.2,
    rows=100
)
```

### 2. 异常日志

```python
from app.common.logging import get_logger

logger = get_logger(__name__)

try:
    result = 1 / 0
except Exception as e:
    # 自动记录堆栈跟踪
    logger.exception("division error", value=0)
    
    # 或者
    logger.error("error occurred", error=str(e), error_type=type(e).__name__)
```

### 3. 日志上下文

```python
from app.common.logging import get_logger

logger = get_logger(__name__)

# 绑定上下文（在所有后续日志中保留）
logger = logger.bind(request_id="req-123", user="alice")

# 所有日志都会包含request_id和user
logger.info("processing request")
logger.info("request completed", status="success")
```

### 4. 不同模块的日志

```python
# module1.py
from app.common.logging import get_logger
logger = get_logger(__name__)  # logger名称: module1
logger.info("message from module1")

# module2.py  
from app.common.logging import get_logger
logger = get_logger(__name__)  # logger名称: module2
logger.info("message from module2")
```

### 5. 性能监控

```python
import time
from app.common.logging import get_logger

logger = get_logger(__name__)

def process_data(data):
    start = time.time()
    
    # 处理数据...
    
    duration = time.time() - start
    logger.info(
        "data processed",
        data_size=len(data),
        duration_ms=duration * 1000,
        items_per_second=len(data) / duration
    )
```

### 6. 请求日志

```python
from app.common.logging import get_logger

logger = get_logger(__name__)

def handle_request(request):
    # 绑定请求上下文
    request_logger = logger.bind(
        request_id=request.id,
        method=request.method,
        path=request.path,
        ip=request.ip
    )
    
    request_logger.info("request received")
    
    try:
        result = process_request(request)
        request_logger.info("request completed", status=200)
        return result
    except Exception as e:
        request_logger.error("request failed", error=str(e), status=500)
        raise
```

### 7. 数据库操作日志

```python
from app.common.logging import get_logger

logger = get_logger(__name__)

def execute_query(sql, params):
    logger.debug("executing query", sql=sql, params=params)
    
    start = time.time()
    result = db.execute(sql, params)
    duration = time.time() - start
    
    logger.info(
        "query executed",
        sql=sql[:100],  # 截断长SQL
        duration_ms=duration * 1000,
        rows=len(result)
    )
    
    return result
```

## 最佳实践

### 1. 使用模块名称

```python
# ✅ 推荐
logger = get_logger(__name__)

# ❌ 不推荐
logger = get_logger()  # 会使用'root'作为名称
```

### 2. 结构化数据

```python
# ✅ 推荐：使用结构化字段
logger.info("order created", order_id=123, amount=99.99, currency="USD")

# ❌ 不推荐：字符串拼接
logger.info(f"order {order_id} created with amount {amount} {currency}")
```

### 3. 选择合适的日志级别

```python
# DEBUG：调试信息
logger.debug("variable value", x=value, y=another_value)

# INFO：正常流程
logger.info("user registered", user_id=123)

# WARNING：潜在问题
logger.warning("rate limit approaching", current=950, limit=1000)

# ERROR：错误但程序继续
logger.error("api call failed", api="payment", error=str(e))

# CRITICAL：严重错误需要立即关注
logger.critical("database connection lost", attempts=3)
```

### 4. 不要记录敏感信息

```python
# ❌ 不要记录密码、token等敏感信息
logger.info("user login", password=password)  # 危险！

# ✅ 只记录必要的非敏感信息
logger.info("user login", user_id=user.id, success=True)
```

### 5. 异常处理

```python
# ✅ 推荐：使用exception方法自动记录堆栈
try:
    process()
except Exception:
    logger.exception("processing failed")

# ✅ 也可以：手动记录错误信息
except Exception as e:
    logger.error("processing failed", error=str(e), error_type=type(e).__name__)
```

### 6. 避免过度日志

```python
# ❌ 不推荐：循环中记录大量日志
for item in large_list:
    logger.debug("processing item", item=item)  # 可能产生上百万条日志

# ✅ 推荐：汇总记录
logger.info("processing items", total=len(large_list))
# ... 处理 ...
logger.info("items processed", successful=success_count, failed=fail_count)
```

## 配置

### 环境变量配置

```bash
# .env.dev
LOG_LEVEL=DEBUG
LOG_FILE=logs/app_dev.log

# .env.prod
LOG_LEVEL=WARNING
LOG_FILE=/var/log/option_trade/app.log
```

### 程序配置

```python
from app.common.logging import init_logging

# 开发环境
init_logging(log_level='DEBUG', log_file='logs/debug.log')

# 生产环境
init_logging(log_level='WARNING', log_file='/var/log/app.log')

# 只输出到控制台
init_logging(log_level='INFO', log_file=None)
```

## 日志文件

### 日志轮转

建议使用logrotate或类似工具管理日志文件：

```bash
# /etc/logrotate.d/option_trade
/var/log/option_trade/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 appuser appgroup
}
```

### 日志查看

```bash
# 实时查看日志
tail -f logs/app.log

# 查看JSON格式化
tail logs/app.log | jq

# 搜索特定日志
grep '"level":"error"' logs/app.log | jq

# 统计错误数量
grep '"level":"error"' logs/app.log | wc -l
```

## 故障排查

### 日志未输出到文件

```python
import logging

# 手动刷新所有handlers
for handler in logging.root.handlers:
    handler.flush()
```

### 修改日志级别

```python
import logging
from app.common.logging import get_logger

# 临时修改特定logger的级别
logger = get_logger('mymodule')
logging.getLogger('mymodule').setLevel(logging.DEBUG)
```

### 查看当前配置

```python
import logging
from app.common.logging import get_logger

logger = get_logger(__name__)

# 查看当前级别
print(f"Logger level: {logging.root.level}")
print(f"Handlers: {logging.root.handlers}")
```

## 注意事项

1. **性能考虑**：避免在高频循环中记录DEBUG日志
2. **文件权限**：确保应用有权限写入日志文件
3. **磁盘空间**：定期清理或轮转日志文件
4. **敏感信息**：不要记录密码、密钥等敏感数据
5. **日志大小**：控制单条日志的大小，避免记录巨大的对象


