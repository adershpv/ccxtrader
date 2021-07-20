from ta.momentum import StochRSIIndicator, rsi
from ta.trend import ema_indicator, sma_indicator, macd, macd_signal, macd_diff, PSARIndicator
from ta.volatility import average_true_range
from ta.volume import volume_weighted_average_price

from constants import *


def rounded(num, decimal_places=CALCULATION_DECIMAL_PLACES):
    return round(num, decimal_places)


class Strategy:
    def __init__(self, df):
        self.df = df
        self.current = df.iloc[-1]
        self.prev = df.iloc[-2]
        self.close_price = self.current[CLOSE_INDEX]
        self.lastRows = self.df.tail(LAST_N_ROWS)
        self.maxValueIndex = self.lastRows.idxmax()
        self.minValueIndex = self.lastRows.idxmin()
        print(f"Close Price\t{self.close_price}")

    def _get_rsi(self):
        self.df["rsi"] = rounded(rsi(self.df["close"], 14))

    def _get_stoch_rsi(self):
        rsi = StochRSIIndicator(self.df["close"], 14, 3, 3)
        self.df["rsi_k"] = rounded(rsi.stochrsi_k() * 100)
        self.df["rsi_d"] = rounded(rsi.stochrsi_d() * 100)

    def _get_ema(self):
        self.df["fast_ema"] = rounded(ema_indicator(
            self.df['close'], FAST_EMA_PERIOD))
        # self.df["medium_ema"] = rounded(ema_indicator(
        #     self.df['close'], MEDIUM_EMA_PERIOD))
        # self.df["slow_ema"] = rounded(ema_indicator(
        #     self.df['close'], SLOW_EMA_PERIOD))

    def _get_trend_sma(self):
        self.df["trend_sma"] = rounded(sma_indicator(
            self.df['close'], TREND_SMA_PERIOD))

    def _get_par_sar(self):
        psari = PSARIndicator(
            self.df['high'], self.df['low'], self.df['close'])
        self.df["par_sar"] = psari.psar()

    def _get_macd(self):
        self.df["macd_line"] = macd(self.df['close'])
        self.df["signal_line"] = macd_signal(self.df['close'])
        self.df["macd_diff"] = macd_diff(self.df['close'])

    def _get_atr(self):
        self.df["atr"] = rounded(average_true_range(
            self.df['high'],
            self.df['low'],
            self.df['close']))

    def _get_vwap(self):
        self.df["vwap"] = volume_weighted_average_price(
            self.df['high'],
            self.df['low'],
            self.df['close'],
            self.df['volume']
        )

    def _get_indicator_values(self):
        # self._get_rsi()
        # self._get_par_sar()
        # self._get_trend_sma()
        # self._get_macd()
        self._get_stoch_rsi()
        # self._get_atr()
        # self._get_vwap()
        # self._get_ema()
        self.current = self.df.iloc[-1]
        self.prev = self.df.iloc[-2]

    def _print_emas(self):
        print("EMA\t\tCurrent\t\t\tPrevious")
        print(
            f"{FAST_EMA_PERIOD}\t {self.current['fast_ema']}\t{self.prev['fast_ema']}")
        print(
            f"{MEDIUM_EMA_PERIOD}\t {self.current['medium_ema']}\t{self.prev['medium_ema']}")
        print(
            f"{SLOW_EMA_PERIOD}\t {self.current['slow_ema']}\t{self.prev['slow_ema']}")

    def _crossover(self, key1, key2):
        return self.current[key1] >= self.current[key2] and self.prev[key1] < self.prev[key2]

    def _crossunder(self, key1, key2):
        return self.current[key1] <= self.current[key2] and self.prev[key1] > self.prev[key2]

    def _get_trading_action(self):
        action = HOLD
        if STRATEGY == STOCH_RSI_STRATEGY:
            print(f'EMA {SLOW_EMA_PERIOD}\t\t{self.current["slow_ema"]}')
            print(f'RSI\t\t{self.current["rsi"]}')
            print(
                f'Stoch RSI\t{self.current["rsi_k"]}\t{self.current["rsi_d"]}')
            if self._crossover("rsi_k", "rsi_d"):
                if self.close_price > self.current["slow_ema"] and self.current["rsi"] > MIN_RSI and self.current["rsi_d"] < MIN_STOCH_RSI:
                    action = SIDE_BUY
                elif self.current["rsi_d"] < MIN_STOCH_RSI_CLOSE:
                    action = CLOSE_SHORT
            if self._crossunder("rsi_k", "rsi_d"):
                if self.close_price < self.current["slow_ema"] and self.current["rsi"] < MAX_RSI and self.current["rsi_d"] > MAX_STOCH_RSI:
                    action = SIDE_SELL
                elif self.current["rsi_d"] > MAX_STOCH_RSI_CLOSE:
                    action = CLOSE_LONG
        return action

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
        return price, rounded(tp, PRICE_DECIMAL_PLACES), rounded(sl, PRICE_DECIMAL_PLACES)

    def _check_price_ema_cross(self):
        action = HOLD
        ema = self.current["fast_ema"]
        open = self.current["open"]
        close = self.current["close"]
        if open <= ema and close > ema:
            action = SIDE_BUY
        if open >= ema and close < ema:
            action = SIDE_SELL
        return action

    def analyse(self):
        self._get_indicator_values()
        action = self._check_price_ema_cross()
        # action = self._get_trading_action()
        if action == SIDE_BUY or action == SIDE_SELL:
            p, tp, sl = self._get_stop_limits(action)
        else:
            p = tp = sl = ''
        return action, p, tp, sl

    def check_stoch_rsi_cross(self):
        self._get_indicator_values()
        cross = ""
        if self._crossover("rsi_k", "rsi_d"):
            cross = "OVER"
        if self._crossunder("rsi_k", "rsi_d"):
            cross = "UNDER"
        return cross
