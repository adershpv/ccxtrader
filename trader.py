from chatbot import send_message
from constants import *


params = {}
params["closePosition"] = True
params["priceProtect"] = True
params["positionSide"] = BOTH
params["workingType"] = MARK_PRICE
params["timeInForce"] = GTE_GTC


def rounded(num, decimal_places=PRICE_DECIMAL_PLACES):
    return round(num, decimal_places)


def get_balance(exchange):
    balance = exchange.fetch_total_balance()
    return rounded(balance[CURRENCY])


def get_amount(balance, p):
    amount = rounded(balance * MARGIN / p, AMOUNT_DECIMAL_PLACES)
    if amount > MAX_AMOUNT:
        return MAX_AMOUNT
    return amount


def notify_order_details(side, balance, amount, p, tp, sl):
    order_type = 'Bought (LONG)' if side == SIDE_BUY else 'Sold (SHORT)'
    message = f"Balance: {CURRENCY} {balance}\n\n{SYMBOL} {order_type}\nAmount: {amount}\nPrice: {p}"
    if ENABLE_TAKE_PROFIT:
        message += f"\nTake Profit: {tp}"
    if ENABLE_STOP_LOSS:
        message += f"\nStop Loss: {sl}"
    print(message)
    send_message(message)


def set_stop_limits(exchange, amount, side, tp, sl):
    if ENABLE_TAKE_PROFIT and tp:
        params["stopPrice"] = tp
        exchange.create_order(SYMBOL, TAKE_PROFIT_MARKET,
                              side, amount, params=params)
    if ENABLE_STOP_LOSS and sl:
        params["stopPrice"] = sl
        exchange.create_order(SYMBOL, STOP_MARKET, side, amount, params=params)


def buy(exchange, posAmt, p, tp, sl):
    try:
        close(exchange, posAmt)

        balance = get_balance(exchange)
        amount = get_amount(balance, p)

        exchange.cancel_all_orders(SYMBOL)
        exchange.create_market_buy_order(SYMBOL, amount)
        set_stop_limits(exchange, amount, SIDE_SELL, tp, sl)
        notify_order_details(SIDE_BUY, balance, amount, p, tp, sl)
    except Exception as e:
        print(e, "\n")
        send_message(f"Unable to place order.\n{e}")


def sell(exchange, posAmt, p, tp, sl):
    try:
        close(exchange, posAmt)

        balance = get_balance(exchange)
        amount = get_amount(balance, p)

        exchange.cancel_all_orders(SYMBOL)
        exchange.create_market_sell_order(SYMBOL, amount)
        set_stop_limits(exchange, amount, SIDE_BUY, tp, sl)
        notify_order_details(SIDE_SELL, balance, amount, p, tp, sl)
    except Exception as e:
        print(e, "\n")
        send_message(f"Unable to place order.\n{e}")


def close(exchange, posAmt):
    if posAmt > 0:
        print("Cancelling current LONG position.")
        exchange.create_market_sell_order(SYMBOL, posAmt)
    elif posAmt < 0:
        print("Cancelling current SHORT position.")
        exchange.create_market_buy_order(SYMBOL, abs(posAmt))


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
                close(exchange, posAmt)
        else:
            buy(exchange, posAmt, p, tp, sl)

    elif side == SIDE_SELL:
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
                close(exchange, posAmt)
        else:
            sell(exchange, posAmt, p, tp, sl)

    elif (posAmt > 0 and side == CLOSE_LONG) or (posAmt < 0 and side == CLOSE_SHORT):
        try:
            close(exchange, posAmt)
            balance = get_balance(exchange)
            message = f"{CLOSE_MESSAGE[side]}\nBalance: {CURRENCY} {balance}"
            print(message)
            send_message(message)
        except Exception as e:
            print(e, "\n")
            send_message(f"Unable to close current position.\n{e}")

    elif posAmt != 0 and side == HOLD and ENABLE_TRAILING_STOP_LOSS:
        try:
            exchange.cancel_all_orders(SYMBOL)
            if posAmt > 0:
                set_stop_limits(exchange, posAmt, SIDE_SELL, "", sl)
            else:
                # In this case "tp" is actually stop loss
                set_stop_limits(exchange, abs(posAmt), SIDE_BUY, "", tp)
            print(
                f"{SYMBOL} Updated Stop Limits (SHORT)\nTake Profit: {tp}\nStop Loss: {sl}")
        except Exception as e:
            print(e, "\n")
            send_message(f"Unable to update stop limits.\n{e}")
            close(exchange, posAmt)
