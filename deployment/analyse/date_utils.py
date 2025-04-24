from datetime import datetime

def get_quarter_dates():
    """获取所有季度末日期"""
    return [
        (3, 31),
        (6, 30),
        (9, 30),
        (12, 31)
    ]

def get_next_quarter_end():
    """获取下一个最近的季度末日期（用于业绩预告）"""
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    day = current_date.day

    quarter_dates = get_quarter_dates()

    for q_month, q_day in quarter_dates:
        if month < q_month or (month == q_month and day <= q_day):
            return f"{year}{q_month:02d}{q_day:02d}"
    
    return f"{year + 1}0331"

def get_prev_quarter_end():
    """获取上一个最近的季度末日期（用于业绩报告）"""
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    
    quarter_dates = get_quarter_dates()
    
    # 获取当前季度的索引
    current_quarter_idx = (month - 1) // 3
    
    # 计算上一个季度的年份和月份
    if current_quarter_idx == 0:  # 如果是第一季度
        prev_year = year - 1
        prev_month, prev_day = quarter_dates[3]  # 返回上一年第四季度
    else:
        prev_year = year
        prev_month, prev_day = quarter_dates[current_quarter_idx - 1]
    
    return f"{prev_year}{prev_month:02d}{prev_day:02d}"


def get_prevdate_by_date(current_date):
    """根据给定的日期获取上一期的日期"""
    year = int(current_date[:4])
    month = int(current_date[4:6])
    
    quarter_dates = get_quarter_dates()
    
    # 获取当前季度的索引
    current_quarter_idx = (month - 1) // 3
    
    # 计算上一期的年份和月份
    if current_quarter_idx == 0:  # 如果是第一季度
        prev_year = year - 1
        prev_month, prev_day = quarter_dates[3]  # 返回上一年第四季度
    else:
        prev_year = year
        prev_month, prev_day = quarter_dates[current_quarter_idx - 1]
    
    return f"{prev_year}{prev_month:02d}{prev_day:02d}"

def get_prev_prev_quarter_end():
    """获取上上个季度末日期（往前推两个季度）"""
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    
    quarter_dates = get_quarter_dates()
    
    # 获取当前季度的索引
    current_quarter_idx = (month - 1) // 3
    
    # 计算上上个季度的索引
    prev_prev_quarter_idx = (current_quarter_idx - 2) % 4
    
    # 计算上上个季度的年份
    year_offset = 0
    if current_quarter_idx == 0:  # 第一季度
        year_offset = -1
    elif current_quarter_idx == 1:  # 第二季度
        year_offset = -1
    
    prev_prev_year = year + year_offset
    prev_prev_month, prev_prev_day = quarter_dates[prev_prev_quarter_idx]
    
    return f"{prev_prev_year}{prev_prev_month:02d}{prev_prev_day:02d}"