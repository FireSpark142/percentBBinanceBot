import csv
from binance.client import Client
from data.config import *
import src.pre_processing as pp


client = Client(API_KEY, API_SECRET, tld='us')

csvfile = open(pp.DATA_FOLDER_LOCATION + '202109_1DayBTC.csv', 'w', newline='')
candlestick_writer = csv.writer(csvfile, delimiter=',')
candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1DAY, "1 Jan, 2020")

for candlestick in candlesticks:
    candlestick[0] = candlestick[0] / 1000
    candlestick_writer.writerow(candlestick)

csvfile.close()
