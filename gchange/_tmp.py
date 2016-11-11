from utils import TimeUtils
import datetime

strret = datetime.datetime.fromtimestamp(1478852048).strftime('%Y-%m-%d %H:%M:%S.%f')

ret = datetime.datetime.strptime(strret, '%Y-%m-%d %H:%M:%S.%f')

print type(ret), ret