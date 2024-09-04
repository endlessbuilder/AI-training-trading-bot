import yfinance as yf
import pandas as pd
import plotly
import plotly.graph_objects as go
import pandas_ta as ta
import matplotlib.pyplot as plt

dataf = yf.download("^NSEI", start="2023-01-01", end="2024-08-30", interval='1d')

dataf = dataf[dataf["High"] != dataf["Low"]]
dataf.reset_index(inplace=True)


def rejection_signal(df):
    # bullish signal
    if (df.Open.iloc[-1] < df.Close.iloc[-1] and
            (df.High.iloc[-1] - df.Close.iloc[-1]) < abs(df.Open.iloc[-1] - df.Close.iloc[-1]) / 10 and
            (df.Open.iloc[-1] - df.Low.iloc[-1]) > abs(df.Open.iloc[-1] - df.Close.iloc[-1]) * 5):
        return 2

    # bearish signal
    elif (df.Open.iloc[-1] > df.Close.iloc[-1] and
          (df.High.iloc[-1] - df.Open.iloc[-1]) > abs(df.Open.iloc[-1] - df.Close.iloc[-1]) * 5 and
          (df.Close.iloc[-1] - df.Low.iloc[-1]) < abs(df.Open.iloc[-1] - df.Close.iloc[-1]) / 10):
        return 1

    # no_signal
    else:
        return 0


def engulfing_signal(df):
    # get the current and previous candles
    prev_candle = df.iloc[-2]
    curr_candle = df.iloc[-1]

    # bullish engulfing
    if ((curr_candle['Close'] > prev_candle['Open'])
            and (curr_candle['Open'] < prev_candle['Close'])
            and (prev_candle['Open'] > prev_candle['Close'])):
        return 2

    # bearish engulfing
    elif ((curr_candle['Open'] > prev_candle['Close'])
          and (curr_candle['Close'] < prev_candle['Open'])
          and (prev_candle['Close'] > prev_candle['Open'])):
        return 1

    else:
        return 0


signal = [0]*len(dataf)
for i in range(3,len(dataf)):
    df = dataf[i-3:i+1]
    signal[i] = rejection_signal(df)
dataf["rejection_signal"] = signal

signal = [0]*len(dataf)
for i in range(1,len(dataf)):
    df = dataf[i-1:i+1]
    signal[i] = engulfing_signal(df)
dataf["engulfing_signal"] = signal

up_count = 0
down_count = 0
total_count = 0


#bullish
for i in range(len(dataf) - 1):
    if dataf.engulfing_signal.iloc[i] == 1:
        total_count += 1
        if dataf.Close.iloc[i+1] > dataf.Open.iloc[i+1]:
            up_count += 1
        elif dataf.Close.iloc[i+1] < dataf.Open.iloc[i+1]:
            down_count += 1

up_per = (up_count/total_count)*100
down_per = (down_count/total_count)*100

print(up_per, down_per, total_count)

print(dataf[dataf["engulfing_signal"]==1])



up_count = 0
down_count = 0
total_count = 0

#bearish
for i in range(len(dataf) - 1):
    if dataf.engulfing_signal.iloc[i] == 2:
        total_count += 1
        if dataf.Close.iloc[i+1] > dataf.Open.iloc[i+1]:
            up_count += 1
        elif dataf.Close.iloc[i+1] < dataf.Open.iloc[i+1]:
            down_count += 1

up_per = (up_count/total_count)*100
down_per = (down_count/total_count)*100

print(up_per, down_per, total_count)

print(dataf[dataf["engulfing_signal"]==2])



#graph visuals
st = 0
dfpl = dataf[st:st+150].copy()
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['Open'],
                high=dfpl['High'],
                low=dfpl['Low'],
                close=dfpl['Close'])])

fig.show()


def average_next_n_candles(df, i, N):
    #if there are N candles after current one
    if i+N >= len(df):
        return None
    #average closing price of next N candles
    avg_price = df['Close'].iloc[i+1:i+N+1].mean()

    #average price v/s current closing price
    if avg_price < df['Close'].iloc[i]:
        return 1
    elif avg_price > df['Close'].iloc[i]:
        return 2
    else:
        return 0

N=4
signal=[0]*len(dataf)
for i in range(len(dataf)-N):
    signal[i] = average_next_n_candles(dataf ,i ,N)
dataf["price_target"] = signal

print(dataf[dataf["engulfing_signal"]==dataf["price_target"]].count())


equal_count = 0
different_count = 0
total_count = 0

for i in range(len(dataf)):
    if dataf.engulfing_signal.iloc[i] != 0:
        total_count += 1
        if dataf.engulfing_signal.iloc[i] == dataf.price_target.iloc[i]:
            equal_count += 1
        else:
            different_count += 1

equal_per = (equal_count/total_count)*100
diff_per = (different_count/total_count)*100

print(equal_per, diff_per)
