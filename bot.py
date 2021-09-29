import websocket, json, pprint, talib, numpy
import pandas
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.us:9443/ws/algousd@kline_1m"

BBPB_PERIOD = 2
BBPB_OVERBOUGHT = .70
BBPB_OVERSOLD = .30
TRADE_SYMBOL = 'ALGOUSD'
TRADE_QUANTITY = 25

closes = []
lows = []
highs = []
in_position = False


def apikey():
    print("Enter your API_KEY from Binance")
    API_KEY = input()
    return API_KEY

def apisecret():
    print("Enter your API_SECRET from Binance")
    API_SECRET = input()
    return API_SECRET

client = Client(apikey(), apisecret(), tld='us')


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
    global closes, in_position, lows, highs

    print('received message')
    json_message = json.loads(message)
    candle = json_message['k']
    is_candle_closed = candle['x']

    low = candle['l']
    high = candle['h']
    close = candle['c']

    if is_candle_closed:
        ### Enable these if you want all candle data in console, otherwise they clog up the interface
        # pprint.pprint(json_message)
        pprint.pprint("candle closed at {}".format(close))
        closes.append(float(close))
        lows.append(float(low))
        highs.append(float(high))
        np_closes = numpy.array(closes)
        np_lows = numpy.array(lows)
        np_highs = numpy.array(highs)
        ### Enable these if you want historical data in console, otherwise they clog up the interface
        # print("Closes")
        # pprint.pprint(np_closes)
        # print("Lows")
        # pprint.pprint(np_lows)
        # print("Highs")
        # pprint.pprint(np_highs)


        if len(closes) > BBPB_PERIOD:


            upperband, middleband, lowerband = talib.BBANDS(np_closes, timeperiod=2, nbdevup=2, nbdevdn=2, matype=0)

            dfupper = pandas.DataFrame(upperband)
            dfupper = dfupper.iloc[2:, :]
            dflower = pandas.DataFrame(lowerband)
            dflower = dflower.iloc[2:, :]
            dfclose = pandas.DataFrame(np_closes)
            dfclose = dfclose.iloc[2:, :]


            BBPB = (dfclose - dflower) / (dfupper - dflower)
            ### Enable this if you want historical data in console, otherwise they clog up the interface
            # pprint.pprint("all BBPB calculated so far")
            # pprint.pprint(BBPB)

            last_low = np_lows[-1]
            previous_low = np_lows[-2]
            last_high = np_highs[-1]
            previous_high = np_highs[-2]
            last_BBPB_list = BBPB.iloc[-1].tolist()
            last_BBPB = last_BBPB_list[0]

            if last_high < previous_high and last_low > previous_low:

                pprint.pprint("Inside Candle Detected")

                if last_BBPB < BBPB_OVERSOLD:
                    if in_position:
                        pprint.pprint("It is oversold, but you already own it, nothing to do.")
                    else:
                        pprint.pprint("Oversold! Buy! Buy! Buy!")
                        # put binance buy order logic here
                        order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                        if order_succeeded:
                            in_position = True
                else:
                    pprint.pprint("It is neither Oversold or Overbought, we do nothing.")

            if last_BBPB > BBPB_OVERBOUGHT:
                if in_position:
                    pprint.pprint("Overbought! Sell! Sell! Sell!")
                    # put binance sell logic here
                    order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False
                else:
                    pprint.pprint("It is overbought, but we don't own any. Nothing to do.")

            else:
                pprint.pprint("Inside Candle Not-Detected Nor Oversold - Waiting")
    if is_candle_closed == False:
        print("Candle Not Closed Yet")



ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
