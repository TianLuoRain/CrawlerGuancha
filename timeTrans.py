import time
from datetime import datetime, timedelta

import re

current_year = datetime.today().strftime("%Y")


def conv_time(t):
    min = int(re.findall('\d+', t)[0])
    if '秒' in t:
        s = (datetime.now() - timedelta(seconds=min))
    elif '分钟' in t:
        s = (datetime.now() - timedelta(minutes=min))

    elif '小时' in t:
        s = (datetime.now() - timedelta(hours=min))

    elif '天' in t:
        s = (datetime.now() - timedelta(days=min))
    else:
        t += ", " + current_year
        s = datetime.strptime(t, "%m-%d, %Y")
    # return str(int(time.mktime(s.timetuple())))
    scape = int((time.mktime(s.timetuple())))
    # print(scape)
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(scape))


def conv_yest_time(t):
    stri = re.findall('\d+:\d\d', t)[0]
    now = datetime.now() - timedelta(days=1)

    hour = re.split(':', stri)[0]
    minute = re.split(':', stri)[1]
    # print(now)
    return str(now.year)+'-'+str(now.month)+ '-'+str( now.day)+' '+str(hour)+ ':'+str( minute)+ ':00'


def main(t):
    # 非标准格式存在’3分钟前‘ ’昨天 时:分‘ ’月-日 时-分‘ 3种
    if re.findall('.*前', t):
        return conv_time(t)
    elif re.findall('昨天', t):
        return conv_yest_time(t)
    elif re.findall('\d?\d-\d?\d \d?\d:\d\d',t):
        return str(current_year)+'-'+t+':'+'00'
    else:
        return t


