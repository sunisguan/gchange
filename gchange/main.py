from exchange.btcc.btcc_exchange import BTCCExchange
from exchange.exchange import Exchange
import json
from exchange.utils import *


def main():

    btcc = BTCCExchange()
    
    #cny_balance = btcc.get_account_balance(currency = Exchange.CNY)
    #print(cny_balance)

    '''price = 100.00
    amount = 0.001
    order = btcc.buy_btc_limit(price, amount)
    
    #cancel = btcc.cancel_btc_order(order.order_id)
    #print('cancal = ', cancel)

    order_list = btcc.get_btc_orders()

    btcc.cancel_btc_orders(order_list)

    #btcc.get_orderbook();
    btcc.get_ticker()'''

    time = time_to_timestamp('2016-08-08 19:10:04:889000', '%Y-%m-%d %H:%M:%S:%f')
    btcc.get_history_data_by_time(time = time, limit = 10)
    

    
    

if __name__ == '__main__':
    main()