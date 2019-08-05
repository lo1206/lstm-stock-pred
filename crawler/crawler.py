# Packages
import proxyscrape
import random
import sys
import yfinance as yf
import pandas as pd
import time
from itertools import cycle
from datetime import datetime
from interruptingcow import timeout
sys.path.append('./utils')
import db


def update_proxy():
    db.taskid = '{date:%Y%m%d-%H%M%S}'.format(date=datetime.now())

    try:
        # Create a collector for https resources
        collector = proxyscrape.create_collector('MyProxy' + str(random.randint(100, 10000)), 'https')
        # Get proxy
        proxies = []
        for i in range(50):
            print('getting proxy:', i)
            proxy = collector.get_proxy({'code': ('us', 'uk'), 'anonymous': True})
            proxies.append(proxy.host + ':' + proxy.port)
        # Add proxis
        db.add_proxy(proxies)
        # Write to Log
        db.add_sys_log('get proxy', 'success', '')
    except Exception as e:
        print(str(e))
        db.add_sys_log('get proxy', 'fail', str(e))


def update_stockprice():
    db.taskid = '{date:%Y%m%d-%H%M%S}'.format(date=datetime.now())

    ################## Download stock data by proxy ###################

    # Get Proxy List
    proxies = db.get_proxy()
    proxy_pool = cycle(proxies)

    # Get new proxy
    proxy = next(proxy_pool)

    # Select Stocks
    df_stock_master = db.show_stock_master()
    stocks = df_stock_master[df_stock_master.industryclassification == '銀行']['stockcode'].tolist()

    # Select Time period
    start = datetime(2018, 1, 1)
    end = datetime.today()

    # Create Empty Stock Price Table
    col_names = ['Stock Code', 'Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']

    # Get stock price data from selected stocks
    for stock in stocks:

        isdownloaded = False
        error_count = 0

        # Download stock
        while isdownloaded is False and error_count < 50:
            try:

                print('--------------------------------------------------------')
                print('stock: ', stock, ' using proxy: ', proxy)

                # Download within 5 seconds
                with timeout(10, exception=RuntimeError):
                    data = yf.download(tickers=stock, start=start, end=end, proxy=proxy)
                    isdownloaded = True
            except Exception as e:
                print("Proxy Error")
                proxy = next(proxy_pool)
                error_count = error_count + 1

        # Check Download Success
        if isdownloaded:
            data['Date'] = data.index
            data['Stock Code'] = stock

            df_stock_price_download = pd.DataFrame(columns=col_names)
            df_stock_price_download = df_stock_price_download.append(data, sort=False)
            df_stock_price_download = df_stock_price_download[col_names]

            ################## Insert into database ###################
            try:
                # Delete original stock price data
                db.delete_stock_price(stock)
                print('finished delete stock:' + stock)

                # Insert stock price data
                stock_prices = []
                for index, row in df_stock_price_download.iterrows():
                    stock_prices.append([row['Stock Code'], row['Date'], row['Open'],
                                         row['High'], row['Low'], row['Close'],
                                         row['Adj Close'], row['Volume']])

                print('Started add stock price:' + stock)
                db.add_stock_price(stock_prices)
                print('Finished add stock price:' + stock)
                time.sleep(10)

                # Add to system log
                db.add_sys_log('add stock price', 'success', stock)
            except Exception as e:
                print('[Error inserting ' + stock + '] '+ str(e))


        else:
            print('[Error downloading '+ stock +']')


if __name__ == '__main__':
    run_time = datetime.now()
    while True:
        print('time diff:' ,(datetime.now() - run_time).seconds)
        if (datetime.now() - run_time).seconds > 10000:
            run_time = datetime.now()
            print('update')
            try:
                update_proxy()
                update_stockprice()
            except Exception as e:
                print('update exception:'+str(e))
        print('sleeping')
        time.sleep(100)
