
import tushare as ts

ts.set_token('00effb4f723c39f5d1d3064d01afad8c19c9656a9ff373166d33ed58')
pro = ts.pro_api()

def stk_holdertrade():
  '''股东增减持'''
  df = pro.stk_holdertrade(ts_code='300199.SZ')
  print(df)
  pass  

if __name__ == "__main__":
  stk_holdertrade()