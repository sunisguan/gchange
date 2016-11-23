# -*- coding: utf-8 -*-
from peewee import *

from gchange.btcc.btcc_model_db import *
import common


class UserProfile(object):
    def __init__(self, username, daily_btc_limit, trade_password_enabled, ltc_withdrawal_address, otp_enabled, api_key_permission, daily_ltc_limit, trade_fee_btcltc, trade_fee, id_verify, ltc_deposit_address, trade_fee_cnyltc, btc_withdrawal_address, btc_deposit_address):
        self.username = username
        self.daily_btc_limit = daily_btc_limit
        self.trade_password_enabled = trade_password_enabled
        self.ltc_withdrawal_address = ltc_withdrawal_address
        self.otp_enabled = otp_enabled
        self.api_key_permission = api_key_permission
        self.daily_ltc_limit = daily_ltc_limit
        self.trade_fee_btcltc = trade_fee_btcltc
        self.trade_fee = trade_fee
        self.id_verify = id_verify
        self.ltc_deposit_address = ltc_deposit_address
        self.trade_fee_cnyltc = trade_fee_cnyltc
        self.btc_withdrawal_address = btc_withdrawal_address
        self.btc_deposit_address = btc_deposit_address

    def __str__(self):
        return '[Profile]: username = {}, daily_btc_limit = {}, trade_password_enabled = {}, ltc_withdrawal_address = {}, otp_enabled = {}, api_key_permission = {}, daily_ltc_limit = {}, trade_fee_btcltc = {}, trade_fee = {}, id_verify = {}, ltc_deposit_address = {}, trade_fee_cnyltc = {}, btc_withdrawal_address = {}, btc_deposit_address = {}'.format(self.username, self.daily_btc_limit, self.trade_password_enabled, self.ltc_withdrawal_address, self.otp_enabled, self.api_key_permission, self.daily_ltc_limit,self.trade_fee_btcltc, self.trade_fee, self.id_verify, self.ltc_deposit_address, self.trade_fee_cnyltc, self.btc_withdrawal_address, self.btc_deposit_address)

class Balance(object):
    def __init__(self, currency, symbol, amount, amount_decimal, amount_integer):
        self.__currency = currency
        self.__symbol = symbol
        self.__amount = amount
        self.__amount_decimal = amount_decimal
        self.__amount_integer = amount_integer

    def get_amount(self):
        return self.__amount

    def __str__(self):
        return 'currency = {}, symbol = {}, amount = {}, amount_decimal = {}, amount_integer = {}'.format(self.__currency, self.__symbol, self.__amount, self.__amount_decimal, self.__amount_decimal)

class AccountInfo(object):
    def __init__(self, userjson = None):
        self.profile = None
        self._balance = {}
        self._frozen = {}
        self._loan = {}

        if userjson:
            if userjson['profile']:
                self.profile = UserProfile(**userjson['profile'])
            if userjson['balance']:
                self._balance = userjson['balance']
            if userjson['frozen']:
                self._frozen = userjson['frozen']
            if userjson['loan']:
                self._loan = userjson['loan']

    def _get_balance(self, type = None):
        return self._balance[type] if type else None

    def get_balance_btc(self):
        return self._get_balance('btc')
    def get_balance_ltc(self):
        return self._get_balance('ltc')
    def get_balance_cny(self):
        return self._get_balance('cny')


    def _get_loan(self, type = None):
        return self._loan[type] if type else None

    def get_loan_btc(self):
        return self._get_loan('btc')
    def get_loan_ltc(self):
        return self._get_loan('ltc')
    def get_loan_cny(self):
        return self._get_loan('cny')

    
    def _get_frozen(self, type = None):
        return self._frozen[type] if type else None

    def get_frozen_btc(self):
        return self._get_frozen('btc')
    def get_frozen_ltc(self):
        return self._get_frozen('ltc')
    def get_frozen_cny(self):
        return self._get_frozen('cny')
    
    
    
    def __str__(self):
        return self.profile.__str__() + '\r[balance]: ' + self._balance.__str__() + '\r[frozen]: ' + self._frozen.__str__() + '\r[loan]: ' + self._loan.__str__() 

