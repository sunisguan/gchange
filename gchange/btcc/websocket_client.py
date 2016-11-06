""" An example for Python Socket.io Client
    Requires: six,socketIO_client
"""
from socketIO_client import SocketIO, BaseNamespace
import time
import re
import hmac
import hashlib
import base64
import tornado

import common
from pyalgotrade.websocket import pusher
import threading
import Queue
import datetime

import logging
#logging.getLogger('socketIO-client').setLevel(logging.DEBUG)

def get_current_datetime():
    return datetime.datetime.now()

class Trade(pusher.Event):
    """
    A trade event
    """

    def __init__(self, dateTime, eventDict):
        super(Trade, self).__init__(eventDict, True)
        self.__dateTime = dateTime

    def getDateTime(self):
        """Returns the :class:`datetime.datetime` when this event was received."""
        return self.__dateTime

    def getId(self):
        """Returns the trade id."""
        return self.getData()['id']

    def getPrice(self):
        """Returns the trade price."""
        return self.getData()["price"]

    def getAmount(self):
        """Returns the trade amount."""
        return self.getData()["amount"]

    def isBuy(self):
        """Returns True if the trade was a buy."""
        return self.getData()["type"] == 0

    def isSell(self):
        """Returns True if the trade was a sell."""
        return self.getData()["type"] == 1

class OrderBookUpdate(pusher.Event):
    """An order book update event."""

    def __init__(self, dateTime, eventDict):
        super(OrderBookUpdate, self).__init__(eventDict, True)
        self.__dateTime = dateTime

    def getDateTime(self):
        """Returns the :class:`datetime.datetime` when this event was received."""
        return self.__dateTime

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


class BtccWebsocketClient(BaseNamespace):

    # Events
    ON_TRADE = 1
    ON_ORDER_BOOK_UPDATE = 2
    ON_CONNECTED = 3
    ON_DISCONNECTED = 4

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

    def stop_client(self):
        self.disconnect()

    def on_connect(self):
        self.__queue = Queue.Queue()
        print('[Connected]')

    def on_disconnect(self):
        print('[Disconnect]')
        self.__queue.put((BtccWebsocketClient.ON_DISCONNECTED, None))

    def on_ticker(self, *args):
        #print('ticker', args)
        pass

    def on_trade(self, *args):
        self.on_trade(Trade(get_current_datetime(), args))

    def on_grouporder(self, *args):
        #print('grouporder', args)
        pass

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

    def on_trade(self, trade):
        common.logger.info('websocket on trade')
        self.__queue.put((BtccWebsocketClient.ON_TRADE, trade))

    def on_order_book_update(self, orderBookUpdate):
        common.logger.info('websocket on_order_book_update')
        self.__queue.put((BtccWebsocketClient.ON_ORDER_BOOK_UPDATE, orderBookUpdate))


class WebSocketClientThread(threading.Thread):
    def get_queue(self):
        return self.__ws_client.get_queue()

    def __init__(self):
        super(WebSocketClientThread, self).__init__()
        self.__socket_io = SocketIO('websocket.btcc.com', 80)
        self.__ws_client = self.__socket_io.define(BtccWebsocketClient)


    def start(self):
        #self.__ws_client.emit('subscribe', 'marketdata_cnybtc')
        #self.__ws_client.emit('subscribe', 'grouporder_cnybtc')
        #self.__socket_io.wait()

        super(WebSocketClientThread, self).start()

    def run(self):

        tornado.ioloop.IOLoop.instance().start()

    def stop(self):
        try:
            common.logger.info("Stopping websocket client.")
            self.__ws_client.stop_client()
        except Exception, e:
            common.logger.error("Error stopping websocket client: %s." % (str(e)))
