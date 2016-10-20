from ..utils import *

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

class CurrencyBlock(object):
    def __init__(self, currency, symbol, amount, amount_decimal, amount_integer):
        self.currency = currency
        self.symbol = symbol
        self.amount = amount
        self.amount_decimal = amount_decimal
        self.amount_integer = amount_integer

    def __str__(self):
        return 'currency = {}, symbol = {}, amount = {}, amount_decimal = {}, amount_integer = {}'.format(self.currency, self.symbol, self.amount, self.amount_decimal, self.amount_decimal)

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
    def __init__(self, id, status, price, amount_original, currency, amount, avg_price, date, type):
        self.order_id = id
        self.status = status
        self.price = price
        self.amount_original = amount_original
        self.currency = currency
        self.amount = amount
        self.avg_price = avg_price
        self.date = date
        self.type = type


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
    def __init__(self, ltc_amount, btc_amount, cny_amount, market, date, type, trans_id):
        self.ltc_amount = ltc_amount
        self.btc_amount = btc_amount
        self.cny_amount = cny_amount
        self.market = market
        self.date = date
        self.type = type
        self.trans_id = trans_id

class Ticker(object):
    def __init__(self, BidPrice, AskPrice, Open, High, Low, Last, LastQuantity, PrevCls, Volume, Volume24H, Timestamp, ExecutionLimitDown, ExecutionLimitUp):
        self.bid_price = format_number_float4(BidPrice)
        self.ask_price = format_number_float4(AskPrice)
        self.open = format_number_float4(Open)
        self.high = format_number_float4(High)
        # 近24小时内最低价格
        self.low = format_number_float4(Low)
        # 最新成交价格
        self.last = format_number_float4(Last)
        # 最新成交数量
        self.last_quantity= LastQuantity
        # 昨日收盘价
        self.prev_cls = format_number_float4(PrevCls)
        self.volume = format_number_float3(Volume)
        self.volume24H = format_number_float3(Volume24H)
        self.timestamp = Timestamp
        # 价格下限
        self.execution_limit_down = format_number_float4(ExecutionLimitDown)
        # 价格上限
        self.execution_limit_up = format_number_float4(ExecutionLimitUp)

    def __str__(self):
        return ('BidPrice = {0:.4f}, AskPrice = {1:.4f}, Open = {2:.4f}, High = {3:.4f}, Low = {4:.4f}, Last = {5:.4f}, ' + \
        'LastQuantity = {6}, PrevCls = {7:.4f}, Volume = {8:.3f}, Volume24H = {9:.3f}, Timestamp ={10}, ' + \
        'ExecutionLimitDown = {11:.4f}, ExecutionLimitUp = {12:.4f}').format(self.bid_price, self.ask_price, self.open, self.high, self.low, self.last, self.last_quantity, self.prev_cls, self.volume, self.volume24H, timestamp_to_str(self.timestamp), self.execution_limit_down, self.execution_limit_up)

class HistoryData(object):
    def __init__(self, Id, Timestamp, Price, Quantity, Side):
        '''
        id: 交易记录编号
        Timestamp: Unix的时间（秒）自1970年1月1日
        Price: 成交价格
        Quantity: 数量
        Side: Sell=卖 Buy=买
        '''

        self.order_id = Id
        self.timestamp = Timestamp
        self.price = Price
        self.quantity = Quantity
        self.side = Side

    def __str__(self):
        return 'timestamp = {}, id = {}, price = {}, amount = {}, side = {}'.format(timestamp_to_str(self.timestamp), self.order_id, self.price, self.quantity, self.side)
        

