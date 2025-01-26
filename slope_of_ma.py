import numpy as np
import yfinance as yf
import pandas as pd
import plotly
import plotly.graph_objects as go
import pandas_ta as ta
import matplotlib.pyplot as plt


def get_data(symbol:str):
    data = yf.download(tickers=symbol, period='100d', interval='1d')
    data.reset_index(inplace=True, drop=True)
    return data

data = get_data("TATAMOTORS.NS")


def calculate_sma(data, length:int):
    return ta.sma(data['Close'], length)

#calculate moving average
data['SMA'] = calculate_sma(data,20)
data.dropna(inplace=True)

#SMA Slope

def calculate_slope(series, period:int=5):
    slopes = [0 for _ in range(period-1)]
    for i in range(period-1, len(series)):
        x = np.arange(period)
        y = series[i-period+1:i+1].values
        slope = np.polyfit(x, y, 1)[0] #linear regression
        percent_slope = (slope/y[0])*100 #slope to a percentage
        slopes.append(percent_slope)
    return slopes

data['slope'] = calculate_slope(data['SMA'])

print(data[40:55])

#plotting

dfpl = data[:]
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['Open'],
                high=dfpl['High'],
                low=dfpl['Low'],
                close=dfpl['Close'])])

fig.add_scatter(x=dfpl.index, y=dfpl['SMA'], mode='markers',
                marker=dict(size=5, color="MediumPurple"),
                name="pivot")

fig.update_layout(xaxis_rangeslider_visible=False)
fig.show()
















