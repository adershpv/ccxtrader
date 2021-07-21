from ta.momentum import StochRSIIndicator, rsi
from ta.trend import ema_indicator, sma_indicator, macd, macd_signal, macd_diff, PSARIndicator
from ta.volatility import average_true_range
from ta.volume import volume_weighted_average_price

from utils import rounded
from constants import *


def get_rsi(df):
    df["rsi"] = rounded(rsi(df["close"], 14))
    return df


def get_stoch_rsi(df):
    rsi = StochRSIIndicator(df["close"], 14, 3, 3)
    df["rsi_k"] = rounded(rsi.stochrsi_k() * 100)
    df["rsi_d"] = rounded(rsi.stochrsi_d() * 100)
    return df


def get_ema(df):
    df["fast_ema"] = rounded(
        ema_indicator(df['close'], FAST_EMA_PERIOD)
    )
    df["medium_ema"] = rounded(
        ema_indicator(df['close'], MEDIUM_EMA_PERIOD)
    )
    df["slow_ema"] = rounded(
        ema_indicator(df['close'], SLOW_EMA_PERIOD)
    )
    return df


def get_trend_sma(df):
    df["trend_sma"] = rounded(
        sma_indicator(df['close'], TREND_SMA_PERIOD)
    )
    return df


def get_par_sar(df):
    psari = PSARIndicator(
        df['high'], df['low'], df['close']
    )
    df["par_sar"] = psari.psar()
    return df


def get_macd(df):
    df["macd_line"] = macd(df['close'])
    df["signal_line"] = macd_signal(df['close'])
    df["macd_diff"] = macd_diff(df['close'])
    return df


def get_atr(df):
    df["atr"] = rounded(
        average_true_range(
            df['high'],
            df['low'],
            df['close']
        )
    )
    return df


def get_vwap(df):
    df["vwap"] = volume_weighted_average_price(
        df['high'],
        df['low'],
        df['close'],
        df['volume']
    )
    return df
