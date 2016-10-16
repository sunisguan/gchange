from exchange.btcc.model import *
from exchange.btcc.btcc_exchange import BTCCExchange
from service import BTCCService, SerRe
import json
from enum import Enum


def main():
    btcc = BTCCService()
    '''res = btcc.get_account_info(BTCCService.GET_ACCOUNT_INFO_PARAMS['ALL'])

    if res.s:
        account = AccountInfo(userjson = res.res)
        print(account)'''

    '''res = btcc.get_market_depth2()
    market_depth = MarketDepth(res.res)
    print(market_depth)'''

    b = BTCCExchange()
        
    number = Enum('number', 'two')
    print('{}, {}'.format(number.two, number.two.value))
    

if __name__ == '__main__':
    main()