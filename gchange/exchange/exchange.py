from abc import ABC, abstractmethod

BTC = 'BTC'
LTC = 'LTC'
CNY = 'CNY'

class Exchange(ABC):
    BTC = 'BTC'
    LTC = 'LTC'
    CNY = 'CNY'

    def buy_btc_limit(self, price, amount):
        pass