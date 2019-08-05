import numpy as np
import pandas as pd
from datetime import timedelta, datetime
import db
from sklearn import preprocessing

# Initialize variables
seq_length = 50
categorical_cols = ['stockcode','date']
numerical_cols = ['open', 'high', 'low', 'close', 'adjclose', 'volume', 'target']


def get_df_stock_price():
    df_stock_price_all = db.show_stock_price()
    df_stock_price_all = df_stock_price_all.sort_values(by=['stockcode', 'date'])

    # Create Empty Dataframe
    df_stock_price = pd.DataFrame(columns=df_stock_price_all.columns.tolist() + ['target'])

    # Calculate rolling average as target for each stock
    for stock in df_stock_price_all.stockcode.unique():
        df_tmp = df_stock_price_all[df_stock_price_all['stockcode'] == stock].copy()
        df_tmp['target'] = df_tmp['adjclose'].rolling(window=5).mean()
        df_stock_price = df_stock_price.append(df_tmp)

    df_stock_price = df_stock_price[df_stock_price.target.notnull()]
    return df_stock_price


def normalize_df(df):
    min_max_scaler = preprocessing.MinMaxScaler()
    df[numerical_cols] = min_max_scaler.fit_transform(df[numerical_cols])
    return df


def get_df_pred(stock):
    df_stock_price = get_df_stock_price()
    num_of_sample = 100

    X = np.zeros((num_of_sample + 1, seq_length, len(numerical_cols)))
    y = np.zeros((num_of_sample + 1))
    D = []

    # Pick A Random Stock
    df = df_stock_price[df_stock_price['stockcode'] == stock].copy()
    df = normalize_df(df)

    print('df:', len(df))

    # Get X, y of the stock
    n = 0
    while n < num_of_sample:
        remain = num_of_sample - n
        X[n] = df[numerical_cols][-seq_length - remain:-remain].values
        y[n] = list(df['target'])[-remain]
        D.append(list(df['date'])[-remain])
        n = n + 1

    X[num_of_sample] = df[numerical_cols][-seq_length:].values
    y[num_of_sample] = np.nan

    D.append(D[-1] + timedelta(days=1))
    return X, y, D
