class Currency(object):

    CurrencyName = ('BTC', 'LTC', 'CNY')

    def __init__(self, currency: str = None, symbol: str = None, amount: float = 0.0, amount_decimal: float = 0.0, amount_integer: float = 0.0):
        self.currency = currency
        self.symbol = symbol
        self.amount = amount
        self.amount_decimal = amount_decimal
        self.amount_integer = amount_integer

    def __str__(self):
        return 'Currenty: currency = {}, symbol = {}, amount = {}, amount_decimal = {}, amount_integer = {}'.format(self.currency, self.symbol, self.amount, self.amount_decimal, self.amount_integer)

class Frozen(object):
    def __init__(self, currency: str = None, symbol: str = None, amount: float = 0.0, amount_decimal: int = 0, amount_integer: int = 0):
        self.currency = currency
        self.symbol = symbol
        self.amount = amount
        self.amount_decimal = amount_decimal
        self.amount_integer = amount_integer

class Profile(object):
    def __init__(self, username: str = None, daily_btc_limit: int = 0, trade_password_enabled: bool = false, ltc_withdrawal_address: str = None, otp_enabled: bool = false, api_key_permission: int = 0, daily_ltc_limit: int = 0, trade_fee_btcltc: int = 0, trade_fee: int = 0, id_verify: int = 0, ltc_deposit_address: str = None, trade_fee_cnyltc: int = 0, btc_withdrawal_address: str = None, btc_deposit_address: str = None):
        
        self.username: str = username

        self.trade_password_enabled: bool = trade_password_enabled

        self.otp_enabled: str = otp_enabled

        self.api_key_permission: int = api_key_permission

        self.trade_fee_btcltc: int = trade_fee_btcltc

        self.id_verify = id_verify

        
        self.daily_btc_limit: int = daily_btc_limit

        self.trade_fee: int = trade_fee
        
        self.btc_withdrawal_address: str = btc_withdrawal_address

        self.btc_deposit_address: str = btc_deposit_address


        self.daily_ltc_limit: int = daily_ltc_limit

        self.ltc_withdrawal_address: str = ltc_withdrawal_address

        self.ltc_deposit_address: str = ltc_deposit_address

        self.trade_fee_cnyltc: str = trade_fee_cnyltc

        self.frozen: dict = {}
        self.loan: dict = {}
        self.balance: dict = {}




        
        

        