SYMBOL = 'MATIC/USDT'
CURRENCY = 'USDT'
TIME_FRAME = '5m'
HIGHER_TIME_FRAME = '15m'
CANDLESTICK_LIMIT = 500

MARGIN = 15
MAX_AMOUNT = 1000

CALCULATION_DECIMAL_PLACES = 4
PRICE_DECIMAL_PLACES = 4
AMOUNT_DECIMAL_PLACES = 0

CURRENT_DF_INDEX = CANDLESTICK_LIMIT - 2
LAST_N_ROWS = 8

MARKET = 'MARKET'
MARK_PRICE = 'MARK_PRICE'
TAKE_PROFIT_MARKET = 'TAKE_PROFIT_MARKET'
STOP_MARKET = 'STOP_MARKET'
MARK_PRICE = 'MARK_PRICE'
SIDE_BUY = 'BUY'
SIDE_SELL = 'SELL'
BOTH = 'BOTH'
GTE_GTC = 'GTE_GTC'

CLOSE_LONG = 'CLOSE_LONG'
CLOSE_SHORT = 'CLOSE_SHORT'

HOLD = 'HODL'
COLUMNS = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

FAST_EMA_PERIOD = 20
MEDIUM_EMA_PERIOD = 50
SLOW_EMA_PERIOD = 200

MAX_RSI = 50  # SHORT
MIN_RSI = 40  # LONG

MAX_STOCH_RSI = 75  # SHORT
MIN_STOCH_RSI = 20  # LONG

MAX_STOCH_RSI_CLOSE = 75  # CLOSE_LONG
MIN_STOCH_RSI_CLOSE = 10  # CLOSE_SHORT

TREND_SMA_PERIOD = 200
ENABLE_TRAILING_STOP_LOSS = False

ENABLE_STOP_LIMITS = True
ENABLE_TAKE_PROFIT = True
ENABLE_STOP_LOSS = True
MAX_TAKE_PROFIT_MARGIN = 2.5
MAX_STOP_LOSS_MARGIN = 1.5

SEVEN_BAR_STRATEGY = "SEVEN_BAR_STRATEGY"
STOCH_RSI_STRATEGY = "STOCH_RSI_STRATEGY"
MULTI_TIME_FRAME_STRATEGY = "MULTI_TIME_FRAME_STRATEGY"
STRATEGY = MULTI_TIME_FRAME_STRATEGY

CLOSE_MESSAGE = {
    CLOSE_LONG: 'Closed Long Position',
    CLOSE_SHORT: 'Closed Short Position'
}

UPDATE_STOP_LOSS = 'UPDATE_STOP_LOSS'
NOTIFY_MESSAGE = 'NOTIFY_MESSAGE'
TRADE = 'TRADE'
