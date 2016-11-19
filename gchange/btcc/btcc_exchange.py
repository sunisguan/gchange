# -*- coding: utf-8 -*-
import btcc_http_client as bhc
import btcc_model as bm
import common
from pyalgotrade import broker

class BtccExchange(object):

    def __init__(self):
        self.__hc = bhc.BtccHttpClient()

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











