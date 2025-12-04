"""XiaTui推送服务模块

提供单例模式的推送服务，用于发送消息到XiaTui推送平台。
"""

import requests
from typing import Optional


class XiaTuiNotifier:
    """XiaTui推送服务单例类
    
    用于发送消息到XiaTui推送平台，支持设置token并发送文本消息。
    """
    
    _instance: Optional['XiaTuiNotifier'] = None
    _initialized: bool = False
    
    def __new__(cls, token: Optional[str] = None):
        """创建单例实例
        
        Args:
            token: 推送token，仅在首次创建时生效
            
        Returns:
            XiaTuiNotifier: 单例实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, token: Optional[str] = None):
        """初始化推送服务
        
        Args:
            token: 推送token，如果已初始化则忽略
        """
        if not XiaTuiNotifier._initialized:
            if token is None:
                raise ValueError("首次初始化时必须提供token")
            self._token = token
            self._base_url = f"https://wx.xtuis.cn/{token}.send"
            XiaTuiNotifier._initialized = True
    
    @property
    def token(self) -> str:
        """获取当前token
        
        Returns:
            str: 推送token
        """
        return self._token
    
    def send(self, text: str, desp: str = "") -> bool:
        """发送推送消息
        
        Args:
            text: 消息标题
            desp: 消息内容，最大支持64KB
            
        Returns:
            bool: 发送是否成功
            
        Raises:
            RuntimeError: 服务未初始化
        """
        if not XiaTuiNotifier._initialized:
            raise RuntimeError("XiaTuiNotifier未初始化，请先使用token创建实例")
        
        mydata = {
            'text': text,
            'desp': desp
        }
        
        try:
            response = requests.post(self._base_url, data=mydata, timeout=10)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            # 可以在这里添加日志记录
            raise RuntimeError(f"推送消息失败: {e}") from e
    
    @classmethod
    def get_instance(cls) -> Optional['XiaTuiNotifier']:
        """获取单例实例
        
        Returns:
            Optional[XiaTuiNotifier]: 单例实例，如果未初始化则返回None
        """
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """重置单例实例（主要用于测试）
        """
        cls._instance = None
        cls._initialized = False

