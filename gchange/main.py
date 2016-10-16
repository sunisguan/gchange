from exchange.btcc.model import *
from service import BTCCService, SerRe
import json

def main():
    btcc = BTCCService()
    res = btcc.get_account_info(BTCCService.GET_ACCOUNT_INFO_PARAMS['ALL'])

    if res.s:
        account = AccountInfo(userjson = res.res)
        print(account)
        
        
    

if __name__ == '__main__':
    main()