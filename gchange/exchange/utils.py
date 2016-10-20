import datetime
import time

def format_number_float4(num):
    return round(num, 4)

def format_number_float3(num):
    return round(num, 3)

def timestamp_to_str(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp) / 1000.0).strftime('%Y-%m-%d %H:%M:%S:%f')

def time_to_timestamp(t, format):
    # '%Y-%m-%d %H:%M:%S:%f'
    return time.mktime(datetime.datetime.strptime(t, format).timetuple())