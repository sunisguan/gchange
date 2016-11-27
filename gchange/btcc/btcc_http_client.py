# -*- coding: utf-8 -*-

import common

import time
import re
import hmac
import hashlib
import base64
import json

import requests
import threading
import logging

class BtccHttpClient(object):

    ERROR_CODE = {
        -32000: "内部错误",
        -32003: "人民币账户余额不足",
        -32004: "比特币账户余额不足",
        -32005: "挂单没有找到",
        -32006: "无效的用户",
        -32007: "无效的货币",
        -32008: "无效的金额",
        -32009: "无效的钱包地址",
        -32010: "没有找到提现记录",
        -32011: "没有找到充值记录",
        -32017: "无效的类型",
        -32018: "无效的价格",
        -32019: "无效的参数",
        -32025: "订单已取消",
        -32026: "订单已完成",
        -32062: "市场深度不足以成交该市场交易",
        -32065: "无效的货币参数",
        -32086: "订单处理中",
    }

    class MarketParams(object):
        ALL = 'all'
        BTC_CNY = 'btccny'
        LTC_CNY = 'ltccny'
        LTC_BTC = 'ltcbtc'

    class AccountParams(object):
        ALL = 'all'
        Frozen = 'frozen'
        Balance = 'balance'
        Loan = 'loan'
        Profile = 'profile'

    def __init__(self):
        self.__access_key = common.BTCC_ACCESS_KEY
        self.__secret_key = common.BTCC_SECRET_KEY
        self.__lock = threading.Lock()
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    def _get_tonce(self):
        return int(time.time()*1000000)

    def _get_params_hash(self, pdict):
        pstring = ""
        # The order of params is critical for calculating a correct hash
        fields = ['tonce', 'accesskey', 'requestmethod', 'id', 'method', 'params']
        for f in fields:
            if pdict[f]:
                if f == 'params':
                    # Convert list to string, then strip brackets and spaces
                    # probably a cleaner way to do this
                    param_string = re.sub("[\[\] ]", "", str(pdict[f]))
                    param_string = re.sub("'", '', param_string)
                    param_string = re.sub("True", '1', param_string)
                    param_string = re.sub("False", '', param_string)
                    param_string = re.sub("None", '', param_string)
                    pstring += f + '=' + param_string + '&'
                else:
                    pstring += f + '=' + str(pdict[f]) + '&'
            else:
                pstring += f + '=&'
        pstring = pstring.strip('&')

        # now with correctly ordered param string, calculate hash
        phash = hmac.new(self.__secret_key, pstring, hashlib.sha1).hexdigest()
        return phash

    def _request(self, post_data):
        tonce = self._get_tonce()
        post_data['tonce'] = tonce
        post_data['accesskey'] = self.__access_key
        post_data['requestmethod'] = 'post'

        if not 'id' in post_data:
            post_data['id'] = tonce

        pd_hash = self._get_params_hash(post_data)

        # must use b64 encode
        auth_string = 'Basic ' + base64.b64encode(self.__access_key + ':' + pd_hash)
        headers = {'Authorization': auth_string, 'Json-Rpc-Tonce': str(tonce)}

        post_data = json.dumps(post_data)

        with self.__lock:
            resp = requests.post(common.BTCC_CLIENT_URL, headers=headers, data=post_data)

        return self._handle_service_resp(resp=resp, post_data=post_data)

    def _handle_service_resp(self, resp, post_data=None):
        if resp.ok:
            resp_dict = json.loads(resp.text)

            # The id's may need to be used by the calling application,
            # but for now, check and discard from the return dict
            if isinstance(resp_dict, dict) and 'id' in resp_dict.keys() and str(resp_dict['id']) == str(
                    json.loads(post_data)['id']):
                if 'result' in resp_dict:
                    res = resp_dict['result']
                    return res, True
                elif 'error' in resp_dict:
                    code = resp_dict['error']['code']
                    common.logger.error("[HTTP CLIENT ERROR] = %s" % BtccHttpClient.ERROR_CODE[code])
                    return resp_dict['error'], False
            return resp_dict
        else:
            # not great error handling....
            print("status: ", resp.status_code)
            print("reason: ", resp.reason)
            return None

    def get_account_info(self, acount_type = None):
        """
        获取账户信息
        :param acount_type: AccountParams, 默认是ALL
        :return:
        """
        post_data = {'method' : 'getAccountInfo'}
        post_data['params'] = [] if not acount_type else [acount_type]
        return self._request(post_data)

    def get_market_depth2(self, limit = 10, market = 'btccny'):
        """
        获取市场深度
        :param limit: 限制返回的买卖单数目。默认是买单卖单各10条。
        :param market: 可选值BTCCNY、LTCCNY、LTCBTC、ALL 默认值为BTCCNY
        :return: 对象数组：market_depth
        """
        post_data = {'method' : 'getMarketDepth2', 'params' : [limit, market]}
        return self._request(post_data)

    def _buy(self, price, amount, market='btccny'):
        """
        买入，不要直接使用
        :param price: 买 1 比特币/莱特币所用人民币的价格，最多支持小数点后2位精度。若以市价单交易，将 price 设置为 null
        :param amount: 要买的比特币或者莱特币数量, BTC最多支持小数点后 4 位精度, 但最小买卖额度为0.001，LTC最多支持小数点后 3 位精度
        :param market: 可使用[BTCCNY],[LTCCNY],[LTCBTC] 默认值为BTCCNY
        :return order id, {"result":12345,"id":"1"}
        """
        if amount <= 0.0:
            print('买入量必须大于0')
            return
        post_data = {'method' : 'buyOrder2'}
        amount_str = '{0:.4f}'.format(round(amount, 4))
        price_str = '{0:.4f}'.format(round(price, 4)) if price else None
        post_data['params'] = [price_str, amount_str, market]
        return self._request(post_data)

    def buy_limit(self, price, amount, market = MarketParams.BTC_CNY):
        """
        限价买入
        :param price: 买 1 比特币/莱特币所用人民币的价格，最多支持小数点后2位精度
        :param amount: 要买的比特币或者莱特币数量, BTC最多支持小数点后 4 位精度, 但最小买卖额度为0.001，LTC最多支持小数点后 3 位精度
        :param market: 可使用[BTCCNY],[LTCCNY],[LTCBTC] 默认值为BTCCNY
        :return: order id
        """
        if not price:
            print('限价单价格不能为空')
        else:
            return self._buy(price, amount, market)

    def buy_market(self, amount, market= MarketParams.BTC_CNY):
        """
        市价买入
        :param amount: 要买的比特币或者莱特币数量, BTC最多支持小数点后 4 位精度, 但最小买卖额度为0.001，LTC最多支持小数点后 3 位精度
        :param market: 可使用[BTCCNY],[LTCCNY],[LTCBTC] 默认值为BTCCNY
        :return:
        """
        return self._buy(None, amount, market)

    def buy_iceberg_order(self):
        # TODO: buy iceberg order
        pass

    def sell_iceberg_order(self):
        # TODO: sell iceberg order
        pass

    def _sell(self, price, amount, market = MarketParams.BTC_CNY):
        """
        卖出，不要直接使用
        :param price: 卖 1 比特币，莱特币所用人民币的价格，最多支持小数点后 2 位精度。若以市价单交易，将 price 设置为 null
        :param amount: 要卖的比特币数量, BTC最多支持小数点后 4 位精度, 但最小买卖额度为0.001，LTC最多支持小数点后 3 位精度
        :param market: 可选值BTCCNY、LTCCNY、LTCBTC 默认值为BTCCNY
        :return: order id
        """
        if amount <= 0.0:
            print('卖出量必须大于0')
            return

        post_data = {'method' : 'sellOrder2'}
        amount_str = '{0:.4f}'.format(round(amount, 4))
        price_str = '{0:.4f}'.format(round(price, 4)) if price else None
        post_data['params'] = [price_str, amount_str, market]
        return self._request(post_data)

    def sell_limit(self, price, amount, market = MarketParams.BTC_CNY):
        """
        限价卖出
        :param price: 卖 1 比特币，莱特币所用人民币的价格，最多支持小数点后 2 位精度
        :param amount: 要卖的比特币数量, BTC最多支持小数点后 4 位精度, 但最小买卖额度为0.001，LTC最多支持小数点后 3 位精度
        :param market: 可选值BTCCNY、LTCCNY、LTCBTC 默认值为BTCCNY
        :return: order id
        """
        if not price:
            print('限价单价格不能为空')
        else:
            return self._sell(price, amount, market)

    def sell_market(self, amount, market = MarketParams.BTC_CNY):
        """
        市价卖出
        :param amount: 要卖的比特币数量, BTC最多支持小数点后 4 位精度, 但最小买卖额度为0.001，LTC最多支持小数点后 3 位精度
        :param market: 可选值BTCCNY、LTCCNY、LTCBTC 默认值为BTCCNY
        :return: order id
        """
        return self._sell(None, amount, market)

    def cancel(self, order_id, market = MarketParams.BTC_CNY):
        """
        取消挂单
        :param order_id: 要取消的挂单的 ID
        :param market:
        :return:
        """
        if not order_id:
            print('取消订单 id 不能为空')
        else:
            post_data = {'method' : 'cancelOrder'}
            post_data['params'] = [order_id, market]
            return self._request(post_data)

    def request_withdrawal(self, currency, amount):
        """
        发起比特币提现请求,为了安全起见,本方法不提供提现地址参数，默认使用上一次提现的比特币地址。
        假如用户希望更改提现地址，需要首先去网站完成一笔提现，到最新更改的比特币收款地址。
        提现比特币/莱特币的最小额度是0.0201.
        :param currency: 货币代码。可能值：BTC 或 LTC
        :param amount: 提现金额
        :return: 返回提现 ID
        """
        post_data = {'method' : 'requestWithdrawal'}
        post_data['params'] = [currency, amount]
        return self._request(post_data)

    def get_deposits(self, currency = common.CoinSymbol.BTC, pending = True):
        """
        获取用户全部充值记录
        :param currency: 目前支持“BTC”，“LTC”，必填
        :param pending: 默认为“true”。如果为“true”，仅返回尚未入账的比特币或者莱特币充值
        :return:
        """
        post_data = {'method' : 'getDeposits'}
        post_data['params']=[currency, pending]
        return self._request(post_data)

    def get_order(self, order_id):
        """
        获取一个挂单状态
        :param order_id: 挂单 ID
        :return: btcc_model.Order
        """
        return self.get_orders(order_id=order_id)

    def get_orders(self, order_id = None, limit = None, offset = 0, with_detail=False, since = None, open_only = True,
                   market = MarketParams.BTC_CNY):
        """
        获取一组挂单状态
        :param order_id: 获取指定挂单信息
        :param limit: 限制返回的交易记录数，默认为 1000。
        :param offset: 分页索引, 默认为 0.
        :param with_detail: 是否返回订单内每笔交易详情。可选值true,false. 默认值为false，不返回交易详情
        :param since: 限制返回交易记录的起始时间.
        :param open_only: 默认为“true”。如果为“true”，仅返回还未完全成交的挂单。
        :param market: 可选值BTCCNY、LTCCNY、LTCBTC、ALL 默认值为BTCCNY
        :return: btcc_model.Order List
        """
        post_data = {}
        # this combines getOrder and getOrders
        if order_id is None:
            post_data['method'] = 'getOrders'
            post_data['params'] = [open_only, market]
        else:
            post_data['method'] = 'getOrder'
            post_data['params'] = [order_id, market, with_detail]
        return self._request(post_data)

    def get_withdrawal(self, withdrawals_id, currency):
        """
        获取提现状态。
        :param withdrawals_id: 提现 ID。必填
        :param currency: BTC 和 LTC 默认为“BTC”
        :return:
        """
        post_data = {'method' : 'getWithdrawal'}
        withdrawals_id = int(withdrawals_id)
        post_data['params'] = [withdrawals_id, currency]
        return self._service.request(post_data)

    def get_withdrawals(self, currency, pending_only):
        """
        获取全部提现记录。
        :param currency: 目前支持“BTC”，“LTC”, 必填
        :param pending_only: 默认为“true”。如果为“true”，仅返回尚未处理的提现记录
        :return:
        """
        post_data = {'method' : 'getWithdrawals'}
        post_data['params'] = [currency, pending_only]
        return self._request(post_data)

    def get_transactions(self, trans_type = 'all', limit = 10, offset = 0, since = None, sincetype = None):
        """
        获取交易记录。
        :param trans_type: 按类型获取交易记录。默认为“all”（全部）。可用类型包括： 'all|fundbtc| withdrawbtc|withdrawbtcfee|
        refundbtc|fundltc | withdrawltc|withdrawltcfee|refundltc|fundmoney | withdrawmoney| withdrawmoneyfee|
        refundmoney|buybtc|sellbtc|buyltc|sellltc| tradefee| rebate '
        :param limit: 限制返回的交易记录数，默认为 10。
        :param offset: 分页索引, 默认为 0.
        :param since: 取从某一点开始的交易记录, 这一点可以是某个交易号或者Unix时间戳, 默认值为0.
        :param sincetype: 指定since参数的类型，可以是“id”或者“time”，默认值为“time”.
        :return:
        """
        post_data = {'method' : 'getTransactions'}
        post_data['params'] = [trans_type, limit, offset]
        return self._request(post_data)

    def get_archived_order(self, order_id, market = MarketParams.BTC_CNY, withdetail = False):
        """
        获得一个归档订单，归档订单指的是被迁移的且订单状态不会再更改的订单。
        :param order_id: 订单 id
        :param market: 缺省是“BTCCNY”. [ BTCCNY | LTCCNY | LTCBTC ]
        :param withdetail: 是否返回订单详细.
        :return:
        """
        post_data = {'method' : 'getArchivedOrder'}
        post_data['params'] = [order_id, market, withdetail]
        return self._request(post_data)

    def get_archived_orders(self, market=MarketParams.BTC_CNY, limit=200, less_than_order_id=0, withdetail=False):
        """
        获得多个归档订单.
        :param market: 缺省是“BTCCNY”. [ BTCCNY | LTCCNY | LTCBTC | ALL]
        :param limit: 最多获得多少个订单，缺省值是200.
        :param less_than_order_id: 起始order_id，返回结果以order_id从大到小排列，缺省值是0（表示以数据库中的order_id最大值作为起始order_id）.
        :param withdetail: 是否返回此订单对应的详细信息.
        :return:
        """
        post_data = {'method' : 'getArchivedOrders'}
        post_data['params'] = [market, limit, less_than_order_id, withdetail]
        return self._request(post_data)

    def buy_stop_order(self):
        # TODO: buyStopOrder
        pass

    def sell_stop_order(self):
        # TODO: sellStopOrder
        pass

    def get_orderbook(self):
        # TODO: get order book
        print('[{} start...]'.format(self.get_orderbook.__name__))
        #return self._handle_service_resp(requests.request('GET', 'https://pro-data.btcc.com/data/pro/orderbook'))

    def get_ticker(self, market=MarketParams.BTC_CNY):
        """
        返回北京时间昨天早上8点，到今天早上8点的数据
        :param market:
        :return:
        """
        url = "https://data.btcchina.com/data/ticker?market=" + market
        return self._handle_service_resp(requests.request('GET', url))



    def get_history_data(self, limit = 100, since = None, sincetype = None):
        """
        获取历史交易数据
        :param limit:
        :param since:
        :param sincetype:
        :return:
        """
        url = 'https://data.btcchina.com/data/historydata?' + 'limit=' + str(limit)

        if sincetype:
            url += '&sincetype=' + sincetype
        if since:
            url += '&since=' + str(since)
        return self._handle_service_resp(requests.request('GET', url))


