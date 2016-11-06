import threading
import time

import Queue
from pyalgotrade import broker

from . import common, btcc_http_client


def build_order_from_open_order(openOrder, instrumentTraits):
    if openOrder.isBuy():
        action = broker.Order.Action.BUY
    elif openOrder.isSell():
        action = broker.Order.Action.SELL
    else:
        raise Exception("Invalid order type")

    ret = broker.LimitOrder(action, common.CoinSymbol.BTC, openOrder.getPrice(), openOrder.getAmount(), instrumentTraits)
    ret.setSubmitted(openOrder.getId(), openOrder.getDateTime())
    ret.setState(broker.Order.State.ACCEPTED)


class TradeMonitor(threading.Thread):
    POLL_FREQUENCY = 2

    # Events
    ON_USER_TRADE = 1

    def __init__(self, httpClient):
        super(TradeMonitor, self).__init__()
        self.__lastTradeId = -1
        self.__httpClient = httpClient
        self.__queue = Queue.Queue()
        self.__stop = False

    def _getNewTrades(self):
        # TODO: 获取用户最新交易
        userTrades = self.__httpClient.get_transactions()
        return 0

    def getQueue(self):
        return self.__queue

    def start(self):
        trades = self._getNewTrades()
        if len(trades):
            self.__lastTradeId = trades[-1].getId()
            common.logger.info('Last trade found: %d' % self.__lastTradeId)
        super(TradeMonitor, self).start()

    def run(self):
        while not self.__stop:
            try:
                trades = self._getNewTrades()
                if len(trades):
                    self.__lastTradeId = trades[-1].getId()
                    common.logger.info('%d new trade/s found' % len(trades))
                    self.__queue.put((TradeMonitor.ON_USER_TRADE, trades))
            except Exception, e:
                common.logger.critical('Error retrieving user transactions', exc_info = e)

            time.sleep(TradeMonitor.POLL_FREQUENCY)

    def stop(self):
        self.__stop = True



class LiveBroker(broker.Broker):
    QUEUE_TIMEOUT = 0.01

    def __init__(self, serviceId, key, secret):
        super(LiveBroker, self).__init__()
        self.__stop = False
        self.__btcService = self.buildBtccService(serviceId, key, secret)
        self.__tradeMonitor = TradeMonitor(self.__btcService)
        self.__cash = 0
        self.__shares = {}
        self.__activeOrders = {}

    def _registerOrder(self, order):
        assert(order.getId() not in self.__activeOrders)
        assert(order.getId() is not None)
        self.__activeOrders[order.getId()] = order

    def _unregisterOrder(self, order):
        assert(order.getId() in self.__activeOrders)
        assert(order.getId() is not None)
        del self.__activeOrders[order.getId()]

    def buildBtccService(self, _id, key, secret):
        # TODO: 新建链接类
        pass

    def refreshAccountBalance(self):
        # 刷新用户账户

        # 防止获取中发生错误
        self.__stop = True

        # TODO: 获取用户账户信息
        balance = None

        # TODO: 获取用户现金
        self.__cash = None

        # TODO: 获取用户可用的BTC
        btc = None
        if btc:
            self.__shares = {common.CoinSymbol.BTC: btc}
        else:
            self.__shares = {}

        # 没有错误发生，继续轮询
        self.__stop = False

    def refreshOpenOrders(self):
        # 防止获取中发生错误
        self.__stop = True

        # TODO: 获取Open Orders
        openOrders = None

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

    def _onUserTrades(self, trades):
        for trade in trades:
            order = self.__activeOrders.get(trade.getOrderId())
            if order is not None:
                fee = trade.getFee()
                # TODO: 获取成交价
                fillPrice = trade.getBTCCNY()
                # TODO: 获取成交量
                btcAmount = trade.getBTC()
                # TODO: 获取交易时间
                dateTime = trade.getDateTime()

                # TODO: 更新账户情况
                self.refreshAccountBalance()

                # TODO: 更新Order
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
                common.logger.info('Trade %d refered to order %d that is not active' % (trade.getId(), trade.getOrderId()))

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
                self.notifyOrderEvent(broker.OrderEvent(order, broker.OrderEvent.Type.ACCEPTED), None)

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
                # TODO: 提交买单
                btccOrder = None
            else:
                # TODO: 提交卖单
                btccOrder = None

            order.setSubmitted(btccOrder.getId(), btccOrder.getDateTime())
            self._registerOrder(order)
            # Switch from INITIAL -> SUBMITTED
            # IMPORTANT: Do not emit an event for this switch because when using the position interface
            # the order is not yet mapped to the position and Position.onOrderUpdated will get called.
            order.switchState(broker.Order.State.SUBMITTED)
        else:
            raise Exception('The order was already processed')

    def createMarketOrder(self, action, instrument, quantity, onClose=False):
        # TODO: create market order
        pass

    def createLimitOrder(self, action, instrument, limitPrice, quantity):
        if instrument != common.CoinSymbol.BTC:
            raise Exception('仅支持 BTC 交易')

        if action == broker.Order.Action.BUY_TO_COVER:
            action = broker.Order.Action.BUY
        elif action == broker.Order.Action.SELL_SHORT:
            action = broker.Order.Action.SELL

        if action not in [broker.Order.Action.BUY, broker.Order.Action.SELL]:
            raise Exception('仅支持 买/卖 交易')

        instrumentTraits = self.getInstrumentTraits(instrument)
        limitPrice = round(limitPrice, 2)
        quantity = instrumentTraits.roundQuantity(quantity)
        return broker.LimitOrder(action, instrument, limitPrice, quantity, instrumentTraits)

    def createStopOrder(self, action, instrument, stopPrice, quantity):
        raise Exception('Stop orders are not supported')

    def createStopLimitOrder(self, action, instrument, stopPrice, limitPrice, quantity):
        raise Exception('Stop limit orders are not supported')

    def cancelOrder(self, order):
        activeOrder = self.__activeOrders.get(order.getId())
        if activeOrder is None:
            raise Exception('The order is not active anymore')
        if activeOrder.isFilled():
            raise Exception('Can not cancel order that has already been filled')

        # TODO: BTCCService cancel order
        self.__btcService = None
        self._unregisterOrder(order)
        order.switchState(broker.Order.State.CANCELED)

        # 更新账户
        self.refreshAccountBalance()

        # 发通知，这个订单被取消
        self.notifyOrderEvent(broker.OrderEvent(order, broker.OrderEvent.Type.CANCELED, "用户主动取消"))

    # END broker.Broker interface

