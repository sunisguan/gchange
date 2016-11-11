# -*- coding: utf-8 -*-
import time
import datetime

class TimeUtils(object):
    @classmethod
    def timestamp_to_datetime(cls, t):
        f = '%Y-%m-%d %H:%M:%S.%f'
        s = datetime.datetime.fromtimestamp(int(t)).strftime(f)
        return datetime.datetime.strptime(s, f)