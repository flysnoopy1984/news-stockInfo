import sys
import os
from datetime import datetime
# from dotenv import load_dotenv
import akshare as ak
from typing import Dict, Any, List, Tuple
import logging

# Add project root to Python path
# PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
# if PROJECT_ROOT not in sys.path:
#     sys.path.insert(0, PROJECT_ROOT)

from analyse import createHtml
from db.db_manager import db_manager

import analyse.date_utils as dateUtil

def load_config():
  
    
    # 加载并处理排除股票代码前缀
    except_stock_str = os.getenv('EXCEPT_STOCK', '')
    except_stock = except_stock_str.replace("'", "").split(',') if except_stock_str else []
    
    return {
        'queryNum': int(os.getenv('QUERY_NUM', 5)),
        'multiple': {
            'low': float(os.getenv('MULTIPLE_LOW', 2)),
            'high': float(os.getenv('MULTIPLE_HIGH', -1))
        },
        'exceedMultiple': {
            'low': float(os.getenv('EXCEED_MULTIPLE_LOW', 2)),
            'high': float(os.getenv('EXCEED_MULTIPLE_HIGH', 5))
        },
        'netProfitYoy': {
            'low': float(os.getenv('NET_PROFIT_YOY_LOW', 200)),  # 默认200%
            'high': float(os.getenv('NET_PROFIT_YOY_HIGH', 1000))  # 默认1000%
        },
        'queryDate': os.getenv('QUERY_DATE', 'auto'),
        'exceptStock': except_stock  # 添加排除股票列表
    }



def get_target_report_dates(query_date):
    """根据配置获取目标分析日期"""
    if query_date.lower() == 'auto':
        exceed_date = dateUtil.get_prev_quarter_end()
        prereport_date = dateUtil.get_prev_quarter_end()
    else:
        # 指定日期模式：预告日期为指定日期，超预期分析日期为指定日期所在期间的上一期
        prereport_date = query_date
        exceed_date = query_date
    
    logging.info("\n=== 目标日期确定 ===")
    logging.info(f"- 预告业绩分析日期: {prereport_date}")
    logging.info(f"- 超预期分析当期日期: {exceed_date}")
    return prereport_date, exceed_date

def check_data_availability(date):
    """检查指定日期的数据是否可用"""
    sql = """
    SELECT COUNT(DISTINCT stock_code) FROM stock_prereport WHERE report_date = %s
    """
    
    db_manager.execute(sql, (date,))
    result = db_manager.fetchone()
    count = result[0] if result else 0
    
    return count > 0

