import logging
import os
import sys
from datetime import datetime

def configure_logging():
    """
    配置内置日志系统
    这个函数会配置根日志记录器，让所有使用logging模块的代码都能共享相同的配置
    """
    # 创建日志目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "log")
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建固定日志文件名，只包含年月
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m')}.log")
    
    # 配置根日志记录器
    root_logger = logging.getLogger()  # 获取根日志记录器
    root_logger.setLevel(logging.INFO)
    
    # 如果根日志记录器已经有处理器，先清除它们
    if root_logger.handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    # 创建格式器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # 创建多种控制台处理器，确保在各种环境下都能正确显示日志
    
    # 1. 标准控制台处理器 (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # 2. 标准错误处理器 (stderr)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.INFO)
    stderr_handler.setFormatter(formatter)
    
    # 3. 直接print处理器
    class PrintHandler(logging.Handler):
        def emit(self, record):
            try:
                msg = self.format(record)
                # 使用多种输出方式确保日志显示
                print(msg)
                print(msg, file=sys.stderr)
                # 强制刷新
                sys.stdout.flush()
                sys.stderr.flush()
            except Exception:
                self.handleError(record)
    
    print_handler = PrintHandler()
    print_handler.setLevel(logging.INFO)
    print_handler.setFormatter(formatter)
    
    # 4. VSCode专用处理器
    class VSCodeDebugHandler(logging.Handler):
        def emit(self, record):
            try:
                msg = self.format(record)
                # VSCode调试环境下的专用输出
                # if hasattr(sys, '__stdout__'):
                #     print(f"【VSCode调试日志】: {msg}", file=sys.__stdout__)
                #     sys.__stdout__.flush()
                # 尝试直接写入控制台
                try:
                    # 尝试直接访问控制台
                    with open('/dev/tty', 'w') as tty:
                        tty.write(f"【控制台直接输出】: {msg}\n")
                        tty.flush()
                except:
                    pass  # 忽略错误
            except Exception:
                self.handleError(record)
    
    # vscode_handler = VSCodeDebugHandler()
    # vscode_handler.setLevel(logging.INFO)
    # vscode_handler.setFormatter(formatter)
    
    # 添加处理器到根日志记录器（只保留必要的处理器，避免重复输出）
    root_logger.addHandler(file_handler)    # 输出到文件
    root_logger.addHandler(console_handler) # 输出到控制台
    
    # # 根据环境选择性添加VSCode处理器
    # if hasattr(sys, '__stdout__'):  # 只在VSCode调试环境中添加
    #     root_logger.addHandler(vscode_handler)
    
    # 注释掉可能导致重复输出的处理器
    # root_logger.addHandler(stderr_handler)
    # root_logger.addHandler(print_handler)
    
    # 在初始化时强制输出消息确认日志已配置
    print("\n======= 日志系统已初始化 =======")
    print(f"日志文件: {log_file}")
    print("日志输出已配置到: 控制台(stdout), 文件")
    if hasattr(sys, '__stdout__'):
        print("VSCode调试模式下的日志输出已配置")
    print("============================\n")
    
    # 设置日志的全局捕获器，确保即使没有处理器的日志也能显示
    def global_excepthook(exc_type, exc_value, traceback):
        # 使用多种方式输出未捕获的异常
        logging.error("未捕获的异常:", exc_info=(exc_type, exc_value, traceback))
        print(f"ERROR: {exc_type.__name__}: {exc_value}", file=sys.stderr)
    
    # 替换系统的默认异常处理器
    sys.excepthook = global_excepthook

# 在模块导入时自动配置日志，确保所有地方都能正常使用日志
configure_logging()
