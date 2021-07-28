from constants import *

# Canldestick Patterns


def green_candle(candle):
    return candle["close"] > candle["open"]


def red_candle(candle):
    return candle["close"] < candle["open"]


def bullish_engulfing(df):
    return df.iloc[-1]["close"] > max(df.iloc[-2]["open"], df.iloc[-2]["close"])


def bearish_engulfing(df):
    return df.iloc[-1]["close"] < min(df.iloc[-2]["open"], df.iloc[-2]["close"])


def three_prev_greens(df):
    return all([
        green_candle(df.iloc[-2]),
        green_candle(df.iloc[-3]),
        green_candle(df.iloc[-4])
    ])


def three_prev_reds(df):
    return all([
        red_candle(df.iloc[-2]),
        red_candle(df.iloc[-3]),
        red_candle(df.iloc[-4])
    ])


def bullish_3L_strike(df):
    return three_prev_reds(df) and bullish_engulfing(df)


def bearish_3L_strike(df):
    return three_prev_greens(df) and bearish_engulfing(df)


# Price Actions

def crossover(df, key1, key2):
    return df.iloc[-1][key1] > df.iloc[-1][key2] and df.iloc[-2][key1] <= df.iloc[-2][key2]


def crossunder(df, key1, key2):
    return df.iloc[-1][key1] < df.iloc[-1][key2] and df.iloc[-2][key1] >= df.iloc[-2][key2]


def stoch_rsi_oversold(df):
    return df.iloc[-1]['rsi_k'] < 20 or df.iloc[-1]['rsi_d'] < 20


def stoch_rsi_overbought(df):
    return df.iloc[-1]['rsi_k'] > 80 or df.iloc[-1]['rsi_d'] > 80

# Calculations


def rounded(num, decimal_places=CALCULATION_DECIMAL_PLACES):
    return round(num, decimal_places)


def get_stop_loss_margin(atr):
    return MAX_TAKE_PROFIT_MARGIN * atr, MAX_STOP_LOSS_MARGIN * atr


def get_swing_low_sl(df):
    c = df[df["close"] < df["open"]]
    sl = min(c.iloc[-1]["low"], c.iloc[-2]["low"]) - SWING_STOP_LOSS_MARGIN
    return rounded(sl, PRICE_DECIMAL_PLACES)


def get_swing_high_sl(df):
    c = df[df["close"] > df["open"]]
    sl = max(c.iloc[-1]["high"], c.iloc[-2]["high"]) + SWING_STOP_LOSS_MARGIN
    return rounded(sl, PRICE_DECIMAL_PLACES)


def get_stop_limits(df, price, atr, side):
    tp_diff, sl_diff = get_stop_loss_margin(atr)
    if side == SIDE_BUY:
        tp = price + tp_diff
        sl = get_swing_low_sl(
            df) if ENABLE_SWING_STOP_LOSS else price - sl_diff
    else:
        tp = price - tp_diff
        sl = get_swing_high_sl(
            df) if ENABLE_SWING_STOP_LOSS else price + sl_diff
    return price, rounded(tp, PRICE_DECIMAL_PLACES), rounded(sl, PRICE_DECIMAL_PLACES)
