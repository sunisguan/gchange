# -*- coding: utf-8 -*-

from pyalgotrade import broker
from pyalgotrade.broker import backtesting
from . import common



class BacktestingBroker(backtesting.Broker):
    # 最小交易金额
    MIN_TRADE_CNY = 1

    """
    btcc backtesting broker

    :param cash: 初始化资金
    :param barFeed: 数据源

    """
    def __init__(self, cash, barFeed):
        super(BacktestingBroker, self).__init__(cash, barFeed, backtesting.NoCommission())

    def getInstrumentTraits(self, instrument):
        return common.BTCTraits()

    def submitOrder(self, order):
        if order.isInitial():
            order.setAllOrNone(False)
            order.setGoodTillCanceled(True)
        return super(BacktestingBroker, self).submitOrder(order)

    def createMarketOrder(self, action, instrument, quantity, onClose=False):
        # TODO: 创建市价订单
        pass

    def createLimitOrder(self, action, instrument, limitPrice, quantity):
        if instrument not in [common.CoinSymbol.BTC, common.CoinSymbol.LTC]:
            raise Exception('只支持 BTC/LTC交易')

        if action == broker.Order.Action.BUY_TO_COVER:
            action = broker.Order.Action.BUY
        elif action == broker.Order.Action.SELL_SHORT:
            action = broker.Order.Action.SELL

        if limitPrice * quantity < BacktestingBroker.MIN_TRADE_CNY:
            raise Exception('交易必须 >= %s' % BacktestingBroker.MIN_TRADE_CNY)

        if action == broker.Order.Action.BUY:
            # 检查是否有足够的现金
            fee = self.getCommission().calculate(None, limitPrice, quantity)
            cashRequired = limitPrice * quantity + fee
            if cashRequired > self.getCash(False):
                raise Exception('没有足够现金进行交易')
        elif action == broker.Order.Action.SELL:
            # 检查是否有足够的币
            if quantity > self.getShares(common.CoinSymbol.BTC):
                raise Exception('没有足够的 %s 进行交易' % common.CoinSymbol.BTC)
        else:
            raise Exception('仅支持 买/卖 交易')

        return super(BacktestingBroker, self).createLimitOrder(action, instrument, limitPrice, quantity)

    def createStopOrder(self, action, instrument, stopPrice, quantity):
        raise Exception('不支持止损订单')

    def createStopLimitOrder(self, action, instrument, stopPrice, limitPrice, quantity):
        raise Exception('不支持限价止损订单')




