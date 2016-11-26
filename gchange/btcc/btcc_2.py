# -*- coding: utf-8 -*-
from gchange.btcc.livefeed import LiveTradeFeed
from gchange.btcc.broker import BacktestingBroker
from gchange.btcc import livebroker
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
import _do_strategy as ds
from btcc_exchange import BtccExchange, BtccWebsocketClient

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

        self.setUseEventDateTimeInLogs(True)

    def __onMarketdepth_update(self, marketdepth):
        bid = marketdepth.get_top_bid()
        ask = marketdepth.get_top_ask()

        if bid != self.__bid or ask != self.__ask:
            self.__bid = bid.get_price()
            self.__ask = ask.get_price()
            self.info("Order book updated. Best bid: %s. Best ask: %s" % (self.__bid, self.__ask))

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

    def onOrderUpdated(self, order):
        super(Strategy, self).onOrderUpdated(order)


"""
========================================
"""


class DoubleSMA(ds.StarategyRun):
    def __init__(self):
        super(DoubleSMA, self).__init__()

    def config_live(self):
        exchange = BtccExchange(duration=ds.CONFIG['DURATION'])
        bar_feed = LiveTradeFeed(exchange)
        brk = livebroker.LiveBroker()
        return Strategy(bar_feed, brk, *ds.CONFIG['SMA_PARAS'])

    def config_backtesting(self):
        exchange = BtccExchange(duration=ds.CONFIG['DURATION'])
        bar_feed = LiveTradeFeed(exchange)
        brk = BacktestingBroker(ds.CONFIG['START_CAPTIAL'], bar_feed)
        return Strategy(bar_feed, brk, *ds.CONFIG['SMA_PARAS'])


def main():
    DoubleSMA().run()

if __name__ == "__main__":
    main()
