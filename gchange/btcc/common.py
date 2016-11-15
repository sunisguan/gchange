from pyalgotrade import broker
import pyalgotrade.logger

BTCC_ACCESS_KEY = "26a5a3c0-5aab-4315-8326-28fc154905ee"
BTCC_SECRET_KEY = "9478bc4f-835d-440c-bf77-6ee96057934b"
BTCC_CLIENT_URL = "https://api.btcc.com/api_trade_v1.php"

logger = pyalgotrade.logger.getLogger("btcc")

class CoinSymbol(object):
    BTC = 'btc'
    LTC = 'ltc'
    CNY = 'cny'
    COIN_SYMBOLS = [BTC, LTC, CNY]

class OrderType(object):
    BID = 'bid'
    ASK = 'ask'

class OrderStatus(object):
    OPEN = 'open'
    CANCELED = 'cancelled'

class TransactionType(object):
    ALL = 'all'

    FUND_BTC = 'fundbtc'
    WITHDRAW_BTC = 'withdrawbtc'
    WITHDRAW_BTC_FEE = 'withdrawbtcfee'
    REFUND_BTC = 'refundbtc'

    BUY_BTC = 'buybtc'
    SELL_BTC = 'sellbtc'
    TRADE_FEE = 'tradefee'


class BTCTraits(broker.InstrumentTraits):
    def roundQuantity(self, quantity):
        return round(quantity, 8)