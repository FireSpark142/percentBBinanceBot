import pandas as pd
import pprint, talib
from binance import ThreadedWebsocketManager
from binance.client import Client
from binance.enums import *
from src.config import API_KEY, API_SECRET
import dask.array as da

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

def main():

    twm = ThreadedWebsocketManager(api_key=API_KEY, api_secret=API_SECRET,tld='com')
    twm.start()

    client = Client(api_key=API_KEY, api_secret=API_SECRET,tld='com')


    def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
        try:
            print("sending order")
            order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
            print(order)
        except Exception as e:
            print("an exception occured - {}".format(e))
            return False

        return True

    def on_message(message):
        global closes, in_position, lows, highs, last_high, previous_high, last_low, previous_low, opens, volumes, trades_qty, l_of_l, symbols, df
        candle = message['k']
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
            dda = da.from_array([symbols, closes, lows, highs, opens, volumes, trades_qty])
            ddacloses = dda[1].astype('float64').compute()
            if len(closes) > BBPB_PERIOD:

                upperband, middleband, lowerband = talib.BBANDS(ddacloses, timeperiod=20, nbdevup=2, nbdevdn=2,
                                                                    matype=0)

                dda_upper = da.from_array(upperband)
                dda_upper = dda_upper[19:].astype('float64').compute()
                dda_lower = da.from_array(lowerband)
                dda_lower = dda_lower[19:].astype('float64').compute()
                ddacloses = ddacloses[19:]

                if (dda_upper[-1] - dda_lower[-1]) != 0:
                    BBPB = (ddacloses[-1] - dda_lower[-1]) / (dda_upper[-1] - dda_lower[-1])

                else:
                    BBPB = (ddacloses[-1] - dda_lower[-1]) / (dda_upper[-1] - (dda_lower[-1] + 0.0000001))

                print("candle PercentB at {}".format(BBPB))

                last_low = dda[2][-1]
                previous_low = dda[2][-2]
                last_high = dda[3][-1]
                previous_high = dda[3][-2]
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

    twm.start_kline_socket(callback=on_message, symbol=TRADE_SYMBOL, interval=KLINE_INTERVAL_30MINUTE)
    twm.join()


if __name__ == "__main__":
   main()