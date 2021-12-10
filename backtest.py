from ischedule import schedule, run_loop
from datetime import datetime, timedelta, time
from threading import Timer, Event
import time
import pandas as pd
import numpy as np
from numpy import median
import subprocess
from csv import writer
import pyautogui
import yfinance as yf

'''
Runs backtests on the model, generating diagnostics such at the absolute error for each prediction
'''


start = datetime.fromisoformat("2021-09-23 21:30")
end = datetime.fromisoformat("2021-09-24 04:00")
window1 = 67
window2 = 327


x = yf.Ticker("TWOU").history(start=start, end=end,  interval="1m", actions= False)
data = pd.DataFrame(x['Open'])
data = data.resample('1min', origin = 'start').agg({'Open': 'first'})
data = data.reset_index()
#times = data['Datetime']
data = data.set_index('Datetime')
data['Open'].interpolate(method='time', inplace=True)
times = data[-263:].reset_index()
times['T+0 price'] = data[67:330].reset_index(drop=True).squeeze()
# normalise

##pop_mean = data['Open'].mean()
##pop_sd = data['Open'].std()
pop_mean = 36.25
pop_sd = 1.3

data['Open'] = (data['Open'] - pop_mean)/(pop_sd)
#data.to_csv('backtestwholedaydatetime.csv', header= False)
data['UNIX'] = data.index.astype(np.int64) // 10**6
data = data.set_index('UNIX')[0:330]
data.to_csv('backtestwholeday.csv', header= False)

#print(data.between_time('10:36', '14:59').index)

##def prediction(filename):
##    forecast_csv = pd.read_csv(filename, header=None)
##    forecast = forecast_csv[0]
##    #print(f'{filename} forecast: {forecast}')
##    return forecast

def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)

prediction_files = ['backtest58.csv', 'backtest60.csv', 'backtest62.csv']

##print(data[0: window1])

print('checking trading API status')
subprocess.run("python buy.py test Stonks_City 62797BA935", check=True)
print('API check passed')

print('backtesting...')
for j in [58,60,62]:
    zeroes = pd.DataFrame(np.zeros((j, 1)), columns=['Open'])
    zeroes = zeroes.set_index(zeroes['Open'])
    df = pd.concat([data, zeroes])
    df.to_csv(f"backtestwindow{j}.csv", header= False)
subprocess.run('python ac.py backtestwindow58.csv leon1126/StonksCity_T+58 Stonks_City2 backtest58.csv')
subprocess.run('python ac.py backtestwindow60.csv leon1126/StonksCity_T+60_3 Stonks_City8 backtest60.csv')
subprocess.run('python ac.py backtestwindow62.csv leon1126/StonksCity_T+62 Stonks_City4 backtest62.csv')

times[f'Open_delta'] = times['Open'] - times['T+0 price']

for filename in prediction_files:
    forecast_csv = pd.read_csv(filename, header=None)
    times[filename] = forecast_csv[-263:].reset_index(drop=True).squeeze()*pop_sd + pop_mean
    times[f'{filename}_error'] = times[filename] - times['Open']
    times[f'{filename}_delta'] = times[filename] - times['T+0 price']
    times[f'{filename}_delta_error'] = times[f'{filename}_delta'] - times[f'Open_delta']

times.to_csv('backtestwholedayforecasts.csv')
print('backtest results saved to backtestwholedayforecasts.csv')
##append_list_as_row('backtestforecasts.csv', row)
##print('predictions saved to backtestforecasts.csv')
##pyautogui.press('volumedown')
##time.sleep(1)
##pyautogui.press('volumeup')
