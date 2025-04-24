import akshare as ak
import pandas as pd
import numpy as np
import pymysql
from datetime import datetime
import sys
import os
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from db.db_manager import db_manager

def create_stock_report_table(stock_yjbb_em_df=None, report_date=None, force_recreate=True):
    """
    根据返回数据创建MySQL表
    表名：stock_report
    
    参数:
        stock_yjbb_em_df: pandas.DataFrame, 包含股票业绩报告数据的DataFrame
        report_date: str, 报告日期，用于关联头表
        force_recreate: bool, 是否强制重新创建表，默认为True
    
    返回:
        bool: 表示操作是否成功
    """
    try:
        # 如果未提供数据，则尝试获取
        if stock_yjbb_em_df is None:
            logging.error("错误：未提供数据")
            return False
        
        # 检查是否有数据返回
        if stock_yjbb_em_df.empty:
            logging.info("没有获取到数据，请检查日期参数或稍后再试")
            return False
        
        # 连接到数据库
        if not db_manager.connect():
            logging.error("数据库连接失败")
            return False
        
        # 删除表（如果已存在且需要重新创建）
        if force_recreate:
            logging.info("删除旧表（如果存在）...")
            db_manager.execute("DROP TABLE IF EXISTS stock_report")
        else:
            # 检查表是否存在
            db_manager.execute("SHOW TABLES LIKE 'stock_report'")
            table_exists = db_manager.fetchone()
            if table_exists:
                logging.info("表 stock_report 已存在，不再重新创建")
                return True
        
        logging.info("创建新表 stock_report...")
        
        # 创建表SQL语句
        create_table_sql = """
        CREATE TABLE stock_report (
            id INT AUTO_INCREMENT PRIMARY KEY,
            report_date VARCHAR(20) NOT NULL COMMENT '报告日期',
            stock_code VARCHAR(10) COMMENT '股票代码',
            stock_name VARCHAR(50) COMMENT '股票简称',
            basic_eps DECIMAL(20,4) COMMENT '每股收益',
            diluted_eps DECIMAL(20,4) COMMENT '每股收益(同basic_eps)',
            revenue DECIMAL(20,2) COMMENT '营业总收入',
            revenue_yoy DECIMAL(10,2) COMMENT '营业总收入同比增长',
            revenue_qoq DECIMAL(20,2) COMMENT '营业总收入季度环比增长',
            net_profit DECIMAL(20,2) COMMENT '净利润',
            net_profit_yoy DECIMAL(10,2) COMMENT '净利润同比增长',
            net_profit_qoq DECIMAL(10,2) COMMENT '净利润季度环比增长',
            net_asset_per_share DECIMAL(20,4) COMMENT '每股净资产',
            roe DECIMAL(10,2) COMMENT '净资产收益率',
            cf_per_share DECIMAL(20,4) COMMENT '每股经营现金流量',
            gross_profit_margin DECIMAL(10,2) COMMENT '销售毛利率',
            industry VARCHAR(100) COMMENT '所处行业',
            notice_date DATE COMMENT '最新公告日期',
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX idx_report_date (report_date),
            CONSTRAINT fk_report_date_report FOREIGN KEY (report_date) REFERENCES stock_report_header(report_date) ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票业绩报告';
        """
        
        db_manager.execute(create_table_sql)
        
        logging.info("表创建成功！表结构如下：")
        db_manager.execute("DESCRIBE stock_report")
        for field in db_manager.fetchall():
            logging.info(str(field))
        
        db_manager.commit()
        
        logging.info("表 stock_report 已成功创建！")
        return True
        
    except Exception as e:
        logging.error(f"表创建过程中发生错误: {e}")
        return False

