from exchange.btcc.btcc_exchange import BTCCExchange
import json


def main():

    btcc = BTCCExchange()

    btcc.get_account_info()
    

if __name__ == '__main__':
    main()