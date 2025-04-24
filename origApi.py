import akshare as ak

stockCode = '000039'
#业绩预告
def getPreData():

    stock_yjyg_em_df = ak.stock_yjyg_em(date="20250331")

    filtered_df = stock_yjyg_em_df[stock_yjyg_em_df["股票代码"] == stockCode]

    # print("\n300274的记录：")
    print(filtered_df)

    # print(stock_yjyg_em_df)

#业绩
def getReport():
    stock_yjbb_em_df = ak.stock_yjbb_em(date="20241231")
    # 筛选股票代码为300274的记录
    # filtered_df = stock_yjbb_em_df[stock_yjbb_em_df["股票代码"] == stockCode]

    # print("\n300274的记录：")
    # print(filtered_df)


def businessAmountFlow():
    '''行业现金流'''
    stock_fund_flow_individual_df = ak.stock_fund_flow_individual(symbol="3日排行")

    filtered_df = stock_fund_flow_individual_df[stock_fund_flow_individual_df["股票代码"] == stockCode]
    print(filtered_df)

def singleAmountFlow():
    '''个股现金流'''
    stock_individual_fund_flow_df = ak.stock_individual_fund_flow(stock=stockCode, market="sh")
    # 按日期倒序排序并取前5条记录
    sorted_df = stock_individual_fund_flow_df.sort_values(by='日期', ascending=False).head(5)
    print(sorted_df)

if __name__ == "__main__":
  getPreData()