def create_report_header_table(force_recreate=True, report_date="20220331"):
    """
    创建业绩报告头表 stock_report_header，记录查询信息
    
    参数:
        force_recreate: bool, 是否强制重新创建表，默认为True
        report_date: str, 报告日期，格式为YYYYMMDD，默认为20220331
    
    返回:
        bool: 表示操作是否成功
        str: 当前报告日期
    """
    try:
        # 连接到数据库
        if not db_manager.connect():
            logging.error("数据库连接失败")
            return False, None
        
        # 判断是否需要重新创建表
        if force_recreate:
            logging.info("删除头表（如果存在）...")
            db_manager.execute("DROP TABLE IF EXISTS stock_report_header")
            
        # 检查表是否存在
        db_manager.execute("SHOW TABLES LIKE 'stock_report_header'")
        table_exists = db_manager.fetchone()
        
        # 如果表不存在，则创建
        if not table_exists or force_recreate:
            logging.info("创建头表 stock_report_header...")
            
            # 创建表SQL语句
            create_table_sql = """
            CREATE TABLE stock_report_header (
                id INT AUTO_INCREMENT PRIMARY KEY,
                report_date VARCHAR(20) NOT NULL COMMENT '报告日期',
                query_param VARCHAR(50) COMMENT '查询参数',
                record_count INT DEFAULT 0 COMMENT '记录数量',
                status VARCHAR(20) DEFAULT 'PENDING' COMMENT '处理状态',
                remark TEXT COMMENT '备注信息',
                create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                UNIQUE KEY uk_report_date (report_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票业绩报告批次信息';
            """
            
            db_manager.execute(create_table_sql)
            logging.info("头表 stock_report_header 创建成功！")
        
        # 插入新的批次记录
        logging.info(f"创建新记录: {report_date}")
        insert_sql = """
        INSERT INTO stock_report_header 
        (report_date, query_param, status) 
        VALUES (%s, %s, %s)
        """
        
        query_param = f"date={report_date}"
        status = "PENDING"
        
        db_manager.execute(insert_sql, (report_date, query_param, status))
        db_manager.commit()
        
        logging.info("头表记录创建成功！")
        
        return True, report_date
        
    except Exception as e:
        logging.error(f"创建头表时发生错误: {e}")
        return False, None
        
    finally:
        db_manager.close()

def check_existing_query(date_str):
    """
    检查是否存在相同日期的记录
    
    参数:
        date_str: str, 报告日期，格式为YYYYMMDD
        
    返回:
        bool: 表示是否存在相同日期的记录
    """
    try:
        if not db_manager.connect():
            logging.error("数据库连接失败")
            return False
            
        check_sql = """
        SELECT COUNT(*) 
        FROM stock_report_header 
        WHERE report_date = %s
        """
        db_manager.execute(check_sql, (date_str,))
        count = db_manager.fetchone()[0]
        
        return count > 0
        
    except Exception as e:
        logging.error(f"检查查询时间时发生错误: {e}")
        return False
        
    finally:
        db_manager.close()

def delete_report_detail_by_date(date_str):
    """
    根据报告日期删除子表中的数据
    
    参数:
        date_str: str, 报告日期，格式为YYYYMMDD
        
    返回:
        bool: 表示操作是否成功
    """
    try:
        if not db_manager.connect():
            logging.error("数据库连接失败")
            return False
            
        # 直接删除日期对应的子表数据
        delete_sql = """
        DELETE FROM stock_report 
        WHERE report_date = %s
        """
        db_manager.execute(delete_sql, (date_str,))
        
        db_manager.commit()
        logging.info(f"成功删除日期参数 {date_str} 的子表数据")
        return True
        
    except Exception as e:
        logging.error(f"删除子表数据时发生错误: {e}")
        return False
        
    finally:
        db_manager.close()

def get_existing_report_data(date_str):
    """
    根据报告日期获取已存在的报告数据
    
    参数:
        date_str: str, 报告日期，格式为YYYYMMDD
        
    返回:
        list: 包含已存在数据的列表，每个元素是一个字典
    """
    try:
        if not db_manager.connect():
            logging.error("数据库连接失败")
            return []
            
        select_sql = """
        SELECT stock_code, stock_name
        FROM stock_report 
        WHERE report_date = %s
        """
        db_manager.execute(select_sql, (date_str,))
        results = db_manager.fetchall()
        
        existing_data = []
        for row in results:
            data = {
                'stock_code': row[0],
                'stock_name': row[1]
            }
            existing_data.append(data)
            
        return existing_data
        
    except Exception as e:
        logging.error(f"获取已存在数据时发生错误: {e}")
        return []
        
    finally:
        db_manager.close()

def is_record_exists(new_record, existing_records):
    """
    检查新记录是否在已存在的记录中
    
    参数:
        new_record: dict, 新的记录数据
        existing_records: list, 已存在的记录列表
    
    返回:
        bool: 如果记录已存在返回True，否则返回False
    """
    for existing in existing_records:
        if existing['stock_code'] == new_record['stock_code']:
            return True
    return False

def update_header_status(report_date, record_count, status="COMPLETED", remark=None):
    """
    更新头表状态
    
    参数:
        report_date: str, 报告日期
        record_count: int, 记录数量
        status: str, 状态 (PENDING, PROCESSING, COMPLETED, FAILED)
        remark: str, 备注信息
        
    返回:
        bool: 表示操作是否成功
    """
    try:
        if not db_manager.connect():
            logging.error("数据库连接失败")
            return False
            
        update_sql = """
        UPDATE stock_report_header 
        SET record_count = %s, status = %s, remark = %s 
        WHERE report_date = %s
        """
        
        db_manager.execute(update_sql, (record_count, status, remark, report_date))
        db_manager.commit()
        
        logging.info(f"头表状态更新成功！报告日期: {report_date}, 状态: {status}, 记录数: {record_count}")
        return True
        
    except Exception as e:
        logging.error(f"更新头表状态时发生错误: {e}")
        return False
        
    finally:
        db_manager.close()