def get_exceed_area_stocks(current_report_date, query_num, exceed_multiple_config):
    """获取业绩超预期的股票
    Returns:
        tuple: (exceed_stocks, actual_report_date, report_info)
        - exceed_stocks: 超预期股票列表
        - actual_report_date: 实际使用的业绩报告期
        - report_info: 期间信息字典
    """
    logging.info("\n=== 业绩超预期分析 ===")
    logging.info("分析参数:")

    exceed_multiple_low = exceed_multiple_config['low']
    exceed_multiple_high = exceed_multiple_config['high']
    # 从config中获取exceptStock
    except_stock = []
    try:
        from db.db_manager import db_manager
        from analyse import createHtml
        # 导入配置
        config = load_config()
        except_stock = config.get('exceptStock', [])
    except Exception as e:
        logging.error(f"获取exceptStock配置失败: {e}")
    
    logging.info(f"- 超预期倍数范围: {exceed_multiple_low}~{exceed_multiple_high}倍")
    logging.info(f"- 返回记录数限制: {query_num}")
    logging.info(f"- 排除股票前缀: {except_stock}")
    
    # 报告SQL参数，初始只包含报告日期
    report_params = [current_report_date]
    
    # 获取业绩报告数据SQL模板，每个股票取净利润最高的一条记录
    base_report_sql = """
    WITH StockProfit AS (
        SELECT 
            stock_code,
            stock_name,
            net_profit as actual_profit,
            notice_date,
            net_profit_yoy,  -- 添加净利润同比增长字段
            ROW_NUMBER() OVER(PARTITION BY stock_code ORDER BY net_profit DESC) as rn
        FROM stock_report 
        WHERE report_date = %s
    """
    
    # 添加排除股票的条件 - 使用参数化查询
    exclude_conditions = []
    if except_stock:
        for prefix in except_stock:
            if prefix:
                exclude_conditions.append("stock_code NOT LIKE %s")
                report_params.append(f"{prefix}%")
        
        if exclude_conditions:
            base_report_sql += "    AND (" + " AND ".join(exclude_conditions) + ")\n"
    
    # 完成WITH子句
    base_report_sql += """
    )
    SELECT 
        stock_code,
        stock_name,
        actual_profit,
        notice_date,
        net_profit_yoy  -- 在SELECT中也添加该字段
    FROM StockProfit 
    WHERE rn = 1 order by notice_date desc,actual_profit DESC
    """
    
    report_sql = base_report_sql
    
    # 获取预告数据SQL模板，每个股票取预测值最高的一条记录
    prereport_sql = """
    WITH StockPredict AS (
        SELECT 
            stock_code,
            stock_name,
            predict_value,
            predict_type,
            predict_indicator,
            ROW_NUMBER() OVER(PARTITION BY stock_code ORDER BY predict_value DESC) as rn
        FROM stock_prereport
        WHERE report_date = %s
    )
    SELECT 
        stock_code,
        stock_name,
        predict_value,
        predict_type,
        predict_indicator
    FROM StockPredict
    WHERE rn = 1
    """
    
    try:
        # 获取当期业绩数据
        db_manager.execute(report_sql, tuple(report_params))
        current_reports = {row[0]: row for row in db_manager.fetchall()}
        
        # 如果当期没有数据，获取上期数据
        # actual_report_date = current_report_date
        # if not current_reports:
        #     logging.info(f"\n当期({current_report_date})没有业绩数据，使用上期数据")
        #     db_manager.execute(report_sql, (prev_period_date,))
        #     current_reports = {row[0]: row for row in db_manager.fetchall()}
        #     actual_report_date = prev_period_date
            
        if not current_reports:
            logging.info("\n当期没有业绩数据")
            return [], None, None
            
        # 根据实际使用的业绩报告期获取对应的预告数据
        # current_prereport_date = actual_report_date
        # current_report_date = (actual_report_date)
        
        # 预告SQL参数化查询 - 同样处理排除条件
        prereport_params = [current_report_date]
        prereport_sql_with_filter = prereport_sql
        
        # 如果有排除条件，添加到预告SQL中
        if except_stock:
            # 因为原始SQL已经有WHERE条件，这里使用AND添加
            filter_conditions = []
            for prefix in except_stock:
                if prefix:
                    filter_conditions.append("stock_code NOT LIKE %s")
                    prereport_params.append(f"{prefix}%")
            
            if filter_conditions:
                # 在WHERE子句后添加条件
                where_index = prereport_sql.find("WHERE")
                if where_index > 0:
                    # 找到WHERE后的换行符位置
                    newline_index = prereport_sql.find("\n", where_index)
                    if newline_index > 0:
                        # 在WHERE行的末尾添加AND条件
                        prereport_sql_with_filter = prereport_sql[:newline_index] + " AND (" + " AND ".join(filter_conditions) + ")" + prereport_sql[newline_index:]
        
        # 获取当期预告数据
        if db_manager.execute(prereport_sql_with_filter, tuple(prereport_params)):
            current_prereports = {row[0]: row for row in db_manager.fetchall()}
        else:
            current_prereports = {}
       
        # 获取上期预告数据
        prev_prereport_date = dateUtil.get_prevdate_by_date(current_report_date)
        prereport_params[0] = prev_prereport_date  # 更新日期参数
        if db_manager.execute(prereport_sql_with_filter, tuple(prereport_params)):
            prev_prereports = {row[0]: row for row in db_manager.fetchall()}
        else:
            prev_prereports = {}
        
        logging.info("\n数据周期:")
        logging.info(f"- 业绩报告期: {current_report_date}")
        logging.info(f"- 当期预告期: {current_report_date}, 数据量: {len(current_prereports)}条")
        logging.info(f"- 上期预告期: {prev_prereport_date}, 数据量: {len(prev_prereports)}条")
        
        # 比较所有股票并计算超预期倍数
        all_exceed_stocks = []
        for stock_code, report in current_reports.items():
            prereport = None
            
            # 先查找当期预告数据
            if stock_code in current_prereports:
                prereport = current_prereports[stock_code]
            # 如果没有当期预告，则查找上期预告
            elif stock_code in prev_prereports:
                prereport = prev_prereports[stock_code]
                
            # prereport[2] 是 预测值，大于0 代表是正向增长
            if prereport and prereport[2] > 0:  
                # 记录使用的预告期间
                used_prereport_date = current_report_date if stock_code in current_prereports else prev_prereport_date
                
                exceed_rate = report[2] / prereport[2]  # actual_profit / predict_value
                net_profit_yoy = report[4] if len(report) > 4 and report[4] is not None else None  # 获取净利润同比增长率
                all_exceed_stocks.append((
                    stock_code,            # stock_code
                    report[1],             # stock_name
                    prereport[2],          # prereport_predict
                    report[2],             # actual_profit
                    exceed_rate,           # exceed_rate
                    prereport[3],          # predict_type
                    prereport[4],          # predict_indicator
                    used_prereport_date,   # 预测值对应期间
                    current_report_date,   # 实际业绩期间
                    report[3],             # notice_date
                    net_profit_yoy         # 净利润同比增长率
                ))
        
        # 先按公告日期降序排序，再按超预期倍数降序排序
        all_exceed_stocks.sort(key=lambda x: (x[9], x[4]), reverse=True)
        
        # 筛选在指定倍数范围内的记录，并返回前N条
        exceed_stocks = [stock for stock in all_exceed_stocks if exceed_multiple_low <= stock[4] <= exceed_multiple_high][:query_num]
        
        logging.info(f"\n查询返回记录数: {len(exceed_stocks)}条")
        report_info = {
            'actual_report_date': current_report_date,
            'current_prereport_date': current_report_date,
            'prev_prereport_date': prev_prereport_date
        }
        return exceed_stocks, current_report_date, report_info
        
    except Exception as e:
        logging.error(f"执行SQL出错: {e}")
        return [], None, None

