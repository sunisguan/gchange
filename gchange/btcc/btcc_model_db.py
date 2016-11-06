from peewee import *

from gchange.btcc.btcc_model import *


class ModelAdapter(object):
    def model_adapt(self):
        raise NotImplementedError

db = SqliteDatabase('btcc.db')

class HistoryData_db(Model, ModelAdapter):
    tid = IntegerField()
    timestamp = CharField()
    date = DateTimeField()
    amount = FloatField()
    type = CharField()
    price = FloatField()

    class Meta:
        database = db

    def model_adapt(self):
        return HistoryData(self.tid, date = self.timestamp, price = self.price, amount = self.amount, type = self.type)
    
    def __str__(self):
        return ('tid = {}, ' + 'timestamp = {}, ' + 'date = {}, ' + 'price = {}, ' + 'amount = {}, ' + 'type = {}').format(self.tid, self.timestamp, self.date, self.price, self.amount, self.type)