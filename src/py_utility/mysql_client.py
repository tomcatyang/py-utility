"""
MySQL数据库客户端模块

提供数据库连接池管理、CRUD操作、事务管理、错误处理和自动重连功能。
"""

import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple

import pymysql
from dbutils.pooled_db import PooledDB
from pymysql.cursors import DictCursor

from .config import get_config
from .logging import get_logger

logger = get_logger(__name__)


class MySQLClient:
    """MySQL数据库客户端类
    
    功能：
    - 连接池管理
    - 自动重连
    - 基础CRUD操作
    - 事务管理
    - 健康检查
    - 错误处理
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        pool_size: int = 5,
        max_connections: int = 20,
        connect_timeout: int = 10,
        read_timeout: int = 30,
        write_timeout: int = 30,
    ):
        """初始化MySQL客户端
        
        Args:
            host: 数据库主机地址，为None时从配置读取
            port: 数据库端口，为None时从配置读取
            user: 数据库用户名，为None时从配置读取
            password: 数据库密码，为None时从配置读取
            database: 数据库名称，为None时从配置读取
            pool_size: 连接池初始大小
            max_connections: 最大连接数
            connect_timeout: 连接超时时间（秒）
            read_timeout: 读取超时时间（秒）
            write_timeout: 写入超时时间（秒）
        """
        config = get_config()
        db_config = config.database
        
        # 从配置加载数据库参数（如果未提供）
        self.host = host or db_config.host
        self.port = port or db_config.port
        self.user = user or db_config.user
        self.password = password or db_config.password
        self.database = database or db_config.name
        
        self.pool_size = pool_size
        self.max_connections = max_connections
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
        
        self._pool: Optional[PooledDB] = None
        self._init_pool()
        
        logger.info(
            "MySQL客户端初始化成功",
            host=self.host,
            port=self.port,
            database=self.database,
            pool_size=pool_size,
            max_connections=max_connections
        )
    
    def _init_pool(self):
        """初始化连接池"""
        try:
            self._pool = PooledDB(
                creator=pymysql,
                maxconnections=self.max_connections,
                mincached=self.pool_size,
                maxcached=self.pool_size,
                blocking=True,
                ping=1,  # 自动ping检测连接
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                cursorclass=DictCursor,
                connect_timeout=self.connect_timeout,
                read_timeout=self.read_timeout,
                write_timeout=self.write_timeout,
                autocommit=False,
            )
            logger.debug("连接池初始化成功")
        except Exception as e:
            logger.error("连接池初始化失败", error=str(e), exc_info=True)
            raise
    
    def _get_connection(self):
        """从连接池获取连接
        
        Returns:
            数据库连接对象
            
        Raises:
            Exception: 连接获取失败
        """
        try:
            if self._pool is None:
                self._init_pool()
            return self._pool.connection()
        except Exception as e:
            logger.error("获取数据库连接失败", error=str(e))
            raise
    
    def ping(self) -> bool:
        """检查数据库连接健康状态
        
        Returns:
            bool: 连接正常返回True，否则返回False
        """
        try:
            conn = self._get_connection()
            try:
                conn.ping()
                logger.debug("数据库连接健康检查通过")
                return True
            finally:
                conn.close()
        except Exception as e:
            logger.warning("数据库连接健康检查失败", error=str(e))
            return False
    
    @contextmanager
    def _get_cursor(self, connection=None):
        """获取游标的上下文管理器
        
        Args:
            connection: 数据库连接，为None时自动获取
            
        Yields:
            游标对象
        """
        conn = connection or self._get_connection()
        cursor = conn.cursor()
        owns_connection = connection is None
        
        try:
            yield cursor
        finally:
            cursor.close()
            if owns_connection:
                conn.close()
    
    def execute(
        self,
        sql: str,
        params: Optional[Tuple] = None,
        retry_count: int = 3,
        retry_delay: float = 0.5
    ) -> int:
        """执行SQL语句（INSERT/UPDATE/DELETE）
        
        Args:
            sql: SQL语句
            params: 查询参数
            retry_count: 重试次数
            retry_delay: 重试延迟（秒）
            
        Returns:
            int: 影响的行数
            
        Raises:
            Exception: 执行失败
        """
        last_error = None
        
        for attempt in range(retry_count):
            try:
                conn = self._get_connection()
                try:
                    with self._get_cursor(conn) as cursor:
                        affected_rows = cursor.execute(sql, params or ())
                        conn.commit()
                        
                        logger.debug(
                            "SQL执行成功",
                            sql=sql[:100],
                            params=params,
                            affected_rows=affected_rows
                        )
                        return affected_rows
                except Exception as e:
                    conn.rollback()
                    raise
                finally:
                    conn.close()
                    
            except (pymysql.OperationalError, pymysql.InterfaceError) as e:
                last_error = e
                if attempt < retry_count - 1:
                    delay = retry_delay * (2 ** attempt)  # 指数退避
                    logger.warning(
                        "SQL执行失败，准备重试",
                        attempt=attempt + 1,
                        retry_count=retry_count,
                        delay=delay,
                        error=str(e)
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        "SQL执行失败，重试次数耗尽",
                        sql=sql[:100],
                        error=str(e),
                        exc_info=True
                    )
            except Exception as e:
                logger.error("SQL执行失败", sql=sql[:100], error=str(e), exc_info=True)
                raise
        
        raise last_error or RuntimeError("SQL执行失败")
    
    def execute_many(
        self,
        sql: str,
        params_list: List[Tuple],
        retry_count: int = 3,
        retry_delay: float = 0.5
    ) -> int:
        """批量执行SQL语句
        
        Args:
            sql: SQL语句
            params_list: 参数列表
            retry_count: 重试次数
            retry_delay: 重试延迟（秒）
            
        Returns:
            int: 影响的总行数
            
        Raises:
            Exception: 执行失败
        """
        if not params_list:
            return 0
        
        last_error = None
        
        for attempt in range(retry_count):
            try:
                conn = self._get_connection()
                try:
                    with self._get_cursor(conn) as cursor:
                        affected_rows = cursor.executemany(sql, params_list)
                        conn.commit()
                        
                        logger.debug(
                            "批量SQL执行成功",
                            sql=sql[:100],
                            batch_size=len(params_list),
                            affected_rows=affected_rows
                        )
                        return affected_rows
                except Exception as e:
                    conn.rollback()
                    raise
                finally:
                    conn.close()
                    
            except (pymysql.OperationalError, pymysql.InterfaceError) as e:
                last_error = e
                if attempt < retry_count - 1:
                    delay = retry_delay * (2 ** attempt)
                    logger.warning(
                        "批量SQL执行失败，准备重试",
                        attempt=attempt + 1,
                        retry_count=retry_count,
                        delay=delay,
                        error=str(e)
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        "批量SQL执行失败，重试次数耗尽",
                        sql=sql[:100],
                        batch_size=len(params_list),
                        error=str(e),
                        exc_info=True
                    )
            except Exception as e:
                logger.error(
                    "批量SQL执行失败",
                    sql=sql[:100],
                    batch_size=len(params_list),
                    error=str(e),
                    exc_info=True
                )
                raise
        
        raise last_error or RuntimeError("批量SQL执行失败")
    
    def query(
        self,
        sql: str,
        params: Optional[Tuple] = None,
        retry_count: int = 3,
        retry_delay: float = 0.5
    ) -> List[Dict[str, Any]]:
        """执行查询SQL语句
        
        Args:
            sql: SQL语句
            params: 查询参数
            retry_count: 重试次数
            retry_delay: 重试延迟（秒）
            
        Returns:
            List[Dict]: 查询结果列表
            
        Raises:
            Exception: 查询失败
        """
        last_error = None
        
        for attempt in range(retry_count):
            try:
                conn = self._get_connection()
                try:
                    with self._get_cursor(conn) as cursor:
                        cursor.execute(sql, params or ())
                        results = cursor.fetchall()
                        
                        logger.debug(
                            "SQL查询成功",
                            sql=sql[:100],
                            params=params,
                            result_count=len(results)
                        )
                        return results
                finally:
                    conn.close()
                    
            except (pymysql.OperationalError, pymysql.InterfaceError) as e:
                last_error = e
                if attempt < retry_count - 1:
                    delay = retry_delay * (2 ** attempt)
                    logger.warning(
                        "SQL查询失败，准备重试",
                        attempt=attempt + 1,
                        retry_count=retry_count,
                        delay=delay,
                        error=str(e)
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        "SQL查询失败，重试次数耗尽",
                        sql=sql[:100],
                        error=str(e),
                        exc_info=True
                    )
            except Exception as e:
                logger.error("SQL查询失败", sql=sql[:100], error=str(e), exc_info=True)
                raise
        
        raise last_error or RuntimeError("SQL查询失败")
    
    def query_one(
        self,
        sql: str,
        params: Optional[Tuple] = None,
        retry_count: int = 3,
        retry_delay: float = 0.5
    ) -> Optional[Dict[str, Any]]:
        """执行查询SQL语句，返回单条记录
        
        Args:
            sql: SQL语句
            params: 查询参数
            retry_count: 重试次数
            retry_delay: 重试延迟（秒）
            
        Returns:
            Optional[Dict]: 查询结果，无结果返回None
            
        Raises:
            Exception: 查询失败
        """
        results = self.query(sql, params, retry_count, retry_delay)
        return results[0] if results else None
    
    @contextmanager
    def transaction(self):
        """事务上下文管理器
        
        使用示例:
            with client.transaction() as cursor:
                cursor.execute("INSERT INTO ...")
                cursor.execute("UPDATE ...")
        
        Yields:
            游标对象
            
        Raises:
            Exception: 事务执行失败时回滚并抛出异常
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            yield cursor
            conn.commit()
            logger.debug("事务提交成功")
        except Exception as e:
            conn.rollback()
            logger.error("事务回滚", error=str(e), exc_info=True)
            raise
        finally:
            cursor.close()
            conn.close()
    
    def insert(
        self,
        table: str,
        data: Dict[str, Any],
        retry_count: int = 3,
        retry_delay: float = 0.5
    ) -> int:
        """插入单条记录
        
        Args:
            table: 表名
            data: 数据字典
            retry_count: 重试次数
            retry_delay: 重试延迟（秒）
            
        Returns:
            int: 插入记录的ID
            
        Raises:
            Exception: 插入失败
        """
        if not data:
            raise ValueError("插入数据不能为空")
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        last_error = None
        
        for attempt in range(retry_count):
            try:
                conn = self._get_connection()
                try:
                    with self._get_cursor(conn) as cursor:
                        cursor.execute(sql, tuple(data.values()))
                        conn.commit()
                        last_id = cursor.lastrowid
                        
                        logger.debug(
                            "记录插入成功",
                            table=table,
                            last_id=last_id,
                            data=data
                        )
                        return last_id
                except Exception as e:
                    conn.rollback()
                    raise
                finally:
                    conn.close()
                    
            except (pymysql.OperationalError, pymysql.InterfaceError) as e:
                last_error = e
                if attempt < retry_count - 1:
                    delay = retry_delay * (2 ** attempt)
                    logger.warning(
                        "记录插入失败，准备重试",
                        attempt=attempt + 1,
                        retry_count=retry_count,
                        delay=delay,
                        error=str(e)
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        "记录插入失败，重试次数耗尽",
                        table=table,
                        error=str(e),
                        exc_info=True
                    )
            except Exception as e:
                logger.error("记录插入失败", table=table, error=str(e), exc_info=True)
                raise
        
        raise last_error or RuntimeError("记录插入失败")
    
    def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: str,
        where_params: Optional[Tuple] = None,
        retry_count: int = 3,
        retry_delay: float = 0.5
    ) -> int:
        """更新记录
        
        Args:
            table: 表名
            data: 更新数据字典
            where: WHERE条件
            where_params: WHERE参数
            retry_count: 重试次数
            retry_delay: 重试延迟（秒）
            
        Returns:
            int: 影响的行数
            
        Raises:
            Exception: 更新失败
        """
        if not data:
            raise ValueError("更新数据不能为空")
        if not where:
            raise ValueError("WHERE条件不能为空")
        
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        params = tuple(data.values()) + (where_params or ())
        
        affected_rows = self.execute(sql, params, retry_count, retry_delay)
        
        logger.debug(
            "记录更新成功",
            table=table,
            where=where,
            affected_rows=affected_rows
        )
        return affected_rows
    
    def delete(
        self,
        table: str,
        where: str,
        where_params: Optional[Tuple] = None,
        retry_count: int = 3,
        retry_delay: float = 0.5
    ) -> int:
        """删除记录
        
        Args:
            table: 表名
            where: WHERE条件
            where_params: WHERE参数
            retry_count: 重试次数
            retry_delay: 重试延迟（秒）
            
        Returns:
            int: 影响的行数
            
        Raises:
            Exception: 删除失败
        """
        if not where:
            raise ValueError("WHERE条件不能为空，防止误删全表")
        
        sql = f"DELETE FROM {table} WHERE {where}"
        affected_rows = self.execute(sql, where_params, retry_count, retry_delay)
        
        logger.debug(
            "记录删除成功",
            table=table,
            where=where,
            affected_rows=affected_rows
        )
        return affected_rows
    
    def close(self):
        """关闭连接池"""
        if self._pool:
            self._pool.close()
            self._pool = None
            logger.info("MySQL连接池已关闭")


# 全局MySQL客户端实例
_mysql_client: Optional[MySQLClient] = None


def init_mysql_client(**kwargs) -> MySQLClient:
    """初始化全局MySQL客户端实例
    
    Args:
        **kwargs: MySQLClient构造函数参数
        
    Returns:
        MySQLClient: 客户端实例
    """
    global _mysql_client
    _mysql_client = MySQLClient(**kwargs)
    return _mysql_client


def get_mysql_client() -> MySQLClient:
    """获取全局MySQL客户端实例
    
    Returns:
        MySQLClient: 客户端实例
        
    Raises:
        RuntimeError: 客户端未初始化
    """
    global _mysql_client
    if _mysql_client is None:
        # 自动初始化
        _mysql_client = MySQLClient()
    return _mysql_client

