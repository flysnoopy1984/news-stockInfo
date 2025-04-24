import pymysql
import os
from dotenv import load_dotenv
import pathlib
import logging

class DBManager:
    """
    数据库管理类，负责数据库连接、关闭等操作
    使用.env文件中的配置信息进行连接
    """
    _instance = None
    
    def __new__(cls):
        """
        单例模式，确保只有一个数据库连接实例
        """
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """
        初始化数据库管理器
        只在第一次创建实例时执行
        """
        if self._initialized:
            return
            
        # 加载.env文件中的环境变量
        env_path = pathlib.Path(__file__).parent / '.env'
        load_dotenv(dotenv_path=env_path)
        
        # 设置数据库连接参数
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', 'password')
        self.db_name = os.getenv('DB_NAME', 'stock_data')
        self.charset = os.getenv('DB_CHARSET', 'utf8mb4')
        
        # 初始化连接和游标为None
        self.conn = None
        self.cursor = None
        self._initialized = True
    
    def connect(self):
        """
        连接到数据库
        如果数据库不存在，则创建
        """
        try:
            # 先连接不指定数据库
            self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                charset=self.charset
            )
            self.cursor = self.conn.cursor()
            
            # 创建数据库（如果不存在）
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
            
            # 关闭当前连接
            self.close()
            
            # 连接到指定数据库
            self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.db_name,
                charset=self.charset
            )
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            logging.error(f"数据库连接出错: {e}")
            return False
    
    def close(self):
        """
        关闭数据库连接和游标
        """
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def execute(self, sql, params=None):
        """
        执行SQL语句
        """
        try:
            if not self.conn or not self.cursor:
                self.connect()
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            return True
        except Exception as e:
            logging.error(f"执行SQL出错: {e}")
            return False
    
    def executemany(self, sql, params_list):
        """
        批量执行SQL语句
        """
        try:
            if not self.conn or not self.cursor:
                self.connect()
            self.cursor.executemany(sql, params_list)
            return True
        except Exception as e:
            logging.error(f"批量执行SQL出错: {e}")
            return False
    
    def fetchall(self):
        """
        获取所有查询结果
        """
        if self.cursor:
            return self.cursor.fetchall()
        return None
    
    def fetchone(self):
        """
        获取一条查询结果
        """
        if self.cursor:
            return self.cursor.fetchone()
        return None
    
    def commit(self):
        """
        提交事务
        """
        if self.conn:
            self.conn.commit()
    
    def rollback(self):
        """
        回滚事务
        """
        if self.conn:
            self.conn.rollback()
    
    def __del__(self):
        """
        析构函数，确保关闭连接
        """
        self.close()
        
# 创建实例供直接导入使用
db_manager = DBManager()