def insert_report_data(stock_yjbb_em_df=None, report_date=None):
    """
    将数据插入到stock_report表中
    
    参数:
        stock_yjbb_em_df: pandas.DataFrame, 包含股票业绩报告数据的DataFrame
        report_date: str, 报告日期，用于关联头表
    
    返回:
        bool: 表示操作是否成功
        int: 插入的记录数量
    """
    try:
        # 如果未提供数据，则尝试获取
        if stock_yjbb_em_df is None:
            logging.error("错误：未提供数据")
            return False, 0
        
        # 检查是否有数据返回
        if stock_yjbb_em_df.empty:
            logging.info("没有获取到数据，请检查日期参数或稍后再试")
            return False, 0
        
        logging.info(f"准备插入{len(stock_yjbb_em_df)}条业绩报告数据")
        
        # 连接到数据库
        if not db_manager.connect():
            logging.error("数据库连接失败")
            return False, 0
        
        # 准备批量插入数据
        insert_count = 0
        
        # 验证报告日期是否存在
        if report_date is None:
            logging.error("错误：未提供报告日期")
            return False, 0
        
        # 检查头表中是否存在该报告日期
        check_sql = "SELECT 1 FROM stock_report_header WHERE report_date = %s"
        db_manager.execute(check_sql, (report_date,))
        if not db_manager.fetchone():
            logging.error(f"错误：报告日期 {report_date} 在头表中不存在")
            return False, 0
            
        for _, row in stock_yjbb_em_df.iterrows():
            # 准备插入的数据
            insert_data = {
                'report_date': report_date,
                'stock_code': str(row.get('股票代码', '')),
                'stock_name': str(row.get('股票简称', '')),
                'basic_eps': float(row.get('每股收益', None) or 0),
                'diluted_eps': float(row.get('每股收益', None) or 0),  # 使用相同的每股收益值
                'revenue': float(row.get('营业总收入-营业总收入', None) or 0),
                'revenue_yoy': float(row.get('营业总收入-同比增长', None) or 0),
                'revenue_qoq': float(row.get('营业总收入-季度环比增长', None) or 0),
                'net_profit': float(row.get('净利润-净利润', None) or 0),
                'net_profit_yoy': float(row.get('净利润-同比增长', None) or 0),
                'net_profit_qoq': float(row.get('净利润-季度环比增长', None) or 0),
                'net_asset_per_share': float(row.get('每股净资产', None) or 0),
                'roe': float(row.get('净资产收益率', None) or 0),
                'cf_per_share': float(row.get('每股经营现金流量', None) or 0),
                'gross_profit_margin': float(row.get('销售毛利率', None) or 0),
                'industry': str(row.get('所处行业', '')),
                'notice_date': row.get('最新公告日期', None)
            }
            
            # 处理数值字段中的NaN值
            for key, value in insert_data.items():
                if isinstance(value, (int, float)) and (pd.isna(value) or np.isnan(value)):
                    insert_data[key] = None
            
            # 处理日期字段
            if isinstance(insert_data['notice_date'], str):
                try:
                    insert_data['notice_date'] = datetime.strptime(insert_data['notice_date'], '%Y-%m-%d %H:%M:%S').date()
                except ValueError:
                    try:
                        insert_data['notice_date'] = datetime.strptime(insert_data['notice_date'], '%Y-%m-%d').date()
                    except ValueError:
                        insert_data['notice_date'] = None
            
            # 构建插入SQL语句
            columns = ', '.join(insert_data.keys())
            placeholders = ', '.join(['%s'] * len(insert_data))
            insert_sql = f"INSERT INTO stock_report ({columns}) VALUES ({placeholders})"
            
            # 执行插入操作
            db_manager.execute(insert_sql, list(insert_data.values()))
            insert_count += 1
        
        # 提交事务
        db_manager.commit()
        logging.info(f"成功插入{insert_count}条数据到stock_report表")
        
        return True, insert_count
        
    except Exception as e:
        logging.error(f"插入数据时发生错误: {e}")
        return False, 0

if __name__ == "__main__":
    # 测试创建头表和插入记录
    success, report_date = create_report_header_table()
    if success and report_date:
        logging.info(f"成功创建头表和记录，报告日期: {report_date}")
        
        # 测试更新状态
        update_success = update_header_status(report_date, 100, "COMPLETED", "测试完成")
        if update_success:
            logging.info("成功更新头表状态")
