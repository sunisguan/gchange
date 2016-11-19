# -*- coding: utf-8 -*-
import threading
import time

import Queue
from pyalgotrade import broker

import common, btcc_exchange


def build_order_from_open_order(openOrder, instrumentTraits):
    if openOrder.is_buy():
        action = broker.Order.Action.BUY
    elif openOrder.is_sell():
        action = broker.Order.Action.SELL
    else:
        raise Exception("Invalid order type")

    ret = broker.LimitOrder(action, common.CoinSymbol.BTC, openOrder.get_price(), openOrder.get_amount(), instrumentTraits)
    ret.setSubmitted(openOrder.get_id(), openOrder.get_datetime())
    ret.setState(broker.Order.State.ACCEPTED)

    return ret

class TradeMonitor(threading.Thread):
    POLL_FREQUENCY = 1

    # Events
    ON_USER_TRADE = 1

    def __init__(self, exchange):
        super(TradeMonitor, self).__init__()
        self.__lastTradeId = -1
        self.__exchange = exchange
        self.__queue = Queue.Queue()
        self.__stop = False

    def _getNewTrades(self):
        """
        获取用户最新交易
        :return:
        """
        userTrades = self.__exchange.get_orders()
        # 只抽取 buybtc和sellbtc交易，并且排序
        # ut.sort(key=lambda x: x.count, reverse=True)
        """
        trans_remove = []
        for trans in userTrades:
            if trans.get_type() not in (common.TransactionType.BUY_BTC, common.TransactionType.SELL_BTC):
                trans_remove.append(trans)
        userTrades = list(set(userTrades) - set(trans_remove))
        userTrades.sort(key=lambda  x: x.get_id(), reverse=True)
        """

        # Get the new trades only.
        ret = []
        for userTrade in userTrades:
            if userTrade.get_id() > self.__lastTradeId:
                ret.append(userTrade)
            else:
                break
        # Older trades first.reverse
        ret.reverse()
        return ret

    def getQueue(self):
        return self.__queue

    def start(self):
        trades = self._getNewTrades()
        if len(trades):
            self.__lastTradeId = trades[-1].get_id()
            common.logger.info('Last trade found: %d' % self.__lastTradeId)
        super(TradeMonitor, self).start()

    def run(self):
        while not self.__stop:
            try:
                trades = self._getNewTrades()
                if len(trades):
                    self.__lastTradeId = trades[-1].get_id()
                    common.logger.info('%d new trade/s found' % len(trades))
                    self.__queue.put((TradeMonitor.ON_USER_TRADE, trades))
            except Exception, e:
                common.logger.critical('Error retrieving user transactions', exc_info = e)

            time.sleep(TradeMonitor.POLL_FREQUENCY)

    def stop(self):
        self.__stop = True

