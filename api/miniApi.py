import json
import requests
import logging
import os

class XxlJobResult:
    """
    模拟Java中XxlJobHelper的功能
    """
    @staticmethod
    def log(message: str, *args):
        """
        记录日志信息
        """
        formatted_message = message.format(*args) if args else message
        logging.info(formatted_message)
    
    @staticmethod
    def handle_fail(message: str):
        """
        处理任务失败情况
        """
        logging.error(message)
        # 在实际XxlJob环境中可能需要额外操作，如报告任务失败状态

def send_user_sub_message():
    """
    发送用户订阅消息
    """
    try:
      
        # 使用传入的kks_host值或默认值
        kks_host = os.environ.get("KKS_HOST")

        req_url = f"{kks_host}xxlJob/sendStockInfoMsg"
        
        # 发送HTTP POST请求
        logging.info(f"正在发送请求到: {req_url}")
        response = requests.post(req_url, timeout=10)
        
        # 检查响应状态码
        response.raise_for_status()  # 如果状态码不是200，会抛出异常
        XxlJobResult.log("订阅消息已发送")
        
        return True  # 表示任务成功
    except Exception as ex:
        # 处理异常
        XxlJobResult.handle_fail(f"发送订阅信息失败{str(ex)}")
        return False  # 表示任务失败
