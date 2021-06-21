from ta.momentum import StochRSIIndicator
from ta.trend import ema_indicator, sma_indicator, macd, macd_signal, PSARIndicator
from ta.volatility import average_true_range
from ta.volume import volume_weighted_average_price

from constants import *


def rounded(num):
    return round(num * 10000)/10000


class Strategy:
    def __init__(self, df):
        self.df = df
        self.current = df.iloc[-1]
        self.close_price = self.current[CLOSE_INDEX]
        print("Close Price", self.close_price)

        self.stoch_rsi_k = None
        self.stoch_rsi_d = None
        self.stoch_rsi_prev_k = None
        self.stoch_rsi_prev_d = None

        self.fast_ema = None
        self.medium_ema = None
        self.slow_ema = None

        self.trend_sma = None
        self.macd_line = None
        self.signal_line = None
        self.macd_prev_line = None
        self.signal_prev_line = None
        self.par_sar = None

        self.atr = None
        self.vwap = None

    def _get_stoch_rsi(self):
        rsi = StochRSIIndicator(self.df['close'], 14, 3, 3)
        self.stoch_rsi_k = rsi.stochrsi_k().iloc[-1] * 100
        self.stoch_rsi_d = rsi.stochrsi_d().iloc[-1] * 100
        print("Stoch RSI", self.stoch_rsi_k, self.stoch_rsi_d)

        # prev_rsi = StochRSIIndicator(self.df[:-1]['close'], 14, 3, 3)
        # self.stoch_rsi_prev_k = prev_rsi.stochrsi_k().iloc[-1] * 100
        # self.stoch_rsi_prev_d = prev_rsi.stochrsi_d().iloc[-1] * 100
        # print("Previous Stoch RSI", self.stoch_rsi_prev_k, self.stoch_rsi_prev_d)

    def _get_ema(self):
        self.fast_ema = ema_indicator(
            self.df['close'], FAST_EMA_PERIOD).iloc[-1]
        self.medium_ema = ema_indicator(
            self.df['close'], MEDIUM_EMA_PERIOD).iloc[-1]
        self.slow_ema = ema_indicator(
            self.df['close'], SLOW_EMA_PERIOD).iloc[-1]
        print("EMA", self.fast_ema, self.medium_ema, self.slow_ema)

    def _get_trend_sma(self):
        self.trend_sma = sma_indicator(
            self.df['close'], TREND_SMA_PERIOD).iloc[-1]
        print("SMA", self.trend_sma)

    def _get_par_sar(self):
        psari = PSARIndicator(
            self.df['high'], self.df['low'], self.df['close'])
        self.par_sar = psari.psar().iloc[-1]
        print("Parabolic SAR", self.par_sar)

    def _get_macd(self):
        self.macd_line = macd(self.df['close']).iloc[-1]
        self.signal_line = macd_signal(self.df['close']).iloc[-1]
        print("MACD", self.macd_line, self.signal_line)
        self.macd_prev_line = macd(self.df[:-1]['close']).iloc[-1]
        self.signal_prev_line = macd_signal(self.df[:-1]['close']).iloc[-1]
        print("Previous MACD", self.macd_prev_line, self.signal_prev_line)

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
        self._get_par_sar()
        self._get_trend_sma()
        # self._get_macd()
        # self._get_stoch_rsi()
        self._get_atr()
        # self._get_vwap()
        # self._get_ema()

    def _bullish(self):
        if STRATEGY == MACD_CROSSOVER_STRATEGY:
            return all([
                self.close_price > self.trend_sma,
                self.stoch_rsi_k > self.stoch_rsi_d,
                self.macd_line > self.signal_line,
                self.macd_prev_line <= self.signal_prev_line
            ])
        if STRATEGY == PARABOLIC_SAR_STRATEGY:
            return all([
                self.close_price > self.trend_sma,
                self.close_price > self.par_sar
            ])
        return False

    def _bearish(self):
        if STRATEGY == MACD_CROSSOVER_STRATEGY:
            return all([
                self.close_price < self.trend_sma,
                self.stoch_rsi_k < self.stoch_rsi_d,
                self.macd_line < self.signal_line,
                self.macd_prev_line >= self.signal_prev_line
            ])
        if STRATEGY == PARABOLIC_SAR_STRATEGY:
            return all([
                self.close_price < self.trend_sma,
                self.close_price < self.par_sar
            ])
        return False

    def _get_stop_loss_margin(self):
        return MAX_TAKE_PROFIT_MARGIN * self.atr, MAX_STOP_LOSS_MARGIN * self.atr

    def _get_stop_limits(self, side):
        price = self.close_price
        tp_diff, sl_diff = self._get_stop_loss_margin()
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
