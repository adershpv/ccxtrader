from chatbot import send_message
from constants import *


params = {}
params["closePosition"] = True
params["priceProtect"] = True
params["positionSide"] = BOTH
params["workingType"] = MARK_PRICE
params["timeInForce"] = GTE_GTC


def notify_balance(exchange):
    balance = exchange.fetch_total_balance()
    message = "Account Balance:"
    for k, v in balance.items():
        message += f"\n{k} : {v}"
    send_message(message)


def set_stop_limits(exchange, side, tp, sl):
    params["stopPrice"] = tp
    exchange.create_order(SYMBOL, TAKE_PROFIT_MARKET,
                          side, AMOUNT, params=params)
    params["stopPrice"] = sl
    exchange.create_order(SYMBOL, STOP_MARKET, side, AMOUNT, params=params)


def buy(exchange, posAmt, p, tp, sl):
    try:
        notify_balance(exchange)
        if posAmt < 0:
            print("Cancelling current SHORT position.")
            exchange.create_market_buy_order(SYMBOL, AMOUNT)
        exchange.cancel_all_orders(SYMBOL)
        exchange.create_market_buy_order(SYMBOL, AMOUNT)
        set_stop_limits(exchange, SIDE_SELL, tp, sl)
        print(
            f"{SYMBOL} Bought (LONG)\nAmount: {AMOUNT}\nPrice: {p}\nTake Profit: {tp}\nStop Loss: {sl}")
        send_message(
            f"{SYMBOL} Bought (LONG)\nAmount: {AMOUNT}\nPrice: {p}\nTake Profit: {tp}\nStop Loss: {sl}")
    except Exception as e:
        print(e, "\n")
        send_message(f"Unable to place order.\n{e}")


def sell(exchange, posAmt, p, tp, sl):
    try:
        notify_balance(exchange)
        if posAmt > 0:
            print("Cancelling current LONG position.")
            exchange.create_market_sell_order(SYMBOL, AMOUNT)
        exchange.cancel_all_orders(SYMBOL)
        exchange.create_market_sell_order(SYMBOL, AMOUNT)
        set_stop_limits(exchange, SIDE_BUY, tp, sl)
        print(
            f"{SYMBOL} Sold (SHORT)\nAmount: {AMOUNT}\nPrice: {p}\nTake Profit: {tp}\nStop Loss: {sl}")
        send_message(
            f"{SYMBOL} Sold (SHORT)\nAmount: {AMOUNT}\nPrice: {p}\nTake Profit: {tp}\nStop Loss: {sl}")
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
                if ENABLE_TRILING_STOP_LOSS:
                    exchange.cancel_all_orders(SYMBOL)
                    set_stop_limits(exchange, SIDE_SELL, tp, sl)
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
                if ENABLE_TRILING_STOP_LOSS:
                    exchange.cancel_all_orders(SYMBOL)
                    set_stop_limits(exchange, SIDE_BUY, tp, sl)
                    print(
                        f"{SYMBOL} Updated Stop Limits (SHORT)\nTake Profit: {tp}\nStop Loss: {sl}")
            except Exception as e:
                print(e, "\n")
                send_message(f"Unable to update stop limits.\n{e}")
        else:
            sell(exchange, posAmt, p, tp, sl)
