#!/usr/bin/python
# coding:utf-8
# mail
# Author: qteqpid.pku@gmail.com

import os
import smtplib
from Date import *

class M:
    def __init__(self, host = 'smtp.ym.163.com', port=25, user='noreply@imeiding.com', passwd='7AceRqX1Az', to='zhanggl@instreet.cn'):
        self.is_connect = True
        self.from_mail = user
        self.to_mail = to
        self.setIp('localhost')

        try:
            self.smtp = smtplib.SMTP()
            self.smtp.connect(host, port)
            self.smtp.login(user, passwd)
        except Exception,m:
            self.is_connect = False
            self.error = m

    def is_connected(self):
        return self.is_connect == True

    def get_error(self):
        return self.error;

    def setIp(self, ip):
        self.ip = ip

    def genMsg(self, content):
        return "[%s]\t[%s]\t%s" %(D.getNow(), self.ip, content)

    def send(self, subject, content):
        if self.is_connect:
            msg = 'Content-Type: text/plain; charset="utf-8"\r\nFrom: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s' % (self.from_mail, self.to_mail, subject, self.genMsg(content))
            self.smtp.sendmail(self.from_mail, self.to_mail, msg)
            self.smtp.close()

if __name__=="__main__":
    m = M()
    m.send('test python','ok')
