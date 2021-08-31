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


if action == NOTIFY:
    strategy = get_strategy(HIGHER_TIME_FRAME)
    chart = f"{SYMBOL} - {HIGHER_TIME_FRAME}"

    side1, message1 = strategy.check_stoch_rsi_extreme()
    side2, message2 = strategy.check_stoch_rsi_cross()
    if side1 == side2:
        notify_message([side1, chart, message1, message2])

    side3, message3 = strategy.check_three_line_strike()
    if side3:
        notify_message([side3, chart, message3])

    side4, message4 = strategy.check_macd_cross()
    if side4:
        notify_message([side4, chart, message4])

    side5, message5 = strategy.check_ema_cross()
    if side5:
        notify_message([side5, chart, message5])


elif action == TRADE:
    auto_trade()
