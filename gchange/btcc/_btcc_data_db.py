from exchange.btcc.btcc_exchange import BTCCExchange
from peewee import *

from gchange.btcc.btcc_model_db import *
from gchange.btcc.btcc_model_db import db

btcc = BTCCExchange()

def _write_history_data():
    if not HistoryData_db.table_exists():
        HistoryData_db.create_table()
    
    # btcc timestamp = 2011-06-13 13:13:24, id = 1, price = 150, amount = 1, type = buy
    
    while True:
        history_datas = []
        limit = 5000
        # 如果为空, count == 0
        if HistoryData_db.select().count():
            last_data = HistoryData_db.select(HistoryData_db, fn.Max(HistoryData_db.tid)).get()
            history_datas = btcc.get_history_data_by_number(start_order_id = last_data.tid, limit = limit)
        else:
            time = strtime_to_timestamp_10('2016-01-01 00:00:00')
            history_datas = btcc.get_history_data_by_time(time = time, limit = limit)

        with db.atomic() as transaction:  # Opens new transaction.
            try:
                for d in history_datas:
                    data = d.model_adapt()
                    print(d)
                    data.save()
            except Exception as e:
                # Because this block of code is wrapped with "atomic", a
                # new transaction will begin automatically after the call
                # to rollback().
                print('db rollback, e = ', e)
                db.rollback()
                break
        if len(history_datas) < limit:
            break

def history_data_write_db():
    try:
        db.connect()
        print('[WRITE] HistoryData_db')
        _write_history_data()
    except Exception as identifier:
        print(identifier)
    finally:
        db.close()

def history_data_delete_db():
    try:
        db.connect()
        print('[DELETE] HistoryData_db')
        HistoryData_db.delete().execute()
    except Exception as identifier:
        print(identifier)
    finally:
        db.close()



