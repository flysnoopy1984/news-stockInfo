import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db.db_manager import db_manager

def check_and_create_tables():
    """
    检查数据库中是否存在必要的表,如果不存在则创建
    """
    try:
        # 连接数据库
        if not db_manager.connect():
            print("数据库连接失败")
            return False
            
        # 获取所有表名
        db_manager.execute("SHOW TABLES")
        existing_tables = {table[0].lower() for table in db_manager.fetchall()}
        
        # 检查并创建表头
        header_tables = {
            'stock_report_header': """
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
            """,
            'stock_prereport_header': """
                CREATE TABLE stock_prereport_header (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    report_date VARCHAR(20) NOT NULL COMMENT '报告日期',
                    query_param VARCHAR(50) COMMENT '查询参数',
                    record_count INT DEFAULT 0 COMMENT '记录数量',
                    status VARCHAR(20) DEFAULT 'PENDING' COMMENT '处理状态',
                    remark TEXT COMMENT '备注信息',
                    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                    UNIQUE KEY uk_report_date (report_date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票业绩预告批次信息';
            """
        }
        
        for table_name, create_sql in header_tables.items():
            if table_name not in existing_tables:
                print(f"表 {table_name} 不存在,准备创建...")
                db_manager.execute(create_sql)
                print(f"表 {table_name} 创建成功")
            else:
                print(f"表 {table_name} 已存在")
        
        # 检查并创建明细表
        detail_tables = {
            'stock_report': """
                CREATE TABLE stock_report (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    report_date VARCHAR(20) NOT NULL COMMENT '报告日期',
                    stock_code VARCHAR(10) COMMENT '股票代码',
                    stock_name VARCHAR(50) COMMENT '股票简称',
                    basic_eps DECIMAL(20,4) COMMENT '每股收益',
                    diluted_eps DECIMAL(20,4) COMMENT '每股收益(同basic_eps)',
                    revenue DECIMAL(20,2) COMMENT '营业总收入',
                    revenue_yoy DECIMAL(10,2) COMMENT '营业总收入同比增长',
                    revenue_qoq DECIMAL(10,2) COMMENT '营业总收入季度环比增长',
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
            """,
            'stock_prereport': """
                CREATE TABLE stock_prereport (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    report_date VARCHAR(20) NOT NULL COMMENT '报告日期',
                    seq_no INT COMMENT '序号',
                    stock_code VARCHAR(10) COMMENT '股票代码',
                    stock_name VARCHAR(50) COMMENT '股票简称',
                    predict_indicator VARCHAR(50) COMMENT '预测指标', 
                    performance_change TEXT COMMENT '业绩变动',
                    predict_value DECIMAL(20,2) COMMENT '预测数值',
                    change_rate DECIMAL(10,2) COMMENT '业绩变动幅度',
                    change_reason TEXT COMMENT '业绩变动原因',
                    predict_type VARCHAR(20) COMMENT '预告类型',
                    last_year_value DECIMAL(20,2) COMMENT '上年同期值',
                    notice_date DATE COMMENT '公告日期',
                    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                    INDEX idx_report_date (report_date),
                    CONSTRAINT fk_report_date FOREIGN KEY (report_date) REFERENCES stock_prereport_header(report_date) ON DELETE CASCADE ON UPDATE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票业绩预告';
            """
        }
        
        for table_name, create_sql in detail_tables.items():
            if table_name not in existing_tables:
                print(f"表 {table_name} 不存在,准备创建...")
                db_manager.execute(create_sql)
                db_manager.commit()
                print(f"表 {table_name} 创建成功")
            else:
                print(f"表 {table_name} 已存在")
        
        return True
        
    except Exception as e:
        print(f"检查和创建表时发生错误: {e}")
        return False
        
    finally:
        db_manager.close()

if __name__ == "__main__":
    check_and_create_tables()
