import backtrader as bt
import datetime
import src.pre_processing as pp


class BBPBStrategy(bt.Strategy):

    def __init__(self):
        self.bbpb = bt.indicators.BollingerBandsPct().pctb
        self.datalow = self.datas[0].low
        self.datahigh = self.datas[0].high


    def next(self):

        if self.datahigh[0] < self.datahigh[-1] and self.datalow[0] > self.datalow[-1]:
            if self.bbpb[0] < 0.3 and not self.position:
                self.buy(size=10000)

            if self.bbpb[0] > 0.7 and self.position:
                self.close()


cerebro = bt.Cerebro()

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

fromdate = datetime.datetime.strptime('2020-01-01', '%Y-%m-%d')
todate = datetime.datetime.strptime('2021-09-30', '%Y-%m-%d')

data = bt.feeds.GenericCSVData(dataname = 'data/202109_1DayALGO.csv', dtformat=2, compression=15, timeframe=bt.TimeFrame.Minutes, fromdate=fromdate, todate=todate)

cerebro.adddata(data)

cerebro.addstrategy(BBPBStrategy)

cerebro.run()

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.plot()