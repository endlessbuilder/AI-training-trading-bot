from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
import yfinance as yf
import numpy as np
import pandas as pd
import pandas_ta as ta


# Fetch Historical Data
def get_data(symbol: str, period='60d', interval='15m'):
    data = yf.download(tickers=symbol, period=period, interval=interval)
    data.reset_index(inplace=True)
    return data


data = get_data('DOGE-USD')


# ATR Calculation
def calculate_atr(data, period=14):
    data['ATR'] = data['High'].rolling(period).max() - data['Low'].rolling(period).min()
    return data.fillna(method='bfill')


data = calculate_atr(data)


# Indicators
def add_indicators(data):
    data['RSI'] = 100 - (100 / (1 + data['Close'].diff().rolling(14).apply(
        lambda x: (x[x > 0].sum() / -x[x < 0].sum()) if x[x < 0].sum() != 0 else 0)))
    data['MACD'] = data['Close'].ewm(span=12, adjust=False).mean() - data['Close'].ewm(span=26, adjust=False).mean()
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
    data['ADX'] = ta.adx(data['High'], data['Low'], data['Close'], length=14)['ADX_14']
    return data


data = add_indicators(data)

print(data[['ADX']].describe())


# Identify Rejection Candles
def identify_rejection(data):
    data['rejection'] = data.apply(lambda row:
                                   2 if (
                                           ((min(row['Open'], row['Close']) - row['Low']) > (
                                                   0.7 * abs(row['Close'] - row['Open']))) and
                                           ((row['High'] - max(row['Close'], row['Open'])) < (
                                                   1.5 * abs(row['Close'] - row['Open']))) and
                                           ((abs(row['Open'] - row['Close']) > row['ATR'] * 0.05))
                                   ) else 1 if (
                                           ((row['High'] - max(row['Open'], row['Close'])) > (
                                                   0.7 * abs(row['Open'] - row['Close']))) and
                                           ((min(row['Close'], row['Open']) - row['Low']) < (
                                                   1.5 * abs(row['Open'] - row['Close']))) and
                                           ((abs(row['Open'] - row['Close']) > row['ATR'] * 0.05))
                                   ) else 0, axis=1)
    return data


data = identify_rejection(data)


# Pivot Points
def calculate_pivot_points(data):
    data['Pivot'] = (data['High'] + data['Low'] + data['Close']) / 3
    data['Resistance_1'] = (2 * data['Pivot']) - data['Low']
    data['Support_1'] = (2 * data['Pivot']) - data['High']
    return data


data = calculate_pivot_points(data)


# Generate Buy/Sell Signals
def generate_signals(data):
    data['signal'] = np.where(
        (data['rejection'] == 2) & (data['Low'] <= data['Support_1']) & (data['RSI'] < 40), 2,
        np.where(
            (data['rejection'] == 1) & (data['High'] >= data['Resistance_1']) & (data['RSI'] > 60), 1, 0
        )
    )
    return data


data = generate_signals(data)

print(data['signal'].value_counts())

# Backtesting Strategy Class
class MyRejectionStrategy(Strategy):
    atr_mult_sl = 1.5  # Default values, will be optimized
    atr_mult_tp = 3.5

    def init(self):
        self.signal = self.I(lambda x: x, self.data.signal)
        self.atr = self.I(lambda x: x, self.data.ATR)
        self.adx = self.I(lambda x: x, self.data.ADX)

    #def init(self):
        #self.signal = self.data.signal
        #self.atr = self.data.ATR
        #self.adx = self.data.ADX

    def next(self):
        for trade in self.trades:
            if trade.is_long:
                trade.sl = max(trade.sl, self.data.Close[-1] - self.atr[-1] * 1.5)
            elif trade.is_short:
                trade.sl = min(trade.sl, self.data.Close[-1] + self.atr[-1] * 1.5)

        if self.signal[-1] == 2 and not self.position and self.adx[-1] > 20:  # Buy Signal
            sl = self.data.Low[-1] - self.atr[-1] * 1.2
            tp = self.data.High[-1] + self.atr[-1] * 3.5
            self.buy(sl=sl, tp=tp)
        elif self.signal[-1] == 1 and not self.position and self.adx[-1] > 20:  # Sell Signal
            sl = self.data.High[-1] + self.atr[-1] * 1.2
            tp = self.data.Low[-1] - self.atr[-1] * 3.5
            self.sell(sl=sl, tp=tp)


# Format Data for Backtesting
bt_data = data[['Open', 'High', 'Low', 'Close', 'ATR', 'ADX', 'signal']].dropna()

# Run Backtest
bt = Backtest(bt_data, MyRejectionStrategy, cash=100000, commission=0.0005)
results = bt.optimize(
    atr_mult_sl=range(1, 3, 1),
    atr_mult_tp=range(2, 5, 1),
    maximize='Return [%]'
)

# Display Results
print(results)

# Plot Backtest
bt.plot()




