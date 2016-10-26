from peewee import *

from btcc_model import *

class HistoryData_db(Model):
    tid = CharField()
    timestamp = CharField()
    date = DateField()
    amount = FloatField()
    type = CharField()

    class Meta:
        database = db

    def convert(self):
        return HistoryData(self.tid, date = self.timestamp, price = self.price, amount = self.amount, type = self.type)