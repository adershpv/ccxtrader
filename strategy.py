from constants import *
from utils import *
from indicators import *


class Strategy:
    def __init__(self, df, timeframe):
        self.timeframe = timeframe
        self.df = df
        self.current = df.iloc[-1]
        self.prev = df.iloc[-2]
        self.close_price = self.current['close']
        print(f"Close Price\t{self.close_price}")

    def _update_current_prev_values(self):
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

    def _get_trading_action(self):
        action = HOLD
        if STOCH_RSI_STRATEGY in STRATEGY:
            self.df = get_rsi(self.df)
            self.df = get_stoch_rsi(self.df)
            self.df = get_ema(self.df)
            self._update_current_prev_values()

            print(f'EMA {MEDIUM_EMA_PERIOD}\t\t{self.current["medium_ema"]}')
            print(f'RSI\t\t{self.current["rsi"]}')
            print(
                f'Stoch RSI\t{self.current["rsi_k"]}\t{self.current["rsi_d"]}')
            if crossover(self.df, "rsi_k", "rsi_d"):
                print("Stoch RSI crossover")
                if price_above_3_emas(self.current) and self.current["rsi"] > MIN_RSI and self.current["rsi_d"] < MIN_STOCH_RSI:
                    action = SIDE_BUY if ENABLE_AUTO_TRADE else CLOSE_SHORT
                elif self.current["rsi_d"] < MIN_STOCH_RSI_CLOSE and ENABLE_CLOSE_POSITION:
                    action = CLOSE_SHORT
            if crossunder(self.df, "rsi_k", "rsi_d"):
                print("Stoch RSI crossunder")
                if price_below_3_emas(self.current) and self.current["rsi"] < MAX_RSI and self.current["rsi_d"] > MAX_STOCH_RSI:
                    action = SIDE_SELL if ENABLE_AUTO_TRADE else CLOSE_LONG
                elif self.current["rsi_d"] > MAX_STOCH_RSI_CLOSE and ENABLE_CLOSE_POSITION:
                    action = CLOSE_LONG

        if THREE_LINE_STRIKE in STRATEGY:
            if bullish_3L_strike(self.df) and self.current["rsi_k"] > self.current["rsi_d"]:
                print("Bullish 3 line strike")
                action = SIDE_BUY
            if bearish_3L_strike(self.df) and self.current["rsi_k"] < self.current["rsi_d"]:
                print("Bearish 3 line strike")
                action = SIDE_SELL

        if EMA_CROSS_STRATEGY in STRATEGY:
            self.df = get_rsi(self.df)
            self.df = get_ema(self.df)
            self._update_current_prev_values()
            if crossover(self.df, "fast_ema", "medium_ema") and self.current["rsi"] > MIN_RSI:
                print("Bullish EMA crossover")
                action = SIDE_BUY
            elif crossunder(self.df, "fast_ema", "medium_ema") and self.current["rsi"] < MAX_RSI:
                print("Bearish EMA crossunder")
                action = SIDE_SELL
            elif self.close_price < self.current["medium_ema"] and ENABLE_CLOSE_POSITION:
                action = CLOSE_LONG
            elif self.close_price > self.current["medium_ema"] and ENABLE_CLOSE_POSITION:
                action = CLOSE_SHORT

        return action

    def apply(self):
        self.df = get_atr(self.df)
        self._update_current_prev_values()

        lc = BULLISH if self.current["close"] > self.current["open"] else BEARISH
        action = self._get_trading_action()
        if action == SIDE_BUY or action == SIDE_SELL:
            p, tp, sl = get_stop_limits(
                self.df, self.close_price, self.current["atr"], action)
        else:
            p = self.close_price
            tp = get_swing_high_sl(self.df)
            sl = get_swing_low_sl(self.df)
        return action, p, tp, sl, lc

    def check_stoch_rsi_cross(self):
        self.df = get_stoch_rsi(self.df)
        self._update_current_prev_values()
        side = ""
        message = ""
        if crossover(self.df, "rsi_k", "rsi_d"):
            side = SIDE_BUY
            message = "Stoch RSI Crossover"
        if crossunder(self.df, "rsi_k", "rsi_d"):
            side = SIDE_SELL
            message = "Stoch RSI Crossunder"
        return side, message

    def check_stoch_rsi_extreme(self):
        self.df = get_stoch_rsi(self.df)
        self._update_current_prev_values()
        side = ""
        message = ""
        if stoch_rsi_oversold(self.df):
            side = SIDE_BUY
            message = "Stoch RSI Oversold"
        if stoch_rsi_overbought(self.df):
            side = SIDE_SELL
            message = "Stoch RSI Overbought"
        return side, message

    def check_engulfing_pattern(self):
        self.df = get_ema(self.df)
        self._update_current_prev_values()
        ema = self.current["medium_ema"]
        side = ""
        message = ""
        if self.current["close"] > ema and red_candle(self.df.iloc[-2]) and bullish_engulfing(self.df):
            side = SIDE_BUY
            message = "Bullish Engulfing Candle"
        if self.current["close"] < ema and green_candle(self.df.iloc[-2]) and bearish_engulfing(self.df):
            side = SIDE_SELL
            message = "Bearish Engulfing Candle"
        return side, message

    def check_three_line_strike(self):
        side = ""
        message = ""
        if bullish_3L_strike(self.df):
            side = SIDE_BUY
            message = "Bullish 3L Strike"
        if bearish_3L_strike(self.df):
            side = SIDE_SELL
            message = "Bearish 3L Strike"
        return side, message

    def check_macd_cross(self):
        self.df = get_macd(self.df)
        self._update_current_prev_values()
        side = ""
        message = ""
        if crossover(self.df, "macd_line", "signal_line"):
            side = SIDE_BUY
            message = "MACD Crossover"
        if crossunder(self.df, "macd_line", "signal_line"):
            side = SIDE_SELL
            message = "MACD Crossunder"
        return side, message

    def check_ema_cross(self):
        self.df = get_ema(self.df)
        self._update_current_prev_values()
        side = ""
        message = ""
        if crossover(self.df, "fast_ema", "medium_ema"):
            side = SIDE_BUY
            message = f"EMA Crossover {FAST_EMA_PERIOD} > {MEDIUM_EMA_PERIOD}"
        if crossunder(self.df, "fast_ema", "medium_ema"):
            side = SIDE_SELL
            message = f"EMA Crossunder {FAST_EMA_PERIOD} > {MEDIUM_EMA_PERIOD}"
        if crossover(self.df, "fast_ema", "slow_ema"):
            side = SIDE_BUY
            message = f"EMA Crossover {FAST_EMA_PERIOD} > {SLOW_EMA_PERIOD}"
        if crossunder(self.df, "fast_ema", "slow_ema"):
            side = SIDE_SELL
            message = f"EMA Crossunder {FAST_EMA_PERIOD} > {SLOW_EMA_PERIOD}"
        return side, message
