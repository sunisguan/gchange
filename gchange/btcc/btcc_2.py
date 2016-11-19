# -*- coding: utf-8 -*-
from gchange.btcc.livefeed import LiveTradeFeed
from gchange.btcc.broker import BacktestingBroker
from gchange.btcc import livebroker
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
import threading

class Strategy(strategy.BaseStrategy):

    """
    双均线策略
    """

    def __init__(self, feed, brk, n, m):
        strategy.BaseStrategy.__init__(self, feed, brk)
        self.__instrument = 'btc'

        self.__bid = None
        self.__ask = None
        self.__posSize = 0.001

        self.__position = None
        self.__prices = feed[self.__instrument].getPriceDataSeries()
        self.__malength1 = int(n)
        self.__malength2 = int(m)

        self.__ma1 = ma.SMA(self.__prices, self.__malength1)
        self.__ma2 = ma.SMA(self.__prices, self.__malength2)

        # Subscribe to order book update events to get bid/ask prices to trade.
        feed.get_marketdepth_update_event().subscribe(self.__onMarketdepth_update)

    def __onMarketdepth_update(self, marketdepth):
        bid = marketdepth.get_top_bid()
        ask = marketdepth.get_top_ask()

        if bid != self.__bid or ask != self.__ask:
            self.__bid = bid.get_price()
            self.__ask = ask.get_price()
            #self.info("Order book updated. Best bid: %s. Best ask: %s" % (self.__bid, self.__ask))

    def onEnterOk(self, position):
        self.info("Position opened at %s" % (position.getEntryOrder().getExecutionInfo().getPrice()))

    def onEnterCanceled(self, position):
        self.info("Position entry canceled")
        self.__position = None

    def onExitOk(self, position):
        self.__position = None
        self.info("Position closed at %s" % (position.getExitOrder().getExecutionInfo().getPrice()))

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.info('on exit canceled')
        #self.__position.exitLimit(self.__bid)

    def onFinish(self, bars):
        print 'finish'

    def enterSignal(self):
        return self.__position is None and cross.cross_above(self.__ma1, self.__ma2) > 0

    def exitSignal(self):
        ret = self.__position is not None and not self.__position.exitActive() and cross.cross_below(self.__ma1, self.__ma2) > 0
        return ret

    def onBars(self, bars):
        bar = bars[self.__instrument]
        #self.info("Price: %s. Volume: %s." % (bar.getClose(), bar.getVolume()))

        # Wait until we get the current bid/ask prices.
        if self.__ask is None or self.__ma2[-1] is None:
            return

        if self.exitSignal():
            self.info("Exit signal. Sell at %s" % (self.__bid))
            self.__position.exitLimit(self.__bid)
        elif self.enterSignal():
            self.info("Entry signal. Buy at %s" % (self.__ask))
            self.__position = self.enterLongLimit(self.__instrument, self.__ask, self.__posSize, True)



import time

DURATION = 60*60
paras = [10, 30]

class _ToStopThread(threading.Thread):
    def __init__(self, feed):
        super(_ToStopThread, self).__init__()
        self.__feed = feed
        self.__count = 1

    def start(self):
        super(_ToStopThread, self).start()

    def run(self):
        super(_ToStopThread, self).run()

        while self.__count < DURATION + 10:
            time.sleep(1)
            self.__count += 1
        print 'stop feed'
        self.__feed.stop()

    def stop(self):
        pass

def __do_live():
    bar_feed = LiveTradeFeed(duration=DURATION)
    brk = livebroker.LiveBroker()
    strat = Strategy(bar_feed, brk, *paras)

    _thread = _ToStopThread(bar_feed)
    _thread.start()

    strat.run()
    print '-------'

def  __do_backtesting():
    bar_feed = LiveTradeFeed(duration=DURATION)
    brk = BacktestingBroker(1000, bar_feed)
    strat = Strategy(bar_feed, brk)
    plot = True

    ############################################# don't change ############################
    from pyalgotrade.stratanalyzer import returns
    from pyalgotrade.stratanalyzer import sharpe
    from pyalgotrade.stratanalyzer import drawdown
    from pyalgotrade.stratanalyzer import trades
    from pyalgotrade import plotter


    retAnalyzer = returns.Returns()
    strat.attachAnalyzer(retAnalyzer)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    strat.attachAnalyzer(sharpeRatioAnalyzer)
    drawDownAnalyzer = drawdown.DrawDown()
    strat.attachAnalyzer(drawDownAnalyzer)
    tradesAnalyzer = trades.Trades()
    strat.attachAnalyzer(tradesAnalyzer)

    if plot:
        plt = plotter.StrategyPlotter(strat, True, True, True)

    _thread = _ToStopThread(bar_feed)
    _thread.start()

    strat.run()
    print '-------'
    if plot:
        plt.plot()

        # 夏普率
        sharp = sharpeRatioAnalyzer.getSharpeRatio(0.05)
        # 最大回撤
        maxdd = drawDownAnalyzer.getMaxDrawDown()
        # 收益率
        return_ = retAnalyzer.getCumulativeReturns()[-1]
        # 收益曲线
        return_list = []
        for item in retAnalyzer.getCumulativeReturns():
            return_list.append(item)


def main():
    __do_live()
    #__do_backtesting()

if __name__ == "__main__":
    main()
