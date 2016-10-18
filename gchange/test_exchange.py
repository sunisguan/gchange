import unittest
from .exchange.btcc.btcc_exchange import BTCCExchange
from .exchange.exchange import Exchange

import logging

class ExchangeTestCase(unittest.TestCase):
    
    def testBtcc(self):

        btcc = BTCCExchange()
        
        btcc.get_account_profile()

        # get btc/ltc/cny balance
        btcc.get_account_balance(Exchange.BTC)
        btcc.get_account_balance(Exchange.LTC)
        btcc.get_account_balance(Exchange.CNY)

        # buy btc/ltc by limit
        price = 100.00
        amount = 0.001
        order = btcc.buy_btc_limit(price, amount)
        btcc.cancel_btc_order(order.order_id)
        order = btcc.buy_btc_limit(price, amount)
        btcc.cancel_btc_orders([order])

        

if __name__ == '__main__': 
    unittest.main()