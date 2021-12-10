import pandas as pd
import numpy as np
import yfinance as yf
import ta

'''This script generates the training data for the model'''

#retrieve data

a = yf.Ticker("TWOU").history(start="2021-09-04",  end="2021-09-11",
                              interval="1m")

b = yf.Ticker("TWOU").history(start="2021-08-28",  end="2021-09-04",
                              interval="1m")

c = yf.Ticker("TWOU").history(start="2021-08-24",  end="2021-08-28",
                              interval="1m")
##d = yf.Ticker("TWOU").history(start="2021-08-14",  end="2021-08-21",
##                              interval="1m")

#merge data
data = pd.concat([a, b, c])

#drop unnecessary columns
data = data['Open']
#resample to retrieve missing data points and sort
data = data.resample('1min', origin = 'start').agg('first')
#get unique days
data = data.reset_index()

days = data['Datetime'].apply(lambda x : str(x)[:-15]).unique()

#filter active trading hour periods only
data = data.set_index('Datetime')
df = data.between_time('09:30', '15:59')

#remove non trading days (long gaps of missing data)
#and fill in missing intraday values
df_a = pd.DataFrame()
for day in days:
    print(day)
    series = df.loc[day]
    check = series.isnull().sum()['Open']
    if check != len(series):
#check whether the number of missing values is equal to the len of the series
#meaning the whole day is full of nan values and is a non trading day
        series['Open'].interpolate(method='ffill', inplace=True)
        df_a = df_a.append(series)

#resample again to retrieve interday missing values
#df_a = df_a.resample('1min', origin = 'start').agg({'Open': 'first'})

df_a['Momentum'] = ta.momentum.ROCIndicator(df_a['Open'], window = 60, fillna= False).roc()
df_a['SMA'] = ta.trend.sma_indicator(df_a['Momentum'], window=15, fillna=False)
df_a['EMA'] = ta.trend.ema_indicator(df_a['Momentum'], window=15, fillna=False)
df_a['StochK'] = (ta.momentum.StochasticOscillator(df_a['Momentum'], df_a['Momentum'], df_a['Momentum'], window = 15, smooth_window = 5, fillna = False).stoch()-50)/50
df_a['RSI'] = (ta.momentum.RSIIndicator(df_a['Momentum'], window = 15, fillna = False).rsi() - 50) / 50
df_a['MACD'] = ta.trend.MACD(df_a['Momentum'], window_slow = 15, window_fast = 5, window_sign= 5, fillna = False).macd_diff() * 20

df_a['Open'] = (df_a['Open'] - df_a['Open'].mean())/df_a['Open'].std()
df_a = df_a[78:]
#convert datetime to miliseconds
df_a.index = df_a.index.astype(np.int64) // 10**6
#df_a = df_a['Open'].round(6)

#save to csv
df_a.to_csv('TWOU_training.csv', header=False)

