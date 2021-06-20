from chatbot import send_message
from constants import *


params = {}
params["closePosition"] = True
params["priceProtect"] = True
params["positionSide"] = BOTH
params["workingType"] = MARK_PRICE
params["timeInForce"] = GTE_GTC


def rounded(num):
    return round(num * 10000)/10000


def get_balance(exchange):
    balance = exchange.fetch_total_balance()
    return rounded(balance[CURRENCY])


def notify_order_details(side, balance, amount, p, tp, sl):
    order_type = 'Bought (LONG)' if side == SIDE_BUY else 'Sold (SHORT)'
    message = f"Balance: {CURRENCY} {balance}\n\n{SYMBOL} {order_type}\nAmount: {amount}\nPrice: {p}\nTake Profit: {tp}\nStop Loss: {sl}"
    print(message)
    send_message(message)


def set_stop_limits(exchange, amount, side, tp, sl):
    params["stopPrice"] = tp
    exchange.create_order(SYMBOL, TAKE_PROFIT_MARKET,
                          side, amount, params=params)
    params["stopPrice"] = sl
    exchange.create_order(SYMBOL, STOP_MARKET, side, amount, params=params)


def buy(exchange, posAmt, p, tp, sl):
    try:
        if posAmt < 0:
            print("Cancelling current SHORT position.")
            exchange.create_market_buy_order(SYMBOL, abs(posAmt))

        balance = get_balance(exchange)
        amount = round(balance * MARGIN / p)

        exchange.cancel_all_orders(SYMBOL)
        exchange.create_market_buy_order(SYMBOL, amount)
        set_stop_limits(exchange, amount, SIDE_SELL, tp, sl)
        notify_order_details(SIDE_BUY, balance, amount, p, tp, sl)
    except Exception as e:
        print(e, "\n")
        send_message(f"Unable to place order.\n{e}")


def sell(exchange, posAmt, p, tp, sl):
    try:
        if posAmt > 0:
            print("Cancelling current LONG position.")
            exchange.create_market_sell_order(SYMBOL, posAmt)

        balance = get_balance(exchange)
        amount = round(balance * MARGIN / p)

        exchange.cancel_all_orders(SYMBOL)
        exchange.create_market_sell_order(SYMBOL, amount)
        set_stop_limits(exchange, amount, SIDE_BUY, tp, sl)
        notify_order_details(SIDE_SELL, balance, amount, p, tp, sl)
    except Exception as e:
        print(e, "\n")
        send_message(f"Unable to place order.\n{e}")


def trade(exchange, side, p, tp, sl):
    pos = exchange.fetch_positions(SYMBOL)
    posAmt = float(pos[0]["info"]["positionAmt"])

    if side == SIDE_BUY:
        if posAmt > 0:
            try:
                print("Already in a LONG position.")
                if ENABLE_TRAILING_STOP_LOSS:
                    exchange.cancel_all_orders(SYMBOL)
                    set_stop_limits(exchange, posAmt, SIDE_SELL, tp, sl)
                    print(
                        f"{SYMBOL} Updated Stop Limits (LONG)\nTake Profit: {tp}\nStop Loss: {sl}")
            except Exception as e:
                print(e, "\n")
                send_message(f"Unable to update stop limits.\n{e}")
        else:
            buy(exchange, posAmt, p, tp, sl)

    if side == SIDE_SELL:
        if posAmt < 0:
            try:
                print("Already in a SHORT position.")
                if ENABLE_TRAILING_STOP_LOSS:
                    exchange.cancel_all_orders(SYMBOL)
                    set_stop_limits(exchange, abs(posAmt), SIDE_BUY, tp, sl)
                    print(
                        f"{SYMBOL} Updated Stop Limits (SHORT)\nTake Profit: {tp}\nStop Loss: {sl}")
            except Exception as e:
                print(e, "\n")
                send_message(f"Unable to update stop limits.\n{e}")
        else:
            sell(exchange, posAmt, p, tp, sl)
