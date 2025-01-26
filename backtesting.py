import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

import numpy as np
import yfinance as yf
import pandas as pd
import plotly
import plotly.graph_objects as go
import pandas_ta as ta
import matplotlib.pyplot as plt


def SMA(values, n):
    return pd.Series(values).rolling(n).mean()

class SmaCross(Strategy):
    n1 = 10
    n2 = 20

    def init(self):
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()

        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()


data = yf.download("TATAMOTORS.NS")

bt = Backtest(data, SmaCross)
stats = bt.run()
pl = bt.plot()
print(stats['_trades'].to_string())
print(pl['_trades'].to_string())