class LiveBroker(broker.Broker):
    QUEUE_TIMEOUT = 0.01

    def __init__(self):
        super(LiveBroker, self).__init__()
        self.__stop = False
        self.__cash = 0
        self.__shares = {}
        self.__activeOrders = {}
        self.__exchange = btcc_exchange.BtccExchange()
        self.__tradeMonitor = TradeMonitor(self.__exchange)

    def _registerOrder(self, order):
        assert(order.getId() not in self.__activeOrders)
        assert(order.getId() is not None)
        self.__activeOrders[order.getId()] = order

    def _unregisterOrder(self, order):
        assert(order.getId() in self.__activeOrders)
        assert(order.getId() is not None)
        del self.__activeOrders[order.getId()]

    def refreshAccountBalance(self):
        """
        刷新用户账户信息
        :return:
        """
        # 防止获取中发生错误
        self.__stop = True

        # 获取用户现金
        self.__cash = self.__exchange.get_cash()
        common.logger.info('Avaliable Cash = %s' % self.__cash)

        # 获取用户可用的BTC
        btc = self.__exchange.get_avaliable_btc()
        if btc:
            self.__shares = {common.CoinSymbol.BTC: btc}
            common.logger.info('Avaliable BTC = %s' % btc)
        else:
            self.__shares = {}

        # 没有错误发生，继续轮询
        self.__stop = False

    def refreshOpenOrders(self):
        # 防止获取中发生错误
        self.__stop = True

        common.logger.info('start refresh open orders')

        openOrders = self.__exchange.get_orders(open_only=True)

        for openOrder in openOrders:
            self._registerOrder(build_order_from_open_order(openOrder, self.getInstrumentTraits(common.CoinSymbol.BTC)))
        common.logger.info('%d open order/s found' % len(openOrders))

        # 没有错误发生，继续轮询
        self.__stop = False

    def _startTradeMonitor(self):
        self.__stop = True
        common.logger.info('初始化 trade monitor')
        self.__tradeMonitor.start()
        self.__stop = False

    def _switch_order_status(self, order, trade):
        if order is not None and trade.get_status() != common.OrderStatus.PENDING:
            fee = trade.get_fee()
            # 获取成交价
            fillPrice = float(trade.get_avg_price())
            # 获取成交量
            btcAmount = float(trade.get_amount_original())
            # 获取交易时间
            dateTime = trade.get_datetime()

            self.refreshAccountBalance()

            # 更新Order
            orderExecutionInfo = broker.OrderExecutionInfo(fillPrice, abs(btcAmount), fee, dateTime)
            order.addExecutionInfo(orderExecutionInfo)
            if not order.isActive():
                self._unregisterOrder(order)
            # 通知更新订单状态
            if order.isFilled():
                eventType = broker.OrderEvent.Type.FILLED
            else:
                eventType = broker.OrderEvent.Type.PARTIALLY_FILLED
            self.notifyOrderEvent(broker.OrderEvent(order, eventType, orderExecutionInfo))
        else:
            pass
            #common.logger.info('Trade %d refered to order %d that is not active' % (trade.get_id(), order.getId()))

    def _onUserTrades(self, trades):
        for trade in trades:
            order = self.__activeOrders.get(trade.get_id())
            self._switch_order_status(order, trade)

    # BEGIN observer.Subject interface
    def start(self):
        super(LiveBroker, self).start()
        self.refreshAccountBalance()
        self.refreshOpenOrders()
        self._startTradeMonitor()

    def stop(self):
        self.__stop = True
        common.logger.info('停止 trade monitor')
        self.__tradeMonitor.stop()

    def join(self):
        if self.__tradeMonitor.isAlive():
            self.__tradeMonitor.join()

    def eof(self):
        return self.__stop

    def dispatch(self):
        # Switch orders from SUBMITTED to ACCEPTED
        ordersToProcess = self.__activeOrders.values()
        for order in ordersToProcess:
            if order.isSubmitted():
                order.switchState(broker.Order.State.ACCEPTED)
                self.notifyOrderEvent(broker.OrderEvent(order, broker.OrderEvent.Type.ACCEPTED, None))

        # Dispatch events from the trade monitor
        try:
            eventType, eventData = self.__tradeMonitor.getQueue().get(True, LiveBroker.QUEUE_TIMEOUT)

            if eventType == TradeMonitor.ON_USER_TRADE:
                self._onUserTrades(eventData)
            else:
                common.logger.error('Invalid event received to dispatch: %s - %s' % (eventType, eventData))
        except Queue.Empty:
            pass

    def peekDateTime(self):
        # return None since this is a realtime subject
        return None
    # END observer.Subject interface

    # BEGIN broker.Broker interface

    def getCash(self, includeShort=True):
        return self.__cash

    def getInstrumentTraits(self, instrument):
        return common.BTCTraits()

    def getShares(self, instrument):
        return self.__shares.get(instrument, 0)

    def getPositions(self):
        return self.__shares

    def getActiveOrders(self, instrument=None):
        return self.__activeOrders.values()

    def submitOrder(self, order):
        if order.isInitial():
            order.setAllOrNone(False)
            order.setGoodTillCanceled(True)

            if order.isBuy():
                if order.getType() == broker.Order.Type.MARKET:
                    btccOrder = self.__exchange.buy(amount=order.getQuantity())
                elif order.getType() == broker.Order.Type.LIMIT:
                    btccOrder = self.__exchange.buy(amount=order.getQuantity(), price=order.getLimitPrice())
                else:
                    raise Exception('仅支持 市价/限价 交易')
                common.logger.info('买入订单 %s' % btccOrder)
            else:
                if order.getType() == broker.Order.Type.MARKET:
                    btccOrder = self.__exchange.sell(amount=order.getQuantity())
                elif order.getType() == broker.Order.Type.LIMIT:
                    btccOrder = self.__exchange.sell(amount=order.getQuantity(), price=order.getLimitPrice())
                else:
                    raise Exception('仅支持 市价/限价 交易')
                common.logger.info('卖出订单 %s' % btccOrder)

            order.setSubmitted(btccOrder.get_id(), btccOrder.get_datetime())
            self._registerOrder(order)
            # Switch from INITIAL -> SUBMITTED
            # IMPORTANT: Do not emit an event for this switch because when using the position interface
            # the order is not yet mapped to the position and Position.onOrderUpdated will get called.
            order.switchState(broker.Order.State.SUBMITTED)
        else:
            raise Exception('The order was already processed')

    def createMarketOrder(self, action, instrument, quantity, onClose=False):
        if instrument != common.CoinSymbol.BTC:
            raise Exception('仅支持 BTC 交易')

        if action == broker.Order.Action.BUY_TO_COVER:
            action = broker.Order.Action.BUY
        elif action == broker.Order.Action.SELL_SHORT:
            action = broker.Order.Action.SELL

        if action not in [broker.Order.Action.BUY, broker.Order.Action.SELL]:
            raise Exception('仅支持 买/卖 交易')

        return broker.MarketOrder(action, instrument, quantity, False, common.BTCTraits())

    def createLimitOrder(self, action, instrument, limitPrice, quantity):
        if instrument != common.CoinSymbol.BTC:
            raise Exception('仅支持 BTC 交易')

        if action == broker.Order.Action.BUY_TO_COVER:
            action = broker.Order.Action.BUY
        elif action == broker.Order.Action.SELL_SHORT:
            action = broker.Order.Action.SELL

        if action not in [broker.Order.Action.BUY, broker.Order.Action.SELL]:
            raise Exception('仅支持 买/卖 交易')

        limitPrice = round(limitPrice, 2)
        return broker.LimitOrder(action, instrument, limitPrice, quantity, common.BTCTraits())

    def createStopOrder(self, action, instrument, stopPrice, quantity):
        raise Exception('Stop orders are not supported')

    def createStopLimitOrder(self, action, instrument, stopPrice, limitPrice, quantity):
        raise Exception('Stop limit orders are not supported')

    def cancelOrder(self, order):
        __id = order.getId()
        activeOrder = self.__activeOrders.get(__id)
        common.logger.info('cancel order %s' % __id)
        if activeOrder is None:
            raise Exception('The order is not active anymore')
        if activeOrder.isFilled():
            raise Exception('Can not cancel order that has already been filled')

        ret = self.__exchange.cancel(order_id=__id)

        # 更新账户
        self.refreshAccountBalance()

        if ret:
            # 取消成功
            self._unregisterOrder(order)
            order.switchState(broker.Order.State.CANCELED)

            # 发通知，这个订单被取消
            self.notifyOrderEvent(broker.OrderEvent(order, broker.OrderEvent.Type.CANCELED, "用户主动取消"))
        else:
            # 取消失败
            trade = self.__exchange.get_order(__id)
            self._switch_order_status(activeOrder, trade)

    # END broker.Broker interface