def get_high_change_stocks(report_date, config):
    """获取业绩变动超过指定倍数的股票"""
    logging.info(f"\n=== 业绩预告高变动分析 ===")
    logging.info(f"分析期: {report_date}")
    
    multiple_low = int(config['multiple']['low'] * 100)
    multiple_high = int(config['multiple']['high'] * 100) if config['multiple']['high'] != -1 else float('inf')
    query_num = config['queryNum']
    except_stock = config.get('exceptStock', [])
    
    logging.info(f"- 业绩变动倍数范围: {multiple_low/100}~{multiple_high/100 if multiple_high != float('inf') else '∞'}倍")
    logging.info(f"- 返回记录数限制: {query_num}")
    logging.info(f"- 排除股票前缀: {except_stock}")
    
    # 构建基础SQL
    base_sql = """
    WITH RankedStocks AS (
        SELECT 
            stock_code, 
            stock_name, 
            predict_indicator, 
            change_rate, 
            predict_value, 
            last_year_value, 
            predict_type,
            change_reason, 
            notice_date,
            ROW_NUMBER() OVER (PARTITION BY stock_code ORDER BY change_rate DESC) as rn
        FROM stock_prereport 
        WHERE report_date = %s 
        AND change_rate >= %s
    """
    
    # 初始化参数列表
    params = [report_date, multiple_low]
    
    # 添加排除股票的条件到WITH子句 - 使用参数化查询
    exclude_conditions = []
    if except_stock:
        for prefix in except_stock:
            if prefix:
                exclude_conditions.append("stock_code NOT LIKE %s")
                params.append(f"{prefix}%")  # 直接添加到params列表
        
        if exclude_conditions:
            base_sql += "    AND (" + " AND ".join(exclude_conditions) + ")\n"
    
    # 完成WITH子句
    base_sql += """
    )
    SELECT 
        stock_code, 
        stock_name, 
        predict_indicator, 
        change_rate, 
        predict_value, 
        last_year_value,
        predict_type,
        change_reason, 
        notice_date
    FROM RankedStocks 
    WHERE rn = 1 
    """
    
    # 添加change_rate上限条件（如果有）
    if multiple_high != float('inf'):
        base_sql += " AND change_rate <= %s"
        params.append(multiple_high)
    
    # 添加排序和限制条件
    base_sql += "  ORDER BY notice_date desc,change_rate desc LIMIT %s"
    params.append(query_num)
    
    sql = base_sql
    
    try:
        # 执行SQL并检查是否成功
        if db_manager.execute(sql, tuple(params)):
            results = db_manager.fetchall()
            logging.info(f"查询结果: {len(results)}条记录")
            return results
        else:
            logging.error("SQL执行失败，无法获取结果")
            return []
    except Exception as e:
        logging.error(f"执行SQL出错: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return []

def get_high_profit_growth_stocks(report_date, config):
    """获取净利润同比增长在指定范围内的股票
    
    Args:
        report_date (str): 报告期日期，格式为YYYYMMDD
        config (dict): 配置参数字典
        
    Returns:
        List[Tuple]: 符合条件的股票列表
    """
    logging.info(f"\n=== 净利润同比增长分析 ===")
    logging.info(f"分析期: {report_date}")
    
    # 配置参数
    yoy_low = config['netProfitYoy']['low']  # 百分比值，如200表示200%
    yoy_high = config['netProfitYoy']['high']  # 百分比值，如1000表示1000%
    query_num = config['queryNum']
    except_stock = config.get('exceptStock', [])
    
    logging.info(f"- 净利润同比增长范围: {yoy_low}%~{yoy_high}%")
    logging.info(f"- 返回记录数限制: {query_num}")
    logging.info(f"- 排除股票前缀: {except_stock}")
    
    # 基础SQL
    sql = """
    SELECT 
        stock_code, 
        stock_name,
        net_profit,
        net_profit_yoy,
        notice_date
    FROM stock_report
    WHERE report_date = %s
    AND net_profit > 0
    """
    
    # 参数列表初始化
    params = [report_date]
    
    # 添加排除股票的条件 - 使用参数化查询
    exclude_conditions = []
    if except_stock:
        for prefix in except_stock:
            if prefix:  # 确保前缀不为空
                exclude_conditions.append("stock_code NOT LIKE %s")
                params.append(f"{prefix}%")
        
        if exclude_conditions:
            sql += "AND (" + " AND ".join(exclude_conditions) + ")\n"
    
    # 添加排序和限制
    sql += """
    ORDER BY notice_date DESC, net_profit_yoy DESC
    LIMIT %s
    """
    params.append(query_num)
    
    try:
        # 执行SQL并检查是否成功
        if db_manager.execute(sql, tuple(params)):
            results = db_manager.fetchall()
            logging.info(f"查询结果: {len(results)}条记录")
            return results
        else:
            logging.error("SQL执行失败，无法获取结果")
            return []
    except Exception as e:
        logging.error(f"执行SQL出错: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return []

def get_stock_fund_flow(stock_code):
    """获取单个股票的资金流数据"""
    try:
        # 根据股票代码判断市场
        market = ''
        if stock_code.startswith('300'):
            market = 'bj'
        elif stock_code.startswith('6'):
            market = 'sh'
        elif stock_code.startswith(('001', '002', '003', '004')):
            market = 'sz'
        else:
            return None
            
        # 获取资金流数据
        df = ak.stock_individual_fund_flow(stock=stock_code, market=market)
        return df.sort_values(by='日期', ascending=False).head(5)
    except Exception as e:
        logging.error(f"获取股票 {stock_code} 资金流数据失败: {e}")
        return None

def add_fund_flow_data(stocks: List[Tuple]) -> List[Dict[str, Any]]:
    """为股票数据添加资金流信息"""
    enhanced_stocks = []
    for stock in stocks:
        stock_dict = {
            str(i): value for i, value in enumerate(stock)  # 将元组转换为字典以便添加额外数据
        }
        stock_dict['fund_flow'] = get_stock_fund_flow(stock[0])
        enhanced_stocks.append(stock_dict)
    return enhanced_stocks

def main():
    try:
        config = load_config()
        
        if not db_manager.connect():
            logging.error("数据库连接失败")
            return
        
        prereport_date, exceed_date = get_target_report_dates(config['queryDate'])
        if not prereport_date or not exceed_date:
            logging.error("无法确定目标报告期")
            return
            
        logging.info("\n=== 分析日期概览 ===")
        logging.info(f"当前日期: {datetime.now().strftime('%Y-%m-%d')}")
        logging.info(f"配置日期: {config['queryDate']}")
        logging.info(f"预报业绩分析期: {prereport_date}")
        logging.info(f"超预期分析期: {exceed_date}")
    
        # 预报业绩变动
        high_change_stocks = get_high_change_stocks(prereport_date, config)
        high_change_stocks_with_fund = add_fund_flow_data(high_change_stocks)
        
        # 实际业绩和预测比较报告
        exceed_area_stocks, current_report_date, report_info = get_exceed_area_stocks(exceed_date, config['queryNum'], config['exceedMultiple'])
        exceed_area_stocks_with_fund = add_fund_flow_data(exceed_area_stocks)

        # 净利润同比增长分析
        high_profit_growth_stocks = get_high_profit_growth_stocks(exceed_date, config)
        high_profit_growth_stocks_with_fund = add_fund_flow_data(high_profit_growth_stocks)
        
        # prev_period_date = get_prev_period_date(actual_report_date if actual_report_date else exceed_date)
        # 使用新的HTML生成模块
        output_path = createHtml.generate_html_report(
            prereport_date=prereport_date,
            exceed_date=current_report_date,
            # prev_period_date=prev_period_date,
            high_change_stocks=high_change_stocks_with_fund,
            exceed_area_stocks=exceed_area_stocks_with_fund,
            high_profit_growth_stocks=high_profit_growth_stocks_with_fund,  # 添加净利润同比增长股票数据
            exceed_area_report_info=report_info,
            query_date=config['queryDate']  # 传递queryDate配置
        )
        
        logging.info(f"\n报告生成完成")
        logging.info(f"报告保存路径: {output_path}")
        
    except Exception as e:
        logging.error(f"生成报告时发生错误: {e}")
        import traceback
        logging.error(traceback.format_exc())
    finally:
        db_manager.close()

if __name__ == "__main__":
    main()
