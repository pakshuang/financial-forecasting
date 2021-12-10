import pandas as pd
import numpy as np
import yfinance as yf
import sys

'''
This script obtains the price history of TWOU for a specific number of minutes
and adds padded rows for the model for the model's input data
'''

def main(filename, rows, paddings, m, s):
    x = yf.Ticker("TWOU").history(period="1d",  interval="1m", actions= False)
    data = pd.DataFrame(x['Open'])
    data = data.resample('1min', origin = 'start').agg({'Open': 'first'})
    data = data.reset_index()
    data = data.set_index('Datetime')
    data['Open'].interpolate(method='time', inplace=True)
    data['Open'] = (data['Open'] - m)/s
    data['UNIX'] = data.index.astype(np.int64) // 10**6
    data = data.set_index('UNIX')
    if len(data)> rows:
        data = data.iloc[-rows:]
    zeroes = pd.DataFrame(np.zeros((paddings, 1)), columns=['Open'])
    zeroes = zeroes.set_index(zeroes['Open'])
    data = pd.concat([data, zeroes])
    data.to_csv(filename, header= False)

main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]))

#main('TWOU.csv', 64, 60, 36.25, 1.3)
