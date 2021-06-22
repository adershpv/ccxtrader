#!/usr/bin/env python3

import ccxt
import time
import pandas as pd

from config import *
from constants import *
from strategy import Strategy
from trader import trade

print("="*80, "\n")
print(SYMBOL, time.ctime())

exchange = ccxt.binanceusdm({
    "apiKey": BINANCE_API_KEY,
    "secret": BINANCE_API_SECRET
})


bars = exchange.fetch_ohlcv(SYMBOL, timeframe=TIME_FRAME, limit=LIMIT)
df = pd.DataFrame(bars[:-1], columns=COLUMNS)

strategy = Strategy(df)
side, p, tp, sl = strategy.analyse()

print(side, p, tp, sl)

if side == SIDE_BUY or side == SIDE_SELL:
    trade(exchange, side, p, tp, sl)
