from ..exchange import Exchange
from .service import BTCCService
from .btcc_model import *
from ..utils import timestamp_to_strtime

class BTCCExchange(Exchange):
    '''
    BTCChina exchange

    '''
    def __init__(self):
        self._service = BTCCService()
        self._account = None

        self._temp_order = None

        # {1453947915451: {asks: [], bids: []}}
        self._orderbook = {}

        self._ticker = None

        self._get_account_info()
    
    def service_callback(r, *args, **kwargs):
        # 网络调用的回调函数
        # 把 response 从参数中拿出来
        resp = args[0]

    def _get_account_info(self):
        resp_dict, status = self._service.get_account_info()
        if status:
            self._account = AccountInfo(resp_dict);
        else:
            print('{} fail'.format(self.get_account_info.__name__))

    def get_account_profile(self):
        if not self._account:
            self._get_account_info()
        return self._account.profile
    
    def get_account_balance(self, currency = Exchange.BTC):
        # currency: btc, ltc, cny
        if currency == Exchange.BTC:
            return self._account.get_balance_btc()
        elif currency == Exchange.LTC:
            return self._account.get_balance_ltc()
        else:
            return self._account.get_balance_cny()
    
    def buy_btc_limit(self, price, amount):
        order_id, status = self._service.buy_limit(price, amount, BTCCService.MARKET_PARAMS_BTCCNY)
        return self.get_btc_order(order_id)
    
    def buy_ltc_limit(self, price, amount):
        return self._service.buy_limit(price, amount, BTCCService.MARKET_PARAMS_LTCCNY)
    
    def sell_btc_limit(self, price, amount):
        return self._service.sell_limit(price, amount, BTCCService.MARKET_PARAMS_BTCCNY)
    
    def sell_ltc_limit(self, price, amount):
        return self._service.sell_limit(price, amount, BTCCService.MARKET_PARAMS_LTCCNY)

    def cancel_btc_order(self, order_id):
        res, status = self._service.cancel(order_id, market = BTCCService.MARKET_PARAMS_BTCCNY)
        return res
    def cancel_btc_orders(self, order_list):
        for order in order_list:
            self.cancel_btc_order(order.order_id)
    
    def cancel_ltc_order(self, order_id):
        return self._service.cancel(order_id, BTCCService.MARKET_PARAMS_LTCCNY)

    def get_btc_order(self, order_id):
        order_json, res = self._service.get_orders(order_id)
        return Order(**order_json['order'])
    
    def get_btc_orders(self):
        order_json, res = self._service.get_orders(market = BTCCService.MARKET_PARAMS_BTCCNY)
        order_list = []
        for order in order_json['order']:
            order_list.append(Order(**order))
        return order_list

    def get_orderbook_btc(self):
        # 获取买卖订单，包含所有公开的要价和出价
        res = self._service.get_orderbook();
        # ask卖价
        # bid买价
        # date
        if 'date' in res.keys():
            return OrderbookList(res)
        else:
            print('get orderbook fail')
    
    def _print_orderbook(self):
        for date, value in self._orderbook.items():
            print('date = ', date, '===========================')
            for ask in value['asks']:
                print('[ask][{}]{}'.format(timestamp_to_str(date), ask))
            for bid in value['bids']:
                print('[bid][{}]{}'.format(timestamp_to_str(date), bid))

    def get_ticker_btc(self):
        res = self._service.get_ticker();

        ticker_json = res['ticker']
        if ticker_json:
            self._ticker = Ticker(**ticker_json)
            return self._ticker
        else:
            print('get ticker fail')

    def get_history_data_by_time(self, time, limit = 100):
        resp = self._service.get_history_data(since = time, sincetype = "time", limit = limit)
        history_data = []
        if resp and isinstance(resp, list):
            for data in resp:
                d = HistoryData(**data)
                history_data.append(d)
        return history_data

    def get_history_data_by_number(self, start_order_id, limit = 100):
        # 查询此 order_id 起后面的 limit 条记录
        resp = self._service.get_history_data(since = start_order_id, limit = limit, sincetype = 'id')
        history_data = []
        if resp and isinstance(resp, list):
            for data in resp:
                d = HistoryData(**data)
                history_data.append(d)
        return history_data
    



    

    



        
    
        

    
