#!/usr/bin/env python3

import ccxt
import time
import pandas as pd

from config import *
from constants import *
from strategy import Strategy
from trader import trade
from chatbot import send_message

print("="*80, "\n")
print(SYMBOL, time.ctime())

exchange = ccxt.binanceusdm({
    "apiKey": BINANCE_API_KEY,
    "secret": BINANCE_API_SECRET
})


bars = exchange.fetch_ohlcv(
    SYMBOL, timeframe=TIME_FRAME, limit=CANDLESTICK_LIMIT)
df = pd.DataFrame(bars[:-1], columns=COLUMNS)

strategy = Strategy(df)


def auto_trade():
    side, p, tp, sl = strategy.apply()
    print(side, p, tp, sl)

    def notify_action_details(side, tp, sl):
        message = 'Buy (LONG)' if side == SIDE_BUY else 'Sell (SHORT)'
        if ENABLE_TAKE_PROFIT:
            message += f"\nTake Profit: {tp}"
        if ENABLE_STOP_LOSS:
            message += f"\nStop Loss: {sl}"
        send_message(message)

    if side != HOLD:
        trade(exchange, side, p, tp, sl)
        notify_action_details(side, tp, sl)


def notify_message(message):
    if message:
        print(message)
        send_message(message)


notify_message(strategy.check_stoch_rsi_cross())
notify_message(strategy.check_engulfing_pattern())
notify_message(strategy.check_three_line_strike())
