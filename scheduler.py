from ischedule import schedule, run_loop
from datetime import datetime, timedelta, time
from threading import Timer, Event
import time
import pandas as pd
from numpy import median
import subprocess
from csv import writer
import pyautogui
from math import floor
import re

### TIME VARIABLES ###

window = 63
# window is the number of prior data rows needed for a prediction (for B:0:-x in Autocaffe, window = x)
trading_starts = timedelta(hours=21, minutes=30) + timedelta(minutes=window)
# trading_starts is the first valid trading minute
trading_ends = timedelta(hours=3, minutes=0)
#trading_ends is the first invalid trading minute
delay = 2
# delay is how many seconds to wait each minute before starting each forecast
interval = 10
#interval is how many minutes between cycles

def test():
    print('checking trading API status')
    subprocess.run("python buy.py test Stonks_City 62797BA935", check=True)
    print('API check passed')
    
m = 36.25
s = 1.3

def get_forecast():
    subprocess.run(f"python prices.py TWOU.csv {window+1} 60 {m} {s}")
    subprocess.run('python ac.py TWOU.csv leon1126/StonksCity_T+58 Stonks_City2 P58.csv')


# retrieve the predicted price from the csv
def prediction(filename):
    forecast_csv = pd.read_csv(filename)
    forecast = float(forecast_csv.columns[0])* s + m
    #print(f'{filename} forecast: {forecast}')
    return forecast


def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)


def price():
    price_data = pd.read_csv("TWOU.csv", header=None)
    return float(price_data[1][window])* s + m


def execute_orders():
    P0 = price()
    print(f'Current price: {P0}')
    P58 = prediction('P58.csv')
    print(f'Prediction: {P58}')
##    P60 = prediction('P60.csv')
##    P62 = prediction('P62.csv')
##    predictions = [P58, P60, P62]
##    predicted_delta = [x-P0 for x in predictions]
    predicted_delta = P58 - P0
    print(f'Predicted delta: {predicted_delta}')
    output = subprocess.run('python buy.py trades Stonks_City 62797BA935', capture_output=True)
    text = output.stdout.decode("utf-8")
    balance = float(re.findall(r"now \d+", text)[-1][4:])
    #balance = 1000000
##    call_6 = floor((balance/2600)*5.36/2)
##    call_5 = floor((balance/2600)*4.30/2)
##    call_4 = floor((balance/2600)*3.49/2)
    call_3 = floor((balance/2600)*2.60)
    call_2 = floor((balance/2600)*1.39)
    call_1 = floor((balance/2600)*1.22)
    put_1 = floor((balance/2600)*1.00)
    put_2 = floor((balance/2600)*1.77)
    put_3 = floor((balance/2600)*3.40)
##    put_4 = floor((balance/2600)*3.49/2)
##    put_5 = floor((balance/2600)*4.30/2)
##    put_6 = floor((balance/2600)*5.36/2)

##    if predicted_delta >= 0.4:
##        print(f'Buying {call_6} calls')
##        #subprocess.run(f'python buy.py buy Stonks_City 62797BA935 call 60 {call_6}')
##    elif predicted_delta >= 0.38:
##        print(f'Buying {call_5} calls')
##        #subprocess.run(f'python buy.py buy Stonks_City 62797BA935 call 60 {call_5}')
##    elif predicted_delta >= 0.36:
##        print(f'Buying {call_4} calls')
##        #subprocess.run(f'python buy.py buy Stonks_City 62797BA935 call 60 {call_4}')
    if predicted_delta >= 0.50:
        print(f'Buying {call_3} calls')
        subprocess.run(f'python buy.py buy Stonks_City 62797BA935 call 60 {call_3}')
    elif predicted_delta >= 0.40:
        print(f'Buying {call_2} calls')
        subprocess.run(f'python buy.py buy Stonks_City 62797BA935 call 60 {call_2}')
    elif predicted_delta >= 0.30:
        print(f'Buying {call_1} calls')
        subprocess.run(f'python buy.py buy Stonks_City 62797BA935 call 60 {call_1}')

##    elif predicted_delta <= -0.4:
##        print(f'Buying {put_6} puts')
##        #subprocess.run(f'python buy.py buy Stonks_City 62797BA935 put 60 {put_6}')
##    elif predicted_delta <= -0.38:
##        print(f'Buying {put_5} puts')
##        #subprocess.run(f'python buy.py buy Stonks_City 62797BA935 put 60 {put_5}')
##    elif predicted_delta <= -0.36:
##        print(f'Buying {put_4} put')
##        #subprocess.run(f'python buy.py buy Stonks_City 62797BA935 put 60 {put_4}')
    elif predicted_delta <= -0.50:
        print(f'Buying {put_3} puts')
        subprocess.run(f'python buy.py buy Stonks_City 62797BA935 put 60 {put_3}')
    elif predicted_delta <= -0.40:
        print(f'Buying {put_2} puts')
        subprocess.run(f'python buy.py buy Stonks_City 62797BA935 put 60 {put_2}')
    elif predicted_delta <= -0.30:
        print(f'Buying {put_1} puts')
        subprocess.run(f'python buy.py buy Stonks_City 62797BA935 put 60 {put_1}')
    else:
        print(f"No order placed.")



### INSTANTIATES STOP EVENT ###

e = Event()



### TRADING MODE AUTOMATED ACTIONS ###

def scheduler():
    now = datetime.now().time()
    now_delta = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
    print('running functions, time:', now_delta)
    # checks if trading window has closed
    if now_delta >= trading_ends and now_delta< trading_starts - timedelta(minutes=2):
        print('trading window has closed, terminating script')
        e.set()
        return
    # automated actions
    get_forecast()
    print('time:', now_delta)
    execute_orders()
##    prices = [now]
##    for file in prediction_files:
##    p = prediction('P58.csv')
##    prices.append(p)
##    append_list_as_row('forecasts.csv', prices)
##    print('predictions saved to forecasts.csv')
    pyautogui.press('volumedown')
    time.sleep(1)
    pyautogui.press('volumeup')
    


### STARTS TRADING MODE ###

def run():
    print('trading mode starting, time:', datetime.now().time())
    schedule(scheduler, interval= interval*60.0)
    test()
    get_forecast()
    execute_orders()
    run_loop(stop_event=e)



### PRINT TIME ###

now = datetime.now().time()
now_delta = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
print("script starting, time:", now_delta)



### LIST OF PREDICTION FILES ###

prediction_files = ['P58.csv', 'P60.csv', 'P62.csv']



### CONTROLS WHEN TRADING MODE (run()) STARTS ###

if now_delta>= trading_starts - timedelta(minutes=1) or now_delta< trading_ends - timedelta(minutes=1):
    print('trading window is open')
    y = timedelta(hours=now.hour, minutes=now.minute+1, seconds=delay)
    delta_t = y - now_delta
    secs = delta_t.total_seconds()
    t = Timer(secs, run)
    print('trading mode will start at the beginning of the second minute from now')
    print('time until trading mode starts:', delta_t)
    t.start()

else:
    print('trading window has not begun, \nwill switch to trading mode when trading window begins')
    y = trading_starts - timedelta(minutes=1) + timedelta(seconds=delay)
    delta_t = y - now_delta
    print('time until trading mode starts:', delta_t)
    secs = delta_t.total_seconds()
    t = Timer(secs, run)
    t.start()
