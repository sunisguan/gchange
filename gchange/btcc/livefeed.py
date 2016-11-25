# -*- coding: utf-8 -*-
from pyalgotrade import bar
from pyalgotrade import barfeed
from pyalgotrade import observer
import common
import time
import datetime
import websocket_client
import Queue
from .btcc_exchange import BtccExchange, BtccWebsocketClient


class TradeBar(bar.Bar):
    __slots__ = ('__dateTime', '__tradeId', '__price', '__amount')

    def __init__(self, dateTime, trade):
        self.__dateTime = dateTime
        self.__tradeId = trade.getId()
        self.__price = trade.getPrice()
        self.__amount = trade.getAmount()
        self.__buy = trade.isBuy()

    def __setstate__(self, state):
        (self.__dateTime, self.__tradeId, self.__price, self.__amount) = state

    def __getstate__(self):
        return (self.__dateTime, self.__tradeId, self.__price, self.__amount)

    def setUseAdjustedValue(self, useAdjusted):
        if useAdjusted:
            raise Exception('Adjusted close is not avaliable')

    def getTradeId(self):
        return self.__tradeId

    def getFrequency(self):
        return bar.Frequency.TRADE

    def getDateTime(self):
        return self.__dateTime

    def getOpen(self, adjusted=False):
        return self.__price

    def getHigh(self, adjusted=False):
        return self.__price

    def getLow(self, adjusted=False):
        return self.__price

    def getClose(self, adjusted=False):
        return self.__price

    def getVolume(self):
        return self.__amount

    def getAdjClose(self):
        return None

    def getTypicalPrice(self):
        return self.__price

    def getPrice(self):
        return self.__price

    def getUseAdjValue(self):
        return False

    def isBuy(self):
        return self.__buy

    def isSell(self):
        return not self.__buy


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
        self.__thread = None
        self.__initializationOk = None
        self.__stopped = False
        self.__exchange = exchange
        self.__exchange.subscribe_event(BtccWebsocketClient.Event.ON_CONNECTED)

    def getCurrentDateTime(self):
        return websocket_client.get_current_datetime()

    def __initializeClient(self):
        return self.__exchange.start_websocket_client()

    def __onConnected(self):
        self.__initializationOk = True

    def __onDisconnected(self):
        if self.__enableReconnection:
            initialized = False
            while not self.__stopped and not initialized:
                common.logger.info('Reconnecting')
                initialized = self.__initializeClient()
                if not initialized:
                    time.sleep(5)
        else:
            self.__stopped = True

    def __dispatchImpl(self, eventFilter):
        ret = False
        try:
            eventType, eventData = self.__thread.get_queue().get(True, LiveTradeFeed.QUEUE_TIMEOUT)
            if eventFilter is not None and eventType not in eventFilter:
                return False
            ret = True
            if eventType == websocket_client.BtccWebsocketClient.ON_TRADE:
                self.__onTrade(eventData)
            elif eventType == websocket_client.BtccWebsocketClient.ON_ORDER_BOOK_UPDATE:
                self.__orderBookUpdateEvent.emit(eventData)
            elif eventType == websocket_client.BtccWebsocketClient.ON_CONNECTED:
                self.__onConnected()
            elif eventType == websocket_client.BtccWebsocketClient.ON_DISCONNECTED:
                self.__onDisconnected()
            elif eventType == websocket_client.BtccWebsocketClient.ON_MARKETDEPTH:
                self.__onMarketDepth(eventData)
                self.__marketdepth_update_event.emit(eventData)
            else:
                ret = False
                common.logger.error('Invalid event received to dispatch: %s - %s' % (eventType, eventData))
        except Queue.Empty:
            pass
        return ret

    def __getTradeDateTime(self, trade):
        """
        Bar datetimes should not duplicate. In case trade object datetimes conflict, we just move
        one slightly forward
        :param trade:
        :return:
        """
        ret = trade.getDateTime()
        if ret == self.__prevTradeDateTime:
            ret += datetime.timedelta(microseconds=1)
        self.__prevTradeDateTime = ret
        return ret

    def __onTrade(self, trade):
        """
        Build a bar for each trade
        :param trade:
        :return:
        """
        barDict = {common.CoinSymbol.BTC: TradeBar(self.__getTradeDateTime(trade), trade)}
        self.__barDicts.append(barDict)

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
        if self.__thread is not None:
            raise Exception('Already running')
        elif not self.__initializeClient():
            self.__stopped = True
            raise Exception('Initialization failed')

    def dispatch(self):
        """
        Note that we may return True even if we didn't dispatch any Bar event
        :return:
        """
        ret = False
        if self.__dispatchImpl(None):
            ret = True
        if super(LiveTradeFeed, self).dispatch():
            ret = None
        return ret

    # This should not raise
    def stop(self):
        try:
            self.__stopped = True
            if self.__thread is not None and self.__thread.is_alive():
                common.logger.info('livefeed Shutting down websocket client')
                self.__thread.stop()
        except Exception, e:
            common.logger.error('Error shutting down client: %s' % str(e))

    # This should not raise
    def join(self):
        if self.__thread is not None:
            self.__thread.join()

    def eof(self):
        return self.__stopped

    def getOrderBookUpdateEvent(self):
        """
        Returns the event that will be emitted when the orderbook gets updated

        Eventh handlers should one parameter:OrderBookUpdate instance

        :return: pyalgotrade.observer.Event
        """
        return self.__orderBookUpdateEvent

    def get_marketdepth_update_event(self):
        return self.__marketdepth_update_event



