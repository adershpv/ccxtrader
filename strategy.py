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

    def _get_stoch_rsi(self):
        rsi = StochRSIIndicator(self.df["close"], 14, 3, 3)
        self.df["rsi_k"] = rsi.stochrsi_k() * 100
        self.df["rsi_d"] = rsi.stochrsi_d() * 100

    def _get_ema(self):
        self.df["fast_ema"] = ema_indicator(
            self.df['close'], FAST_EMA_PERIOD)
        self.df["medium_ema"] = ema_indicator(
            self.df['close'], MEDIUM_EMA_PERIOD)
        self.df["slow_ema"] = ema_indicator(
            self.df['close'], SLOW_EMA_PERIOD)

    def _get_trend_sma(self):
        self.df["trend_sma"] = sma_indicator(
            self.df['close'], TREND_SMA_PERIOD)

    def _get_par_sar(self):
        psari = PSARIndicator(
            self.df['high'], self.df['low'], self.df['close'])
        self.df["par_sar"] = psari.psar()

    def _get_macd(self):
        self.df["macd_line"] = macd(self.df['close'])
        self.df["signal_line"] = macd_signal(self.df['close'])

    def _get_atr(self):
        self.df["atr"] = average_true_range(
            self.df['high'],
            self.df['low'],
            self.df['close'])

    def _get_vwap(self):
        self.df["vwap"] = volume_weighted_average_price(
            self.df['high'],
            self.df['low'],
            self.df['close'],
            self.df['volume']
        )

    def _get_indicator_values(self):
        # self._get_par_sar()
        # self._get_trend_sma()
        self._get_macd()
        self._get_stoch_rsi()
        self._get_atr()
        # self._get_vwap()
        # self._get_ema()
        self.current = self.df.iloc[-1]
        self.prev = self.df.iloc[-2]
        print(self.current)

    def _bullish(self):
        if STRATEGY == MACD_CROSSOVER_STRATEGY:
            return all([
                self.current["macd_line"] > self.current["signal_line"],
                self.prev["macd_line"] <= self.prev["signal_line"],
                self.current["rsi_k"] > self.current["rsi_d"]
            ])
        else:
            return all([
                self.current["medium_ema"] > self.prev["medium_ema"],
                self.current["medium_ema"] <= self.prev["medium_ema"],
                self.current["fast_ema"] > self.prev["medium_ema"],
                self.current["slow_ema"] > self.prev["trend_sma"],
                self.current["rsi_k"] > self.current["rsi_d"],
                self.current["rsi_k"] < MAX_STOCH_RSI
            ])

    def _bearish(self):
        if STRATEGY == MACD_CROSSOVER_STRATEGY:
            return all([
                self.current["macd_line"] < self.current["signal_line"],
                self.prev["macd_line"] >= self.prev["signal_line"],
                self.current["rsi_k"] < self.current["rsi_d"]
            ])
        else:
            return all([
                self.current["medium_ema"] < self.prev["medium_ema"],
                self.current["medium_ema"] >= self.prev["medium_ema"],
                self.current["fast_ema"] < self.prev["medium_ema"],
                self.current["slow_ema"] < self.prev["trend_sma"],
                self.current["rsi_k"] < self.current["rsi_d"],
                self.current["rsi_k"] > MIN_STOCH_RSI
            ])

    def _get_stop_loss_margin(self):
        return MAX_TAKE_PROFIT_MARGIN * self.current["atr"], MAX_STOP_LOSS_MARGIN * self.current["atr"]

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
