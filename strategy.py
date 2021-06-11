from ta.momentum import StochRSIIndicator
from ta.trend import ema_indicator
from ta.volatility import average_true_range
from ta.volume import volume_weighted_average_price

from constants import *


def rounded(num):
    return round(num * 10000)/10000


class Strategy:
    def __init__(self, df):
        self.df = df
        self.current = df.iloc[-1]

        self.stoch_rsi_k = None
        self.stoch_rsi_d = None
        self.stoch_rsi_prev_k = None
        self.stoch_rsi_prev_d = None

        self.fast_ema = None
        self.medium_ema = None
        self.slow_ema = None

        self.atr = None
        self.vwap = None

    def _get_stoch_rsi(self):
        rsi = StochRSIIndicator(self.df['close'], 14, 3, 3)
        self.stoch_rsi_k = rsi.stochrsi_k().iloc[-1] * 100
        self.stoch_rsi_d = rsi.stochrsi_d().iloc[-1] * 100
        print("Stoch RSI", self.stoch_rsi_k, self.stoch_rsi_d)

        prev_rsi = StochRSIIndicator(self.df[:-1]['close'], 14, 3, 3)
        self.stoch_rsi_prev_k = prev_rsi.stochrsi_k().iloc[-1] * 100
        self.stoch_rsi_prev_d = prev_rsi.stochrsi_d().iloc[-1] * 100
        print("Previous Stoch RSI", self.stoch_rsi_prev_k, self.stoch_rsi_prev_d)

    def _get_ema(self):
        self.fast_ema = ema_indicator(
            self.df['close'], FAST_EMA_PERIOD).iloc[-1]
        self.medium_ema = ema_indicator(
            self.df['close'], MEDIUM_EMA_PERIOD).iloc[-1]
        self.slow_ema = ema_indicator(
            self.df['close'], SLOW_EMA_PERIOD).iloc[-1]
        print("EMA", self.fast_ema, self.medium_ema, self.slow_ema)

    def _get_atr(self):
        atr = average_true_range(
            self.df['high'],
            self.df['low'],
            self.df['close'])
        self.atr = atr.iloc[-1]
        print("ATR", self.atr)

    def _get_vwap(self):
        vwap = volume_weighted_average_price(
            self.df['high'],
            self.df['low'],
            self.df['close'],
            self.df['volume']
        )
        self.vwap = vwap.iloc[-1]
        print("VWAP", self.vwap)

    def _get_indicator_values(self):
        self._get_stoch_rsi()
        self._get_ema()
        self._get_atr()
        self._get_vwap()

    def _bullish(self):
        if STRATEGY == RSI_CROSSING_STRATEGY:
            return all([
                self.stoch_rsi_k < 50,
                self.stoch_rsi_k > self.stoch_rsi_d,
                self.stoch_rsi_prev_k <= self.stoch_rsi_prev_d
            ])
        elif STRATEGY == EMA_RSI_STRATEGY:
            return all([
                self.stoch_rsi_k < 30,
                self.stoch_rsi_k > self.stoch_rsi_d,
                self.fast_ema > self.medium_ema,
                self.medium_ema > self.slow_ema
            ])
        elif STRATEGY == EMA_CROSSING_STRATEGY:
            return self.fast_ema > self.medium_ema
        return False

    def _bearish(self):
        if STRATEGY == RSI_CROSSING_STRATEGY:
            return all([
                self.stoch_rsi_k > 50,
                self.stoch_rsi_k < self.stoch_rsi_d,
                self.stoch_rsi_prev_k >= self.stoch_rsi_prev_d
            ])
        elif STRATEGY == EMA_RSI_STRATEGY:
            return all([
                self.stoch_rsi_k > 70,
                self.stoch_rsi_k < self.stoch_rsi_d,
                self.fast_ema < self.medium_ema,
                self.medium_ema < self.slow_ema
            ])
        elif STRATEGY == EMA_CROSSING_STRATEGY:
            return self.fast_ema < self.medium_ema
        return False

    def _get_stop_loss_margin(self, side):
        is_against_trend = (
            side == SIDE_BUY and self.fast_ema < self.slow_ema) or (
            side == SIDE_SELL and self.fast_ema > self.slow_ema)
        if is_against_trend:
            return MIN_TAKE_PROFIT_MARGIN * self.atr, MIN_STOP_LOSS_MARGIN * self.atr
        else:
            return MAX_TAKE_PROFIT_MARGIN * self.atr, MAX_STOP_LOSS_MARGIN * self.atr

    def _get_stop_limits(self, side):
        price = self.current[CLOSE_INDEX]
        tp_diff, sl_diff = self._get_stop_loss_margin(side)
        if side == SIDE_BUY:
            tp = price + tp_diff
            sl = price - sl_diff
        else:
            tp = price - tp_diff
            sl = price + sl_diff
        return rounded(price), rounded(tp), rounded(sl)

    def analyse(self):
        self._get_indicator_values()
        if self._bullish():
            p, tp, sl = self._get_stop_limits(SIDE_BUY)
            return SIDE_BUY, p, tp, sl
        elif self._bearish():
            p, tp, sl = self._get_stop_limits(SIDE_SELL)
            return SIDE_SELL, p, tp, sl
        else:
            return HOLD, "", "", ""
