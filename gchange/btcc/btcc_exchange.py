# -*- coding: utf-8 -*-
import btcc_http_client as bhc
import btcc_model as bm
import common
from socketIO_client import SocketIO, BaseNamespace
import time
import re
import hmac
import hashlib
import base64
import threading
import Queue
from pyalgotrade import observer
import json
import abc


class BtccExchange(object):

    def __init__(self, duration=''):
        self.__hc = bhc.BtccHttpClient()
        # 准备事件回调
        self.__orderbook_update_event = observer.Event()
        self.__trade_event = observer.Event()
        self.__ticker_event = observer.Event()

        self.__events = {
            BtccWebsocketClient.Event.ON_ORDER_BOOK_UPDATE: observer.Event(),
            BtccWebsocketClient.Event.ON_TRADE: observer.Event(),
            BtccWebsocketClient.Event.ON_TICKER: observer.Event(),
            BtccWebsocketClient.Event.ON_DISCONNECTED: observer.Event()
        }
        self.__socket_thread = WebSocketClientThread(duration=duration, events=self.__events)

    def subscribe_event(self, event_type, handler):
        if event_type not in self.__events.keys() or handler is None:
            return
        else:
            self.__events[event_type].subscribe(handler)

    def start_websocket_client(self):
        """
        开启 websocket 监听，包括市场深度，交易，订单更新
        :return:
        """
        try:
            self.__socket_thread.start()
            common.logger.info('web socket start ok')
        except Exception as e:
            common.logger.error('web socket start error: %s' % e)
        finally:
            return self.__socket_thread.isAlive()

    def stop_websocket_client(self):
        ret = False
        try:
            if self.__socket_thread is not None and self.__socket_thread.is_alive():
                common.logger.info('livefeed Shutting down websocket client')
                self.__socket_thread.stop()
                ret = True
        except Exception, e:
            common.logger.error('Error shutting down client: %s' % str(e))
        finally:
            return ret

    def is_client_alive(self):
        return self.__socket_thread is not None and self.__socket_thread.isAlive()

    def join_websocket_client(self):
        if self.is_client_alive():
            self.__socket_thread.join()

    def get_socket_queue(self):
        return self.__socket_thread.get_queue()

    def get_account_profile(self):
        """
        获取用户信息
        :return: btcc_model.UserProfile
        """
        resp, status = self.__hc.get_account_info(acount_type=bhc.BtccHttpClient.AccountParams.Profile)

        if status:
            return bm.UserProfile(**resp)
        else:
            raise Exception('获取用户信息失败')

    def get_balance(self, coin_symbol):
        """
        获取用户账户对应货币余额
        :param coin_symbol: common.CoinSymbol
        :return:
        """
        resp, status = self.__hc.get_account_info(acount_type=bhc.BtccHttpClient.AccountParams.Balance)
        if status and coin_symbol in common.CoinSymbol.COIN_SYMBOLS:
            return bm.Balance(**resp['balance'][coin_symbol])
        else:
            raise Exception('获取用户账户对应货币余额失败')

    def get_cash(self):
        balance = self.get_balance(common.CoinSymbol.CNY)
        return balance.get_amount()

    def get_avaliable_btc(self):
        balance = self.get_balance(common.CoinSymbol.BTC)
        return balance.get_amount()

    def buy(self, amount, price=None, market=bhc.BtccHttpClient.MarketParams.BTC_CNY):
        """
        挂买单
        :param amount: 买入量
        :param price: 买入价格，None 为市价买入
        :param market: 买入货币类型, btcc_http_client.BtccHttpClient.MarketParams
        :return: Order，如果挂单后获取挂单信息失败，则 Order 只有 Order id
        """
        if price is None:
            # buy market price
            resp, status = self.__hc.buy_market(amount=amount, market=market)
        else:
            # buy limit price
            resp, status = self.__hc.buy_limit(price=price, amount=amount, market=market)
        if status:
            # 买单报单成功, 获取挂单状态，初始化order
            time.sleep(1)
            order_id = resp
            resp, status = self.__hc.get_order(order_id=order_id)
            if status:
                return bm.Order(**resp['order'])
            else:
                return bm.Order(id=order_id)
        else:
            raise Exception('买单挂单失败')

    def buy_stop(self):
        # TODO:
        pass

    def sell(self, amount, price=None, market=bhc.BtccHttpClient.MarketParams.BTC_CNY):
        """
        挂卖单
        :param amount: 卖出量
        :param price: 卖出价格， None 为市价卖出
        :param market: 卖出货币类型, btcc_http_client.BtccHttpClient.MarketParams
        :return: Order，如果挂单后获取挂单信息失败，则 Order 只有 Order id
        """
        if price is None:
            # sell market price
            resp, status = self.__hc.sell_market(amount=amount, market=market)
        else:
            # sell limit price
            resp, status = self.__hc.sell_limit(price=price, amount=amount, market=market)
        if status:
            # 卖单报单成功, 获取挂单状态，初始化order
            time.sleep(1)
            order_id = resp
            resp, status = self.__hc.get_order(order_id=resp)
            if status:
                return bm.Order(**resp['order'])
            else:
                return bm.Order(id=order_id)
        else:
            raise Exception('买单挂单失败')

    def sell_stop(self):
        # TODO:
        pass

    def cancel(self, order_id, market=bhc.BtccHttpClient.MarketParams.BTC_CNY):
        """
        取消挂单
        :param order_id: 要取消的订单号
        :param market: 取消货币类型, btcc_http_client.BtccHttpClient.MarketParams
        :return: True 取消成功
        """
        resp, status = self.__hc.cancel(order_id=order_id, market=market)
        if not status:
            common.logger.info('取消挂单失败')
        return status

    def cancel_stop(self):
        # TODO:
        pass

    def get_orders(self, market=bhc.BtccHttpClient.MarketParams.BTC_CNY, open_only=False):
        resp, status = self.__hc.get_orders(market=market, open_only=open_only)
        if status:
            return [bm.Order(**order) for order in resp['order']]
        else:
            raise Exception('获取订单信息失败')

    def get_order(self, order_id):
        resp, status = self.__hc.get_order(order_id=order_id)
        if status:
            return bm.Order(**resp['order'])
        else:
            return bm.Order(id=order_id)

    def get_transactions(self, trans_type=common.TransactionType.ALL, since=None):
        """
        获取交易记录，从 since 开始后的10条交易记录
        :param trans_type: common.TransactionType
        :param since: transaction id
        :return:
        """
        resp, status = self.__hc.get_transactions(trans_type=trans_type, since=since, sincetype='id')
        if status:
            if len(resp):
                return [bm.Transaction(**trans) for trans in resp['transaction']]
            else:
                raise Exception('获取交易记录失败')


