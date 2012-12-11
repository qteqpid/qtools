#!/usr/bin/python
# coding:utf-8
# logger
# Author: qteqpid.pku@gmail.com

import logging
from Date import *

class L:
    def __init__(self, log_file, log_level):
        self.logger = logging.getLogger()
        self.logger.addHandler(logging.FileHandler(log_file))
        self.logger.setLevel(log_level)

    def getTime(self):
        return "[%s]" % D.getNow()

    def info(self, msg):
        self.logger.info(self.getTime()+" [INFO] "+str(msg))

    def warn(self, msg):
        self.logger.warn(self.getTime()+" [WARN] "+str(msg))

    def error(self, msg):
        self.logger.error(self.getTime()+" [ERROR] "+str(msg))

if __name__=="__main__":
    pass
