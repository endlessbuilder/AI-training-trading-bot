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

url = 'https://margincalculator.angelone.in/OpenAPI_File/files/OpenAPIScripMaster.json'
d = requests.get(url).json()
token_df = pd.DataFrame.from_dict(d)
token_df['expiry'] = pd.to_datetime(token_df['expiry'], format='%Y-%m-%d', errors='coerce')
token_df = token_df.astype({'strike': float})


def gettokenInfo(df, exch_seg, symbol):
    # Filter based on exchange and symbol
    eq_df = df[(df['exch_seg'] == exch_seg) & (df['symbol'] == symbol)]

    if not eq_df.empty:
        return eq_df[['token']]  # Return only the token column
    else:
        return "Symbol not found"

# Fetch token ID
token_id = gettokenInfo(token_df, 'NSE', 'VIKASECO-EQ')
print(token_id)