class PriceAmount(object):
    def __init__(self, price, amount):
        self.price = format_number_float4(price)
        self.amount = format_number_float3(amount)

    def __cmp__(self, other):
        if self.price > other.price:
            return 1
        elif self.price < other.price:
            return -1
        else:
            return 0

    def __str__(self):
        return 'price = {0:.4f}, amount = {1:.4f}'.format(self.price, self.amount)


class MarketDepth(object):
    def __init__(self, json_data):
        self.ask = []
        self.bid = []
        self._data = None

        if json_data:
            json_data = json_data['market_depth']
            ask_data = json_data['ask']
            for item in ask_data:
                self.ask.append(PriceAmount(item['price'], item['amount']))
            
            ask_data = json_data['bid']
            for item in ask_data:
                self.bid.append(PriceAmount(item['price'], item['amount']))

            self._data = json_data['date']

class Order(object):

    class SubOrder(object):
        def __init__(self, amount, price, dateline):
            self.__amount = amount
            self.__price = price
            self.__dateline = dateline

    def __init__(self, id, status=None, price=None, amount_original=None, currency=None, amount=None, avg_price=None, date=None, type=None):
        self.__order_id = id
        self.__status = status
        self.__price = price
        self.__amount_original = amount_original
        self.__currency = currency
        self.__amount = amount
        self.__avg_price = avg_price
        self.__date = date
        self.__type = type

        self.__sub_orders = []

    def __str__(self):
        str = "order id = {}, status = {}, price = {}".format(self.__order_id, self.__status, self.__price)
        str += ", amount_original = {}, currency = {}, amount = {}".format(self.__amount_original, self.__currency, self.__amount)
        str += ", avg_price = {}, date = {}, type = {}".format(self.__avg_price, self.__date, self.__type)
        return str

    def empty(self):
        return self.status is None

    def get_id(self):
        return self.__order_id

    def get_datetime(self):
        return self.__date

    def get_price(self):
        return self.__price

    def get_amount(self):
        return self.__amount

    def get_amount_original(self):
        return self.__amount_original

    def is_market_order(self):
        return self.__price == 0.0

    def is_limit_order(self):
        return not self.is_market_order()

    def get_status(self):
        return self.__status

    def get_currency(self):
        return self.__currency

    def get_type(self):
        return self.__type

    def get_sub_orders(self):
        return self.__sub_orders

    def get_avg_price(self):
        return self.__avg_price if self.get_price() == 0.0 else self.get_price()

    def set_sub_orders(self, sub_orders):
        # 市价订单被拆分成不同价格成交
        if len(sub_orders):
            self.__sub_orders = []
            self.__sub_orders.append(Order.SubOrder(**order) for order in sub_orders)

    def is_filled(self):
        # 是否成交
        return self.__status == common.OrderStatus.CLOSED and self.__type == common.OrderType.BID

    def is_canceled(self):
        # 是否取消
        return self.__status == common.OrderStatus.CANCELED

    def is_buy(self):
        return self.__type == common.OrderType.BID

    def is_sell(self):
        return self.__type == common.OrderType.ASK

    def get_fee(self):
        return 0.0

class Deposit(object):
    DEPOSIT_STATUS_PENDING = 'pending'
    DEPOSIT_STATUS_COMPLETED = 'completed'
    def __init__(self, status, currency, amount, address, date, deposit_id):
        self.status = status
        self.currency = currency
        self.amount = amount
        self.address = address
        self.date = date
        self.deposit_id = deposit_id

