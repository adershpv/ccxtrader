#!/usr/bin/env python3

import ccxt
import time
import pandas as pd
import sys

from config import *
from constants import *
from strategy import Strategy
from trader import trade
from chatbot import send_message

time.sleep(2)

action = TRADE

try:
    action = sys.argv[1]
except IndexError:
    pass


print("="*80, "\n")
print(SYMBOL, time.ctime())

exchange = ccxt.binanceusdm({
    "apiKey": BINANCE_API_KEY,
    "secret": BINANCE_API_SECRET
})


def get_strategy(timeframe):
    bars = exchange.fetch_ohlcv(
        SYMBOL, timeframe=timeframe, limit=CANDLESTICK_LIMIT)
    df = pd.DataFrame(bars[:-1], columns=COLUMNS)
    return Strategy(df, timeframe)


def auto_trade():
    strategy = get_strategy(TIME_FRAME)
    side, p, tp, sl, lc = strategy.apply()
    print(side, p, tp, sl, lc)
    trade(exchange, side, p, tp, sl, lc)


def notify_message(m):
    message = "\n".join([x for x in m if x])
    if message:
        print(message)
        send_message(message)


if action == NOTIFY_MESSAGE:
    strategy = get_strategy(TIME_FRAME)
    side, message = strategy.check_stoch_rsi_extreme()

    htf_strategy = get_strategy(HIGHER_TIME_FRAME)
    htf_side1, htf_message1 = htf_strategy.check_stoch_rsi_extreme()
    htf_side2, htf_message2 = htf_strategy.check_stoch_rsi_cross()

    if side and side == htf_side1 and htf_side1 == htf_side2:
        notify_message([side, SYMBOL, message, htf_message1, htf_message2])

elif action == TRADE:
    auto_trade()
