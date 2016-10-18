from exchange.btcc.btcc_exchange import BTCCExchange
from exchange.exchange import Exchange
import json


def main():

    btcc = BTCCExchange()
    
    #cny_balance = btcc.get_account_balance(currency = Exchange.CNY)
    #print(cny_balance)

    price = 100.00
    amount = 0.001
    order = btcc.buy_btc_limit(price, amount)
    
    #cancel = btcc.cancel_btc_order(order.order_id)
    #print('cancal = ', cancel)

    order_list = btcc.get_btc_orders()

    btcc.cancel_btc_orders(order_list)



    
    

if __name__ == '__main__':
    main()