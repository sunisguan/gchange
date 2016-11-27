# -*- coding: utf-8 -*-
from gchange.btcc.livefeed import LiveTradeFeed
from gchange.btcc.broker import BacktestingBroker
from gchange.btcc import livebroker
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
import common
from btcc_exchange import BtccExchange, BtccWebsocketClient
import _do_strategy as ds


class Strategy(strategy.BaseStrategy, ds.StrategyHelper):

    """
    单均线策略
    """
    def __init__(self, feed, brk):
        strategy.BaseStrategy.__init__(self, feed, brk)
        sma_period = ds.CONFIG['SMA_PERIOD']
        self.__instrument = common.CoinSymbol.BTC
        self.__prices = feed[self.__instrument].getExtraDataSeries(common.OrderType.ASK)
        self.__sma = ma.SMA(self.__prices, sma_period)
        self.__bid = None
        self.__ask = None
        self.__position = None
        self.__posSize = ds.CONFIG['POSITION_SIZE']

        feed.get_exchange().subscribe_event(BtccWebsocketClient.Event.ON_TICKER, self.__on_ticker)
        feed.get_exchange().subscribe_event(BtccWebsocketClient.Event.ON_DISCONNECTED, self.__on_disconnected)

    def __on_ticker(self, ticker):
        self.__bid = ticker.get_bid()
        self.__ask = ticker.get_ask()

    def __on_disconnected(self):
        self.info('__on_disconnected')
        self.stop()

    # override StrategyHelper
    def get_position(self):
        return self.__position

    def get_sma(self):
        # return dict
        return {
            'single': self.__sma
        }

    # override Strategy
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
        pass

    def enterSignal(self):
        return self.__position is None and cross.cross_above(self.__prices, self.__sma) > 0

    def exitSignal(self):
        ret = self.__position is not None and not self.__position.exitActive() and cross.cross_below(self.__prices, self.__sma) > 0
        return ret

    def onBars(self, bars):
        bar = bars[self.__instrument]
        self.info('Ask: %s, Bid: %s, Time: %s' % (bar.getExtraColumns()[common.OrderType.ASK], bar.getExtraColumns()[common.OrderType.BID], bar.getDateTime()))

        if self.__ask is None:
            return

        if self.exitSignal():
            self.info("Exit signal. Sell at %s" % (self.__bid))
            self.__position.exitLimit(self.__bid)
        elif self.enterSignal():
            self.info("Entry signal. Buy at %s" % (self.__ask))
            self.__position = self.enterLongLimit(self.__instrument, self.__ask, self.__posSize, True)

"""
========================================
"""


class SingleSMA(ds.StrategyRun):

    def __init__(self):
        super(SingleSMA, self).__init__()

    def config_live(self):
        exchange = BtccExchange(duration=ds.CONFIG['DURATION'])
        bar_feed = LiveTradeFeed(exchange)
        brk = livebroker.LiveBroker()
        return Strategy(bar_feed, brk)

    def config_backtesting(self):
        exchange = BtccExchange(duration=ds.CONFIG['DURATION'])
        bar_feed = LiveTradeFeed(exchange)
        brk = BacktestingBroker(ds.CONFIG['START_CAPTIAL'], bar_feed)
        return Strategy(bar_feed, brk)


def main():
    SingleSMA().run()

if __name__ == "__main__":
    main()
