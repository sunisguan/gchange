from ..exchange import Exchange
from .service import BTCCService
from .model import *

class BTCCExchange(Exchange):
    '''
    BTCChina exchange

    '''

    # get_account_info params
    GET_ACCOUNT_INFO_PARAMS = {'ALL': 'all', 'Fronze': 'fronze', 'Balance': 'balance', 'Loan': 'loan', 'Profile': 'profile'}
    # get_market_depth2, buy params
    # market: 可选值BTCCNY、LTCCNY、LTCBTC、ALL 默认值为BTCCNY
    MARKET_PARAMS_ALL = 'all'
    MARKET_PARAMS_BTCCNY = 'btccny'
    MARKET_PARAMS_LTCCNY = 'ltccny'
    MARKET_PARAMS_LTCBTC = 'ltcbtc'

    def __init__(self):
        self._service = BTCCService()

    def get_account_info(self, type = None):
        # type: GET_ACCOUNT_INFO_PARAMS, None == all
        print('[{} start...]'.format(self.get_account_info.__name__))
        post_data = {}
        post_data['method'] = 'getAccountInfo'
        post_data['params'] = [] if not type else [type]
        return self._service.request(post_data) 

    def get_market_depth2(self, limit = 10, market = 'btccny'):
        # limit: 限制返回的买卖单数目。默认是买单卖单各10条。
        # market: 可选值BTCCNY、LTCCNY、LTCBTC、ALL 默认值为BTCCNY
        # return: 对象数组：market_depth
        print('[{} start...]'.format(self.get_market_depth2.__name__))
        post_data = {}
        post_data['method'] = 'getMarketDepth2'
        post_data['params'] = [limit, market]
        return self._service.request(post_data)

    def _buy(self, price, amount, market = 'btccny'):
        '''
        名称 类型 必选？ 描述 price | string | 是 | 买 1 比特币/莱特币所用人民币的价格，最多支持小数点后2位精度。
        若以市价单交易，将 price 设置为 null amount | string| 是 | 要买的比特币或者莱特币数量, BTC最多支持小数点后 4 位精度, 
        但最小买卖额度为0.001，LTC最多支持小数点后 3 位精度 market | string| 否 | 可使用[BTCCNY],[LTCCNY],[LTCBTC] 默认值为BTCCNY
        
        return: order id
        
        '''
        if amount <= 0.0:
            print('买入量必须大于0')
            return
        amount_str = '{0:.4f}'.format(round(amount, 4))
        post_data['method'] = 'buyOrder2'
        price_str = '{0:.4f}'.format(round(price, 4)) if price else None
        post_data['params'] = [price_str, amount_str, market]
        return self._service.request(post_data)

    def buy_limit(self, price, amount, market = 'btccny'):
        print('[{} start...]'.format(self.buy_limit.__name__))
        if not price:
            print('限价单价格不能为空')
        else:
            return self._buy(price, amount, market)
    
    def buy_market(self, amount, market = 'btccny'):
        print('[{} start...]'.format(self.buy_market.__name__))
        return self._buy(None, amount, market)

    def buy_iceberg_order():
        pass
    def sell_iceberg_order():
        pass

    def _sell(self, price, amount, market = 'btccny'):
        '''
        下比特币或莱特币卖单。卖单类型包括市价单和限价单，具体请参照参数表内描述。此方法返回订单号。
        print: 卖 1 比特币，莱特币所用人民币的价格，最多支持小数点后 2 位精度。若以市价单交易，将 price 设置为 null, 必填
        amount: 要卖的比特币数量, BTC最多支持小数点后 4 位精度, 但最小买卖额度为0.001，LTC最多支持小数点后 3 位精度, 必填
        market: 可选值BTCCNY、LTCCNY、LTCBTC 默认值为BTCCNY

        return: order id
        '''
        if amount <= 0.0:
            print('卖出量必须大于0')
            return
        amount_str = '{0:.4f}'.format(round(amount, 4))
        post_data['method'] = 'buyOrder2'
        price_str = '{0:.4f}'.format(round(price, 4)) if price else None
        post_data['params'] = [price_str, amount_str, market]
        return self._service.request(post_data)

    def sell_limit(self, price, amount, market = 'btccny'):
        print('[{} start...]'.format(self.sell_limit.__name__))
        if not price:
            print('限价单价格不能为空')
        else:
            return self._sell(price, amount, market)
    
    def sell_market(self, amount, market = 'btccny'):
        print('[{} start...]'.format(self.sell_market.__name__))
        return self._sell(None, amount, market)

    def cancel(self, order_id, market = 'btccny'):
        # order_id: 要取消的挂单的 ID
        # return: 是否取消成功 true or false
        post_data = {}
        post_data['params'] = [order_id, market]
        return self._service.request(post_data)

    def request_withdrawal(self, currency, amount):
        '''
        发起比特币提现请求,为了安全起见,本方法不提供提现地址参数，默认使用上一次提现的比特币地址。
        假如用户希望更改提现地址，需要首先去网站完成一笔提现，到最新更改的比特币收款地址。 
        提现比特币/莱特币的最小额度是0.0201.

        currency: 货币代码。可能值：BTC 或 LTC
        amount: 提现金额
        return: 返回提现 ID
        '''
        post_data = {}
        post_data['method'] = 'requestWithdrawal'
        post_data['params'] = [currency, amount]
        return self._service.request(post_data)
    
    def get_deposits(self, currency: Exchange.BTC, pending = True):
        # 获得用户全部充值记录。
        # currency: 目前支持“BTC”，“LTC”，必填
        # pending: 默认为“true”。如果为“true”，仅返回尚未入账的比特币或者莱特币充值
        post_data = {}
        post_data['method'] = 'getDeposits'
        post_data['params']=[currency, pending]
        return self._service.request(post_data)

    def get_orders(self, order_id = None, limit = None, offset = 0, with_detail = False, since = None, open_only = True, market = MARKET_PARAMS_BTCCNY):
        '''
        获得一组挂单的状态。
        
        order_id: 获取指定挂单信息
        open_only: 默认为“true”。如果为“true”，仅返回还未完全成交的挂单。
        market: 可选值BTCCNY、LTCCNY、LTCBTC、ALL 默认值为BTCCNY
        limit: 限制返回的交易记录数，默认为 1000。
        offset: 分页索引, 默认为 0.
        since: 限制返回交易记录的起始时间.
        with_detail: 是否返回订单内每笔交易详情。可选值true,false. 默认值为false，不返回交易详情

        '''
        post_data = {}
        # this combines getOrder and getOrders
        if id is None:
            post_data['method']='getOrders'
            post_data['params']=[open_only, market]
        else:
            post_data['method']='getOrder'
            post_data['params']=[id, market,details]
        return self._service.request(post_data)

    def get_withdrawal(self, withdrawals_id, currency):
        '''
        获取提现状态。

        withdrawals_id: 提现 ID。必填
        currency: BTC 和 LTC 默认为“BTC”
        '''
        post_data = {}
        try:
            withdrawals_id = int(withdrawals_id)
            post_data['method'] = 'getWithdrawal'
            post_data['params'] = [withdrawals_id, currency]
            return self._service.request(post_data)
        except expression as identifier:
            return

    def get_withdrawals(self, currency, pending_only):
        '''
        获取全部提现记录。
        currency: 目前支持“BTC”，“LTC”, 必填
        pending_only: 默认为“true”。如果为“true”，仅返回尚未处理的提现记录

        '''
        post_data = {}
        post_data['method']='getWithdrawals'
        post_data['params']=[currency, pending_only]
        return self._service.request(post_data)

    def get_transactions(self, trans_type = 'all', limit = 10, offset = 0, since = None, sincetype = None):
        '''
        获取交易记录。

        trans_type: 按类型获取交易记录。默认为“all”（全部）。可用类型包括： 'all|fundbtc| withdrawbtc|withdrawbtcfee|
        refundbtc|fundltc | withdrawltc|withdrawltcfee|refundltc|fundmoney | withdrawmoney| withdrawmoneyfee|
        refundmoney|buybtc|sellbtc|buyltc|sellltc| tradefee| rebate '
        limit: 限制返回的交易记录数，默认为 10。
        offset: 分页索引, 默认为 0.
        since: 取从某一点开始的交易记录, 这一点可以是某个交易号或者Unix时间戳, 默认值为0.
        sincetype: 指定since参数的类型，可以是“id”或者“time”，默认值为“time”.

        '''
        post_data = {}
        post_data['method'] = 'getTransactions'
        post_data['params'] = [trans_type, limit, offset]
        return self._service.request(post_data)

    def get_archived_order(self, order_id, market='btccny', withdetail = False):
        '''
        获得一个归档订单，归档订单指的是被迁移的且订单状态不会再更改的订单。

        order_id: 订单 id
        market: 缺省是“BTCCNY”. [ BTCCNY | LTCCNY | LTCBTC ]
        withdetail: 是否返回订单详细.

        '''
        post_data = {}
        post_data['method'] = 'getArchivedOrder'
        post_data['params'] = [order_id, market, withdetail]
        return self._service.request(post_data)

    def get_archived_orders(self, market = 'btccny', limit = 200, less_than_order_id = 0, withdetail = False):
        '''
        获得多个归档订单.

        market: 缺省是“BTCCNY”. [ BTCCNY | LTCCNY | LTCBTC | ALL]
        limit: 最多获得多少个订单，缺省值是200.
        less_than_order_id: 起始order_id，返回结果以order_id从大到小排列，缺省值是0（表示以数据库中的order_id最大值作为起始order_id）.
        withdetail: 是否返回此订单对应的详细信息.

        '''
        post_data = {}
        post_data['method']='getArchivedOrders'
        post_data['params']=[market, limit, less_than_order_id, withdetail]
        return self._service.request(post_data)

    def buy_stop_order():
        # buyStopOrder
        pass
    def sell_stop_order():
        # sellStopOrder
        pass


