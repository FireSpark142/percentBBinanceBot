import pandas as pd
import websocket, json, pprint, talib, numpy
from binance.client import Client
from binance.enums import *
from src.config import API_KEY, API_SECRET

SOCKET = "wss://stream.binance.us:9443/ws/algousdt@kline_1m"

BBPB_PERIOD = 20
BBPB_OVERBOUGHT = .70
BBPB_OVERSOLD = .30
TRADE_SYMBOL = 'ALGOUSDT'
TRADE_QUANTITY = 25

closes = []
lows = []
highs = []
opens = []
volumes = []
trades_qty = []
l_of_l = []
symbols = []
df = pd.DataFrame()

in_position = False

client = Client(API_KEY, API_SECRET, tld='com')


def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True


def on_open(ws):
    print('opened connection')


def on_close(ws):
    print('closed connection')


def on_message(ws, message):
    global closes, in_position, lows, highs, last_high, previous_high, last_low, previous_low, opens, volumes, trades_qty, l_of_l, symbols, df
    json_message = json.loads(message)
    candle = json_message['k']
    ticker = candle['s']
    is_candle_closed = candle['x']
    open = candle['o']
    volume = candle['v']
    num_of_trades = candle['n']
    low = candle['l']
    high = candle['h']
    close = candle['c']

    if is_candle_closed:
        pprint.pprint("candle closed at {}".format(close))
        closes.append(float(close))
        lows.append(float(low))
        highs.append(float(high))
        opens.append((float(open)))
        volumes.append((float(volume)))
        trades_qty.append((float(num_of_trades)))
        symbols.append(ticker)
        l_of_l = [symbols, closes, lows, highs, opens, volumes, trades_qty]
        df = pd.DataFrame(l_of_l).T
        df.columns = ['Ticker', 'Close', 'Low', 'High', 'Open', 'Volume', "Qty of Trades"]
        df.to_csv(index=False)
        np_closes = numpy.array(closes)
        np_lows = numpy.array(lows)
        np_highs = numpy.array(highs)


        if len(closes) > BBPB_PERIOD:


            upperband, middleband, lowerband = talib.BBANDS(np_closes, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

            np_upper = numpy.array(upperband)
            np_upper = np_upper[19:]
            np_lower = numpy.array(lowerband)
            np_lower = np_lower[19:]
            np_closes = np_closes[19:]

            if (np_upper[-1] - np_lower[-1]) != 0:
                BBPB = (np_closes[-1] - np_lower[-1]) / (np_upper[-1] - np_lower[-1])

            else:
                BBPB = (np_closes[-1] - np_lower[-1]) / (np_upper[-1] - (np_lower[-1] + 0.0000001))





            print("candle PercentB at {}".format(BBPB))

            last_low = np_lows[-1]
            previous_low = np_lows[-2]
            last_high = np_highs[-1]
            previous_high = np_highs[-2]
            if last_high < previous_high and last_low > previous_low:

                print("Inside Candle Detected")

                if BBPB < BBPB_OVERSOLD:
                    if in_position:
                        print("It is oversold, but you already own it, nothing to do.")
                    else:
                        print("Oversold! Buy! Buy! Buy!")
                        # put binance buy order logic here
                        order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                        if order_succeeded:
                            in_position = True
                if BBPB >= BBPB_OVERSOLD:
                    print("It is neither Oversold or Overbought, we do nothing.")

                if BBPB > BBPB_OVERBOUGHT:
                    if in_position:
                        print("Overbought! Sell! Sell! Sell!")
                        # put binance sell logic here
                        order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                        if order_succeeded:
                            in_position = False
                    else:
                        print("It is overbought, but we don't own any. Nothing to do.")

        if (last_high < previous_high and last_low > previous_low) == False:
            print("Inside Candle Not-Detected Nor Oversold - Waiting")


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
