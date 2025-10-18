# -*- coding: utf-8 -*-
"""
MySQL客户端模块测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from py_utility import MySQLClient, get_mysql_client, init_mysql_client


class TestMySQLClient:
    """MySQL客户端测试"""
    
    def test_init_with_default_config(self):
        """测试使用默认配置初始化"""
        with patch('py_utility.mysql_client.get_config') as mock_get_config:
            # 模拟配置
            mock_config = Mock()
            mock_config.database.host = "localhost"
            mock_config.database.port = 3306
            mock_config.database.user = "root"
            mock_config.database.password = ""
            mock_config.database.name = "test_db"
            mock_get_config.return_value = mock_config
            
            # 模拟连接池
            with patch('py_utility.mysql_client.PooledDB') as mock_pooled_db:
                mock_pool = Mock()
                mock_pooled_db.return_value = mock_pool
                
                # 创建客户端
                client = MySQLClient()
                
                # 验证配置
                assert client.host == "localhost"
                assert client.port == 3306
                assert client.user == "root"
                assert client.password == ""
                assert client.database == "test_db"
    
    def test_init_with_custom_config(self):
        """测试使用自定义配置初始化"""
        with patch('py_utility.mysql_client.get_config') as mock_get_config:
            # 模拟配置
            mock_config = Mock()
            mock_config.database.host = "localhost"
            mock_config.database.port = 3306
            mock_config.database.user = "root"
            mock_config.database.password = ""
            mock_config.database.name = "test_db"
            mock_get_config.return_value = mock_config
            
            # 模拟连接池
            with patch('py_utility.mysql_client.PooledDB') as mock_pooled_db:
                mock_pool = Mock()
                mock_pooled_db.return_value = mock_pool
                
                # 创建客户端，使用自定义配置
                client = MySQLClient(
                    host="custom_host",
                    port=3307,
                    user="custom_user",
                    password="custom_password",
                    database="custom_db",
                    pool_size=10,
                    max_connections=30
                )
                
                # 验证配置
                assert client.host == "custom_host"
                assert client.port == 3307
                assert client.user == "custom_user"
                assert client.password == "custom_password"
                assert client.database == "custom_db"
                assert client.pool_size == 10
                assert client.max_connections == 30
    
    def test_ping_success(self):
        """测试ping成功"""
        with patch('py_utility.mysql_client.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.database.host = "localhost"
            mock_config.database.port = 3306
            mock_config.database.user = "root"
            mock_config.database.password = ""
            mock_config.database.name = "test_db"
            mock_get_config.return_value = mock_config
            
            with patch('py_utility.mysql_client.PooledDB') as mock_pooled_db:
                mock_pool = Mock()
                mock_conn = Mock()
                mock_conn.ping.return_value = None
                mock_pool.connection.return_value = mock_conn
                mock_pooled_db.return_value = mock_pool
                
                client = MySQLClient()
                result = client.ping()
                
                assert result is True
                mock_conn.ping.assert_called_once()
                mock_conn.close.assert_called_once()
    
    def test_ping_failure(self):
        """测试ping失败"""
        with patch('py_utility.mysql_client.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.database.host = "localhost"
            mock_config.database.port = 3306
            mock_config.database.user = "root"
            mock_config.database.password = ""
            mock_config.database.name = "test_db"
            mock_get_config.return_value = mock_config
            
            with patch('py_utility.mysql_client.PooledDB') as mock_pooled_db:
                mock_pool = Mock()
                mock_pool.connection.side_effect = Exception("Connection failed")
                mock_pooled_db.return_value = mock_pool
                
                client = MySQLClient()
                result = client.ping()
                
                assert result is False
    
    def test_execute_success(self):
        """测试执行SQL成功"""
        with patch('py_utility.mysql_client.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.database.host = "localhost"
            mock_config.database.port = 3306
            mock_config.database.user = "root"
            mock_config.database.password = ""
            mock_config.database.name = "test_db"
            mock_get_config.return_value = mock_config
            
            with patch('py_utility.mysql_client.PooledDB') as mock_pooled_db:
                mock_pool = Mock()
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_cursor.execute.return_value = 1
                mock_conn.cursor.return_value = mock_cursor
                mock_pool.connection.return_value = mock_conn
                mock_pooled_db.return_value = mock_pool
                
                client = MySQLClient()
                result = client.execute("INSERT INTO test (name) VALUES (%s)", ("test",))
                
                assert result == 1
                mock_cursor.execute.assert_called_once_with("INSERT INTO test (name) VALUES (%s)", ("test",))
                mock_conn.commit.assert_called_once()
                mock_conn.close.assert_called_once()
    
    def test_query_success(self):
        """测试查询成功"""
        with patch('py_utility.mysql_client.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.database.host = "localhost"
            mock_config.database.port = 3306
            mock_config.database.user = "root"
            mock_config.database.password = ""
            mock_config.database.name = "test_db"
            mock_get_config.return_value = mock_config
            
            with patch('py_utility.mysql_client.PooledDB') as mock_pooled_db:
                mock_pool = Mock()
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_cursor.fetchall.return_value = [{"id": 1, "name": "test"}]
                mock_conn.cursor.return_value = mock_cursor
                mock_pool.connection.return_value = mock_conn
                mock_pooled_db.return_value = mock_pool
                
                client = MySQLClient()
                result = client.query("SELECT * FROM test WHERE id = %s", (1,))
                
                assert result == [{"id": 1, "name": "test"}]
                mock_cursor.execute.assert_called_once_with("SELECT * FROM test WHERE id = %s", (1,))
                mock_cursor.fetchall.assert_called_once()
                mock_conn.close.assert_called_once()
    
    def test_query_one_success(self):
        """测试查询单条记录成功"""
        with patch('py_utility.mysql_client.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.database.host = "localhost"
            mock_config.database.port = 3306
            mock_config.database.user = "root"
            mock_config.database.password = ""
            mock_config.database.name = "test_db"
            mock_get_config.return_value = mock_config
            
            with patch('py_utility.mysql_client.PooledDB') as mock_pooled_db:
                mock_pool = Mock()
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_cursor.fetchall.return_value = [{"id": 1, "name": "test"}]
                mock_conn.cursor.return_value = mock_cursor
                mock_pool.connection.return_value = mock_conn
                mock_pooled_db.return_value = mock_pool
                
                client = MySQLClient()
                result = client.query_one("SELECT * FROM test WHERE id = %s", (1,))
                
                assert result == {"id": 1, "name": "test"}
    
    def test_query_one_empty(self):
        """测试查询单条记录为空"""
        with patch('py_utility.mysql_client.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.database.host = "localhost"
            mock_config.database.port = 3306
            mock_config.database.user = "root"
            mock_config.database.password = ""
            mock_config.database.name = "test_db"
            mock_get_config.return_value = mock_config
            
            with patch('py_utility.mysql_client.PooledDB') as mock_pooled_db:
                mock_pool = Mock()
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_cursor.fetchall.return_value = []
                mock_conn.cursor.return_value = mock_cursor
                mock_pool.connection.return_value = mock_conn
                mock_pooled_db.return_value = mock_pool
                
                client = MySQLClient()
                result = client.query_one("SELECT * FROM test WHERE id = %s", (1,))
                
                assert result is None
    
    def test_insert_success(self):
        """测试插入成功"""
        with patch('py_utility.mysql_client.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.database.host = "localhost"
            mock_config.database.port = 3306
            mock_config.database.user = "root"
            mock_config.database.password = ""
            mock_config.database.name = "test_db"
            mock_get_config.return_value = mock_config
            
            with patch('py_utility.mysql_client.PooledDB') as mock_pooled_db:
                mock_pool = Mock()
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_cursor.lastrowid = 123
                mock_conn.cursor.return_value = mock_cursor
                mock_pool.connection.return_value = mock_conn
                mock_pooled_db.return_value = mock_pool
                
                client = MySQLClient()
                result = client.insert("test", {"name": "test", "age": 25})
                
                assert result == 123
                mock_cursor.execute.assert_called_once()
                mock_conn.commit.assert_called_once()
    
    def test_update_success(self):
        """测试更新成功"""
        with patch('py_utility.mysql_client.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.database.host = "localhost"
            mock_config.database.port = 3306
            mock_config.database.user = "root"
            mock_config.database.password = ""
            mock_config.database.name = "test_db"
            mock_get_config.return_value = mock_config
            
            with patch('py_utility.mysql_client.PooledDB') as mock_pooled_db:
                mock_pool = Mock()
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_cursor.execute.return_value = 1
                mock_conn.cursor.return_value = mock_cursor
                mock_pool.connection.return_value = mock_conn
                mock_pooled_db.return_value = mock_pool
                
                client = MySQLClient()
                result = client.update("test", {"age": 26}, "id = %s", (1,))
                
                assert result == 1
                mock_cursor.execute.assert_called_once()
                mock_conn.commit.assert_called_once()
    
    def test_delete_success(self):
        """测试删除成功"""
        with patch('py_utility.mysql_client.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.database.host = "localhost"
            mock_config.database.port = 3306
            mock_config.database.user = "root"
            mock_config.database.password = ""
            mock_config.database.name = "test_db"
            mock_get_config.return_value = mock_config
            
            with patch('py_utility.mysql_client.PooledDB') as mock_pooled_db:
                mock_pool = Mock()
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_cursor.execute.return_value = 1
                mock_conn.cursor.return_value = mock_cursor
                mock_pool.connection.return_value = mock_conn
                mock_pooled_db.return_value = mock_pool
                
                client = MySQLClient()
                result = client.delete("test", "id = %s", (1,))
                
                assert result == 1
                mock_cursor.execute.assert_called_once()
                mock_conn.commit.assert_called_once()
    
    def test_transaction_success(self):
        """测试事务成功"""
        with patch('py_utility.mysql_client.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.database.host = "localhost"
            mock_config.database.port = 3306
            mock_config.database.user = "root"
            mock_config.database.password = ""
            mock_config.database.name = "test_db"
            mock_get_config.return_value = mock_config
            
            with patch('py_utility.mysql_client.PooledDB') as mock_pooled_db:
                mock_pool = Mock()
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_conn.cursor.return_value = mock_cursor
                mock_pool.connection.return_value = mock_conn
                mock_pooled_db.return_value = mock_pool
                
                client = MySQLClient()
                
                with client.transaction() as cursor:
                    cursor.execute("INSERT INTO test (name) VALUES (%s)", ("test",))
                
                mock_cursor.execute.assert_called_once()
                mock_conn.commit.assert_called_once()
                mock_cursor.close.assert_called_once()
                mock_conn.close.assert_called_once()
    
    def test_transaction_rollback(self):
        """测试事务回滚"""
        with patch('py_utility.mysql_client.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.database.host = "localhost"
            mock_config.database.port = 3306
            mock_config.database.user = "root"
            mock_config.database.password = ""
            mock_config.database.name = "test_db"
            mock_get_config.return_value = mock_config
            
            with patch('py_utility.mysql_client.PooledDB') as mock_pooled_db:
                mock_pool = Mock()
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_conn.cursor.return_value = mock_cursor
                mock_pool.connection.return_value = mock_conn
                mock_pooled_db.return_value = mock_pool
                
                client = MySQLClient()
                
                with pytest.raises(Exception):
                    with client.transaction() as cursor:
                        cursor.execute("INSERT INTO test (name) VALUES (%s)", ("test",))
                        raise Exception("Test error")
                
                mock_conn.rollback.assert_called_once()
                mock_cursor.close.assert_called_once()
                mock_conn.close.assert_called_once()
    
    def test_close(self):
        """测试关闭连接池"""
        with patch('py_utility.mysql_client.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.database.host = "localhost"
            mock_config.database.port = 3306
            mock_config.database.user = "root"
            mock_config.database.password = ""
            mock_config.database.name = "test_db"
            mock_get_config.return_value = mock_config
            
            with patch('py_utility.mysql_client.PooledDB') as mock_pooled_db:
                mock_pool = Mock()
                mock_pooled_db.return_value = mock_pool
                
                client = MySQLClient()
                client.close()
                
                mock_pool.close.assert_called_once()
                assert client._pool is None


class TestGlobalFunctions:
    """全局函数测试"""
    
    def test_get_mysql_client(self):
        """测试获取全局MySQL客户端"""
        with patch('py_utility.mysql_client.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.database.host = "localhost"
            mock_config.database.port = 3306
            mock_config.database.user = "root"
            mock_config.database.password = ""
            mock_config.database.name = "test_db"
            mock_get_config.return_value = mock_config
            
            with patch('py_utility.mysql_client.PooledDB') as mock_pooled_db:
                mock_pool = Mock()
                mock_pooled_db.return_value = mock_pool
                
                client = get_mysql_client()
                assert isinstance(client, MySQLClient)
    
    def test_init_mysql_client(self):
        """测试初始化全局MySQL客户端"""
        with patch('py_utility.mysql_client.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.database.host = "localhost"
            mock_config.database.port = 3306
            mock_config.database.user = "root"
            mock_config.database.password = ""
            mock_config.database.name = "test_db"
            mock_get_config.return_value = mock_config
            
            with patch('py_utility.mysql_client.PooledDB') as mock_pooled_db:
                mock_pool = Mock()
                mock_pooled_db.return_value = mock_pool
                
                client = init_mysql_client(host="custom_host")
                assert isinstance(client, MySQLClient)
                assert client.host == "custom_host"


if __name__ == "__main__":
    pytest.main([__file__])
