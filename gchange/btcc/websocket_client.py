# -*- coding: utf-8 -*-
""" An example for Python Socket.io Client
    Requires: six,socketIO_client
"""
from socketIO_client import SocketIO, BaseNamespace
import time
import re
import hmac
import hashlib
import base64

import common
from pyalgotrade.websocket import pusher
import threading
import Queue
import datetime

from ..utils import TimeUtils

def get_current_datetime():
    return datetime.datetime.now()

class Trade(object):
    """
    A trade event
    """

    def __init__(self, price, trade_id, amount, date, type, market):
        self.__price = price
        self.__tid = trade_id
        self.__amount = amount
        self.__date = date
        self.__type = type
        self.__market = market
        self.__datetime = TimeUtils.timestamp_to_datetime(self.__date)

    def getDateTime(self):
        """Returns the :class:`datetime.datetime` when this event was received."""
        return self.__datetime

    def updateDateTime(self, m=0):
        if m <= 0:
            return self.getDateTime()
        else:
            self.__datetime += datetime.timedelta(milliseconds=m)
            return self.getDateTime()

    def getId(self):
        """Returns the trade id."""
        return self.__tid

    def getPrice(self):
        """Returns the trade price."""
        return self.__price

    def getAmount(self):
        """Returns the trade amount."""
        return self.__amount

    def isBuy(self):
        """Returns True if the trade was a buy."""
        return self.__type == 'buy'

    def isSell(self):
        """Returns True if the trade was a sell."""
        return self.__type == 'sell'

class Ticker(object):
    """An order book update event."""

    def __init__(self, high, low, buy, sell, last, vol, date, vwap, prev_close, open):
        self.__high = high
        self.__low = low
        self.__buy = buy
        self.__sell = sell
        self.__last = last
        self.__vol = vol
        self.__date = date
        self.__vwap = vwap
        self.__prev_close = prev_close
        self.__open = open
        self.__datetime = TimeUtils.timestamp_to_datetime(self.__date)

    def getDateTime(self):
        """Returns the :class:`datetime.datetime` when this event was received."""
        return self.__datetime

    def getBidPrices(self):
        """Returns a list with the top 20 bid prices."""
        return [float(bid[0]) for bid in self.getData()["bids"]]

    def getBidVolumes(self):
        """Returns a list with the top 20 bid volumes."""
        return [float(bid[1]) for bid in self.getData()["bids"]]

    def getAskPrices(self):
        """Returns a list with the top 20 ask prices."""
        return [float(ask[0]) for ask in self.getData()["asks"]]

    def getAskVolumes(self):
        """Returns a list with the top 20 ask volumes."""
        return [float(ask[1]) for ask in self.getData()["asks"]]

class MarketDepth(object):
    class Depth(object):
        def __init__(self, totalamount, price, type):
            self.__totalamount = totalamount
            self.__price = price
            self.__type = type

        def get_type(self):
            return self.__type
        def get_amount(self):
            return self.__totalamount
        def get_price(self):
            return self.__price

    def __init__(self, ask, bid, market):
        self.__asks = []
        self.__bids = []
        self.__market = market
        for item in ask:
            item = MarketDepth.Depth(**item)
            self.__asks.append(item)
        for item in bid:
            item = MarketDepth.Depth(**item)
            self.__bids.append(item)

        self.__asks.sort(key=lambda x:x.get_price(), reverse=True)
        self.__bids.sort(key=lambda x: x.get_price(), reverse=True)

    def get_asks(self):
        return self.__asks
    def get_bids(self):
        return self.__bids
    def get_top_ask(self):
        return self.__asks[0]
    def get_top_bid(self):
        return self.__bids[0]

