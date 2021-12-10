from datetime import datetime, timedelta, time
from threading import Timer, Event
from ischedule import schedule, run_loop
import subprocess

'''
This script was my scratchpad for building a script that I could run before
the trading window began. When trading begins, the task is run every single
minute at precisely the same microsecond.
'''

def task_1():
    now = datetime.now().time()
    now_delta = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
    print(now_delta)
##    if now_delta >= trading_ends:
##        print('trading window has closed, terminating script')
##        e.set()
##        return
    print("task 1")
    subprocess.run("python prices.py TWOU.csv 101 60")

e = Event()

def run():
    print(datetime.now().time())
    schedule(task_1, interval=60.0)
    run_loop(stop_event=e)

print("time:", datetime.now().time())
now = datetime.now().time()
now_delta = timedelta(hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
trading_starts = timedelta(hours=13, minutes=49)
#trading_starts is the first valid trading minute
trading_ends = timedelta(hours=3, minutes=0)
#trading_ends is the first invalid trading minute
delay = 1
#delay is how many seconds to wait each minute before starting each forecast

if now_delta>= trading_starts - timedelta(minutes=2):# or now_delta< trading_ends - timedelta(minutes=2):
    print('trading window is open')
    y = timedelta(hours=now.hour, minutes=now.minute+1, seconds=delay)
    delta_t = y - now_delta
    print('timer:', delta_t)
    secs = delta_t.total_seconds()
    t = Timer(secs, run)
    print('trading mode will start at the beginning of the second minute from now')
    t.start()

else:
    print('trading window has not begun, \nwill switch to trading mode when trading window begins')
    y = trading_starts - timedelta(minutes=1) + timedelta(seconds=delay)
    delta_t = y - now_delta
    print('timer:', delta_t)
    secs = delta_t.total_seconds()
    t = Timer(secs, run)
    t.start()
