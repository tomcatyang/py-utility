# -*- coding: utf-8 -*-
"""
XiaTui推送服务测试脚本
"""

from py_utility.xt.xiatui import XiaTuiNotifier


if __name__ == "__main__":
    # 初始化推送服务
    notifier = XiaTuiNotifier(token="")
    
    # 发送测试消息
    notifier.send(
        text="测试消息标题",
        desp="这是一条测试消息，用于验证推送功能是否正常工作。"
    )
    
    print("消息发送成功！")
