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

def generate_html_report(prereport_date, exceed_date, high_change_stocks, exceed_area_stocks, high_profit_growth_stocks=None, exceed_area_report_info=None, query_date='auto'):
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
        f'<h2 class="section-title" data-table="high-change-table">业绩预告变动<span class="date-info">业绩预告分析期: {formatted_prereport_date}</span></h2>'
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
        f'<h2 class="section-title" data-table="exceed-expect-table">业绩超预期{exceed_area_dates}</h2>'
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

    # 为section-title添加点击功能的CSS和JavaScript
    section_toggle_scripts = """
    <style>
    /* 为section-title添加可点击样式 */
    .section-title {
        cursor: pointer;
        position: relative;
        padding-right: 30px; /* 为图标留出空间 */
    }

    /* 添加展开/折叠指示器 */
    .section-title:after {
        content: '▼';
        position: absolute;
        right: 15px;
        transition: transform 0.3s;
    }

    .section-title.collapsed:after {
        transform: rotate(-90deg);
    }

    /* 表格的显示/隐藏过渡效果 */
    table.section-table {
        transition: all 0.3s;
        overflow: hidden;
        display: table;
    }

    table.section-table.collapsed {
        display: none;
    }
    </style>
    <script>
    // 切换section内容的显示/隐藏
    function toggleSection(tableId) {
        const title = document.querySelector(`h2[data-table="${tableId}"]`);
        const table = document.getElementById(tableId);
        
        if (title && table) {
            title.classList.toggle('collapsed');
            table.classList.toggle('collapsed');
        }
    }

    // 页面加载时初始化
    document.addEventListener('DOMContentLoaded', function() {
        // 为每个section-title添加点击事件
        document.querySelectorAll('.section-title').forEach(title => {
            const tableId = title.getAttribute('data-table');
            if (tableId) {
                title.addEventListener('click', function() {
                    toggleSection(tableId);
                });
            }
        });
    });
    </script>
    """

    # 添加新样式和JavaScript
    html_content = html_content.replace('</head>', f'{additional_styles}\n{section_toggle_scripts}\n</head>')

    logging.info("生成业绩变动股票数据行...")
    high_change_rows = ""
    for stock in high_change_stocks:
        change_class = "positive-change" if float(stock['3']) > 0 else "negative-change"
        # 添加主行（加入stock-main-row类）
        high_change_rows += f"""
        <tr class="stock-main-row">
            <td data-label="股票代码"><a href="https://www.kakasong.cn/webview?url=https://stockpage.10jqka.com.cn/{stock['0']}/" target="_blank" class="stock-link">{stock['0']}</a></td>
            <td data-label="股票名称"><a href="https://www.kakasong.cn/webview?url=https://stockpage.10jqka.com.cn/{stock['0']}/" target="_blank" class="stock-link">{stock['1']}</a></td>
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
        
        # 处理净利润同比增长率
        net_profit_yoy_class = ""
        net_profit_yoy_display = "-"
        
        if '10' in stock and stock['10'] is not None:
            net_profit_yoy = float(stock['10'])
            net_profit_yoy_display = f"{net_profit_yoy:+.2f}%" if net_profit_yoy != 0 else "0.00%"
            net_profit_yoy_class = "positive-change" if net_profit_yoy > 0 else "negative-change"
            
        exceed_rows += f"""
        <tr class="stock-main-row">
            <td data-label="股票代码"><a href="https://www.kakasong.cn/webview?url=https://stockpage.10jqka.com.cn/{stock['0']}/" target="_blank" class="stock-link">{stock['0']}</a></td>
            <td data-label="股票名称"><a href="https://www.kakasong.cn/webview?url=https://stockpage.10jqka.com.cn/{stock['0']}/" target="_blank" class="stock-link">{stock['1']}</a></td>
            <td data-label="上期预测值(万元)">{format_number(stock['2'])} ({stock['7'][:4]}年{stock['7'][4:6]}月)</td>
            <td data-label="本期实际净利润(万元)">{format_number(stock['3'])} ({stock['8'][:4]}年{stock['8'][4:6]}月)</td>
            <td data-label="超预期倍数" class="positive-change">{exceed_rate:.2f}倍</td>
            <td data-label="净利润同比增长" class="{net_profit_yoy_class}">{net_profit_yoy_display}</td>
            <td data-label="预告类型" class="small-text">{stock['5'] or ''}</td>
            <td data-label="预测指标">{stock['6']}</td>
            <td data-label="公告日期">{stock['9']}</td>
        </tr>
        """
        
        fund_flow = stock.get('fund_flow')
        if fund_flow is not None and not fund_flow.empty:
            exceed_rows += f"""
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
    # 添加id属性和section-table类到表格
    html_content = html_content.replace(
        '<table id="high-change-table">',
        '<table id="high-change-table" class="section-table">'
    )
    # 修改业绩超预期表格的表头，添加净利润同比增长列
    html_content = html_content.replace(
        '<table id="exceed-expect-table">',
        '<table id="exceed-expect-table" class="section-table">'
    )
    
    # 在表头添加净利润同比增长列
    html_content = html_content.replace(
        '<tr>\n                        <th>股票代码</th>\n                        <th>股票名称</th>\n                        <th>上期预测值(万元)</th>\n                        <th>本期实际净利润(万元)</th>\n                        <th>超预期倍数</th>\n                        <th>预告类型</th>\n                        <th>预测指标</th>\n                        <th>公告日期</th>\n                    </tr>',
        '<tr>\n                        <th>股票代码</th>\n                        <th>股票名称</th>\n                        <th>上期预测值(万元)</th>\n                        <th>本期实际净利润(万元)</th>\n                        <th>超预期倍数</th>\n                        <th>净利润同比增长</th>\n                        <th>预告类型</th>\n                        <th>预测指标</th>\n                        <th>公告日期</th>\n                    </tr>'
    )
    
    html_content = html_content.replace(
        '<!-- 数据将通过Python脚本动态生成 -->', 
        high_change_rows if high_change_stocks else "<tr><td colspan='9'>没有找到符合条件的数据</td></tr>", 
        1
    )
    html_content = html_content.replace(
        '<!-- 数据将通过Python脚本动态生成 -->', 
        exceed_rows if exceed_area_stocks else "<tr><td colspan='9'>没有找到符合条件的数据</td></tr>", 
        1
    )
    
    # 添加净利润同比增长表格部分
    if high_profit_growth_stocks:
        logging.info("生成净利润同比增长数据行...")
        
        # 在最后一个section后添加新的表格部分
        high_profit_growth_section = f"""
        <div class="section">
            <h2 class="section-title" data-table="high-profit-growth-table">净利润同比增长<span class="date-info">报告期: {formatted_exceed_date}</span></h2>
            <table id="high-profit-growth-table" class="section-table">
                <thead>
                    <tr>
                        <th>股票代码</th>
                        <th>股票名称</th>
                        <th>净利润(万元)</th>
                        <th>同比增长率</th>
                        <th>公告日期</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        growth_rows = ""
        for stock in high_profit_growth_stocks:
            net_profit = float(stock['2']) if stock.get('2') is not None else 0
            growth_rate = float(stock['3']) if stock.get('3') is not None else 0
            
            growth_rows += f"""
            <tr class="stock-main-row">
                <td data-label="股票代码"><a href="https://www.kakasong.cn/webview?url=https://stockpage.10jqka.com.cn/{stock['0']}/" target="_blank" class="stock-link">{stock['0']}</a></td>
                <td data-label="股票名称"><a href="https://www.kakasong.cn/webview?url=https://stockpage.10jqka.com.cn/{stock['0']}/" target="_blank" class="stock-link">{stock['1']}</a></td>
                <td data-label="净利润(万元)">{format_number(net_profit)}</td>
                <td data-label="同比增长率" class="positive-change">{growth_rate:+.2f}%</td>
                <td data-label="公告日期">{stock['4'] if stock.get('4') else ''}</td>
            </tr>
            """
            
            # 添加资金流数据
            fund_flow = stock.get('fund_flow')
            if fund_flow is not None and not fund_flow.empty:
                growth_rows += f"""
                <tr class="fund-flow-header">
                    <td colspan="5" onclick="toggleFundFlow('{stock['0']}_growth')">
                        最近5日资金流向（万元）
                    </td>
                </tr>
                <tr>
                    <td colspan="5" style="padding: 0;">
                        <table class="nested-table" data-stock="{stock['0']}_growth">
                            <tr class="fund-flow-data-header">
                                <td>日期</td>
                                <td>主力净流入</td>
                                <td>小单净流入</td>
                                <td>中单净流入</td>
                            </tr>
                """
                
                for _, row in fund_flow.iterrows():
                    inflow_class = "fund-inflow" if row['主力净流入-净额'] > 0 else "fund-outflow"
                    growth_rows += f"""
                            <tr class="fund-flow-row">
                                <td>{row['日期']}</td>
                                <td class="{inflow_class}">{format_number(row['主力净流入-净额'])}</td>
                                <td>{format_number(row['小单净流入-净额'])}</td>
                                <td>{format_number(row['中单净流入-净额'])}</td>
                            </tr>
                    """
                
                growth_rows += """
                        </table>
                    </td>
                </tr>
                """
        
        high_profit_growth_section += growth_rows if growth_rows else "<tr><td colspan='5'>没有找到符合条件的数据</td></tr>"
        high_profit_growth_section += """
                </tbody>
            </table>
        </div>
        """
        
        # 在最后一个section后添加新的section
        html_content = html_content.replace('</div>\n    </div>\n</body>', f'</div>\n    {high_profit_growth_section}\n    </div>\n</body>')
    
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
