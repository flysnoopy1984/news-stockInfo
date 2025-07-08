import sys
import os
import dotenv
from datetime import datetime
import traceback

# 添加项目根目录到Python路径
# PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# if PROJECT_ROOT not in sys.path:
#     sys.path.insert(0, PROJECT_ROOT)
# 导入日志模块，配置会自动运行
from log.logger import configure_logging  # 模块导入时已自动配置
import logging

# 导入自定义模块
from db.report.main_report import process_report_data
from db.pre.main_preReport import process_preReport_data

from analyse.date_utils import get_next_quarter_end, get_prev_quarter_end,get_prev_prev_quarter_end
from analyse.generate_report import main as generate_report_main

from api.miniApi import send_user_sub_message
 
dotenv.load_dotenv()
# 使用内置的logging模块记录启动信息
logging.info("xxlJobRun启动")

def process_daily_report(date=None):
    """
    处理每日业绩报告和业绩预告数据
    
    参数:
        date (str, optional): 指定处理日期，格式为'YYYYMMDD'。如果为None，则自动计算日期。
    
    返回:
        tuple: (bool, bool) 表示(业绩报告处理结果, 业绩预告处理结果)
        
    说明:
        1. 如果指定了日期，则两种数据都使用指定的日期
        2. 如果没有指定日期：
           - 业绩报告使用当期日期（如20250402应使用20250331）
           - 业绩预告使用下期日期（如20250402应使用20250630）
    """
    try:
        # 获取日期参数并打印
        current_date = datetime.now()
        logging.info("=== 日期参数 ===")
        logging.info(f"当前日期: {current_date.strftime('%Y-%m-%d')}")
        
        # 确定处理日期
        report_date, prereport_date = _determine_dates(date)
        logging.info(f"业绩报告处理日期: {report_date}")
        logging.info(f"业绩预告处理日期: {prereport_date}")

        # 预告数据
        prereport_result = _process_prereport(prereport_date)
        
        # 处理业绩报告数据
        report_result = _process_report(report_date)
        
        # 生成分析报告
        _generate_report()
        
        return report_result, prereport_result
        
    except KeyboardInterrupt:
        logging.warning("操作已取消")
        return False, False
    except Exception as e:
        logging.error(f"处理数据时发生错误: {e}")
        logging.error(traceback.format_exc())
        return False, False

def _determine_dates(date):
    """
    根据输入参数确定处理日期
    
    参数:
        date (str, optional): 指定处理日期，格式为'YYYYMMDD'
        
    返回:
        tuple: (report_date, prereport_date) 两个日期字符串
    """
    if date:
        # 如果指定了日期，则两种数据都使用指定的日期
        return date, date
    else:
        # 都是用上一个季度作为日期，比如今天4月21 那么就是0330 这个档
        prereport_date = get_prev_quarter_end()  
        report_date = get_prev_quarter_end()  
        
        return report_date, prereport_date

def _process_report(report_date):
    """
    处理业绩报告数据
    
    参数:
        report_date (str): 处理日期，格式为'YYYYMMDD'
        
    返回:
        bool: 处理是否成功
    """
    try:
        logging.info("=== 处理业绩报告数据 ===")
        report_result = process_report_data(date=report_date)
        # 如果只是没有获取到数据，认为是正常情况
        if report_result is False:
            logging.info("业绩报告：没有获取到数据")
            report_result = True
        return report_result
    except Exception as e:
        logging.error(f"业绩报告数据处理出错: {e}")
        logging.error(traceback.format_exc())
        return False

def _process_prereport(prereport_date):
    """
    处理业绩预告数据
    
    参数:
        prereport_date (str): 处理日期，格式为'YYYYMMDD'
        
    返回:
        bool: 处理是否成功
    """
    try:
        logging.info("=== 处理业绩预告数据 ===")
        prereport_result = process_preReport_data(date=prereport_date)
        # 如果只是没有获取到数据，认为是正常情况
        if prereport_result is False:
            logging.info("业绩预告：没有获取到数据")
            prereport_result = True
        return prereport_result
    except Exception as e:
        logging.error(f"业绩预告数据处理出错: {e}")
        logging.error(traceback.format_exc())
        return False

def _generate_report():
    """
    生成分析报告
    """
    try:
        logging.info("=== 生成分析报告 ===")
        generate_report_main()
    except Exception as e:
        logging.error(f"生成分析报告时出错: {e}")
        logging.error(traceback.format_exc())

if __name__ == "__main__":

    """加载.env配置文件"""


    # 从命令行参数获取日期

    date_param = sys.argv[1] if len(sys.argv) > 1 else None
    
    # 执行处理
    report_result, prereport_result = process_daily_report(date_param)

   
    
    # 根据处理结果设置退出码
    if not report_result or not prereport_result:
        logging.error("任务执行失败")
        sys.exit(1)

    send_user_sub_message()
    logging.info("任务已成功执行")
    sys.exit(0)
