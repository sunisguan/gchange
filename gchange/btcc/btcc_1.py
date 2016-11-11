# -*- coding: utf-8 -*-
from gchange.btcc.livefeed import LiveTradeFeed
from gchange.btcc.broker import BacktestingBroker
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross


class Strategy(strategy.BaseStrategy):
    def __init__(self, feed, brk):
        strategy.BaseStrategy.__init__(self, feed, brk)
        smaPeriod = 20
        self.__instrument = "btc"
        self.__prices = feed[self.__instrument].getCloseDataSeries()
        self.__sma = ma.SMA(self.__prices, smaPeriod)
        self.__bid = None
        self.__ask = None
        self.__position = None
        self.__posSize = 0.05

        # Subscribe to order book update events to get bid/ask prices to trade.
        #feed.getOrderBookUpdateEvent().subscribe(self.__onOrderBookUpdate)
        feed.get_marketdepth_update_event().subscribe(self.__onMarketdepth_update)

    def __onMarketdepth_update(self, marketdepth):
        bid = marketdepth.get_top_bid()
        ask = marketdepth.get_top_ask()

        if bid != self.__bid or ask != self.__ask:
            self.__bid = bid.get_price()
            self.__ask = ask.get_price()
            self.info("Order book updated. Best bid: %s. Best ask: %s" % (self.__bid, self.__ask))

    """
    def __onOrderBookUpdate(self, orderBookUpdate):
        bid = orderBookUpdate.getBidPrices()[0]
        ask = orderBookUpdate.getAskPrices()[0]

        if bid != self.__bid or ask != self.__ask:
            self.__bid = bid
            self.__ask = ask
            self.info("Order book updated. Best bid: %s. Best ask: %s" % (self.__bid, self.__ask))

    """

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
        self.__position.exitLimit(self.__bid)

    def onFinish(self, bars):
        print 'finish'

    def onBars(self, bars):
        bar = bars[self.__instrument]
        #self.info("Price: %s. Volume: %s." % (bar.getClose(), bar.getVolume()))

        # Wait until we get the current bid/ask prices.
        if self.__ask is None:
            return

        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if cross.cross_above(self.__prices, self.__sma) > 0:
                self.info("Entry signal. Buy at %s" % (self.__ask))
                self.__position = self.enterLongLimit(self.__instrument, self.__ask, self.__posSize, True)
        # Check if we have to close the position.
        elif not self.__position.exitActive() and cross.cross_below(self.__prices, self.__sma) > 0:
            self.info("Exit signal. Sell at %s" % (self.__bid))
            self.__position.exitLimit(self.__bid)


def main():
    bar_feed = LiveTradeFeed()
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

if __name__ == "__main__":
    main()
