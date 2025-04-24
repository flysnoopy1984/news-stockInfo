from datetime import datetime, date
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from db.db_manager import db_manager

def generate_period_dates():
    """生成从2014年到2100年的特定日期列表"""
    dates = []
    for year in range(2014, 2101):
        dates.extend([
            date(year, 3, 31),
            date(year, 6, 30), 
            date(year, 9, 30),
            date(year, 12, 31)
        ])
    return dates

def init_period_data():
    """初始化stock_period表的period数据"""
    # 生成日期列表
    dates = generate_period_dates()
    
    # 准备SQL语句和参数
    sql = "INSERT INTO stock_period (period) VALUES (%s)"
    # 将日期对象转换为字符串格式
    date_strings = [(d.strftime('%Y%m%d'),) for d in dates]
    
    try:
        # 执行批量插入
        if db_manager.executemany(sql, date_strings):
            db_manager.commit()
            print(f"成功插入{len(dates)}条日期数据")
        else:
            db_manager.rollback()
            print("数据插入失败")
    except Exception as e:
        db_manager.rollback()
        print(f"初始化期间数据出错: {e}")
    finally:
        db_manager.close()

if __name__ == "__main__":
    init_period_data()
