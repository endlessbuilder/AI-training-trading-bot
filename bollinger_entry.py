import numpy as np
import yfinance as yf
import pandas as pd
import plotly
import plotly.graph_objects as go
import pandas_ta as ta
import matplotlib.pyplot as plt


def get_data(symbol: str):
    data = yf.download(tickers=symbol, period='300d', interval='1d')
    data.reset_index(inplace=True, drop=True)  ##changes
    return data


data = get_data("TATAMOTORS.NS")

data.ta.bbands(length=10, std=1.5, append=True)

data['Upper Band'] = data['BBU_10_1.5']
data['Lower Band'] = data['BBL_10_1.5']


def calc_sma(data, length: int):
    return ta.sma(data['Close'], length)

data['SMA'] = calc_sma(data, 20)
data.dropna(inplace=True)


def check_candles(data, backcandles, ma_column):
    categories=[0 for _ in range(backcandles)]
    for i in range(backcandles, len(data)):
        if all(data['Close'][i-backcandles:i] > data[ma_column][i-backcandles:i]):
            categories.append(2) #up_trend
        elif all(data['Close'][i-backcandles:i] < data[ma_column][i-backcandles:i]):
            categories.append(1) #down_trend
        else:
            categories.append(0) #no_trend
    return categories


data['Trend'] = check_candles(data, 7, 'SMA')

data['entry'] = 0

#Buy entry
buy_entry = (data['Trend'] == 2) & ((data['Open'] < data['Lower Band']) & (data['Close'] > data['Lower Band']))
data.loc[buy_entry, 'entry'] = 2
#sell entry
sell_entry = (data['Trend'] == 1) & ((data['Open'] > data['Upper Band']) & (data['Close'] < data['Upper Band']))
data.loc[sell_entry, 'entry'] = 1

data[data['entry'] != 0]
pd.set_option('display.max_columns', None)
print(data)

#plotting
dfpl=data[:]
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['Open'],
                high=dfpl['High'],
                low=dfpl['Low'],
                close=dfpl['Close'])])

fig.add_trace(go.Scatter(x=dfpl.index, y=dfpl['SMA'], mode='lines', line=dict(color="red"), name="SMA"))
fig.add_trace(go.Scatter(x=dfpl.index, y=dfpl['Lower Band'], mode='lines', line=dict(color="blue"), name="Lower Band "))
fig.add_trace(go.Scatter(x=dfpl.index, y=dfpl['Upper Band'], mode='lines', line=dict(color="blue"), name="Upper Band"))


fig.update_layout(xaxis_rangeslider_visible=False)
fig.show()


