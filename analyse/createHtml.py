import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def format_number(number):
    """格式化数字为万元"""
    if number is None:
        return "0"
    return format(number / 10000, ',.2f')

def generate_html_report(prereport_date, exceed_date, high_change_stocks, exceed_area_stocks, exceed_area_report_info=None, query_date='auto'):
    """生成HTML报告"""
    logging.info("开始生成HTML报告...")
    template_path = os.path.join(os.path.dirname(__file__), 'performance_analysis.html')
    logging.info(f"使用模板文件：{template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    formatted_prereport_date = f"{prereport_date[:4]}年{prereport_date[4:6]}月{prereport_date[6:]}日"
    formatted_exceed_date = f"{exceed_date[:4]}年{exceed_date[4:6]}月{exceed_date[6:]}日" if exceed_date else "无可用数据"
    # formatted_prev_date = f"{prev_period_date[:4]}年{prev_period_date[4:6]}月{prev_period_date[6:]}日"
    
    logging.info("替换表格标题中的日期...")
    # 替换表格标题中的日期
    html_content = html_content.replace(
        '<h2 class="section-title">业绩预告变动</h2>',
        f'<h2 class="section-title">业绩预告变动<span class="date-info">业绩预告分析期: {formatted_prereport_date}</span></h2>'
    )
    
    exceed_area_dates = ""
    if exceed_area_report_info:
        exceed_area_dates = f"""
        <span class="date-info">
            实际业绩期: {formatted_exceed_date}<br>
            当期预测期: {exceed_area_report_info['current_prereport_date'][:4]}年{exceed_area_report_info['current_prereport_date'][4:6]}月{exceed_area_report_info['current_prereport_date'][6:]}日<br>
            上期预测期: {exceed_area_report_info['prev_prereport_date'][:4]}年{exceed_area_report_info['prev_prereport_date'][4:6]}月{exceed_area_report_info['prev_prereport_date'][6:]}日
        </span>
        """
    html_content = html_content.replace(
        '<h2 class="section-title">业绩预告超预期股票</h2>',
        f'<h2 class="section-title">业绩超预期{exceed_area_dates}</h2>'
    )
    
    # 移除原有的日期显示区域
    html_content = html_content.replace(
        '<div class="report-dates">\n            <!-- 日期信息将通过Python脚本动态生成 -->\n        </div>',
        ''
    )
    
    logging.info("添加CSS样式和JavaScript代码...")
    # 生成CSS样式和JavaScript代码
    additional_styles = """
    <style>
    .stock-main-row {
        background-color: #f0f8ff !important;
    }
    .nested-table {
        width: 100%;
        margin: 0;
        display: none;
    }
    .nested-table.visible {
        display: table;
    }
    .fund-flow-row {
        background-color: #f9f9f9;
    }
    /* PC端资金流样式 */
    .fund-flow-row td {
        font-size: 0.85em;
        color: #666;
        text-align: center;
    }
    .fund-flow-header {
        font-weight: bold;
        background-color: #f5f5f5 !important;
        cursor: pointer;
    }
    .fund-flow-header td {
        text-align: right !important;
        font-size: 0.9em !important;
        color: #333 !important;
        padding: 8px !important;
    }
    .fund-flow-data-header {
        background-color: #f5f5f5;
        font-size: 0.85em;
        color: #666;
    }
    .fund-flow-data-header td {
        text-align: center;
        padding: 6px !important;
    }
    .fund-inflow {
        color: #d14836 !important;
    }
    .fund-outflow {
        color: #093 !important;
    }
    .stock-link {
        color: #333;
        text-decoration: none;
    }
    .stock-link:hover {
        text-decoration: underline;
        color: #1a0dab;
    }
    
    /* 确保PC端嵌套表格内容居中 */
    .nested-table td {
        text-align: center;
    }
    
    @media screen and (max-width: 768px) {
        .nested-table {
            display: none !important;
            margin: 0 !important;
            width: 100% !important;
        }
        .nested-table.visible {
            display: table !important;
        }
        .nested-table tr {
            display: table-row !important;
            margin: 0 !important;
            border: none !important;
        }
        .nested-table td {
            display: table-cell !important;
            padding: 6px !important;
            text-align: right !important; /* 移动端保持右对齐 */
            position: static !important;
            border: 1px solid #ddd !important;
        }
        .nested-table td:first-child {
            text-align: left !important;
        }
        .fund-flow-header td {
            padding: 10px !important;
            text-align: right !important;
            background-color: #f5f5f5 !important;
        }
        .fund-flow-data-header {
            display: table-row !important;
        }
        .fund-flow-data-header td {
            background-color: #f9f9f9 !important;
            text-align: center !important;
            font-weight: bold !important;
            padding: 8px !important;
        }
    }
    </style>
    <script>
    function toggleFundFlow(stockCode) {
        console.log('Toggle clicked for stock:', stockCode);
        var nestedTable = document.querySelector(`table[data-stock="${stockCode}"]`);
        console.log('Found nested table:', nestedTable);
        
        if (nestedTable) {
            var isVisible = nestedTable.classList.contains('visible');
            console.log('Current visibility:', isVisible);
            nestedTable.classList.toggle('visible');
            console.log('New visibility:', !isVisible);
        }
    }
    </script>
    """

    # 添加新样式和JavaScript
    html_content = html_content.replace('</head>', f'{additional_styles}\n</head>')

    logging.info("生成业绩变动股票数据行...")
    high_change_rows = ""
    for stock in high_change_stocks:
        change_class = "positive-change" if float(stock['3']) > 0 else "negative-change"
        # 添加主行（加入stock-main-row类）
        high_change_rows += f"""
        <tr class="stock-main-row">
            <td data-label="股票代码"><a href="http://kakasong.cn/webview?url=https://stockpage.10jqka.com.cn/{stock['0']}/" target="_blank" class="stock-link">{stock['0']}</a></td>
            <td data-label="股票名称"><a href="http://kakasong.cn/webview?url=https://stockpage.10jqka.com.cn/{stock['0']}/" target="_blank" class="stock-link">{stock['1']}</a></td>
            <td data-label="预测指标">{stock['2']}</td>
            <td data-label="变动幅度" class="{change_class}">{float(stock['3']):+.2f}%</td>
            <td data-label="预测值(万元)">{format_number(stock['4'])}</td>
            <td data-label="上年同期值(万元)">{format_number(stock['5'])}</td>
            <td data-label="预告类型" class="small-text">{stock['6'] or ''}</td>
            <td data-label="变动原因" class="change-reason small-text">{stock['7'] or ''}</td>
            <td data-label="公告日期">{stock['8']}</td>
        </tr>
        """
        
        # 添加资金流数据
        fund_flow = stock.get('fund_flow')
        if fund_flow is not None and not fund_flow.empty:
            # 添加资金流表头（可点击）
            high_change_rows += f"""
            <tr class="fund-flow-header">
                <td colspan="9" onclick="toggleFundFlow('{stock['0']}')">
                    最近5日资金流向（万元）
                </td>
            </tr>
            <tr>
                <td colspan="9" style="padding: 0;">
                    <table class="nested-table" data-stock="{stock['0']}">
                        <tr class="fund-flow-data-header">
                            <td>日期</td>
                            <td>主力净流入</td>
                            <td>小单净流入</td>
                            <td>中单净流入</td>
                        </tr>
            """
            
            for _, row in fund_flow.iterrows():
                inflow_class = "fund-inflow" if row['主力净流入-净额'] > 0 else "fund-outflow"
                high_change_rows += f"""
                        <tr class="fund-flow-row">
                            <td>{row['日期']}</td>
                            <td class="{inflow_class}">{format_number(row['主力净流入-净额'])}</td>
                            <td>{format_number(row['小单净流入-净额'])}</td>
                            <td>{format_number(row['中单净流入-净额'])}</td>
                        </tr>
                """
            
            high_change_rows += """
                    </table>
                </td>
            </tr>
            """
    
    logging.info("生成业绩超预期股票数据行...")
    exceed_rows = ""
    for stock in exceed_area_stocks:
        exceed_rate = float(stock['4'])
        exceed_rows += f"""
        <tr class="stock-main-row">
            <td data-label="股票代码"><a href="http://kakasong.cn/webview?url=https://stockpage.10jqka.com.cn/{stock['0']}/" target="_blank" class="stock-link">{stock['0']}</a></td>
            <td data-label="股票名称"><a href="http://kakasong.cn/webview?url=https://stockpage.10jqka.com.cn/{stock['0']}/" target="_blank" class="stock-link">{stock['1']}</a></td>
            <td data-label="上期预测值(万元)">{format_number(stock['2'])} ({stock['7'][:4]}年{stock['7'][4:6]}月)</td>
            <td data-label="本期实际净利润(万元)">{format_number(stock['3'])} ({stock['8'][:4]}年{stock['8'][4:6]}月)</td>
            <td data-label="超预期倍数" class="positive-change">{exceed_rate:.2f}倍</td>
            <td data-label="预告类型" class="small-text">{stock['5'] or ''}</td>
            <td data-label="预测指标">{stock['6']}</td>
            <td data-label="公告日期">{stock['9']}</td>
        </tr>
        """
        
        fund_flow = stock.get('fund_flow')
        if fund_flow is not None and not fund_flow.empty:
            exceed_rows += f"""
            <tr class="fund-flow-header">
                <td colspan="8" onclick="toggleFundFlow('{stock['0']}')">
                    最近5日资金流向（万元）
                </td>
            </tr>
            <tr>
                <td colspan="8" style="padding: 0;">
                    <table class="nested-table" data-stock="{stock['0']}">
                        <tr class="fund-flow-data-header">
                            <td>日期</td>
                            <td>主力净流入</td>
                            <td>小单净流入</td>
                            <td>中单净流入</td>
                        </tr>
            """
            
            for _, row in fund_flow.iterrows():
                inflow_class = "fund-inflow" if row['主力净流入-净额'] > 0 else "fund-outflow"
                exceed_rows += f"""
                        <tr class="fund-flow-row">
                            <td>{row['日期']}</td>
                            <td class="{inflow_class}">{format_number(row['主力净流入-净额'])}</td>
                            <td>{format_number(row['小单净流入-净额'])}</td>
                            <td>{format_number(row['中单净流入-净额'])}</td>
                        </tr>
                """
            
            exceed_rows += """
                    </table>
                </td>
            </tr>
            """
    
    logging.info("替换表格内容...")
    html_content = html_content.replace(
        '<!-- 数据将通过Python脚本动态生成 -->', 
        high_change_rows if high_change_stocks else "<tr><td colspan='9'>没有找到符合条件的数据</td></tr>", 
        1
    )
    html_content = html_content.replace(
        '<!-- 数据将通过Python脚本动态生成 -->', 
        exceed_rows if exceed_area_stocks else "<tr><td colspan='8'>没有找到符合条件的数据</td></tr>", 
        1
    )
    
    # 根据query_date决定使用当前日期还是预告日期
    if query_date.lower() == 'auto':
        # auto模式使用当前日期
        current_date = datetime.now().strftime("%Y%m%d")
        filename = f"performance_analysis_{current_date}.html"
    else:
        # 非auto模式使用预告日期
        filename = f"performance_analysis_{prereport_date}.html"
    
    # 使用环境变量中配置的输出路径
    output_path = os.path.join(os.getenv('HTML_OUTPUT_PATH'), filename)
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    logging.info(f"写入HTML文件到: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logging.info("HTML报告生成完成")
    return output_path
