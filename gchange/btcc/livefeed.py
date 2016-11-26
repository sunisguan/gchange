# -*- coding: utf-8 -*-
from pyalgotrade import bar
from pyalgotrade import barfeed
import common
import datetime
from .btcc_exchange import BtccExchange, BtccWebsocketClient


class TickerBar(bar.Bar):
    def __init__(self, datetime_, ticker):
        self.__datetime = datetime_
        self.__ticker = ticker

    def setUseAdjustedValue(self, useAdjusted):
        pass

    def getUseAdjValue(self):
        return False

    def getDateTime(self):
        return self.__datetime

    def getOpen(self, adjusted=False):
        #return self.__ticker.get_open()
        return self.getPrice()

    def getHigh(self, adjusted=False):
        #return self.__ticker.get_high()
        return self.getPrice()

    def getLow(self, adjusted=False):
        #return self.__ticker.get_low()
        return self.getPrice()

    def getClose(self, adjusted=False):
        #return self.__ticker.get_close()
        return self.getPrice()

    def getVolume(self):
        return self.__ticker.get_volume()

    def getAdjClose(self):
        return self.getClose()

    def getFrequency(self):
        return bar.Frequency.SECOND

    def getPrice(self):
        return self.__ticker.get_last()

    def getExtraColumns(self):
        return {
            common.OrderType.ASK: self.__ticker.get_ask(),
            common.OrderType.BID: self.__ticker.get_bid()
        }

class LiveTradeFeed(barfeed.BaseBarFeed):
    """
    A real-time BarFeed that builds bars from live trades
    """

    QUEUE_TIMEOUT = 0.01

    def __init__(self, exchange, maxLen=None):
        super(LiveTradeFeed, self).__init__(bar.Frequency.TRADE, maxLen)
        self.__barDicts = []
        self.registerInstrument(common.CoinSymbol.BTC)
        self.__prevTradeDateTime = None
        self.__stopped = False
        self.__exchange = exchange
        # 注册监听事件
        self.__exchange.subscribe_event(BtccWebsocketClient.Event.ON_CONNECTED, self.__on_connected)
        self.__exchange.subscribe_event(BtccWebsocketClient.Event.ON_DISCONNECTED, self.__on_disconnected)
        self.__exchange.subscribe_event(BtccWebsocketClient.Event.ON_TICKER, self.__on_ticker)

    def get_exchange(self):
        return self.__exchange

    def __initializeClient(self):
        return self.__exchange.start_websocket_client()

    def subscribe_ticker_event(self, handler):
        self.__exchange.subscribe_event(BtccWebsocketClient.Event.ON_TICKER, handler)

    def subscribe_disconnected_event(self, handler):
        self.__exchange.subscribe_event(BtccWebsocketClient.Event.ON_DISCONNECTED, handler)

    # 实现 web socket handler
    def __on_ticker(self, ticker):
        common.logger.debug('__on_ticker')
        barDict = {common.CoinSymbol.BTC: TickerBar(self.__get_ticker_datetime(ticker), ticker)}
        self.__barDicts.append(barDict)

    def __on_connected(self):
        common.logger.debug('__on_connected')

    def __on_disconnected(self):
        common.logger.debug('__on_disconected')

    def __get_ticker_datetime(self, tickr):
        ret = tickr.get_datetime()
        if ret == self.__prevTradeDateTime:
            ret += datetime.timedelta(microseconds=1)
        self.__prevTradeDateTime = ret
        return ret

    # 开始 override
    def getCurrentDateTime(self):
        return datetime.datetime.now()

    def barsHaveAdjClose(self):
        return False

    def getNextBars(self):
        ret = None
        if len(self.__barDicts):
            ret = bar.Bars(self.__barDicts.pop(0))
        return ret

    def peekDateTime(self):
        """
        Return None since this is a realtime subject
        :return: None
        """
        return None

    # This may raise
    def start(self):
        super(LiveTradeFeed, self).start()
        self.__exchange.start_websocket_client()

    # This should not raise
    def stop(self):
        if self.__exchange.stop_websocket_client():
            self.__stopped = True

    def join(self):
        self.__exchange.join_websocket_client()

    def eof(self):
        return self.__stopped

    # 结束 override


