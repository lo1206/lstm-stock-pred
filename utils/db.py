from datetime import datetime
import psycopg2
import pandas as pd

taskid = '{date:%Y%m%d-%H%M%S}'.format(date=datetime.now())

def get_db():

    #conn = psycopg2.connect(dbname='stock',
    #                       user='user',
    #                        password='hunter2',
    #                       host='db')

    conn = psycopg2.connect(dbname='postgres',
                            user='postgres',
                            password='D80gGEiYQ6JO0haClJJt',
                            host='database-1.cmmlivx2dkqn.us-west-2.rds.amazonaws.com')
    return conn


#---------------------------------------------------------------
# System Log
#---------------------------------------------------------------


def add_sys_log(action, status, message):
    sql = """
            INSERT INTO sys_log (taskid, action, status, message, created_at)
            VALUES (%s, %s, %s, %s, %s);
          """
    db = get_db()
    cur = db.cursor()
    cur.execute(sql, (taskid, action, status, message, datetime.today()))
    db.commit()
    cur.close()
    db.close()

#---------------------------------------------------------------
# Proxy
#---------------------------------------------------------------


def add_proxy(proxies):
    sql = """
            INSERT INTO proxy (taskid, proxy)
            VALUES (%s, %s);
          """
    db = get_db()
    cur = db.cursor()

    records = [(taskid,proxy) for proxy in proxies]
    cur.executemany(sql, records)

    db.commit()
    cur.close()
    db.close()


def get_proxy():
    sql = """
            SELECT proxy
            FROM proxy
            ORDER BY id desc
            LIMIT 100
            ;
        """
    cur = get_db().cursor()
    cur.execute(sql)

    proxies = []
    for row in cur.fetchall():
        proxies.append(row[0])

    cur.close()
    return proxies

#---------------------------------------------------------------
# Stock Master
#---------------------------------------------------------------


def show_stock_master():
    sql = """
            SELECT stockcode,industryclassification
            FROM stock_master;
        """
    cur = get_db().cursor()
    cur.execute(sql)

    stocks = []
    for row in cur.fetchall():
        stocks.append([row[0], row[1]])

    cur.close()
    df = pd.DataFrame(stocks, columns=['stockcode', 'industryclassification'])
    return df

#---------------------------------------------------------------
# Stock Price
#---------------------------------------------------------------


def add_stock_price(stock_prices):
    sql = """
            INSERT INTO stock_price (taskid, stockcode, date, 
                                     open, high, low, close, 
                                     adjclose, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
          """
    db = get_db()
    cur = db.cursor()

    records = [(taskid,
                stock_price[0],stock_price[1],stock_price[2],
                stock_price[3],stock_price[4],stock_price[5],
                stock_price[6],stock_price[7]) for stock_price in stock_prices]
    cur.executemany(sql, records)

    db.commit()
    cur.close()
    db.close()


def delete_stock_price(stockcode):
    sql = """
            DELETE FROM stock_price WHERE stockcode = %s ;
          """
    db = get_db()
    cur = db.cursor()
    cur.execute(sql, (stockcode,))
    db.commit()
    cur.close()
    db.close()


def show_stock_price():
    sql = """
            SELECT stockcode, date, open, high, low, close, adjclose, volume
            FROM stock_price;
        """
    cur = get_db().cursor()
    cur.execute(sql)

    stocks = []
    for row in cur.fetchall():
        stocks.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]])

    cur.close()
    df = pd.DataFrame(stocks, columns=['stockcode', 'date', 'open', 'high', 'low', 'close', 'adjclose', 'volume'])
    return df
