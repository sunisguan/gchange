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
        self.price = price
        self.amount = amount

    def __cmp__(self, other):
        if self.price > other.price:
            return 1
        elif self.price < other.price:
            return -1
        else:
            return 0


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
