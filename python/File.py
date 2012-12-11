#!/usr/bin/python
# coding:utf-8
# file function collections
# Author: qteqpid.pku@gmail.com

import os
import sys

class F:

    @staticmethod
    def readDir(root, level, stack=[], result=[]):
        pre = "/".join(stack)+"/"
        if pre == "/": pre = ""

        for f in os.listdir(root):
            src = os.path.join(root, f)
            if os.path.isdir(src):
                if f[0:1] == ".": continue
                if level == 1:
                    result.append(pre+f)
                else:
                    stack.append(f)
                    F.readDir(src, level-1, stack, result)
                    stack.pop()

        return result

    @staticmethod
    def readFileToArray(filename):
        result = []
        if os.path.exists(filename):
            fh = open(filename)
            for i in fh:
                result.append(i.rstrip())
            fh.close()
        return result

if __name__=="__main__":
    print F.readDir(os.getcwd(), 2)
    print F.readFileToArray("xx")
