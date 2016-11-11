""" An example for Python Socket.io Client
    Requires: six,socketIO_client    
""" 
from socketIO_client import SocketIO, BaseNamespace
import json
<<<<<<< Updated upstream
import time
import re
import hmac
import hashlib
import base64

import logging
logging.getLogger('socketIO-client').setLevel(logging.DEBUG)


access_key = "<YOUR-ACCESS-KEY>"
secret_key = "<YOUE-SECRET-KEY>"

def get_tonce():
        return int(time.time() * 1000000)

def get_postdata():
        post_data = {}
        tonce = get_tonce()
        post_data['tonce'] = tonce
        post_data['accesskey'] = access_key
        post_data['requestmethod'] = 'post'

        if 'id' not in post_data:
                post_data['id'] = tonce

        #modefy here to meet your requirement
        post_data['method'] = 'subscribe'
        post_data['params'] = ['order_cnybtc', 'order_cnyltc', 'order_btcltc', 'account_info']
        return post_data

def get_sign(pdict):
        pstring = ''
        fields = ['tonce', 'accesskey', 'requestmethod', 'id', 'method', 'params']
        for f in fields:
                if pdict[f]:
                        if f == 'params':
                                param_string=str(pdict[f])
                                param_string=param_string.replace('None', '')
                                param_string=re.sub("[\[\] ]","",param_string)
                                param_string=re.sub("'",'',param_string)
                                pstring+=f+'='+param_string+'&'
                        else:
                                pstring+=f+'='+str(pdict[f])+'&'
                else:
                        pstring+=f+'=&'
        pstring=pstring.strip('&')
        phash = hmac.new(secret_key, pstring, hashlib.sha1).hexdigest()

        return base64.b64encode(access_key + ':' + phash)

class Namespace(BaseNamespace):

    def on_connect(self):
        print('[Connected]')

    def on_disconnect(self):
        print('[Disconnect]')

    def on_ticker(self, *args):
        print('ticker', args)

    def on_trade(self, *args):
        print('trade', args)
        pass

    def on_grouporder(self, *args):
        print('grouporder', args)
        pass

    def on_order(self, *args):
        #print('order', args)
        pass

    def on_account_info(self, *args):
        #print('account_info', args)
        pass

    def on_message(self, *args):
        print('message', args)
        pass

    def on_error(self, data):
        print(data)

socketIO = SocketIO('websocket.btcc.com', 80)
namespace = socketIO.define(Namespace)
namespace.emit('subscribe', 'marketdata_cnybtc')
namespace.emit('subscribe', 'marketdata_cnyltc')
namespace.emit('subscribe', 'marketdata_btcltc')
namespace.emit('subscribe', 'grouporder_cnybtc')
namespace.emit('subscribe', 'grouporder_cnyltc')
namespace.emit('subscribe', 'grouporder_btcltc')

payload = get_postdata()
arg = [json.dumps(payload), get_sign(payload)]
namespace.emit('private', arg)
socketIO.wait(seconds=10)
print 'aaaa'
namespace.disconnect()
=======
from exchange.utils import *

from exchange.btcc._btcc_data_db import *

from datetime import datetime




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


    # btcc timestamp = 2011-06-13 13:13:24, id = 1, price = 150, amount = 1, type = buy 
    # time = strtime_to_timestamp_10('2011-01-01 00:00:00')
    # history_datas = btcc.get_history_data_by_time(time = time, limit = 100)




    '''
    workbook = Workbook(encoding='UTF-8')
    worksheet = workbook.add_sheet('history_data')
    
    if len(history_datas):
        for row_index in range(0, len(history_datas)):
            data = history_datas[row_index]
            worksheet.write(row_index, 0, data.tid)
            worksheet.write(row_index, 1, data.timestamp)
            worksheet.write(row_index, 2, data.price)
            worksheet.write(row_index, 3, data.amount)
            worksheet.write(row_index, 4, data.type)
        workbook.save('/Users/guanyayang/Documents/history_data_out.xls')
    '''

    #history_data_delete_db()

    #history_data_write_db()


    #last = HistoryData_db.select(HistoryData_db, fn.Max(HistoryData_db.tid)).get()
    #print('last = ', last)

    #for d in HistoryData_db.select():
     #  print(d)

    #print(HistoryData_db.select().count())

    import pdb; pdb.set_trace()  # breakpoint dcd8bffc //
    # 获取 tick 数据
    ticker = btcc.get_ticker_btc()
    print(ticker)

    # 获取 ask, bid
    orderbook_list = btcc.get_orderbook_btc()
    print(orderbook_list)

    

    

if __name__ == '__main__':
    main()
>>>>>>> Stashed changes
