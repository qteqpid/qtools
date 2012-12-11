#!/usr/bin/python
# coding=utf-8
# 常见日期时间函数

import time
import datetime

class D:
    @staticmethod
    def getYesterday():
        '''
        获取昨天日期字符串
        '''
        today = datetime.date.today()
        oneday = datetime.timedelta(days=1)
        yesterday = today - oneday
        return str(yesterday)

    @staticmethod
    def getToday():
        '''
        获取今天日期字符串
        '''
        return str(datetime.date.today())

    @staticmethod
    def getNow():
        '''
        获取当前时间，精确到秒
        '''
        now = datetime.datetime.now()
        return now.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def getWeekday():
        '''
        获取星期几,1表示周一
        '''
        d = datetime.date.today()
        return d.isoweekday()

    @staticmethod
    def getLastHour(format = '%Y-%m-%d %H'):
        '''
        获取前一小时的时间字符串
        '''
        return D.getTimeStr(format,time.time()+3600*7)

    @staticmethod
    def getNowHour(format = '%Y-%m-%d %H'):
        '''
        获取当前小时的时间字符串
        '''
        return D.getTimeStr(format,time.time()+3600*8)

    @staticmethod
    def getTimeStamp(str, format):
        '''
        获取时间字符串对应的时间戳
        '''
        return int(time.mktime(time.strptime(str,format)))

    @staticmethod
    def getTimeStr(format, ts):
        '''
        获取时间戳对应的时间字符串表示
        '''
        return time.strftime(format, time.gmtime(ts))

    @staticmethod
    def getDayBefore(n=0):
        '''
        如果n大于0，表示之前的日期，反之亦然
        日期格式是"YYYY-MM-DD"
        '''
        if(n>0):
            return str(datetime.date.today()-datetime.timedelta(days=n))
        else:
            n = abs(n)
            return str(datetime.date.today()+datetime.timedelta(days=n))

if __name__ == '__main__':
    print "D.getYesterday():",D.getYesterday()
    print "D.getToday():",D.getToday()
    print "D.getNow():",D.getNow()
    print "D.getWeekday():",D.getWeekday()
    print "D.getLastHour():",D.getLastHour()
    print "D.getNowHour():",D.getNowHour()
    print "D.getTimeStamp('2012-09-12','%Y-%m-%d'):",D.getTimeStamp('2012-09-12','%Y-%m-%d')
    print "D.getDayBefore(1):",D.getDayBefore(1)