class BtccWebsocketClient(BaseNamespace):

    # Events
    class Event(object):
        ON_TRADE = 1
        ON_ORDER_BOOK_UPDATE = 2
        ON_CONNECTED = 3
        ON_DISCONNECTED = 4
        ON_MARKETDEPTH = 5
        ON_TICKER = 6

    def __init__(self, io, path = ''):
        super(BtccWebsocketClient, self).__init__(io, path)
        self.__queue = Queue.Queue()
        # btcc返回的 trade 时间没有毫秒，导致时间时间相同
        self.__millisecond_to_add = 1
        self.__events = None

    def get_queue(self):
        return self.__queue

    def set_events(self, events):
        self.__events = events

    def on_connect(self):
        self.__dispatch(self.Event.ON_CONNECTED)

    def on_disconnect(self):
        self.__dispatch(self.Event.ON_CONNECTED)

    def on_ticker(self, *args):
        # 接收到市场 Ticker 数据
        self.__dispatch(self.Event.ON_TICKER, bm.Ticker(**args[0]['ticker']))

    def on_trade(self, *args):
        # 接收到市场交易数据
        self.__dispatch(self.Event.ON_TRADE, bm.Trade(**args[0]))

    def on_grouporder(self, *args):
        # 接收到市场深度
        # TODO:
        self.__queue.put((BtccWebsocketClient.Event.ON_MARKETDEPTH, bm.MarketDepth(**(args[0]['grouporder']))))

    def on_order(self, *args):
        # 接收到订单状态更新
        # TODO:
        self.__queue.put((BtccWebsocketClient.Event.ON_ORDER_BOOK_UPDATE, bm.Order(**args[0])))

    def on_account_info(self, *args):
        pass

    def on_message(self, *args):
        pass

    def on_error(self, data):
        common.logger.error("Error: %s" % data)

    def __dispatch(self, event_type, data=None):
        if self.__events is not None and event_type in self.__events.keys():
            self.__events[event_type].emit(data)

class WebSocketClientThread(threading.Thread):
    def __init__(self, duration='', events=None):
        self.__socketIO = None
        self.__ws_client = None
        self.__duration = duration
        self.__events = events

        super(WebSocketClientThread, self).__init__()

    def get_queue(self):
        return self.__ws_client.get_queue()

    def start(self):
        self.__socketIO = SocketIO('websocket.btcc.com', 80)
        self.__ws_client = self.__socketIO.define(BtccWebsocketClient)
        self.__ws_client.set_events(self.__events)

        self.__ws_client.emit('subscribe', 'marketdata_cnybtc')
        self.__ws_client.emit('subscribe', 'grouporder_cnybtc')

        payload = _get_postdata()
        arg = [json.dumps(payload), _get_sign(payload)]
        self.__ws_client.emit('private', arg)

        common.logger.info('btcc web socket client start')

        super(WebSocketClientThread, self).start()

    def run(self):
        super(WebSocketClientThread, self).run()
        if self.__duration != '':
            self.__socketIO.wait(self.__duration)
        else:
            self.__socketIO.wait()

        self.__ws_client.off('subscribe')
        self.__ws_client.off('private')
        self.__ws_client.disconnect()
        self.__events[BtccWebsocketClient.Event.ON_DISCONNECTED].emit()

    def stop(self):
        common.logger.info("WebSocketClientThread Stopping websocket client.")


def _get_postdata():
    post_data = {}
    tonce = int(time.time() * 1000000)
    post_data['tonce'] = tonce
    post_data['accesskey'] = common.BTCC_ACCESS_KEY
    post_data['requestmethod'] = 'post'

    if 'id' not in post_data:
        post_data['id'] = tonce

    # modefy here to meet your requirement
    post_data['method'] = 'subscribe'
    post_data['params'] = ['order_cnybtc', 'order_cnyltc', 'order_btcltc', 'account_info']
    return post_data


def _get_sign(pdict):
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











