"""XiaTui推送服务模块

提供单例模式的推送服务，用于发送消息到XiaTui推送平台。
支持推送队列机制，自动处理每分钟10条推送限制。
"""

import requests
import queue
import threading
import time
from typing import Optional
from dataclasses import dataclass


@dataclass
class _PushMessage:
    """推送消息数据类"""
    text: str
    desp: str
    future: 'queue.Queue[bool]'  # 用于返回发送结果


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
            
            # 推送队列相关属性
            self._message_queue: queue.Queue[_PushMessage] = queue.Queue()
            self._worker_thread: Optional[threading.Thread] = None
            self._last_send_time: float = 0.0
            self._min_interval: float = 6.0  # 每分钟10条 = 每6秒1条
            self._lock = threading.Lock()
            
            XiaTuiNotifier._initialized = True
    
    @property
    def token(self) -> str:
        """获取当前token
        
        Returns:
            str: 推送token
        """
        return self._token
    
    def send(self, text: str, desp: str = "") -> bool:
        """发送推送消息（异步，加入队列）
        
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
        
        # 如果线程不存在或已停止，则启动线程
        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._start_worker()
        
        # 创建结果队列
        result_queue: queue.Queue[bool] = queue.Queue()
        
        # 创建消息对象并加入队列
        message = _PushMessage(text=text, desp=desp, future=result_queue)
        self._message_queue.put(message)
        
        # 等待发送结果（设置超时避免永久阻塞）
        try:
            return result_queue.get(timeout=300)  # 5分钟超时
        except queue.Empty:
            raise RuntimeError("推送消息超时")
    
    def _send_message(self, text: str, desp: str) -> bool:
        """实际发送推送消息（内部方法）
        
        Args:
            text: 消息标题
            desp: 消息内容
            
        Returns:
            bool: 发送是否成功
            
        Raises:
            RuntimeError: 发送失败
        """
        mydata = {
            'text': text,
            'desp': desp
        }
        
        try:
            response = requests.post(self._base_url, data=mydata, timeout=10)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            raise RuntimeError(f"推送消息失败: {e}") from e
    
    def _start_worker(self) -> None:
        """启动后台处理线程"""
        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._worker_thread = threading.Thread(
                target=self._worker_loop,
                daemon=True,
                name="XiaTuiWorker"
            )
            self._worker_thread.start()
    
    def _worker_loop(self) -> None:
        """后台工作线程循环，处理推送队列
        
        当队列为空且没有新消息时，线程自动退出。
        """
        idle_timeout = 5.0  # 队列为空5秒后退出
        last_message_time: Optional[float] = None  # None表示还未处理过消息
        
        while True:
            try:
                # 从队列获取消息，设置超时以便定期检查队列是否为空
                message = self._message_queue.get(timeout=1.0)
                last_message_time = time.time()  # 更新最后消息时间
            except queue.Empty:
                # 队列为空，检查是否应该退出
                if last_message_time is not None:
                    # 已经处理过消息，检查空闲时间
                    if time.time() - last_message_time >= idle_timeout:
                        # 队列已空闲超过超时时间，退出循环
                        break
                # 如果还未处理过消息，继续等待
                continue
            
            # 速率限制：确保距离上次发送至少间隔min_interval秒
            current_time = time.time()
            sleep_time = 0.0
            
            with self._lock:
                time_since_last_send = current_time - self._last_send_time
                if time_since_last_send < self._min_interval:
                    sleep_time = self._min_interval - time_since_last_send
            
            if sleep_time > 0:
                time.sleep(sleep_time)
                current_time = time.time()
            
            # 发送消息
            try:
                success = self._send_message(message.text, message.desp)
                with self._lock:
                    self._last_send_time = current_time
            except Exception as e:
                success = False
                # 可以在这里添加日志记录
            
            # 将结果返回给调用者
            message.future.put(success)
            self._message_queue.task_done()
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> None:
        """等待队列中的所有消息处理完成
        
        Args:
            timeout: 超时时间（秒），None表示不设置超时
            
        Raises:
            TimeoutError: 如果设置了超时且超时时间已到
        """
        if timeout is None:
            self._message_queue.join()
        else:
            start_time = time.time()
            check_interval = 0.1  # 每0.1秒检查一次
            
            # 循环检查未完成的任务数
            while True:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    raise TimeoutError(f"等待队列处理完成超时（{timeout}秒）")
                
                # 检查未完成的任务数
                if self._message_queue.unfinished_tasks == 0:
                    # 所有任务都已完成
                    break
                
                time.sleep(check_interval)
    
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
        
        会清空队列，工作线程会在队列为空后自动退出。
        """
        if cls._instance is not None:
            # 清空队列
            while not cls._instance._message_queue.empty():
                try:
                    message = cls._instance._message_queue.get_nowait()
                    # 通知调用者消息被取消
                    message.future.put(False)
                    cls._instance._message_queue.task_done()
                except queue.Empty:
                    break
            
            # 等待线程结束（最多等待5秒）
            if cls._instance._worker_thread is not None and cls._instance._worker_thread.is_alive():
                cls._instance._worker_thread.join(timeout=5.0)
        
        cls._instance = None
        cls._initialized = False

