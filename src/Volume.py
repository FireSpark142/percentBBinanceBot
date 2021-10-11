import asyncio
import dask.dataframe as dd
import numpy as np
from binance.client import Client
from config import API_KEY, API_SECRET
import datetime
from aiostream import stream
from binance import AsyncClient

startTime = datetime.datetime.now()
print(datetime.datetime.now() - startTime)

async def main():
    client = await AsyncClient.create(API_KEY, API_SECRET, tld='com')

    res = await client.get_exchange_info()
    symbols = res['symbols']

    ls = []
    async for s in stream.iterate(symbols):
        if 'USDT' in s['symbol']:
            if 'BUSD' not in s['symbol']:
                ls.append(s['symbol'])

    async def test(i):
        info = await client.get_klines(symbol=i, interval=Client.KLINE_INTERVAL_1DAY, limit=1)
        full = [i, info]
        return full

    xz = stream.iterate(ls)
    comblist = []

    xs = stream.map(xz, test, ordered=True, task_limit=10000)
    async for result in xs:
        x = result[0]
        y = result[1][0]
        y = list(y)
        y.append(x)
        volume = y[5]
        total_trades = y[8]
        ticker = y[12]
        finalls = [ticker,total_trades,volume]
        comblist.append(finalls)

    npa = np.array(comblist)
    df = dd.from_array(npa, columns=["Pair", "Total Trades", "Volume"])
    print(dd.compute(df))
    dd.to_csv(df, 'Volume-*.csv')
    await client.close_connection()


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print(datetime.datetime.now() - startTime)