class BtccWebsocketClient(BaseNamespace):

    # Events
    ON_TRADE = 1
    ON_ORDER_BOOK_UPDATE = 2
    ON_CONNECTED = 3
    ON_DISCONNECTED = 4
    ON_MARKETDEPTH = 5

    def __init__(self, io, path = ''):
        super(BtccWebsocketClient, self).__init__(io, path)
        self.__queue = Queue.Queue()
        # btcc返回的 trade 时间没有毫秒，导致时间时间相同
        self.__millisecond_to_add = 1

    def get_queue(self):
        return self.__queue

    def _get_tonce(self):
        return int(time.time() * 1000000)

    def _get_postdata(self):
        post_data = {}
        tonce = self._get_tonce()
        post_data['tonce'] = tonce
        post_data['accesskey'] = common.BTCC_ACCESS_KEY
        post_data['requestmethod'] = 'post'

        if 'id' not in post_data:
            post_data['id'] = tonce

        # modefy here to meet your requirement
        post_data['method'] = 'subscribe'
        post_data['params'] = ['order_cnybtc', 'order_cnyltc', 'order_btcltc', 'account_info']
        return post_data


    def _get_sign(self, pdict):
        pstring = ''
        fields = ['tonce', 'accesskey', 'requestmethod', 'id', 'method', 'params']
        for f in fields:
            if pdict[f]:
                if f == 'params':
                    param_string = str(pdict[f])
                    param_string = param_string.replace('None', '')
                    param_string = re.sub("[\[\] ]", "", param_string)
                    param_string = re.sub("'", '', param_string)
                    pstring += f + '=' + param_string + '&'
                else:
                    pstring += f + '=' + str(pdict[f]) + '&'
            else:
                pstring += f + '=&'
        pstring = pstring.strip('&')
        phash = hmac.new(common.BTCC_SECRET_KEY, pstring, hashlib.sha1).hexdigest()

        return base64.b64encode(common.BTCC_ACCESS_KEY + ':' + phash)

    def on_connect(self):
        print('[Connected]')
        self.__queue.put((BtccWebsocketClient.ON_CONNECTED, None))

    def on_disconnect(self):
        print('[Disconnect]')
        #self.__queue.put(BtccWebsocketClient.ON_DISCONNECTED, None)


    def on_ticker(self, *args):
        #print('ticker', args)
        pass

    def on_trade(self, *args):
        t = Trade(**args[0])
        t.updateDateTime(self.__millisecond_to_add)
        self.__millisecond_to_add += 1
        self.__queue.put((BtccWebsocketClient.ON_TRADE, t))

    def on_grouporder(self, *args):
        #print args[0]['grouporder']
        __marketdepth = MarketDepth(**(args[0]['grouporder']))
        self._on_marketdepth(__marketdepth)

    def on_order(self, *args):
        #print('order', args)
        pass

    def on_account_info(self, *args):
        #print('account_info', args)
        pass

    def on_message(self, *args):
        #print('message', args)
        pass

    def on_error(self, data):
        common.logger.error("Error: %s" % (data))

    def _on_marketdepth(self, marketdepth):
        self.__queue.put((BtccWebsocketClient.ON_MARKETDEPTH, marketdepth))

    def on_order_book_update(self, orderBookUpdate):
        self.__queue.put((BtccWebsocketClient.ON_ORDER_BOOK_UPDATE, orderBookUpdate))


class WebSocketClientThread(threading.Thread):
    def __init__(self):
        self.__socketIO = None
        self.__ws_client = None

        super(WebSocketClientThread, self).__init__()

    def get_queue(self):
        return self.__ws_client.get_queue()

    def start(self):
        self.__socketIO = SocketIO('websocket.btcc.com', 80)
        self.__ws_client = self.__socketIO.define(BtccWebsocketClient)
        self.__ws_client.emit('subscribe', 'marketdata_cnybtc')
        self.__ws_client.emit('subscribe', 'grouporder_cnybtc')
        super(WebSocketClientThread, self).start()

    def run(self):
        super(WebSocketClientThread, self).run()
        self.__socketIO.wait(60*10)
        print '__socketIO.wait(30)'
        self.__ws_client.off('subscribe')
        self.__ws_client.disconnect()

    def stop(self):
        try:
            common.logger.info("WebSocketClientThread Stopping websocket client.")
        except Exception, e:
            common.logger.error("Error stopping websocket client: %s." % (str(e)))