class Transaction(object):
    def __init__(self, ltc_amount, btc_amount, cny_amount, market, date, type, id):
        """
        交易记录
        :param ltc_amount: LTC 交易量
        :param btc_amount: BTC 交易量
        :param cny_amount: CNY 变化量
        :param market: btcc_http_client.MarketParams
        :param date: 交易时间
        :param type: common.TransactionType
        :param trans_id: 交易号
        """
        self.__ltc_amount = ltc_amount
        self.__btc_amount = btc_amount
        self.__cny_amount = cny_amount
        self.__market = market
        self.__date = date
        self.__type = type
        self.__trans_id = id

    def get_btc_amount(self):
        return abs(self.__btc_amount)

    def get_datetime(self):
        return self.__date

    def get_cny_amount(self):
        return abs(self.__cny_amount)

    def get_btc_price(self):
        return abs(round(self.__cny_amount % self.__btc_amount, 2))

    def get_fee(self):
        return 0

    def get_id(self):
        return self.__trans_id

    def get_type(self):
        return self.__type

class Ticker(object):
    def __init__(self, high, low, buy, sell, last, vol, date, vwap, prev_close, open):
        # 近24小时内最高价格
        self.__high = high
        # 近24小时内最低价格
        self.__low = low
        # 最高出价
        self.__buy = buy
        # 最低要价
        self.__sell = sell
        # 最新成交价
        self.__last = last
        # 近24小时内比特币成交量
        self.__vol = vol
        # 最新更新时间戳
        self.__date = date
        # 近24小时内平均成交价
        self.__vwap = vwap
        # 昨日收盘价
        self.__prev_close = prev_close
        # 今日开盘价
        self.__open = open

    def __str__(self):
        s = [
            'high = %s' % self.__high,
            'low = %s' % self.__low,
            'buy = %s' % self.__buy,
            'sell = %s' % self.__sell,
            'last = %s' % self.__last,
            'vol = %s' % self.__vol,
            'date = %s' % self.__date,
            'vwap = %s' % self.__vwap,
            'prev_close = %s' % self.__prev_close,
            'open = %s' % self.__open
        ]
        return '\n'.join(s)

class HistoryData(ModelAdapter):

    def __init__(self, tid, date, price, amount, type):
        '''
        id: 交易记录编号
        Timestamp: Unix的时间（秒）自1970年1月1日, 13位
        Price: 成交价格
        Quantity: 数量
        Side: Sell=卖 Buy=买
        '''
        '''
        date	string	Unix的时间（秒）自1970年1月1日, 10位
        price	string	1个比特币的价格
        amount	string	成交的比特币总量
        tid	string	交易单号
        type	string	表示交易为“买”或者“卖”

        '''

        self.tid = tid
        self._timestamp = date
        self.price = price
        self.amount = amount
        self.type = type

    @property
    def timestamp(self):
        return timestamp_to_strtime_10(self._timestamp)

    def model_adapt(self):
        if HistoryData_db.select().where(HistoryData_db.tid == self.tid).exists():
            return HistoryData_db.get(HistoryData_db.tid == self.tid)
        else:
            return HistoryData_db.create(tid = self.tid, timestamp = self._timestamp, date = self.timestamp, amount = self.amount, type = self.type, price = self.price)

    def __str__(self):
        return 'timestamp = {}, id = {}, price = {}, amount = {}, type = {}'.format(self.timestamp, self.tid, self.price, self.amount, self.type)

class OrderbookList(object):
    '''
    用于 btcc_exchange, get_orderbook_*
    '''
    def __init__(self, json_data):
        # json_data
            # ask卖价
            # bid买价
            # date

        self.ask_bids = {'asks': [], 'bids': []}
        self.date = None
        
        ask = json_data['asks']
        bids = json_data['bids']

        for p, a in ask:
            self.ask_bids['asks'].append(PriceAmount(p, a))
        for p, a in bids:
            self.ask_bids['bids'].append(PriceAmount(p, a))
            
        self.date = timestamp_to_strtime_10(json_data['date'])

    @property
    def asks(self):
        return self.ask_bids['asks']
    
    @property
    def bids(self):
        return self.ask_bids['bids']

    def __str__(self):
        s = self.date + '\n'
        for a in self.asks:
            s += 'asks:'
            s += str(a)
            s += '\n'
        for b in self.bids:
            s += 'bids:'
            s += str(b)
            s += '\n'

        return s
        

