import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import numpy as np
import warnings
import matplotlib.pyplot as plt
import mplfinance as mpf
from pykrx import stock

def stock_name_to_code(stock_name):
    ticker_list = stock.get_market_ticker_list()
    
    for code in ticker_list:
        name = stock.get_market_ticker_name(code)
        if name == stock_name:
            return code
    else:
        return 0

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.options.display.float_format = '{:,.0f}'.format
warnings.simplefilter(action='ignore', category=FutureWarning)

while 1:
    stock_name = input('종목 입력:')
    stock_code = stock_name_to_code(stock_name)
    if stock_code != 0:
        print(f"{stock_name}의 종목 코드는 {stock_code}입니다.")
        break
    else:
        print('종목 코드를 찾을 수 없습니다')

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}
df = pd.DataFrame()
excel_df = pd.DataFrame()
sise_url = f'https://finance.naver.com/item/sise_day.nhn?code={stock_code}'
for page in range(1,51):
    page_url = '{}&page={}'.format(sise_url, page)
    response = requests.get(page_url, headers=headers)
    html = bs(response.text, 'html.parser')
    html_table = html.select("table")
    table = pd.read_html(str(html_table))
    df = pd.concat([df, table[0].dropna()])
    # pf = pd.DataFrame(table[0].dropna())

df = df.reset_index(drop=True)
df.drop(columns=['전일비'], inplace=True)
df = df.rename(columns={"날짜":"date","시가":"open","고가":"high","저가":"low","종가":"close","거래량":"volume"})

# ================================================================
sort_df = df.sort_index(ascending=False)
date_format = "%Y.%m.%d"
sort_df['date'] = pd.to_datetime(sort_df['date'], format=date_format)
sort_df.set_index('date',inplace=True)

df['date'] = pd.to_datetime(df['date'], format=date_format)
df.set_index('date',inplace=True)
# df['날짜_정수'] = df['date'].dt.strftime('%Y%m%d').astype(int)

sort_df['sma5'] = sort_df['close'].rolling(window=5).mean()
sort_df['sma20'] = sort_df['close'].rolling(window=20).mean()
sort_df['sma100'] = sort_df['close'].rolling(window=100).mean()

df['stddev'] = sort_df['close'].rolling(window=20).std()
sort_df['upper'] = sort_df['sma20'] + (df['stddev']*2)
sort_df['lower'] = sort_df['sma20'] - (df['stddev']*2)


sma5 = mpf.make_addplot(sort_df['sma5'],type='line',color = 'r', width=1, alpha=0.5)
sma20 = mpf.make_addplot(sort_df['sma20'],type='line',color = 'b', width=1, alpha=0.5)
sma100 = mpf.make_addplot(sort_df['sma100'],type='line',color = 'g', width=1, alpha=0.5)

upper = mpf.make_addplot(sort_df['upper'],type='line',color = 'y', width=0.7, alpha=1)
lower = mpf.make_addplot(sort_df['lower'],type='line',color = 'y', width=0.7, alpha=1)

mpf.plot(sort_df, type='candle', addplot=[sma5,sma20,sma100,upper,lower],style='charles',show_nontrading=True,figratio=(15, 6))