# package import statement
from SmartApi import SmartConnect
#import config
import pyotp
import time as tt
from logzero import logger
import pandas as pd
import login as l
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from datetime import datetime, date, time
import pandas as pd
from datetime import datetime
import requests
import numpy as np

obj = SmartConnect(api_key=l.api_key)
token = pyotp.TOTP(l.totp).now()
data = obj.generateSession(l.user_name, l.password, token)

refreshToken = data['data']['refreshToken']
print("refresh token" + refreshToken)

feedToken = obj.getfeedToken()
l.feed_token = feedToken

print(feedToken)
userProfile = obj.getProfile(refreshToken)
print(userProfile)


def place_order(symbol, token, qty, exch_seg, buy_sell, ordertype, price):
    try:
        orderparams = {
            "variety": "NORMAL",
            "tradingsymbol": "VIKASECO-EQ",
            "symboltoken": "3045",
            "transactiontype": "BUY",
            "exchange": "NSE",
            "ordertype": "LIMIT",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price":price,
            "squareoff": "0",
            "stoploss": "0",
            "quantity": "1"
        }
        # Method 1: Place an order and return the order ID
        orderid = smartApi.placeOrder(orderparams)
        logger.info(f"PlaceOrder : {orderid}")
        # Method 2: Place an order and return the full response
        response = smartApi.placeOrderFullResponse(orderparams)
        logger.info(f"PlaceOrder : {response}")
    except Exception as e:
        logger.exception(f"Order placement failed: {e}")
